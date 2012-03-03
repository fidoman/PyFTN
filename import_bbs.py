#!/usr/local/bin/python3

import sys
import fileinput
import getopt

import ftn.addr
import ftnimport

faillist=[]

with ftnimport.session(ftnimport.db) as sess:

 for fname, domain in [("subscriptions/areas.bbs", ftnimport.FIDOECHO), ("subscriptions/fareas.bbs", ftnimport.FIDOFECHO)]:
  sys.stdout.write(fname+"\n")
  startline=True
  for l in fileinput.input(fname):
    if startline:
      startline=False
      continue
    x=l.rstrip().split(" ")
    opt=getopt.getopt(x[2:], "z:l:k:t:r:s:")
    #print(x[1], opt[0])
    first=True
    for subscriber in ftn.addr.addr_expand(opt[1], (None,None,None,None)):
      #print (" ", ftn.addr.addr2str(subscriber))

      vital=first
      target_domain=domain
      target_addr=x[1].upper()
      subscriber_addr=subscriber
      #print (vital, target_domain, target_addr, ftn.addr.addr2str(subscriber_addr))
      try:
        sess.add_subscription(vital, target_domain, target_addr, ftn.addr.addr2str(subscriber_addr))
      except ftnimport.NoAddressInBaseException as e:
        print(e)
        faillist.append([str(e), vital, target_domain, target_addr, ftn.addr.addr2str(subscriber_addr)])
      first=None

 of=open("faillist","w")
 for f in faillist:
   of.write(repr(f)+"\n")
 of.close()
