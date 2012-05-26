#!/usr/local/bin/python3 -bb

# check that messages in dupearea really the same as in database

import os
from ftnconfig import *
import ftn.msg
import postgresql
import xml.etree.ElementTree

from ftnimport import normalize_message
from stringutil import *

db=connectdb()

Q_msgget = db.prepare("select m.msgid, m.header, m.body, s.domain, s.text, d.domain, d.text "
            "from messages m, addresses s, addresses d "
            "where m.msgid=$1 and m.source=s.id and m.destination=d.id")

#DUPDIR=BADDIR

print(DUPDIR)
for f in os.listdir(DUPDIR):
  if f.endswith(".msg"):

    print("======================================================================")
    print(f)

    m=ftn.msg.MSG(os.path.join(DUPDIR,f))

    (origdomname, origaddr), (destdomname, destaddr), msgid, header, body, charset = normalize_message(m)

    print(msgid)

    if destdomname!="echo":
        print ("not echomail")
        continue

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

    body = body.strip()
    dbbody = dbbody.strip()

    subj1 = header.find("subject").text
    subj2 = dbheader.find("subject").text

    if subj1 is None:
        subj1 = ""

    if subj2 is None:
        subj2 = ""

    #print (subj1==subj2, body==dbbody)

    subjmatch = subj1==subj2
    if not subjmatch:
        subjmatch = subj1==clean_str(subj2)

    print (subjmatch)
    match = subjmatch and body==dbbody

    print(match, origdomname, destdomname)
    if destdomname=="echo" and match:
      os.unlink(os.path.join(DUPDIR,f))
      os.unlink(os.path.join(DUPDIR,f[:-4]+".status"))

    else:
      print (repr(subj1), repr(subj2))
      open("check1", "w").write(body)
      open("check2", "w").write(dbbody)
      print("look at check1, check2")
      break
