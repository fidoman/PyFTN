#!/usr/local/bin/python3

link='2:5020/1200'
domain = "fileecho"

import ftnconfig
import ftnimport

robot = ftnconfig.robotnames[domain]

db=ftnconfig.connectdb()

lid = ftnconfig.get_addr_id(db, db.FTN_domains["node"], link)

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
