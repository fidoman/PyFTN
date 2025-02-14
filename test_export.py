#!/bin/env python3

link_addr = "2:5097/31"
encoding = "utf-8"

import os
import time

get_time = time.time

try:
  os.mkdir("test")
except:
  pass

if not os.path.isdir("test"):
  print ("please make dir test")
  exit()

import ftnconfig
import ftnaccess
from ftnexport import get_subscriptions_x

from ftnconfig import BUNDLETIMELIMIT

def get_subscriber_messages_e(db, subscriber, domain):
  start_time = get_time()
  for target_id, target_name, target_last, subs_id, subs_last in get_subscriptions_x(db, subscriber, domain):
    if get_time()-start_time>BUNDLETIMELIMIT-5:
      print("Abandoning do to export time limit")
      break
    if target_last>subs_last:
      print ("something new", target_id, target_name, target_last, subs_id, subs_last)

      start_id = subs_last # position to start export 
      # after exporting block ('LIMIT 200') start from position after last exported message

      while True:
        last_id = None # update to number if something is exported

        query = db.prepare(
            "select m.id, m.source, m.destination, m.msgid, m.header, "
            "m.body, m.origcharset, m.receivedfrom, m.processed from messages m where destination=$1 and id>$2 order by id limit 200")

        data = query.chunks(target_id, start_id)

        for x in data:
          for mid,msrc,mdst,mmsgid,mhdr,mbody,mchr,mrecvfrom,mproc in x:
            last_id = mid
            yield mid, msrc, mdst, mmsgid, mhdr, mbody, mchr, mrecvfrom, subs_id, mproc

        if last_id is None:
          break
        start_id = last_id



db=ftnconfig.connectdb()
link_id = ftnconfig.find_link(db, link_addr)
my_id, password = ftnaccess.link_password(db, link_id, forrobots=False)

print (link_addr, my_id, password)
addr_id = ftnconfig.get_addr_id(db, db.FTN_domains["node"], link_addr)

for id_msg, xxsrc, dest, msgid, header, body, origcharset, recvfrom, withsubscr, processed in get_subscriber_messages_e(db, addr_id, db.FTN_domains["echo"]):
  print("id", id_msg)
