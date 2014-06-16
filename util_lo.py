#!/usr/local/bin/python3 -bb

import sys
import postgresql

import ftnconfig

db=ftnconfig.connectdb()

lo=sys.argv[1]
cmd=sys.argv[2]

if cmd=="save":
  db.execute("begin")
  lo_h=db.prepare("select lo_open($1, 131072)").first(int(lo))
  f=open(sys.argv[3], "wb")
  while True:
    d = db.prepare("select loread($1, 1024*1024)").first(lo_h)
    if not d:
      break
    print (len(d), "bytes read")
    print(f.write(d), "bytes written")
  f.close()
  db.prepare("select lo_close($1)").first(lo_h)
  db.execute("commit")
