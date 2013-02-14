#!/usr/local/bin/python3 -bb

import ftnconfig
import ftnimport

db=ftnconfig.connectdb()

area="FLUID.LOCAL"

robot = ftnconfig.robotnames["echo"]

with ftnimport.session(db) as sess:
  for (link_addr,) in db.prepare("select a.text from links l, addresses a where a.id=l.address"):
    print (link_addr)
    sess.add_subscription(None, "echo", area, link_addr)
    pw=ftnconfig.get_link_password(db, link_addr, forrobots=True)
    sess.send_message(ftnconfig.SYSOP, ("node", link_addr), robot, None, pw, "+"+area, sendmode="direct")
