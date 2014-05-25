#!/usr/local/bin/python3 -bb

import sys
import os
import re
import zlib

import ftnconfig
import ftnaccess

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

def get_single(t, k):
  x = t.get(k)
  if not x:
    raise BadTic("tic does not have required field %s"%k)
  if len(x)>1:
    raise BadTic("tic has not single field %s"%k)
  return x[0]


tic = open(fullname, "r", encoding="cp866")
ticdata = {}
for l in tic:
  op, data = re.split("\s+", l, 1)
  data = data.strip()
#  print (op, ">>", data)
  ticdata.setdefault(op.upper(), []).append(data)

print (ticdata)
db = ftnconfig.connectdb()

try:
  tic_dest = get_single(ticdata, "TO")
  print ("to", tic_dest)
  if tic_dest != ftnconfig.ADDRESS:
    raise WrongTic("tic for %s"%tic_dest)

  tic_src = get_single(ticdata, "FROM")
  print ("from", tic_src)
  if expect_addr:
    if tic_src!=expect_addr:
      raise WrongTic("source address do not match expected")
  else:
    passw = get_single(ticdata, "PW")
    linkpassw = ftnconfig.get_link_password(db, tic_src)
    if passw!=linkpassw:
      raise WrongTic("invalid password for %s"%tic_src)

  # source and destination verified, now try to find file
  # but before we should check if link can post to specified area
  area = get_single(ticdata, "AREA")
  print (area)
  maypost = ftnaccess.may_post(db, tic_src, ("fileecho", area))
  if not maypost:
    raise WrongTic("%s may not post to %s"%(tic_src, area))

  fname = os.path.split(get_single(ticdata, "FILE"))[1]
  fsize = get_single(ticdata, "SIZE")
  fcrc = get_single(ticdata, "CRC")

  print (fname, fsize, fcrc)
  ffullname=os.path.join(filepath, fname)
  if not os.path.exists(ffullname):
    raise NoFile("file %s does not exists"%ffullname)

  if str(os.path.getsize(ffullname))!=fsize:
    raise NoFile("file %s size != %s"%(ffullname, fsize))

  checksum=0
  f=open(ffullname, "rb")
  while(True):
    z=f.read(262144)
    if not z:
      break
    checksum=zlib.crc32(z, checksum)
  f.close()
  if "%08X"%checksum != fcrc:
    raise NoFile("file %s crc32 %s != %s"%(ffullname, checksum, fcrc))

  print ("file matches")

except BadTic as e:
  print (e)
