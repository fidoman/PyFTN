#!/usr/local/bin/python3 -bb

# parse query reply from 2:5020/715

import sys
import re

qansw = re.compile(".... (\S+)")

for f in sys.argv[1:]:
  x=open(f)
  x.readline()
  x.readline()

  go = False
  for l in x:
    if go and l == "\n":
      break
    m = qansw.match(l)
    if m:
      go = True
      print (m.group(1))
    