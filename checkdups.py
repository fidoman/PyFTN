#!/usr/local/bin/python3 -bb

# check that messages in dupearea really the same as in database

import os
import sys
from ftnconfig import *
import ftn.msg
import postgresql
import xml.etree.ElementTree
import ast

from ftnimport import normalize_message
from stringutil import *
import ftnexport

db=connectdb()

Q_msgget = db.prepare("select m.id, m.msgid, m.header, m.body, m.origcharset, s.domain, s.text, d.domain, d.text "
            "from messages m, addresses s, addresses d "
            "where m.msgid=$1 and m.source=s.id and m.destination=d.id")

#DUPDIR=BADDIR

if len(sys.argv)<2:
  print(DUPDIR)
  filelist=os.listdir(DUPDIR)
else:
  filelist=sys.argv[1:]

for f in filelist:
  fn, fext = os.path.splitext(f)
  if fext==".msg" and fn.find(".db")==-1:

    print(f, end=' ')

    m=ftn.msg.MSG(os.path.join(DUPDIR,f))

    (origdomname, origaddr), (destdomname, destaddr), msgid, header, body, charset = normalize_message(m)

    print("msgid='%s'"%msgid,end=' ')

#    if destdomname!="echo":
#        print ("not echomail")
#        continue

#    print("---")
#    print("From:",header.find("sendername").text, origdomname, origaddr)
#    print("To:  ",header.find("recipientname").text, destdomname, destaddr)
#    print("Date:",header.find("date").text)
#    print("Subj:",header.find("subject").text)

    #print(body)

#    print("message in database ---")
    dbmessages=Q_msgget(msgid)
    if len(dbmessages)>1:
      raise Exception("multiple messages in database with this MSGID")
    dbid, dbmsgid, dbheader, dbbody, dbcharset, dbsd, dbst, dbdd, dbdt = dbmessages[0]
    dbsd = db.FTN_backdomains[dbsd]
    dbdd = db.FTN_backdomains[dbdd]

#    print("From:",dbheader.find("sendername").text, dbsd, dbst)
#    print("To:  ",dbheader.find("recipientname").text, dbdd, dbdt)
#    print("Date:",dbheader.find("date").text)
#    print("Subj:",dbheader.find("subject").text)
#    print("----------------------------------------------------------------------")

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
    if not subjmatch:
        subj1=ast.literal_eval('"'+subj1+'"')
        subjmatch = subj1.replace("\x0A","")==subj2.replace("\x0A","")

    print ("Same subject:",subjmatch)

    match = subjmatch and (body.strip()==dbbody.strip() or dbbody.strip().startswith(body.strip()))

    print("and same body:", match)
    if destdomname=="echo" and match and (destdomname,destaddr)==(dbdd,dbdt):
      os.unlink(os.path.join(DUPDIR,f))
      os.unlink(os.path.join(DUPDIR,f[:-4]+".status"))
      try:
        os.unlink(os.path.join(DUPDIR, fn+".db%d.msg"%dbid))
      except:
        pass

    else:
      dupf=open(os.path.join(DUPDIR, fn+".db%d.msg"%dbid), "wb")
      dbmsg,_=ftnexport.denormalize_message(
        (dbsd, dbst), (dbdd, dbdt),
        dbmsgid, dbheader, dbbody, dbcharset, echodest=ADDRESS, addpath=ADDRESS)
      dupf.write(dbmsg.pack())
      dupf.close()
