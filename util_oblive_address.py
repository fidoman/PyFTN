#!/usr/local/bin/python3 -bb

import sys
import ftnconfig
import ftnaccess
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

addr_id = ftnconfig.get_taddr_id(db, (domain, area))
if addr_id is None:
  print ("not found")
  exit()

msg_from = db.prepare("select count (*) from messages where source=$1").first(addr_id)
msg_to = db.prepare("select count (*) from messages where destination=$1").first(addr_id)
print (addr_id, "from:", msg_from, "to:", msg_to)

assert( input("enter 'yes' to confirm: ")=="yes" )

with ftnimport.session(db) as sess:
  for (link_addr,subs_id) in db.prepare("select a.text, s.id from addresses a, subscriptions s where a.id=s.subscriber and s.target=$1")(addr_id):
    print ("unsubscribing",link_addr)
    link_id = ftnconfig.find_link(db, link_addr)
    my_id, pw=ftnaccess.link_password(db, link_id, forrobots=True)
    sess.send_message(ftnconfig.get_taddr(db, my_id), ftnconfig.SYSOP, ("node", link_addr), robot, None, pw, "-"+area, sendmode="direct")
    db.prepare("delete from subscriptions where id=$1")(subs_id)
  sess.send_message(("node", ftnconfig.ADDRESS), ftnconfig.SYSOP, ("echo", "FLUID.LOCAL"), "All", None, "removal", domain+" "+area+" removed from node")
  db.prepare("delete from deletedvitalsubscriptionwatermarks where target=$1")(addr_id)
  db.prepare("delete from addresses where id=$1")(addr_id)

exit()
