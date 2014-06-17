#!/usr/local/bin/python3 -bb

import sys
import os
import re
import zlib
import hashlib
import datetime
import json

import ftnconfig
import ftnaccess
import ftnimport

skip_access_check = True

if len(sys.argv)<2:
  print ("specify file name of tic file to process")
  exit (-1)

fullname = sys.argv[1]
filepath, filename = os.path.split(fullname)

if len(sys.argv)>2:
  expect_addr = sys.argv[2]
else:
  expect_addr = None

if len(sys.argv)>3:
  print ("too many parameters")
  exit (-2)

print(filepath, filename, expect_addr)

if not filename.lower().endswith(".tic"):
  print ("this should be .tic file")
  exit (-3)

# read tic
# if format is wrong rename to .bad
# find and open correspondig file (check CRC)
# if OK push to database and remove
# if no matching file check tic age
# if greater that TICWAIT rename to .bad
# else leave as is

class BadTic(Exception):
  pass

class WrongTic(BadTic):
  pass

class NoFile(BadTic):
  pass

class DupPost(BadTic):
  pass


def get_single(t, k, conv=None):
  x = t.get(k)
  if not x:
    raise BadTic("tic does not have required field %s"%k)
  if len(x)>1:
    raise BadTic("tic has not single field %s"%k)
  if conv:
    try:
      r = conv(x[0])
    except:
      raise BadTic("cannot use value in field %s"%k)
  else:
    r = x[0]
  del t[k]
  return r

def get_optional(t, k, conv=None):
  x = t.get(k)
  if not x:
    return None
  if len(x)>1:
    raise BadTic("tic has not single field %s"%k)
  if conv:
    try:
      r = conv(x[0])
    except:
      raise BadTic("cannot use value in field %s"%k)
  else:
    r = x[0]
  del t[k]
  return r

def get_first(t, k):
  x = t.get(k)
  if not x:
    raise BadTic("tic does not have required field %s"%k)
  return x[0]


tic = open(fullname, "r", encoding="cp866")
ticdata = {}
for l in tic:
  op, data = re.split("\s+", l, 1)
  data = data.strip()
#  print (op, ">>", data)
  ticdata.setdefault(op.upper(), []).append(data)

db = ftnconfig.connectdb()

try:
  # need to change it
  # if "TO" is present
  #   get from links with matching from and to addresses and verify password
  # if "TO" is absent
  #   get to and password from links by from. if two rows are fetched - refuse tic
  #
  # in both cases refuse tic if no row fetched - tics are allowed for password links only

  tic_src = get_optional(ticdata, "FROM")
  print ("from", tic_src)
  if tic_src is None:
    tic_src=expect_addr

  tic_dest = get_optional(ticdata, "TO")
  print ("to", tic_dest)

  q="select l.address, l.my, l.authentication from links l"
  q_args=[]
  if tic_src:
    src_id = ftnconfig.get_addr_id(db, db.FTN_domains["node"], tic_src)
    q += (" and" if q_args else " where") + " address=$%d"%(len(q_args)+1)
    q_args.append(src_id)
  else:
    src_id = None

  if tic_dest:
    dest_id = ftnconfig.get_addr_id(db, db.FTN_domains["node"], tic_dest)
    q += (" and" if q_args else " where") + " my=$%d"%(len(q_args)+1)
    q_args.append(src_id)
  else:
    dest_id = None

  print (q)
  print (q_args)

  possible_links = db.prepare(q)(*q_args)
  if len(possible_links) > 1:
    raise WrongTic("ambiguos link %s->%s"%(str(tic_src),str(tic_dest)))

  if len(possible_links) == 0:
    raise WrongTic("no matching link %s->%s"%(str(tic_src),str(tic_dest)))

  src_id, dest_id, authinfo = possible_links[0]
  pw = authinfo.find("RobotsPassword").text

  print (src_id, dest_id, pw)

  tic_passw = get_single(ticdata, "PW")
  if tic_passw!=pw:
    raise WrongTic("invalid password for %s"%tic_src)

  # source and destination verified, now try to find file
  # but before we should check if link can post to specified area
  area = get_single(ticdata, "AREA")
  print (area)
  maypost = ftnaccess.may_post(db, tic_src, ("fileecho", area))
  if not skip_access_check and not maypost:
    raise WrongTic("%s may not post to %s"%(tic_src, area))

  fname = os.path.split(get_single(ticdata, "FILE"))[1]

  try:
    fsize = get_single(ticdata, "SIZE", int)
  except BadTic:
    fsize = None

  fcrc = get_single(ticdata, "CRC")

  print (fname, fsize, fcrc)
  ffullname=os.path.join(filepath, fname)
  if not os.path.exists(ffullname):
    raise NoFile("file %s does not exists"%ffullname)

  if fsize is not None and os.path.getsize(ffullname)!=fsize:
    raise NoFile("file %s size != %d"%(ffullname, fsize))

  checksum=0
  f=open(ffullname, "rb")
  fsize = 0
  while(True):
    z=f.read(262144)
    fsize += len(z)
    if not z:
      break
    checksum=zlib.crc32(z, checksum)
  f.close()
  if "%08X"%checksum != fcrc:
    raise NoFile("file %s crc32 %s != %s"%(ffullname, checksum, fcrc))

  print ("file matches")
  # >>> LOCK FILEECHOES POSTINGS

  # calculate hash
  # verify if it exists in database
  # if not, post as new (new blob, new name, new destination)
  # if yes, register new name (if differ) and destination for file

  # check if it is not duplicate tic
  # select posting of same origin, area, filename, origin_record
  # if any has same filesize and hash - compare content and drop duplicate

  tic_origin = get_single(ticdata, "ORIGIN")
  tic_origin_id = ftnconfig.get_addr_id(db, db.FTN_domains["node"], tic_origin)
  area_id = ftnconfig.get_addr_id(db, db.FTN_domains["fileecho"], area)
  tic_originrec = get_first(ticdata, "PATH")

  print("check if tic is first %s %d %s %s"%((tic_origin, area_id, fname, tic_originrec)))

  for prev_f, prev_l, prev_h, prev_p in db.prepare("select f.id, f.length, f.sha512, p.id from files f inner join file_post p ON p.filedata=f.id "
        "where p.origin=$1 and p.destination=$2 and p.filename=$3 and p.origin_record=$4")(tic_origin_id, area_id, fname, tic_originrec):
    raise DupPost("similar posting %d, abandom"%prev_p)
    # not sure would one check here if file content is different

  sha512 = hashlib.new("sha512")
  f=open(ffullname, "rb")
  while(True):
    z=f.read(262144)
    if not z:
      break
    sha512.update(z)
  f.close()
  print(sha512.hexdigest())

  oldf_id = db.prepare("select id from files where sha512=$1").first(sha512.digest())
  if oldf_id is None:
    print("new file content")
    if fsize<=262144:
      print ("save as bytea")
      newf_id = db.prepare("insert into files (length, sha512, content) values ($1, $2, $3) returning id").first(fsize, sha512.digest(), open(ffullname, "rb").read())
    else:
      print ("save as large object")
      with ftnimport.session(db) as sess:
        lo=sess.db.prepare("select lo_create(0)").first()
        print("created lo", lo)
        lo_handle=sess.db.prepare("select lo_open($1, 131072)").first(lo)
        f=open(ffullname, "rb")
        while(True):
          z=f.read(262144)
          if not z:
            break
          if sess.db.prepare("select lowrite($1, $2)").first(lo_handle, z) != len(z):
            raise Exception("error writing file data to database")
        f.close()
        if sess.db.prepare("select lo_close($1)").first(lo_handle) != 0:
          raise Exception("error closing large object")

        newf_id = db.prepare("insert into files (length, sha512, lo) values ($1, $2, $3) returning id").first(fsize, sha512.digest(), lo)

    f_id = newf_id
  else:
    print("use old", oldf_id)
    f_id = oldf_id

  # add name for filedata
  is_with_name = db.prepare("select id from files where $1 = ANY(names)").first(fname)
  if not is_with_name:
    fnameslen = int(db.prepare("select array_upper(names, 1) from files where id=$1").first(f_id) or 0)
    db.prepare("update files set names[$1]=$2")(fnameslen+1, fname)

  db.prepare("insert into file_post (filedata, origin, destination, recv_from, recv_timestamp, origin_record, filename, other) values ($1, $2, $3, $4, $5, $6, $7, $8)")\
    (f_id, tic_origin_id, area_id, ftnconfig.get_link_id(db, tic_src), datetime.datetime.now(datetime.timezone.utc), tic_originrec, fname, json.dumps(ticdata))
  print ("inserted successfully")
  os.unlink(ffullname)
  os.unlink(fullname)

  # <<< UNLOCK FILEECHOES POSTINGS

except DupPost as e:
  print (e)
  os.rename(ffullname, ffullname+".dup")
  os.rename(fullname, fullname+".dup")

except BadTic as e:
  print (e)

