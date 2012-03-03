#!/usr/local/bin/python3

import ftnconfig
import ftnexport
import ftnimport

db = ftnconfig.connectdb()

bydomain = {}

for domain in ["echo", "fileecho"]:
  #print ("domain", domain)
  for t in ftnexport.get_all_targets(db, domain):
    tid = ftnconfig.get_addr_id(db, db.FTN_domains[domain], t)
    ulist = []
    for x in ftnexport.get_subscribers(db, tid, True):
        ulist.append("%d|%s"%ftnconfig.get_addr(db, x[0])+"!%d"%x[2])
    #print 

    bydomain.setdefault(domain, {}).setdefault(", ".join(ulist), []).append(t)


with ftnimport.session(db) as sess:
  for d, byuplink in bydomain.items():
    outp=[]
    for u, targets in byuplink.items():
      outp.append("  uplink = ["+u+"]\n")
      for t in targets:
        outp.append("    "+t+"\n")
      outp.append("\n")
      
    outp.append("\n")
    outp.append("\n")



#    sess.send_message("Sergey Dorofeev", ("echo", "FLUID.REPORTS"), "All", None, "uplinks by "+d, ("".join(outp)))


print ("".join(outp))