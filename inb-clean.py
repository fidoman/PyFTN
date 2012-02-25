#!/usr/local/bin/python3 -bb

import os, glob
import ftnconfig

def cleandir(d):
  empty=True
  for i in glob.glob(d+"/*"):
    if os.path.isdir(i):
      if not cleandir(i):
        empty=False
        continue
      else:
        print ("remove", i)
        os.rmdir(i)
      continue
    else:
      empty=False
  return empty

cleandir(ftnconfig.INBOUND)
cleandir(ftnconfig.OUTBOUND)
