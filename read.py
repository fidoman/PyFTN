#!/usr/local/bin/python3 -bb

import xml.etree.ElementTree
import ftnconfig

db=ftnconfig.connectdb()

#did=db.prepare("select id from addresses where text='N5020.CRISIS' and domain=2").first()
#did=db.prepare("select id from addresses where text='N5020.SYSOP' and domain=2").first()
#did=db.prepare("select id from addresses where text='R50.SYSOP' and domain=2").first()
#did=db.prepare("select id from addresses where text='R50.SYSOP.TALK' and domain=2").first()
#did=db.prepare("select id from addresses where text='FLUID.REPORTS' and domain=2").first()
#did=db.prepare("select id from addresses where text='FLUID.LOCAL' and domain=2").first()
#did=db.prepare("select id from addresses where text='PUSHKIN.LOCAL' and domain=2").first()
#did=db.prepare("select id from addresses where text='MO.IZMAILOVO' and domain=2").first()
#did=db.prepare("select id from addresses where text='MO.VIDNOE' and domain=2").first()
#did=db.prepare("select id from addresses where text='RU.SOCIONIC' and domain=2").first()
#did=db.prepare("select id from addresses where text='RU.BIOLOGY' and domain=2").first()
#did=db.prepare("select id from addresses where text='RU.PSYCHOLOGY' and domain=2").first()
#did=db.prepare("select id from addresses where text='TESTING' and domain=2").first()
did=db.prepare("select id from addresses where text='FIDOTEST' and domain=2").first()

#for src, dst, header, body in db.prepare("select source, destination, header, body from messages where id=$1")(1170744):
for mid, src, dst, header, body in db.prepare(
    "select id, source, destination, header, body from messages "
        "where destination=$1 and id>1170000 "
        "order by id")(did):
    print ("*"*79)
    print (mid, src, dst)
    print (xml.etree.ElementTree.tostring(header, encoding='utf-8').decode('utf-8'))
    print (body)
