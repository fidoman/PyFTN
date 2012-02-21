#!/bin/env python3 -bb

# check that messages in dupearea really the same as in database

import os
from ftnconfig import *
import ftn.msg
import postgresql
import xml.etree.ElementTree

from ftnimport import normalize_message

db=connectdb()

Q_msgget = db.prepare("select m.msgid, m.header, m.body, s.domain, s.text, d.domain, d.text "
            "from messages m, addresses s, addresses d "
            "where m.msgid=$1 and m.source=s.id and m.destination=d.id")


for f in os.listdir(DUPDIR):
  if f.endswith(".msg"):

    print("======================================================================")
    print(f)

    m=ftn.msg.MSG(os.path.join(DUPDIR,f))

    (origdomname, origaddr), (destdomname, destaddr), msgid, header, body = normalize_message(m)

    print(msgid)

    print("----------------------------------------------------------------------")
    print(header.find("sendername").text, origdomname, origaddr)
    print(header.find("recipientname").text, destdomname, destaddr)
    print(header.find("date").text)
    print(header.find("subject").text)

    #print(body)

    print("----------------------------------------------------------------------")
    dbmsgid, dbheader, dbbody, dbsd, dbst, dbdd, dbdt = Q_msgget(msgid)[0]

    print(dbheader.find("sendername").text, dbsd, dbst)
    print(dbheader.find("recipientname").text, dbdd, dbdt)
    print(dbheader.find("date").text)
    print(dbheader.find("subject").text)
    print("----------------------------------------------------------------------")

    match= header.find("subject").text==dbheader.find("subject").text and body==dbbody

    print(match, origdomname, destdomname)
    if destdomname=="echo" and match:
      os.unlink(os.path.join(DUPDIR,f))
      os.unlink(os.path.join(DUPDIR,f[:-4]+".status"))

    else:
      pass
      #open("check1", "w").write(body)
      #open("check2", "w").write(dbbody)
      #print("look at check1, check2")
      