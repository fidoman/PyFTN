#!/bin/env python3 -bb

""" Create vital netmail subscription (and remove unneeded) """

from ftnconfig import connectdb, ADDRESS, NETMAIL_peers, NETMAIL_peerhosts, NETMAIL_uplinks, get_addr_id
from ftnimport import session
from ftn.ftn import FTNAlreadySubscribed
import ftn

# 1. Create subscription for myself and for all nodes that designate me as group (they get netmail directly)
# 1a. Also create the same subscriptions for peers

db = connectdb()

my_id = get_addr_id(db, db.FTN_domains["node"], ADDRESS)
downlinks = [(db.FTN_backdomains[x[0]], x[1]) for 
    x in db.prepare("""select domain, text from addresses where "group"=$1""")(my_id)] # need here recursion?

peers = [("node", x) for x in NETMAIL_peers]

selfsubscribers = set([("node", ADDRESS)] + downlinks + peers)

with session(db) as sess:

  for subs_dom, subs_text in selfsubscribers:
    print("receives own mail:", subs_dom, subs_text)
    sess.add_subscription(True, subs_dom, subs_text, subs_text)

  # Create subscriptions for peer hosts

  for host, peer in NETMAIL_peerhosts:
    print(peer, "receives for", host)
    sess.add_subscription(True, "node", host, peer)


  # Create subscriptions for zones to default netmail uplinks

  for (ungrouped,) in (db.prepare("""select text from addresses where "group" is NULL and domain=$1""")(db.FTN_domains["node"])):
    z, n, f, p = ftn.addr.str2addr(ungrouped)
    if n or f or p or not z: continue # better to check by nodelist
    for subs in NETMAIL_uplinks:
      sess.add_subscription(True, "node", ungrouped, subs)
      print(subs, "receives mail for", ungrouped)


# 3. Create subscription for hub links, if uplink hub is linked to me
# ... 

# should use network/region routing files for it
