#!/usr/local/bin/python3 -bb

# parse query reply from 2:5020/715

import sys
import re

qansw = re.compile(".... (\S+)")

RE_echo = re.compile("(\S+) \.+$")
echofieldlen=43
RE_stat = re.compile(" \S+\s+\[\S+\] \".*?\"")


prv = ""

for f in sys.argv[1:]:
  x=open(f)
  x.readline()
  x.readline()

  for l in x:
    l=l.strip()

    if RE_stat.match(l[echofieldlen:]):    

      if l[:echofieldlen] == "."*echofieldlen:
        l = prv+" "+l

      print (l.split(" ")[0])


    prv = l
