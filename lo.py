#!/usr/local/bin/python3 -bb

#import sys
#import postgresql

#import ftnconfig

#db=ftnconfig.connectdb()

#lo=sys.argv[1]
#cmd=sys.argv[2]

def lo_save(db, lo, filename):
  db.execute("begin")
  lo_h=db.prepare("select lo_open($1, 131072)").first(lo)
  f=open(filename, "wb")
  l=0
  while True:
    d = db.prepare("select loread($1, 1024*1024)").first(lo_h)
    if not d:
      break
    print (len(d), "bytes read")
    print(f.write(d), "bytes written")
    l+=len(d)
  f.close()
  db.prepare("select lo_close($1)").first(lo_h)
  db.execute("commit")

  return l
