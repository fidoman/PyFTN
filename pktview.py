#!/usr/local/bin/python3

import sys
import ftn.pkt

format = "pkt2"
chrs = "CP866"

if len(sys.argv)>2:
  format=sys.argv[2]
  if format=="utf8z":
    chrs="utf-8"
if len(sys.argv)>3:
  chrs=sys.argv[3]


f=open(sys.argv[1], "rb")

p=ftn.pkt.PKT(f, format=format)
f.close()

print ("packet source:      ", p.source)
print ("packet destination: ", p.destination)
print ("packet date:        ", p.date)
print ("packet password:    ", p.password)
print ()

for m in p.msg:
  print(m.as_str().decode(chrs))
