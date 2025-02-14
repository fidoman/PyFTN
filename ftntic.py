#!/usr/bin/python3 -bb

import sys
import os
import re
import zlib
import hashlib
import datetime
import json
import time

import ftnconfig
import ftnaccess
import ftnimport

import postgresql

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
  def __init__(self, msg, filename):
    BadTic.__init__(self, msg)
    self.filename = filename

def get_single(t, k, conv=None, remove=True):
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
  if remove:
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


def read_tic(f):
  if f[-4:].lower()!=".tic":
    raise BadTic("it should be .tic file")
  ticdata = {}
  for l in open(f, "r", encoding=ftnconfig.TIC_CHARSET):
    op, data = re.split("\s+", l, 1)
    data = data.strip()
#    print (op, ">>", data)
    ticdata.setdefault(op.upper(), []).append(data)
  return ticdata

def sz_crc32(fn):
  f=open(fn, "rb")
  s, c = sz_crc32fd(f)
  f.close()
  return s, c

def sz_crc32fd(fd):
  checksum=0
  fsize = 0
  while(True):
    z=fd.read(4*1024*1024)
    fsize += len(z)
    if not z:
      break
    checksum=zlib.crc32(z, checksum)
  return fsize, "%08X"%checksum

def sz_crc32s(s):
  fsize = len(s)
  checksum=zlib.crc32(s, 0)
  return fsize, "%08X"%checksum


def find_file(name, path):
  n1=os.path.join(path, name)
  if os.path.exists(n1):
    return n1
  n1=os.path.join(path, name.lower())
  if os.path.exists(n1):
    return n1
  n1=os.path.join(path, name.upper())
  if os.path.exists(n1):
    return n1
  raise NoFile("no match for %s at %s"%(name, path))

def find_matching_file(filepath, name, size, crc):
  """ search in the directory for file with similar name and matching size and CRC """
  # if size and CRC not specified then require strict name matching
#  print(crc); os.abort()

  filepath=os.path.join(filepath, crc.lower())

  files = os.listdir(filepath)
  candidates=[]
  for f in files:
    if f==name or f.startswith(name+"."):
      candidates.append(f)
  if not candidates:
    for f in files:
      if f.lower()==name.lower() or f.lower().startswith(name.lower()+"."):
        candidates.append(f)
  if not candidates:
    for f in files:
      if name.lower().startswith(f.lower()):
        candidates.append(f)

  print(name, candidates)
  for c in candidates:
    cf = os.path.join(filepath, c)
    print(c)
    fsz, fcrc = sz_crc32(cf)
    print(fsz, fcrc)
    if fsz == size and fcrc==crc:
      print("exact match")
      return cf
    if size is None and fcrc==crc:
      print("match bases on CRC (size unknown)")
      return cf

  return None


def import_tic(db, fullname, expect_addr=None, import_utime=None, ticdata=None, ignore_pw=False, skip_access_check=False):
  " specify older import_utime value to make imported file the status of aarchive "
  # if "TO" is present
  #   get from links with matching from and to addresses and verify password
  # if "TO" is absent
  #   get to and password from links by from. if two rows are fetched - refuse tic
  #
  # in both cases refuse tic if no row fetched - tics are allowed for password links only
  if ticdata is None:
    filepath, filename = os.path.split(fullname)
    ticdata = read_tic(fullname)
  else:
    filepath = os.path.dirname(fullname)

  tic_src = get_optional(ticdata, "FROM")
  print ("TIC from:", tic_src)
  if tic_src is None:
    tic_src=expect_addr

  tic_dest = get_optional(ticdata, "TO")
  print ("TIC to", tic_dest)

  if tic_src is None and tic_dest is None and skip_access_check:
    print ("Importing non-FTN file")
    src_id = None
    dest_id = None

  else:

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
      q_args.append(dest_id)
    else:
      dest_id = None

    #print (q)
    #print (q_args)

    possible_links = db.prepare(q)(*q_args)
    if len(possible_links) > 1:
      raise WrongTic("ambiguos link %s->%s"%(str(tic_src),str(tic_dest)))

    if len(possible_links) == 0:
      raise WrongTic("no matching link %s->%s"%(str(tic_src),str(tic_dest)))

    src_id, dest_id, authinfo = possible_links[0]
    pw = authinfo.find("RobotsPassword").text

    print ("TIC src_id, dst_id, pw:", src_id, dest_id, pw)

    if not ignore_pw:
      tic_passw = get_single(ticdata, "PW")
      if not ftnaccess.check_pw(pw, tic_passw):
        raise WrongTic("invalid password [%s] for %s"%(tic_passw,tic_src))

  # source and destination verified, now try to find file
  # but before we should check if link can post to specified area
  area = get_single(ticdata, "AREA").upper() # FTN areas must be uppercase
  print("TIC area:", area)
  if not skip_access_check:
    maypost = ftnaccess.may_post(db, src_id, ("fileecho", area))
    if not maypost:
      raise WrongTic("%s may not post to %s"%(tic_src, area))

  fname = os.path.split(get_single(ticdata, "FILE"))[1]

  try:
    fsize = get_single(ticdata, "SIZE", int)
  except BadTic:
    fsize = None

  fcrc = get_single(ticdata, "CRC", remove=False)

  print ("TIC name, size, crc:", fname, fsize, fcrc)
  ffullname=find_matching_file(filepath, fname, fsize, fcrc)

  if not os.path.exists(ffullname):
    raise NoFile("file %s does not exists"%ffullname)

  if fsize is not None and os.path.getsize(ffullname)!=fsize:
    raise NoFile("file %s size != %d"%(ffullname, fsize))

  fsize, checksum = sz_crc32(ffullname)

  if checksum != fcrc.upper():
    raise NoFile("file %s crc32 %s != %s"%(ffullname, checksum, fcrc))

  print ("file matches")
  # >>> LOCK FILEECHOES POSTINGS
  if db.FECHOIMPORTLOCK is None:
    db.FECHOIMPORTLOCK=db.prepare("select oid from pg_class where relname='file_post'").first()
  with postgresql.alock.ExclusiveLock(db, db.FECHOIMPORTLOCK, 0):
    # calculate hash
    # verify if it exists in database
    # if not, post as new (new blob, new name, new destination)
    # if yes, register new name (if differ) and destination for file

    # check if it is not duplicate tic
    # select posting of same origin, area, filename, origin_record
    # if any has same filesize and hash - compare content and drop duplicate

    tic_origin = get_optional(ticdata, "ORIGIN")
    if tic_origin:
      with ftnimport.session(db) as sess:
        tic_origin_id = sess.check_addr("node", tic_origin)
    else:
      tic_origin_id = None

    area_id = ftnconfig.get_addr_id(db, db.FTN_domains["fileecho"], area)

    try:
      tic_originrec = get_first(ticdata, "PATH")
    except BadTic as e:
      print ("PATH is missing, no dupe checking")
      print (e)
      tic_originrec = None

    if tic_originrec:
      print("check if tic is first %s %d %s %s"%((tic_origin, area_id, fname, tic_originrec)))

      for prev_f, prev_l, prev_h, prev_p in db.prepare("select f.id, f.length, f.sha512, p.id from files f inner join file_post p ON p.filedata=f.id "
          "where p.origin=$1 and p.destination=$2 and p.filename=$3 and p.origin_record=$4")(tic_origin_id, area_id, fname, tic_originrec):
        os.rename(ffullname, ffullname+".dup")
        if not fullname.endswith(".faketic"):
          os.rename(fullname, fullname+".dup")
        raise DupPost("similar posting %d, abandom"%prev_p, ffullname)
        # tic with the same first record of PATH - the same posting

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
          print("created lo", lo,end='')
          lo_handle=sess.db.prepare("select lo_open($1, 131072)").first(lo)
          f=open(ffullname, "rb")
          while(True):
            z=f.read(262144)
            if not z:
              break
            print(".", end='', flush=True)
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
    is_with_name = db.prepare("select id from files where $1 = ANY(names) and id=$2").first(fname, f_id)
    if not is_with_name:
      fnameslen = int(db.prepare("select array_upper(names, 1) from files where id=$1").first(f_id) or 0)
      db.prepare("update files set names[$1]=$2 where id=$3")(fnameslen+1, fname, f_id)

    if import_utime is None:
      utime = int(time.mktime(time.gmtime())) # convert_post  time to float and use fractions if you have rate more than one file per some seconds 
    else:
      utime = int(import_utime)

    print ("post_time=", utime)

    db.prepare("insert into file_post (filedata, origin, destination, recv_from, recv_as, recv_timestamp, origin_record, filename, other, post_time) "
                    "values ($1, $2, $3, $4, $5, $6, $7, $8, $9, free_posttime($10))")\
      (f_id, tic_origin_id, area_id, src_id, dest_id, datetime.datetime.now(datetime.timezone.utc), tic_originrec, fname, json.dumps(ticdata), utime)
    print ("inserted successfully")
    print ("unlink", ffullname)
    os.unlink(ffullname)
    if not fullname.endswith(".faketic"):
      print ("unlink", fullname)
      os.unlink(fullname)

  # <<< UNLOCK FILEECHOES POSTINGS

def make_tic(t_from, t_to, t_pw, t_area, t_origin, t_file, t_size, t_crc, t_other):
  # CRC must be extracted from other by caller or regenerated
  tic="""FROM %s\r
TO %s\r
PW %s\r
AREA %s\r
ORIGIN %s\r
FILE %s\r
SIZE %d\r
CRC %s\r
"""%(t_from, t_to, t_pw, t_area, t_origin or 'UNKNOWN', t_file, t_size, t_crc)
  for k, v in t_other.items():
    for v1 in v:
      tic += k+" "+v1.replace("\n", " ")+"\r\n"

  return tic.encode(ftnconfig.TIC_CHARSET)


if __name__=="__main__":
  db = ftnconfig.connectdb()
  if len(sys.argv)<2:
    print ("specify file name of tic file to process")
    exit (-1)

  fullname = sys.argv[1]

  if len(sys.argv)>2:
    expect_addr = sys.argv[2]
  else:
    expect_addr = None

  if len(sys.argv)>3:
    print ("too many parameters")
    exit (-2)

  import_tic(db, fullname, expect_addr)
