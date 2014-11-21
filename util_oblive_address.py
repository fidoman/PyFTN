#!/usr/local/bin/python3 -bb

import sys
import ftnconfig
import ftnaccess
import ftnimport

def autoclean(db):
  for (a_id,) in db.prepare("select id from addresses where domain=2 and text like 'RU.LIST.%'"):
    n = db.prepare("select count(*) from messages where destination=$1").first(a_id)
    print (a_id, n)
    if n==0:
      oblive(db, ftnconfig.get_taddr(db, a_id))

  ok4441=set(map(str.strip, open("4441").readlines()))
  my4441=set(map(str.strip, open("4441my").readlines()))
  for (a_id, a_text) in db.prepare("select id, text from addresses where domain=2"):
    if a_text in my4441 and a_text not in ok4441:
      n = db.prepare("select count(*) from messages where destination=$1").first(a_id)
      if n==0:
        print (a_text)
        oblive(db, ftnconfig.get_taddr(db, a_id))

def oblive(db, address):
  robot = ftnconfig.robotnames[address[0]]

  addr_id = ftnconfig.get_taddr_id(db, address)
  if addr_id is None:
    raise Exception("not found")

  msg_from = db.prepare("select count (*) from messages where source=$1").first(addr_id)
  msg_to = db.prepare("select count (*) from messages where destination=$1").first(addr_id)
  print (address, addr_id, "from:", msg_from, "to:", msg_to)

  if msg_from!=0 or msg_to!=0:
    print("messages exist")
    return
#  assert( input("enter 'yes' to confirm: ")=="yes" )

  with ftnimport.session(db) as sess:
    for (link_addr,subs_id) in db.prepare("select a.text, s.id from addresses a, subscriptions s where a.id=s.subscriber and s.target=$1")(addr_id):
      print ("unsubscribing",link_addr)
      link_id = ftnconfig.find_link(db, link_addr)
      my_id, pw=ftnaccess.link_password(db, link_id, forrobots=True)
      sess.send_message(ftnconfig.get_taddr(db, my_id), ftnconfig.SYSOP, ("node", link_addr), robot, None, pw, "-"+address[1], sendmode="direct")
      db.prepare("delete from subscriptions where id=$1")(subs_id)
    sess.send_message(("node", ftnconfig.ADDRESS), ftnconfig.SYSOP, ("echo", "FLUID.LOCAL"), "All", None, "removal", address[0]+" "+address[1]+" removed from node")
    db.prepare("delete from deletedvitalsubscriptionwatermarks where target=$1")(addr_id)
    db.prepare("delete from addresses where id=$1")(addr_id)



print ("pq://username:password@host/database")
db=ftnconfig.connectdb(input("enter connection string for admin connection: "))

if len(sys.argv)!=3:
  print ("specify address: domain text, for example fileecho xpicsysop")
  autoclean(db)
else:
  domain=sys.argv[1]
  area=sys.argv[2].upper()
  oblive(db, (domain, area))
