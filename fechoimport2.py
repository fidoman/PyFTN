#!/usr/local/bin/python3 -bb

import os

import ftnconfig
import ftntic

from fechoimport import read_info

db=ftnconfig.connectdb()

fechoes_started = False

for l in open("post_s.dat"):
  ts, t, fn = l.rstrip().split("\t")
  print (ts, t, fn)
  if t=="del":
    print ("delete", fn, "and info and desc")
    if os.path.exists(fn):
      os.unlink(fn)
    if os.path.exists(fn+".desc"):
      os.unlink(fn+".desc")
    if os.path.exists(fn+".info"):
      os.unlink(fn+".info")
  elif t=="tic":
    print ("tic=", fn)
    try:
      ftntic.import_tic(db, fn, import_utime=ts, skip_access_check=True)
    except ftntic.DupPost:
      print ("dup detected")
  elif t=="farea":
    print ("post from fecho", fn)

    if not os.path.exists(fn) and not fechoes_started:
      continue
    else:
      fechoes_started = True

    if os.path.exists(fn+".info"):
      tic = read_info(fn+".info")
    else:
      tic = {}

    #if "FILE" not in tic:
    tic["FILE"] = [fn] # Always use real file name

    if "SIZE" not in tic:
      tic["SIZE"] = [os.path.getsize(fn)]

    if "DESC" not in tic:
      if os.path.exists(fn+".desc"):
        desc = open(fn+".desc").read().strip()
        tic["DESC"] = desc.split("\n")

    if "AREA" not in tic:
      area=os.path.dirname(fn).split(os.path.sep)[-1].upper()
      tic["AREA"] = [area]

    if "CRC" not in tic:
      _, crc = ftntic.sz_crc32(fn)
      tic["CRC"] = [crc]

    print (tic)

    try:
      ftntic.import_tic(db, fn+".faketic", ticdata=tic, import_utime=ts, ignore_pw=True, skip_access_check=True)
    except ftntic.DupPost:
      print ("dup detected")

    if os.path.exists(fn+".desc"):
      os.unlink(fn+".desc")
    if os.path.exists(fn+".info"):
      os.unlink(fn+".info")

  else:
    print ("bad type", l)
    exit()
