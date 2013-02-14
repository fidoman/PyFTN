#!/usr/local/bin/python3

#link='2:5020/1200'
domain = "echo"
purgelist = 'orphans'

import ftnconfig
import ftnimport
import ftnexport
import os

robot = ftnconfig.robotnames[domain]

db=ftnconfig.connectdb()

for area in open(purgelist):
  area=area.strip().upper()
  aid = ftnconfig.get_addr_id(db, db.FTN_domains[domain], area)

  # 1. verify that there is nothing there
  if domain == "fileecho":
    print (area, os.listdir("/tank/home/fido/fareas/"+area.lower()))
  elif domain == "echo":
    count = db.prepare("select count(*) from messages where destination=$1").first(aid)
    print (area, count)
    if count:
      continue

  else:
    1/0
  # 2. send message to subscribers
  # 3. remove subscriptions and address
  with ftnimport.session(db) as sess:
    for node in [ftnconfig.get_addr(db, x[0])[1] for x in ftnexport.get_subscribers(db, aid)]:
      print (node)

    input("enter to purge, Ctrl-C to abort")
    for node in [ftnconfig.get_addr(db, x[0])[1] for x in ftnexport.get_subscribers(db, aid)]:
      print (node)
      sess.send_message(ftnconfig.SYSOP, ("node", node),
                            "Sysop", None, "Area Expunging notification", """Dear Sysop,

%s %s is about to be deleted from node %s.
Please find new uplink for the area or 
expunge it too.
"""%(domain, area, ftnconfig.ADDRESS))

      sess.remove_subscription(domain, area, node)

      if node != ftnconfig.ADDRESS:
        sess.send_message(ftnconfig.SYSOP, ("node", node), robot, None, 
            ftnconfig.get_link_password(db, node, forrobots=True), "-"+area)

      sess.forget_address(domain, area)



  exit()

outp=[]

pw = ftnconfig.get_link_password(db, link, True)
#print(pw)

for echo in db.prepare("select a.text from subscriptions s, addresses a "
            "where a.id=s.target and s.subscriber=$1 and a.domain=$2")(lid, db.FTN_domains[domain]):

    outp.append("+"+echo[0]+"\n")

if len(outp)==0:
    print ("nothing to relink")
else:
    print ("".join(outp))

    with ftnimport.session(db) as sess:
        sess.send_message("Sergey Dorofeev", ("node", link),
                            robot, None, pw, "".join(outp))
