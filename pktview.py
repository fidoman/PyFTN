#!/usr/local/bin/python3

import sys
import ftn.pkt

f=open(sys.argv[1], "rb")
p=ftn.pkt.PKT(f)
f.close()

print ("packet source:      ", p.source)
print ("packet destination: ", p.destination)
print ("packet date:        ", p.date)
print ("packet password:    ", p.password)
print ()

for m in p.msg:
  print(m.as_str().decode("cp866"))
