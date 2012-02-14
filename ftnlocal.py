#!/usr/local/bin/python3 -bb

""" process local mail """

from ftnconfig import *
import ftnexport
import ftnimport
import time
from ftn.ftn import *

from badwriter import BadWriter

localmsgs=BadWriter(LOCALNETMAIL, os.path.join(LOCALNETMAIL, "next"), "msg")

def fix(db, sess, src, srcname, destname, domain, password, msgid, cmdtext):
  dom, text = db.prepare("select domain, text from addresses where id=$1").first(src)
  if dom != db.FTN_domains["node"]:
    raise FTNFail("not our domain")
  print(text)
  if password != get_link_password(db, text):
    reply=["wrong password"]
  else:
    reply=[]
    for cmd in map(str.strip, cmdtext.upper().strip().split("\n")):
      if cmd.startswith("---"):
        break
      elif len(cmd)==0:
        continue
      elif cmd.startswith("%RESCAN "):
        reply.append("Rescan not implemented, contact sysop: "+cmd)
      elif cmd.startswith("%PING"):
        reply.append("NOP: "+cmd)
      elif cmd.startswith("%QUERY"):
        reply.append("Sorry not implemented: "+cmd)
      elif cmd.startswith("%INFO"):
        reply.append("Sorry not implemented: "+cmd)
      elif cmd.startswith("%HELP"):
        reply.append("Sorry not implemented: "+cmd)
      elif cmd.startswith("%LIST"):
        reply.append("Sorry not implemented: "+cmd)
      elif cmd.startswith("%AVAIL"):
        reply.append("Sorry not implemented: "+cmd)
      elif cmd.startswith("%PAUSE"):
        reply.append("Sorry not implemented: "+cmd)
      elif cmd.startswith("-"):
        try:
          reply.append(sess.remove_subscription(domain, cmd[1:], text) + ": " + cmd)
        except FTNNoAddressInBase:
          reply.append("no such area: " + cmd)
      elif cmd.startswith("+"):
        try:
          reply.append(sess.add_subscription(False, domain, cmd[1:], text) + ": " + cmd)
        except FTNNoAddressInBase:
          reply.append("no such area: " + cmd)
        except FTNAlreadySubscribed:
          reply.append("seems you are uplink for it: " + cmd)
      elif cmd.startswith("%"):
        reply.append("Unknown command: "+cmd)
        print(cmd)
        1/0
      else:
        try:
          reply.append(sess.add_subscription(False, domain, cmd, text) + ": " + cmd)
        except FTNNoAddressInBase:
          reply.append("no such area: " + cmd)
        except FTNAlreadySubscribed:
          reply.append("seems you are uplink for it: " + cmd)
  reply.append("")
  sess.send_message(destname+" Robot", ("node", text), srcname, msgid, "report", "\n".join(reply))
  print(reply)


#for s in ftnexport.get_node_subscriptions(db, "2:5020/4441", "echo"):
#  print(db.prepare("select a.domain, a.text from addresses a, subscriptions s where s.id=$1 and a.id=s.target")(s)[0])
#exit()

db = connectdb()
me = db.prepare("select id from addresses where domain=$1 and text=$2").first(db.FTN_domains["node"], ADDRESS)

fixes_e = []
fixes_f = []
my = []


for id_msg, src, dest, msgid, header, body, recvfrom in ftnexport.get_subscriber_messages_n(db, me, db.FTN_domains["node"]):

  if header.find("recipientname").text.lower() == "areafix":
    fixes_e.append((id_msg, src, time.mktime(time.strptime(header.find("date").text, "%d %b %y  %H:%M:%S")), 
        header.find("sendername").text, header.find("subject").text, msgid, body))

  elif header.find("recipientname").text.lower() in ("filefix", "allfix"):
    fixes_f.append((id_msg, src, time.mktime(time.strptime(header.find("date").text, "%d %b %y  %H:%M:%S")), 
        header.find("sendername").text, header.find("subject").text, msgid, body))

  else:

    srca=db.prepare("select domain, text from addresses where id=$1").first(src)
    dsta=db.prepare("select domain, text from addresses where id=$1").first(dest)

    print(srca)

    m = ftnexport.denormalize_message(
        (db.FTN_backdomains[srca[0]], srca[1]),
        (db.FTN_backdomains[dsta[0]], dsta[1]),
        msgid, header, body)

    my.append((id_msg, time.mktime(time.strptime(header.find("date").text, "%d %b %y  %H:%M:%S")), m))

    print("*************"+str(id_msg)+"*"+msgid+"*****************")
    print("From:", header.find("sendername").text, src)
    print("To  :", header.find("recipientname").text, dest)
    print("Date:", header.find("date").text)
    print("Subj:", header.find("subject").text)
#    print(body)
    # process
    # if fail abort
    # if ok update watermark update_subscription_watermark(db, localnetmailsubscription, id_msg)


fixes_e.sort(key = lambda x: x[2])
fixes_f.sort(key = lambda x: x[2])
my.sort(key = lambda x: x[1])

for id_msg, _, m in my:
  localmsgs.write(m.pack(), None)
  db.prepare("update messages set processed=1 where id=$1")(id_msg)

for id_msg, src, _, sn, h, mi, b in fixes_e:
  with ftnimport.session(db) as sess:
    fix(db, sess, src, sn, "AreaFix", db.FTN_domains["echo"], h, mi, b)
    db.prepare("update messages set processed=1 where id=$1")(id_msg)
    

for id_msg, src, _, sn, h, mi, b in fixes_f:
  with ftnimport.session(db) as sess:
    fix(db, sess, src, sn, "FileFix", db.FTN_domains["fileecho"], h, mi, b)
    db.prepare("update messages set processed=1 where id=$1")(id_msg)

exit()

#for s in ftnexport.get_node_subscriptions(db, "2:5020/12000", "node"):
#  print(db.prepare("select a.domain, a.text from addresses a, subscriptions s where s.id=$1 and a.id=s.target")(s)[0])


for sub_id, target_id, lastsent in ftnexport.get_node_subscriptions(db, ADDRESS, "node"):
  print(sub_id, ": mail directed to", 
        db.prepare("select a.domain, a.text from addresses a, subscriptions s where s.id=$1 and a.id=s.target").first(sub_id))
  
  for id_msg, srcdom, srctext, msgid, header, body, recvfrom in ftnexport.get_messages(db, target_id, lastsent):
    print("*************"+str(id_msg)+"*"+msgid+"*****************")
    print("From:", header.find("sendername").text.encode("utf-8"), srcdom,srctext)
    print("To  :", header.find("recipientname").text.encode("utf-8"), "node",ADDRESS)
    print("Date:", header.find("date").text.encode("utf-8"))
    print("Subj:", header.find("subject").text.encode("utf-8"))
    print(body.encode("utf-8"))
    # process
    # if fail abort
    # if ok update watermark update_subscription_watermark(db, localnetmailsubscription, id_msg)
