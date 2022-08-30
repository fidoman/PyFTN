#!/usr/bin/python3 -bb

import re

""" Create vital netmail subscription (and remove unneeded) """

from ftnconfig import connectdb, ADDRESS, NETMAIL_peers, NETMAIL_peerhosts, NETMAIL_uplinks, format1files, format2files, find_link
from ftnimport import session
from ftn.ftn import FTNAlreadySubscribed, FTNNoAddressInBase
from ftn.addr import addr2str, str2addr, addr_expand
import ftnexport

# 1. Create subscription for myself and for all nodes that designate me as group (they get netmail directly)
# 1a. Also create the same subscriptions for peers

db = connectdb()

""" load routing inforation from N5020/R50 config files """

re_S=re.compile("\s+")

hubs = {}
links = set(NETMAIL_peers)
#print ("links=",links)
manualrouted = {}

for host, peer in NETMAIL_peerhosts:
    links.add(peer)
    hubs.setdefault(peer, set()).add(host)
    manualrouted[host] = peer

# load routing files and make dict node: downlinks
# then for keys of this dict check if they are my links
# and if yes create hubscriptions for them

for f1 in format1files:
  print (f1)
  for l in open(f1, encoding="cp866"):
    l=l.split(";")[0].strip()
    if not l: continue
    #print (l)
    l=l.replace("/*", "/0") # routing to 5020/* is hubscribing to 5020/0
    l=re.sub("(\d+):\*/0", "\g<1>:\g<1>/0", l)
    #print (l)
    #print ("\n")

    x=re_S.split(l)
    if x[0][0]==">":
        withhop=True
        x[0]=x[0][1:]
    else:
        withhop=False

    x = [addr2str(x) for x in addr_expand(x, str2addr(ADDRESS))]

    if withhop: # hubscribe first to second (hop) and hop to all other
      if x[0] == ADDRESS:
        links.add(x[1])
        x = x[1:]
      else:
        x = x[:1] + x[2:]

    else:
      if x[0] == ADDRESS:
        links.update(x[1:])
        x = x[:1]

    for y in x[1:]:
      if y != ADDRESS:
        #if x[0]=='2:50/9999': 
        #  continue
        if y in manualrouted:
          print ("manual route to", y, "config", manualrouted[y], "ignore", x[0])
        else:
          hubs.setdefault(x[0], set()).add(y)
        #routed[y] = x[0]

#print (links)
#for k, v in hubs.items():
#  print ("%-17s: "%k, ", ".join(v))
#print ()
#exit()

for f2 in format2files:
  print (f2)
  for l in open(f2, encoding="cp866"):
    l=l.split(";")[0].strip()
    if not l: continue
    x=re_S.split(l.replace("*", "0")) # routing to 5020/* is hubscribing to 5020/0

    x = [addr2str(x) for x in addr_expand(x, str2addr(ADDRESS))]

    if x[0] != ADDRESS: # ignore own tru record
      if ADDRESS in x[1:]:
        links.add(x[0])
      else:
        for y in x[1:]:
          hubs.setdefault(y, set()).add(x[0])

#print ("direct by route files =", ", ".join(links))
#for k, v in hubs.items():
#  print ("%-17s: "%k, ", ".join(v))
#print ()
#exit()

downlinks = ftnexport.get_subnodes(db, ADDRESS)
#print (downlinks)
#exit()

selfsubscribers = set()
selfsubscribers.add(ADDRESS)
selfsubscribers.add(ADDRESS+".999")

# filter links that are not password-protected
for x in list(links) + downlinks:
  if not find_link(db, x, netmail=True):
    print ("skip", x)
  else:
    selfsubscribers.add(x)

#print ("direct links =", ", ".join(selfsubscribers))

# add subscription for self
for l in selfsubscribers:
  hubs.setdefault(l, set()).add(l)

#print ("subscriptions")
#for k, v in hubs.items():
#  print ("subscribe %s to"%k, ", ".join(v))
#print ()
#exit()

# first, we assign to direct links all configured routes

def get_chain(hub):
  targets = set()
  routed = hubs.get(hub).copy()

  while routed:
    downlink = routed.pop()
    if downlink in targets:
      continue

    if downlink in selfsubscribers:
#      if downlink == peer:
#        #print ("add route for self")
#        targets.add(downlink)
#      else:
#        #print ("skip direct link", downlink)
#        pass
      continue
    #print("target", downlink)

    targets.add(downlink)
    if downlink in hubs:
        #print ("target has downlinks", hubs[downlink])
        routed.update(hubs[downlink])
#        filerouted.add(downlink)
  return targets

dr = {}
haveroute = set()

#print("zero pass. add direct links")

for ss in selfsubscribers:
  dr.setdefault(ss, set()).add(ss)
  haveroute.add(ss)

#print("1st pass. add direct links' downlinks")

for ss in selfsubscribers:
  dr.setdefault(ss, set()).update(get_chain(ss))
  haveroute.update(dr[ss])

#print("2nd pass - nodelist routing for other hubs")

# get superaddresses for remaining hubs and check via which link it can be routed
#print ("unrouted:", hubs.keys())

dr2 = {}

#if False:
for x in list(hubs.keys()):
  if x in haveroute:
    continue
  #print ("nodelist routing for", x)
  # find direct link under which some parent of this address exists

  s = x
  group = False
  while not group:

    s = ftnexport.get_supernode(db, s) # retry with super super if group = 0
    if s is None:
      print (x, "not grouped")
      break

    #print (x, "is under", s)

    for drk, drv in dr.items():
      if s in drv:
        #print(x, "can be routed via", drk)
        # add to dr with all underlying links!
        dr2.setdefault(drk, set()).update(get_chain(x))
        #print("via",drk,":(",x,")",get_chain(x))
        group = True

for k, v in dr2.items():
  dr.setdefault(k, set()).update(v)

alls = set()
for peer, targets in dr.items():
  for t in targets:
      #print(peer, "receives for", t)
      alls.add(("node", t, peer))


#for x, y, z in alls:
#  print ("%s %-24s via %-24s"%(x,y,z))
#exit()

with session(db) as sess:
  # fetch old subscriptions
  for sid, target, subscriber in db.prepare("select s.id, t.text, sr.text from subscriptions s, addresses t, addresses sr "
            "where s.target=t.id and t.domain=$1 and s.subscriber=sr.id")(db.FTN_domains["node"]):
    if ('node', target, subscriber) in alls:
      alls.remove(('node', target, subscriber))
    else:
      print ("remove subscription to", target, "for", subscriber)
      db.prepare("delete from subscriptions where id = $1")(sid)
    
  for domain, target, subscriber in alls:
    print (target,"via",subscriber)
    try:
        sess.add_subscription(True, "node", target, subscriber)
        pass
    except FTNNoAddressInBase:
        print ("non-existent address")


  # Create subscriptions for zones to default netmail uplinks
# now it all is presented in routing files

#  for (ungrouped,) in (db.prepare("""select text from addresses where "group" is NULL and domain=$1""")(db.FTN_domains["node"])):
#    z, n, f, p = ftn.addr.str2addr(ungrouped)
#    if n or f or p or not z: continue # better to check by nodelist
#    for subs in NETMAIL_uplinks:
#      sess.add_subscription(True, "node", ungrouped, subs)
#      print(subs, "receives mail for", ungrouped)

