#!/usr/local/bin/python3 -bb

import os

import ftnconfig
import ftntic

from fechoimport import read_info

db=ftnconfig.connectdb()

for l in open("post_s.dat"):
  ts, t, fn = l.rstrip().split("\t")
  print (ts, t, fn)
  if t=="del":
    print ("delete", fn, "and info and desc")
    exit()
  elif t=="tic":
    print ("tic=", fn)
    ftntic.import_tic(db, fn, import_utime=ts)
  elif t=="farea":
    print ("post from fecho", fn)

    if os.path.exists(fn+".info"):
      tic = read_info(fn+".info")
    else:
      tic = {}

    if "FILE" not in tic:
      tic["FILE"] = [fn]

    if "SIZE" not in tic:
      tic["SIZE"] = [os.path.getsize(fn)]

    if "DESC" not in tic:
      if os.path.exists(fn+".desc"):
        desc = open(fn+".desc", encoding="cp866").read().strip()
        tic["DESC"] = [desc]

    if "AREA" not in tic:
      area=os.path.dirname(fn).split(os.path.sep)[-1].upper()
      tic["AREA"] = [area]

    if "CRC" not in tic:
      _, crc = ftntic.sz_crc32(fn)
      tic["CRC"] = [crc]

    print (tic)

    ftntic.import_tic(db, fn+".faketic", ticdata=tic, import_utime=ts, ignore_pw=True, skip_access_check=True)
    if os.path.exists(fn+".desc"):
      os.unlink(fn+".desc")
    if os.path.exists(fn+".info"):
      os.unlink(fn+".info")

  else:
    print ("bad type", l)
    exit()
