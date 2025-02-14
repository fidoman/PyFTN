#!/usr/bin/python3 -bb

import ftnconfig
import ftnaccess

db=ftnconfig.connectdb()

pwfile=open("passwd", "w")

for link_id, addr_text in db.prepare("select l.id, a.text from links l, addresses a "
            "where l.address=a.id and a.domain=$1 order by a.text")(db.FTN_domains["node"]):
  my, pw = ftnaccess.link_password(db, link_id, False)
  if pw:
    pwfile.write("password %-23s %s\n"%(addr_text, pw))

pwfile.close()
