#!/usr/local/bin/python3 -bb

import sys
import ftnconfig
import ftnimport

if len(sys.argv)!=3:
  print ("specify address: domain text, for example fileecho xpicsysop")
  exit(-1)

db=ftnconfig.connectdb()

domain=sys.argv[1]
area=sys.argv[2].upper()

print ("pq://username:password@host/database")
db=ftnconfig.connectdb(input("enter connection string for admin connection: "))

robot = ftnconfig.robotnames[domain]

addr_id = ftnconfig.get_addr_id(db, db.FTN_domains[domain], area)
print (addr_id)
#msg_from = db.prepare("select count (*) from messages where source=$1")(addr_id)
#print ("from:", msg_from)
#msg_from = db.prepare("select count (*) from messages where destination=$1")(addr_id)
#print ("to:", msg_from)

assert( input("enter 'yes' to confirm: ")=="yes" )

with ftnimport.session(db) as sess:
  for (link_addr,subs_id) in db.prepare("select a.text, s.id from addresses a, subscriptions s where a.id=s.subscriber and s.target=$1")(addr_id):
    print ("unsubscribing",link_addr)
    db.prepare("delete from subscriptions where id=$1")(subs_id)
    pw=ftnconfig.get_link_password(db, link_addr, forrobots=True)
    sess.send_message(ftnconfig.SYSOP, ("node", link_addr), robot, None, pw, "-"+area, sendmode="direct")
  sess.send_message(ftnconfig.SYSOP, ("echo", "FLUID.LOCAL"), "All", None, "removal", domain+" "+area+" removed from node")
  db.prepare("delete from addresses where id=$1")(addr_id)

exit()
