#!/usr/local/bin/python3

import sys
import ftn.msg

#f=open(sys.argv[1], "rb")
m=ftn.msg.MSG(sys.argv[1])
#f.close()

print(m.as_str().decode("cp866"))
