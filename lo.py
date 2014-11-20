#!/usr/local/bin/python3 -bb

#import sys
#import postgresql

#import ftnconfig

#db=ftnconfig.connectdb()

#lo=sys.argv[1]
#cmd=sys.argv[2]

def lo_save(db, lo, f):
  db.execute("begin")
  lo_h=db.prepare("select lo_open($1, 131072)").first(lo)
  l=0
  while True:
    d = db.prepare("select loread($1, 1024*1024)").first(lo_h)
    if not d:
      break
    print (len(d), "bytes read")
    print(f.write(d), "bytes written")
    l+=len(d)
  db.prepare("select lo_close($1)").first(lo_h)
  db.execute("commit")

  return l

import io

class LOIOReader(io.RawIOBase):
  def __init__(self, db, lo_id):
    self.db = db.clone() # lo functions require own transaction context
    self.lo_id = lo_id
    self.db.execute("begin")
    self.lo_h = self.db.prepare("select lo_open($1, 131072)").first(self.lo_id)

  def read(self, n):
    return self.db.prepare("select loread($1, $2)").first(self.lo_h, n)

  def __del__(self):
    self.db.prepare("select lo_close($1)").first(self.lo_h)
    self.db.execute("commit")
    self.db.close()
