#!/usr/local/bin/python3 -bb

import ftnconfig
import ftntic

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
    exit()
  else:
    print ("bad type", l)
    exit()
