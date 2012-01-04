#!/bin/env python3 -bb

""" legacy tosser - create bundles on periodical basis (contrast to on-session packing) """

import time

from ftnconfig import *
import ftnexport

class packer:
  def __init__(self, me, node, bundle=True):
    self.bundle=None
    self.packet=None
    self.node=node
    self.me=me

  def init_bundle(self):
    raise

  def init_pkt(self):
    raise

  def add_message(self, m):
    if not self.packet:
      self.packet=ftn.pkt.PKT()
      self.packet.password=get_link_password(db, node)
      self.packet.source=ftn.addr.str2addr(self.me)
      self.packet.destination=ftn.addr.str2addr(self.node)
      self.packet.date=time.localtime()
      self.packet.msg=[m]
      self.packet.approxlen=100+len(m.body)
    else:
      self.packet.msg.append(m)
      self.packet.approxlen+=100+len(m.body)

    if self.packet.approxlen>1000000:
      #write pkt to outbound
      ...

  def flush(self):
    raise

  def __del__(self):
    self.flush()


# 1. Get all addresses having subscription

for link, linkaddr, ladom, latext in db.prepare("select l.id, l.address, a.domain, a.text from links l, addresses a where l.address=a.id"):
  print(latext)
  p=None
#  for sub_id, sub_targ, sub_last in db.prepare("select id, target, lastsent from subscriptions where subscriber=$1").rows(linkaddr):
  for sub_id, sub_targ, sub_lastsent in ftnexport.get_node_subscriptions(db, latext, "echo"):
    #print("   ", sub_id)

    # --- begin work with messages in subscription  ---

    max_id=sub_lastsent
    sub_content=False
    for m in ftnexport.get_messages(db, sub_targ, sub_lastsent):
      if not p:
        p=packer(latext, True)
      print(m)
      if m[0]>max_id: 
        max_id=m[0]
      msg=ftnexport.denormalize_message(m)
      p.add(msg)
      sub_content=True
      


    # --- end work with messages in subscription  ---

    if sub_content:
      p.flush()
      ftnexport.update_subscription_watermark(db, sub_id, max_id)

  if p:
    p.flush()

    exit()
exit()

# all the unsent
#for a in db.prepare("select m.id, s.subscriber from messages m, subscriptions s where s.target=m.destination and (s.lastsent<m.id or s.lastsent is NULL)"):
#  print(a)

# for each address for each its subscriptions do tossing
# don't forget about path and seen-by

#for s in ftnexport.get_node_subscriptions(db, "2:5020/4441", "echo"):
#  print(db.prepare("select a.domain, a.text from addresses a, subscriptions s where s.id=$1 and a.id=s.target")(s)[0])
#exit()

#for s in ftnexport.get_node_subscriptions(db, "2:5020/12000", "node"):
#  print(db.prepare("select a.domain, a.text from addresses a, subscriptions s where s.id=$1 and a.id=s.target")(s)[0])

#for localnetmailsubscription in ftnexport.get_node_subscriptions(db, ADDRESS, "node"):
#  print(localnetmailsubscription, ": mail directed to", 
#        db.prepare("select a.domain, a.text from addresses a, subscriptions s where s.id=$1 and a.id=s.target").first(localnetmailsubscription))
#  
#  for id_msg, srcdom, srctext, dstdom, dsttext, msgid, header, body in ftnexport.get_subscription_messages(db, localnetmailsubscription):
#    print("*************"+str(id_msg)+"*"+msgid+"*****************")
#    print("From:", header.find("sendername").text,srcdom,srctext)
#    print("To  :", header.find("recipientname").text,dstdom,dsttext)
#    print("To  :", header.find("date").text)
#    print("Subj:", header.find("subject").text)
#    print(body)
#    # process
#    # if fail abort
#    # if ok update watermark update_subscription_watermark(db, localnetmailsubscription, id_msg)
