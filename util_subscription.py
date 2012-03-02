#!/usr/local/bin/python3

import sys
import ftnconfig
import ftnimport
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

if domain=="echo":
  robot = "AreaFix"
elif domain=="fileecho":
  robot = "FileFix"
else:
  raise Exception("cannot manage subscriptions in domain", domain)

pw = ftnconfig.get_link_password(db, subscriber, forrobots=True)

with ftnimport.session(db) as sess:
  if cmd == "add":
    try:
      sess.add_subscription(False, domain, area, subscriber)
    except FTNAlreadySubscribed:
      print ("local subscription exists")
    sess.send_message(ftnconfig.SYSOP, ("node", subscriber), robot, None, pw, "+"+area)
  elif cmd == "remove":
    sess.remove_subscription(domain, area, subscriber)
    sess.send_message(ftnconfig.SYSOP, ("node", subscriber), robot, None, pw, "-"+area)
  elif cmd == "addvital":
    sess.add_subscription(True, domain, area, subscriber)
#    except FTNAlreadySubscribed:
#      print ("local subscription exists")
    sess.send_message(ftnconfig.SYSOP, ("node", subscriber), robot, None, pw, "+"+area)
  else:
    raise Exception("unknown command", cmd)
