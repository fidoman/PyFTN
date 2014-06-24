#!/usr/local/bin/python3 -bb

import ftnconfig
import ftntic

for l in open("post_s.dat"):
  ts, t, fn = l.rstrip().split("\t")
  #print (ts, t, fn)
  if t=="del":
    print ("delete", fn, "and info and desc")
  elif t=="arch":
    print ("tic=", fn)
  elif t=="farea":
    print ("post from fecho", fn)
  else:
    print ("bad type", l)
    exit()
