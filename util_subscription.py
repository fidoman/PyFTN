#!/usr/local/bin/python3

import sys
import ftnconfig
import ftnimport
import ftnexport
from ftn.ftn import FTNAlreadySubscribed

# add|remove domain area subscriber

db=ftnconfig.connectdb()

try:
  cmd = sys.argv[1]
  domain = sys.argv[2]
  area = sys.argv[3]
  subscriber = sys.argv[4]
except:
  print("usage: ./util_subscription.py add|addvital|remove echo|fileecho AREANAME 2:5020/9999")
  exit()

try:
  robot = ftnconfig.robotnames[domain]
except:
  raise Exception("cannot manage subscriptions in domain", domain)

pw = ftnconfig.get_link_password(db, subscriber, forrobots=True)

with ftnimport.session(db) as sess:
  if cmd == "add":
    try:
      sess.add_subscription(None, domain, area, subscriber)
    except FTNAlreadySubscribed:
      print ("local subscription exists")
    if subscriber != ftnconfig.ADDRESS:
      sess.send_message(ftnconfig.SYSOP, ("node", subscriber), robot, None, pw, "+"+area)
    else:
      print ("local subscription")

  elif cmd == "remove":
    sess.remove_subscription(domain, area, subscriber)
    if subscriber != ftnconfig.ADDRESS:
      sess.send_message(ftnconfig.SYSOP, ("node", subscriber), robot, None, pw, "-"+area)
    else:
      print ("local subscription")

  elif cmd == "addvital":
    sess.add_subscription(True, domain, area, subscriber)
#    except FTNAlreadySubscribed:
#      print ("local subscription exists")
    if subscriber != ftnconfig.ADDRESS:
      sess.send_message(ftnconfig.SYSOP, ("node", subscriber), robot, None, pw, "+"+area)
    else:
      print ("local subscription")

  elif cmd == "createfrom":
    sess.check_addr(domain, area)
    sess.add_subscription(True, domain, area, subscriber)
    if subscriber != ftnconfig.ADDRESS:
      sess.send_message(ftnconfig.SYSOP, ("node", subscriber), robot, None, pw, "+"+area)
    else:
      print ("local subscription")

  elif cmd == "query": # send areafix request
    sess.send_message(ftnconfig.SYSOP, ("node", subscriber), robot, None, pw, "%QUERY")

  elif cmd == "list": # send areafix request
    sess.send_message(ftnconfig.SYSOP, ("node", subscriber), robot, None, pw, "%LIST")

  elif cmd == "show": # show subscribed areas
    if area==".": # show for link
      for x in ftnexport.get_node_subscriptions(db, subscriber, domain):
        print (x)
    else: # show from area
      tid =  ftnconfig.get_addr_id(db, db.FTN_domains[domain], area)
      print (tid)
      for aid, vital, level in ftnexport.get_subscribers(db, tid):
        print (ftnconfig.get_addr(db, aid))      

  elif cmd == "showuplink": # show areas subsribed as vital
    if area==".": # show for link
      for x in ftnexport.get_node_subscriptions(db, subscriber, domain, asuplink=True):
        print (x)
    else: # show from area
      tid =  ftnconfig.get_addr_id(db, db.FTN_domains[domain], area)
      print (tid)
      for x in ftnexport.get_subscribers(db, tid, True):
        print (x)      

  elif cmd == "verifyuplink":
    a_uplink = set(ftnexport.get_node_subscriptions(db, subscriber, domain, asuplink=True))
    a_all = set(ftnexport.get_node_subscriptions(db, subscriber, domain))
    print ("linked not as uplink to:")
    for a in a_all - a_uplink:
      tid =  ftnconfig.get_addr_id(db, db.FTN_domains[domain], a)
      if not list(ftnexport.get_subscribers(db, tid, onlyvital=True)):
        print (a)

  elif cmd == "makeuplink":
    a_uplink = set(ftnexport.get_node_subscriptions(db, subscriber, domain, asuplink=True))
    a_all = set(ftnexport.get_node_subscriptions(db, subscriber, domain))
    print ("linked not as uplink to:")
    for a in a_all - a_uplink:
      tid =  ftnconfig.get_addr_id(db, db.FTN_domains[domain], a)
      if not list(ftnexport.get_subscribers(db, tid, onlyvital=True)):
        print (a)
        sess.add_subscription(True, domain, a, subscriber)

  elif cmd == "demoteuplink":
    if area == ".":
      a_uplink = set(ftnexport.get_node_subscriptions(db, subscriber, domain, asuplink=True))
      print ("linked as uplink to:")
      for a in a_uplink:
        print (a)
        sess.add_subscription(False, domain, a, subscriber)
    else:
      sess.add_subscription(False, domain, area, subscriber)


  elif cmd == "promoteuplink":
    sess.add_subscription(True, domain, area, subscriber)

  elif cmd == "check":
    # read query file and report extra or missing subscriptions
    remote = set()
    for l in open(area):
        remote.add(l.strip())
    local = set(ftnexport.get_node_subscriptions(db, subscriber, domain))
    print ("Local but not remote:", local-remote)
    print ("Remote but not local:", remote-local)


  else:
    raise Exception("unknown command", cmd)
