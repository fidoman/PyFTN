#!/usr/local/bin/python3 -bb

import ftnconfig

db=ftnconfig.connectdb()

Q_max = db.prepare("select max(id) from messages where destination=$1")

for (addr,domain,text,last) in db.prepare("select id, domain, text, last from addresses")():
#  print (addr, end=' ')
  maxid = Q_max(addr)[0][0]
  if last!=maxid:
    print ("update %d/%s"%(domain, text), repr(last), "->", repr(maxid))
    db.prepare("update addresses set last=$2 where id=$1")(addr, maxid)
