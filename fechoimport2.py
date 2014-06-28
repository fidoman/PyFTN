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
      exit()
    else:
      print ("MAKING FAKE TIC")
      tic = {"FILE": [fn], "SIZE": [os.path.getsize(fn)]}
      if os.path.exists(fn+".desc"):
        desc = open(fn+".desc", encoding="cp866").read().strip()
        print (desc)
        tic["DESC"]=[desc]
      area=os.path.dirname(fn).split(os.path.sep)[-1].upper()
      tic["AREA"]=[area]
      _, crc = ftntic.sz_crc32(fn)
      tic["CRC"]=[crc]

    print (tic)
    ftntic.import_tic(db, fn+".faketic", ticdata=tic, import_utime=ts)
    if os.path.exists(fn+".desc"):
      os.unlink(fn+".desc")
    if os.path.exists(fn+".info"):
      os.unlink(fn+".info")

  else:
    print ("bad type", l)
    exit()
