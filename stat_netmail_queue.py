#!/usr/local/bin/python3 -bb

import ftnconfig
import ftnimport

db=ftnconfig.connectdb()

x=db.prepare("""select m.id, s.domain, s.text, d.domain, d.text, d.id 
                from messages m, addresses s, addresses d 
                where d.id=m.destination and m.processed=0 and d.domain=1 and s.id=m.source""")

outp = []

for mid, sd, st, dd, dt, did in x():
  outp.append("msg #%d %d|%s->%d|%s (destid %d)\n"%(mid,sd,st,dd,dt,did))

with ftnimport.session(db) as sess:
  sess.send_message("Sergey Dorofeev", ("echo", "FLUID.REPORTS"), "All", None, "почтовая очередь",
"""Привет All

%s

Вот так
"""%("".join(outp)))
