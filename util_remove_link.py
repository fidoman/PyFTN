#!/usr/local/bin/python3 -bb

import ftnconfig
import sys

link_address = sys.argv[1]

print ("pq://username:password@host/database")
db=ftnconfig.connectdb(input("enter connection string for admin connection: "))

addr_id = ftnconfig.get_addr_id(db, db.FTN_domains["node"], link_address)
link_id = ftnconfig.get_link_id(db, link_address)

print(addr_id, link_id)

print( db.prepare("select t.domain, t.text from subscriptions s, addresses t where s.subscriber=$1 and t.id=s.target")(addr_id) )

assert( input("enter 'yes' to confirm: ")=="yes" )

db.prepare("delete from links where id=$1")(link_id)
db.prepare("delete from subscriptions where subscriber=$1")(addr_id)
