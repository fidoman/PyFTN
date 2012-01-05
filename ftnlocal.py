#!/bin/env python3 -bb

""" process local mail """

from ftnconfig import *
import ftnexport

#for s in ftnexport.get_node_subscriptions(db, "2:5020/4441", "echo"):
#  print(db.prepare("select a.domain, a.text from addresses a, subscriptions s where s.id=$1 and a.id=s.target")(s)[0])
#exit()

#for s in ftnexport.get_node_subscriptions(db, "2:5020/12000", "node"):
#  print(db.prepare("select a.domain, a.text from addresses a, subscriptions s where s.id=$1 and a.id=s.target")(s)[0])

for sub_id, target_id, lastsent in ftnexport.get_node_subscriptions(db, ADDRESS, "node"):
  print(sub_id, ": mail directed to", 
        db.prepare("select a.domain, a.text from addresses a, subscriptions s where s.id=$1 and a.id=s.target").first(sub_id))
  
  for id_msg, srcdom, srctext, msgid, header, body, recvfrom in ftnexport.get_messages(db, target_id, lastsent):
    print("*************"+str(id_msg)+"*"+msgid+"*****************")
    print("From:", header.find("sendername").text,srcdom,srctext)
    print("To  :", header.find("recipientname").text,"node",ADDRESS)
    print("Date:", header.find("date").text)
    print("Subj:", header.find("subject").text)
    print(body)
    # process
    # if fail abort
    # if ok update watermark update_subscription_watermark(db, localnetmailsubscription, id_msg)
