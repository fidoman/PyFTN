#!/usr/bin/python3

import sys
import getopt
import ftn.msg

#f=open(sys.argv[1], "rb")
m=ftn.msg.MSG(sys.argv[1])
if len(sys.argv)==3:
  charset = sys.argv[2]
else:
  charset = "cp866"
#f.close()

print(m.as_str().decode(charset))
