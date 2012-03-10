#!/usr/local/bin/python3 -bb

import textwrap

import ftnconfig
import ftnimport

db=ftnconfig.connectdb()

x=db.prepare("""select t.text, sr.text 
                from subscriptions s, addresses t, addresses sr
                where t.id=s.target and sr.id=s.subscriber and t.domain=$1""")

outp = []

peers = {}

for t, sr in x(db.FTN_domains["node"]):
  peers.setdefault(sr, []).append(t if t!=sr else "self")

plist = list(peers.keys())
plist.sort()

direct = []

outp.append ("Route netmail via:\n")
outp.append ("\n")

for p in plist:
  ts = peers[p]
  ts.sort()
  targstr=", ".join(ts)
  if targstr == "self":
    direct.append(p)
  else:

    pre = "%-17s: "%p
    for l in textwrap.wrap(targstr, 55):
      outp.append (pre + l + "\n")
      pre = " "*19

outp.append ("\n")
dirstr = ", ".join(direct) or "none"
outp.append ("Direct links:\n")
for l in textwrap.wrap(dirstr, 70):
  outp.append ("   %s\n"%l)

print("".join(outp))
exit()

with ftnimport.session(db) as sess:
  sess.send_message("Sergey Dorofeev", ("echo", "FLUID.REPORTS"), "All", None, "схема роутинга нетмейла",
"""Привет All

%s

Вот так
"""%("".join(outp)))
