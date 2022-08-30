#!/usr/bin/python3 -bb

import ftnconfig
import ftnimport

db=ftnconfig.connectdb()
try:
    msgmark = int(open(ftnconfig.MSGMARKESTAT).read())
except:
    print("mark not found")
    msgmark = 0

outp = []
total = 0

Q_stat = db.prepare("select d.text, count(m.id) from messages m, addresses d "
            "where m.id>$1 and m.processed=0 and m.destination=d.id and d.domain=$2 "
            "group by d.text "
            "having count(m.id)>0 "
            "order by count(m.id) desc ")

Q_msg = db.prepare("select max(id) from messages")


with db.xact(isolation='SERIALIZABLE', mode='READ ONLY'):

    newmsgmark = Q_msg.first()

    for e, c in Q_stat(msgmark, db.FTN_domains["echo"]):
        outp.append ("%-30s %d\n"%(e, c))
        total += c


with ftnimport.session(db) as sess:
    sess.send_message(("node", ftnconfig.ADDRESS), "Sergey Dorofeev", ("echo", "FLUID.REPORTS"), "All", None, "статистика эхомейла",
"""Привет All

Traffic since last statistics generation:

%s

Total: %d
Last message id: %d

Вот так
"""%("".join(outp), total, newmsgmark))

    open(ftnconfig.MSGMARKESTAT, "w").write(str(newmsgmark))
