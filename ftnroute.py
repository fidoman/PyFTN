#!/bin/env python3 -bb

""" Create vital netmail subscription (and remove unneeded) """

from ftnconfig import *
from ftnimport import session
from ftn.ftn import FTNAlreadySubscribed
import ftn

# 1. Create subscription for myself and for all nodes that designate me as group (they get netmail directly)
# 1a. Also create the same subscriptions for peers

netmail_domain=db.FTN_domains["node"]

my_id = db.prepare("select id from addresses where domain=$1 and text=$2").first(netmail_domain, ADDRESS)
downlinks = db.prepare("""select domain, text from addresses where "group"=$1""")(my_id)

#peers = []
#for paddr in NETMAIL_peers:
#  peers.append(db.prepare("select id from addresses where domain=$1 and text=$2").first(netmail_domain, paddr))

peers = [(netmail_domain, x) for x in NETMAIL_peers]

selfsubscribers = set([(netmail_domain, ADDRESS)] + downlinks + peers)

with session(db) as sess:
  for subs_dom, subs_text in selfsubscribers:
    print(subs_dom, subs_text)
    sess.add_subscription(True, subs_dom, subs_text, subs_text)

# 2. Create subscriptions for zones to default netmail uplinks

  for (ungrouped,) in (db.prepare("""select text from addresses where "group" is NULL and domain=$1""")(netmail_domain)):
    z, n, f, p = ftn.addr.str2addr(ungrouped)
    if n or f or p or not z: continue # better to check by nodelist
    print(ungrouped)
    for subs in NETMAIL_uplinks:
      sess.add_subscription(True, netmail_domain, ungrouped, subs)
  

# 3. Create subscription for hub links, if uplink hub is linked to me

# should use network/region routing files for it
