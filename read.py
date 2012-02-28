#!/usr/local/bin/python3 -bb

import re
import tempfile
import os
import ast
import xml.etree.ElementTree
import ftnconfig
import ftnexport
import ftnimport

db=ftnconfig.connectdb()

my_id = ftnconfig.get_addr_id (db, db.FTN_domains["node"], ftnconfig.ADDRESS)
RE_s = re.compile("\s+")
RE_quote = re.compile("\s*(\S{0,2})(\>+)\s*(.*)$")

MAXW=79

def quote(qname, block):
  if len(block) and block[-1].startswith(" * "):
    block.pop(-1)
  if len(block) and block[-1].startswith("---"):
    block.pop(-1)
  if len(block) and block[-1].startswith("..."):
    block.pop(-1)
  while len(block) and block[-1]=="":
    block.pop(-1)
  while len(block) and block[0]=="":
    block.pop(0)
  if len(block) and block[0].strip().startswith("Hello") or block[0].strip().startswith("Привет"):
    block.pop(0)
  while len(block) and block[0]=="":
    block.pop(0)

  # go line by line looking for quote level.
  # reformat text in one quote level 

  outp = []
  qlblock = []
  qlevel = 0


  print ("\n".join(block)+"\n")


txt="""    Приветствую Вас, Sergey!

23 фев 12 23:54, Sergey Dorofeev wrote to Alex Barinov:

 AB>> С уходом Юры Богоявленского информаци по бекбону 5020 не
 AB>> публиковалась, впрочем, ничего в ней с тех пор и не поменялось.
 AB>> Разве что кто-то из хабов сеть покинул... Если есть необходимость,
 AB>> могу восстановить публикацию этой информации, предварительно её
 AB>> обновив. А так - спрашивай, отвечу. :-)
 SD> Было бы неплохо обновить, поскольку изменения такие, что /400 свалил,
 SD> /758 написал о полном автопилоте. В общем освежить картинку

Угу. Эхолист начал актуализировать. Хабов тоже обновлю как руки дойдут. Кстати, /400, таки вернулся и пока стабильно работает, так что не вижу смысла гнать его из хабов, тем более, что многие вторичники с него кормятся.

                                      Алексей Баринов

E-Mail: bav (at) sirena-travel.ru ICQ: 24466689 Skype: huba-huba
[Team Бородатые]
--- GoldED+/W32-MSVC 1.1.5-20051112
 * Origin: Alex at Work (2:5020/715.1)
"""
  
#quote("AB", txt.splitlines())
#exit()



def submit(file):
  doheader = True
  for l in file.splitlines():
    l=l.rstrip()
    if doheader:
      if l=="":
        doheader = False
        body = []
        continue
      if l.startswith("From: "):
        fromname = ast.literal_eval(l[6:])
      elif l.startswith("To: "):
        toname = ast.literal_eval(l[4:])
      elif l.startswith("Subject: "):
        subj = ast.literal_eval(l[9:])
      elif l.startswith("ReplyTo: "):
        msgid = ast.literal_eval(l[9:])
      elif l.startswith("Destination: "):
        dest = ast.literal_eval(l[13:])
      else:
        if l[0]!="#":
          raise Exception("invalid header %s"%repr(l))
    else:
      body.append(l)

  with ftnimport.session(db) as sess:
    sess.send_message(fromname, dest, toname, msgid, subj, "\n".join(body))


def reply(srcid, dstid, msgid, header, body):

      nameparts = RE_s.split(header.find("sendername").text.strip())
      senderfirstname = nameparts[0]
      if senderfirstname:
        qname = senderfirstname[0]
      else:
        qname = ''
      if len(nameparts)>1:
        qname += nameparts[-1][0]

      origdom, origtext = ftnconfig.get_addr(db, srcid)
      origdom = db.FTN_backdomains[origdom]
      destdom, desttext = ftnconfig.get_addr(db, dstid)
      destdom = db.FTN_backdomains[destdom]
      
      tpl = ["From: " + repr(ftnconfig.SYSOP) + "\n"]
      tpl.append("To: " + repr(header.find("sendername").text) + "\n")
      tpl.append("Subject: " + repr(header.find("subject").text) + "\n")
      tpl.append("ReplyTo: " + repr(msgid) + "\n")
      tpl.append("Destination: " + repr((destdom, desttext)) + "\n")
      tpl.append("#Destination: " + repr((origdom, origtext)) + "\n")
      tpl.append("\n")
      tpl.append(" ".join(("Hello", senderfirstname))+",\n")
      tpl.append("\n")
      tpl.append("orig.message to %s %s on "%(destdom, desttext) + header.find("date").text.strip() + "\n")

      for bl in body.splitlines():
        while len(bl)>72:
            spc=bl.rfind(" ", 0, 72)
            if spc==-1:
              spc=72
            tpl.append(" "+qname+"> " + bl[:spc] +"\n")
            bl=bl[spc:].lstrip()
        tpl.append(" "+qname+"> " + bl +"\n")

      tpl.append("\n")
      tpl.append("Sergey\n")
      tpl.append("\n")
      tpl.append("... vim\n")

      newmsg = "".join(tpl)
      (fh, fname) = tempfile.mkstemp()
      fo = os.fdopen(fh, "w")
      fo.write(newmsg)
      fo.close()
      os.system ("vi " + fname)
      editedmsg = open(fname).read()
      if newmsg == editedmsg:
        print("no changes")
        r = False
      else:
        submit(editedmsg)
        r = True
      os.unlink(fname)
      return r


def view(mid, srcid, dstid, header, body):
    print ("="*10 + " %20d "%mid + "="*47)
    print ("From: %-36s, %s"%(header.find("sendername").text, str(ftnconfig.get_addr(db, srcid))))
    print ("To  : %-36s, %s"%(header.find("recipientname").text, str(ftnconfig.get_addr(db, dstid))))
    print ("Subj: %s"%header.find("subject").text)
    print ("Date: %s"%header.find("date").text)
    print ("-"*79)
    print (body)
    print ("="*79)


committer = ftnexport.netmailcommitter(db)

for mid, srcid, dstid, msgid, header, body, origcharset, receivedfrom in ftnexport.get_subscriber_messages_n(db, my_id, db.FTN_domains["node"]):
    view(mid, srcid, dstid, header, body)
    cmd = None
    while not cmd:
      x = input("Commit, Reply, Quit> ")
      if x in ("c", "r", "q"):
        cmd = x
      elif x == "":
        cmd = "m" # more

    if cmd == "q":
      break
    elif cmd == "c":
      committer.add (mid)
      committer.commit()
    elif cmd == "r":
      if reply (srcid, dstid, msgid, header, body):
        committer.add (mid)
        committer.commit()

    print ()


committer = ftnexport.echomailcommitter(db)

for mid, srcid, dstid, msgid, header, body, origcharset, receivedfrom, subsid in ftnexport.get_subscriber_messages_e(db, my_id, db.FTN_domains["echo"]):
    view(mid, srcid, dstid, header, body)
    committer.add ((subsid, mid))
    cmd = None
    while not cmd:
      x = input("Commit, Reply, Quit> ")
      if x in ("c", "r", "q"):
        cmd = x
      elif x == "":
        cmd = "m" # more

    if cmd == "q":
      break
    elif cmd == "c":
      committer.commit()
    elif cmd == "r":
      if reply (srcid, dstid, msgid, header, body):
        committer.commit()

    print ()

exit()

#did=db.prepare("select id from addresses where text='N5020.CRISIS' and domain=2").first()
#did=db.prepare("select id from addresses where text='N5020.SYSOP' and domain=2").first()
#did=db.prepare("select id from addresses where text='R50.SYSOP' and domain=2").first()
#did=db.prepare("select id from addresses where text='R50.SYSOP.TALK' and domain=2").first()
#did=db.prepare("select id from addresses where text='FLUID.REPORTS' and domain=2").first()
did=db.prepare("select id from addresses where text='FLUID.LOCAL' and domain=2").first()
#did=db.prepare("select id from addresses where text='PUSHKIN.LOCAL' and domain=2").first()
#did=db.prepare("select id from addresses where text='MO.IZMAILOVO' and domain=2").first()
#did=db.prepare("select id from addresses where text='MO.VIDNOE' and domain=2").first()
#did=db.prepare("select id from addresses where text='RU.SOCIONIC' and domain=2").first()
#did=db.prepare("select id from addresses where text='RU.BIOLOGY' and domain=2").first()
#did=db.prepare("select id from addresses where text='RU.PSYCHOLOGY' and domain=2").first()
#did=db.prepare("select id from addresses where text='TESTING' and domain=2").first()
#did=db.prepare("select id from addresses where text='FIDOTEST' and domain=2").first()
#did=db.prepare("select id from addresses where text='$CRACK$' and domain=2").first()
#did=db.prepare("select id from addresses where text='$CRACK$.TALKS' and domain=2").first()
#did=db.prepare("select id from addresses where text='FN_SYSOP' and domain=2").first()
#did=db.prepare("select id from addresses where text='BBS_ADS' and domain=2").first()
#did=db.prepare("select id from addresses where text='ESTAR.TEST' and domain=2").first()

#for src, dst, header, body, origcharset in db.prepare("select source, destination, header, body from messages where id=$1")(1170744):
for mid, src, dst, header, body, origcharset in db.prepare(
    "select id, source, destination, header, body, origcharset from messages "
        "where destination=$1 and id>1170000 and processed<>5"
        "order by id")(did):
    print ("*"*79)
    print (mid, src, dst)
    print (xml.etree.ElementTree.tostring(header, encoding='utf-8').decode('utf-8'))
#    print (body.encode(origcharset).decode("cp437"))
    print (body)
