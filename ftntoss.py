#!/bin/env python3 -bb

""" legacy tosser - create bundles on periodical basis (contrast to on-session packing) """

import time
import os
from ast import literal_eval
import xml.etree.ElementTree
import traceback

from ftnconfig import *
import ftnexport
import ftn.pkt
import ftn.addr


class packer:
  def __init__(self, me, node, bundle=True):
    self.bundle=None
    self.packet=None
    self.node=node
    self.me=me
    self.destdir=os.path.join(OUTBOUND, '.'.join(map(str,ftn.addr.str2addr(self.node))))

  def init_bundle(self):
    raise

  def init_pkt(self):
    raise

  def add_message(self, m):
    if not self.packet:
      self.packet=ftn.pkt.PKT()
      self.packet.password=(get_link_password(db, self.node) or '').encode("utf-8")[:8]
      self.packet.source=ftn.addr.str2addr(self.me)
      self.packet.destination=ftn.addr.str2addr(self.node)
      self.packet.date=time.localtime()
      self.packet.msg=[m]
      self.packet.approxlen=100+len(m.body)
    else:
      self.packet.msg.append(m)
      self.packet.approxlen+=100+len(m.body)

    if self.packet.approxlen>1000000:
      self.flush_packet()

  def flush_packet(self):
      #write pkt to outbound
      
      if not os.path.exists(self.destdir):
        os.makedirs(self.destdir)
      try:
        counter=literal_eval(open(self.destdir+".pktcounter").read())
      except IOError as e:
        if e.args[0]!=2:
          raise e
        counter=0
      pktfile=os.path.join(self.destdir, "%08x.pkt"%counter)
      open(self.destdir+".pktcounter", "w").write(str(counter+1))
      self.packet.save(pktfile)
      self.packet=None


  def flush(self):
    if self.packet:
      self.flush_packet()
    if self.bundle:
      self.flush_bundle()

# no auto flush - only when correctly updating lastsent
#  def __del__(self):
#    self.flush()


subscriber_cache = {}

# 1. Get all addresses having subscription

for link_id, link_addr, ladom, latext in db.prepare("select l.id, l.address, a.domain, a.text from links l, addresses a where l.address=a.id"):
  print(latext)
  p=None
  flush_list=[]

#  for sub_id, sub_targ, sub_last in db.prepare("select id, target, lastsent from subscriptions where subscriber=$1").rows(link_addr):
  for sub_id, sub_targ, sub_lastsent in ftnexport.get_node_subscriptions(db, latext, "echo"):
    #print("   ", sub_id)

    destdom, desttext = db.prepare("select domain, text from addresses where id=$1").first(sub_targ)
    destdom = db.FTN_domains[destdom]

    #!!!print("move it to ftnexport and update for recursive queries")
    
    if sub_targ in subscriber_cache:
        subscribers = subscriber_cache[sub_targ]
    else:
        subscribers = db.prepare("select a.domain, a.text from subscriptions s, addresses a where s.target=$1 and s.subscriber=a.id")(sub_targ)

        if not all([x[0]==db.FTN_domains["node"] for x in subscribers]):
          raise FTNFail("subscribers from wrong domain for "+str(sub_targ))

        #    print(sub_id, sub_targ, "all subscribers:", [x[1] for x in subscribers])

        subscribers = subscriber_cache[sub_targ] = [x[1] for x in subscribers]

    # --- begin work with messages in subscription  ---

    max_id=sub_lastsent
    sub_content=False
    for m_id, m_srcdom, m_srctext, m_msgid, m_header, m_body, m_recvfrom in ftnexport.get_messages(db, sub_targ, sub_lastsent):
      sub_content=True
      if not p:
        p=packer(ADDRESS, latext, True)

      if m_id>max_id: 
        max_id=m_id

      #.. skip the message if is is received from this node or this node is commuter as node from which message was received
      if m_recvfrom == link_addr:
        continue # received from this node

      subscriber_comm = db.FTN_commuter.get(sub_id)
      if subscriber_comm in not None:
        # get subscription through what message was received
        recvfrom_subscription = db.prepare("select id from subscriptions where target=$1 and subscriber=$2").first(sub_tart, m_recvfrom)
        recvfrom_comm = db.FTN_commuter.get(recvfrom_subscription)
        if recvfrom_comm == subscriber_comm:
          continue # do not forward between subscriptions in one commuter group (e.g. two uplinks)
      

      # modify path and seen-by
      # seen-by's - get list of all subscribers of this target; add subscribers list
      #... if go to another zone remove path and seen-by's and only add seen-by's of that zone -> ftnexport
      try:
        msg=ftnexport.denormalize_message((m_srcdom, m_srctext), (destdom, desttext), m_msgid, m_header, m_body, latext, addseenby=subscribers, addpath=ADDRESS)
      except:
        raise Exception("denormalization error on message id=%d"%m[0]+"\n"+traceback.format_exc())
      p.add_message(msg)
      


    # --- end work with messages in subscription  ---

    if sub_content:
    #  p.flush()
    #  ftnexport.update_subscription_watermark(db, sub_id, max_id)
      flush_list.append((sub_id, max_id))

  if p:
    p.flush()
    for sub_id, max_id in flush_list:
      ftnexport.update_subscription_watermark(db, sub_id, max_id)

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
