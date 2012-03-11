#!/usr/local/bin/python3 -bb

import xml.etree.ElementTree
import ftnconfig

db=ftnconfig.connectdb()

START = 1198161

did=db.prepare("select id from addresses where text='FLUID.REPORTS' and domain=2").first()

#for src, dst, header, body, origcharset in db.prepare("select source, destination, header, body from messages where id=$1")(1170744):
for mid, src, dst, header, body, origcharset in db.prepare(
    "select id, source, destination, header, body, origcharset from messages "
        "where destination=$1 and id>$2 and processed<>5"
        "order by id")(did, START):
    print ("*"*79)
    print (mid, src, dst)
    print (xml.etree.ElementTree.tostring(header, encoding='utf-8').decode('utf-8'))
#    print (body.encode(origcharset).decode("cp437"))
    print (body)
