#!/usr/bin/python3

import sys
import ftnconfig
import ftnaccess
import ftnimport
import ftnexport
import functools
from ftn.ftn import FTNAlreadySubscribed, FTNNoAddressInBase

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

link_id = ftnconfig.find_link(db, subscriber)
my_id, pw = ftnaccess.link_password(db, link_id, forrobots=True)
my_addr = ftnconfig.get_taddr(db, my_id)

with ftnimport.session(db) as sess:
  if cmd == "add":
    try:
      sess.add_subscription(None, domain, area, subscriber)
    except FTNAlreadySubscribed:
      print ("local subscription exists")
    if subscriber != ftnconfig.ADDRESS:
      sess.send_message(my_addr, ftnconfig.SYSOP, ("node", subscriber), robot, None, pw, "+"+area, sendmode="direct")
    else:
      print ("local subscription")

  elif cmd == "remove":
    sess.remove_subscription(domain, area, subscriber)
    if subscriber != ftnconfig.ADDRESS:
      sess.send_message(my_addr, ftnconfig.SYSOP, ("node", subscriber), robot, None, pw, "-"+area, sendmode="direct")
    else:
      print ("local subscription")

  elif cmd == "addvital":
    sess.add_subscription(True, domain, area, subscriber)
#    except FTNAlreadySubscribed:
#      print ("local subscription exists")
    if subscriber != ftnconfig.ADDRESS:
      sess.send_message(my_addr, ftnconfig.SYSOP, ("node", subscriber), robot, None, pw, "+"+area, sendmode="direct")
    else:
      print ("local subscription")

  elif cmd == "createfrom":
    sess.check_addr(domain, area)
    sess.add_subscription(True, domain, area, subscriber)
    if subscriber != ftnconfig.ADDRESS:
      sess.send_message(my_addr, ftnconfig.SYSOP, ("node", subscriber), robot, None, pw, "+"+area, sendmode="direct")
    else:
      print ("local subscription")

  elif cmd == "query": # send areafix request
    sess.send_message(my_addr, ftnconfig.SYSOP, ("node", subscriber), robot, None, pw, "%QUERY", sendmode="direct")

  elif cmd == "list": # send areafix request
    sess.send_message(my_addr, ftnconfig.SYSOP, ("node", subscriber), robot, None, pw, "%LIST", sendmode="direct")

  elif cmd == "show": # show subscribed areas
    if area==".": # show for link
      for x in ftnexport.get_node_subscriptions(db, subscriber, domain):
        print (x)
    else: # show from area
      tid =  ftnconfig.get_addr_id(db, db.FTN_domains[domain], area)
      print (tid)
      for aid, vital, level, ls in ftnexport.get_subscribers(db, tid, with_lastsent=True):
        print (ftnconfig.get_addr(db, aid), level, ls)

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

  elif cmd == "completevital":
    """ read file and vital-subscribe the link to non-existent here or orphan addresses """
    for aname in open(area):
      aname = aname.strip()
      #print (aname)
      try:
        tid = ftnconfig.get_addr_id(db, db.FTN_domains[domain], aname)
      except FTNNoAddressInBase:
        tid = None
      #print (tid)
      if tid is not None:
        uplinks = [x for x in ftnexport.get_subscribers(db, tid, True)]
      else:
        uplinks = []
      if len(uplinks) == 0:
        print (aname, "create from", subscriber)
        sess.check_addr(domain, aname)
        try:
          sess.add_subscription(True, domain, aname, subscriber)
        except:
          print ("already subscribed")
        if subscriber != ftnconfig.ADDRESS:
          sess.send_message(my_addr, ftnconfig.SYSOP, ("node", subscriber), robot, None, pw, "+"+aname, sendmode="direct")
        else:
          print ("local subscription")

  elif cmd == "relink":
    subslist = ftnexport.get_node_subscriptions(db, subscriber, domain)
    if len(subslist)==0:
      print ("nothing to relink")
    else:
      substext = functools.reduce(lambda x, y: x + "+" + y + "\n", subslist, "")
      print ("".join(substext))
      sess.send_message(my_addr, "Sergey Dorofeev", ("node", subscriber), robot, None, pw, substext)

  elif cmd == "rescan":
    substext = "%rescan * 3"
    sess.send_message(my_addr, "Sergey Dorofeev", ("node", subscriber), robot, None, pw, substext)


  else:
    raise Exception("unknown command", cmd)
