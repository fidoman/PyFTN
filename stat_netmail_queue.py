#!/usr/local/bin/python3 -bb

import ftnconfig
import ftnimport
import ftnexport
from functools import *

db=ftnconfig.connectdb()

x=db.prepare("""select m.id, s.domain, s.text, d.domain, d.text, d.id 
                from messages m, addresses s, addresses d 
                where d.id=m.destination and m.processed=0 and d.domain=$1 and s.id=m.source""")

outp = []

for mid, sd, st, dd, dt, did in x(db.FTN_domains["node"]):
  s = {}
  for sid, _, slevel in ftnexport.get_subscribers(db, did, True):
     s.setdefault(slevel, []).append(sid)

  if len(s.keys()):
    lev=min(s.keys())
    links = "via " + ", ".join(map(lambda x: ftnexport.get_addr(db, x)[1], s[lev]))
  else:
    links = "nowhere to route"

  outp.append("msg #%d %d|%s->%d|%s (destid %d, %s)\n"%(mid,sd,st,dd,dt,did,links))

print("".join(outp))
exit()

with ftnimport.session(db) as sess:
  sess.send_message("Sergey Dorofeev", ("echo", "FLUID.REPORTS"), "All", None, "почтовая очередь",
"""Привет All

%s

Вот так
"""%("".join(outp)))
