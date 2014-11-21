#!/usr/local/bin/python3 -bb

import sys
import re
import os

f=open(sys.argv[1], "rb")
for l in f:
  x=re.split(b"\s+", l.rstrip(), 1)
  if len(x)>1:
    if os.path.exists(x[0].decode("ascii")) and not os.path.exists(x[0].decode("ascii")+".desc"):
      print (x[0].decode("ascii"), x[1].decode("cp866"))
      open(x[0].decode("ascii")+".desc", "wb").write(x[1])
