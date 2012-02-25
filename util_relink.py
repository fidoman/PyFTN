#!/usr/local/bin/python3

link='2:5020/758'

import ftnconfig
import ftnimport

db=ftnconfig.connectdb()

lid=db.prepare("select id from addresses where domain=$1 and text=$2").first(db.FTN_domains["node"], link)

outp=[]

pw = ftnconfig.get_link_password(db, link, True)
#print(pw)

for echo in db.prepare("select a.text from subscriptions s, addresses a "
            "where a.id=s.target and s.subscriber=$1 and a.domain=$2")(lid, db.FTN_domains["echo"]):

    outp.append("+"+echo[0]+"\n")

if len(outp)==0:
    print ("nothing to relink")
else:
    print ("".join(outp))

    with ftnimport.session(db) as sess:
        sess.send_message("Sergey Dorofeev", ("node", link),
                            "AreaFix", None, pw, "".join(outp))
