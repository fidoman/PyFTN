#!/usr/local/bin/python3

import sys
import ftn.pkt

f=open(sys.argv[1], "rb")
p=ftn.pkt.PKT(f)
f.close()

for m in p.msg:
  print(m.as_str().decode("cp866"))
