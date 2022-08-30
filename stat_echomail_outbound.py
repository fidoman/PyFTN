#!/usr/bin/python3 -bb

import ftnconfig
import ftnimport

db=ftnconfig.connectdb()

outp = []

Q_stat = db.prepare("select sr.text, count(m.id) from messages m, subscriptions s, addresses sr "
                "where s.target=m.destination and s.subscriber=sr.id and sr.domain=$1 "
                "and s.lastsent<m.id and m.processed=0 and m.receivedfrom<>sr.id "
                "group by sr.text "
                "order by sr.text")

for subs, count in Q_stat(db.FTN_domains["node"]):
    outp.append("%-23s %d\n"%(subs, count))


#print("".join(outp))
#exit()

with ftnimport.session(db) as sess:
    sess.send_message(("node", ftnconfig.ADDRESS), "Sergey Dorofeev", ("echo", "FLUID.REPORTS"), "All", None, "новый эхомейл для линков",
"""Привет All

Количество незабранных сообщений в подписанных эхах

%s

Вот так
"""%("".join(outp)))
