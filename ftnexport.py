"""
Message flow from database to links and users
"""

#from ftnconfig import *

import ftn.msg

def get_node_subscriptions(db, addr, msgdom):
  """ addr - address of subscriber node
      msgdom - destination domain of messages (no combining supported)
  """
  domains = db.FTN_domains
  try:
    Q_get_node_subscriptions = db.Q_get_node_subscriptions
  except AttributeError as e:
    # target: any but domain msgdom
    # subscriber: addr
    Q_get_node_subscriptions = db.Q_get_node_subscriptions = db.prepare("select s.id, t.id, s.lastsent from subscriptions s, addresses sr, addresses t "
        "where s.target=t.id and t.domain=$1 and s.subscriber=sr.id and sr.domain=$2 and sr.text=$3")

  return Q_get_node_subscriptions.rows(domains[msgdom], domains["node"], addr)




def get_messages(db, dest_id, lastsent):
  try:
    Q_get_subscription_messages = db.Q_get_subscription_messages
  except AttributeError:
#    Q_get_subscription_messages = db.Q_get_subscription_messages = db.prepare("select m.id, s.domain, s.text, d.domain, d.text, m.msgid, m.header, m.body from "
#        "subscriptions sr, messages m, addresses s, addresses d "
#        "where sr.id=$1 and (m.id>sr.lastsent or sr.lastsent is NULL) and m.destination=sr.target and (m.processed is NULL or m.processed<>5)"
#        "and m.source=s.id and m.destination=d.id")

    Q_get_subscription_messages = db.Q_get_subscription_messages = db.prepare("select m.id, s.domain, s.text, d.domain, d.text, m.msgid, m.header, m.body from "
        "messages m, addresses s, addresses d "
        "where m.id>$2 and m.destination=$1 and (m.processed is NULL or m.processed<>5)"
        "and m.source=s.id and m.destination=d.id")

  for m in Q_get_subscription_messages(dest_id, lastsent):
    yield m[0], db.FTN_backdomains[m[1]], m[2], db.FTN_backdomains[m[3]], m[4], m[5], m[6], m[7]

  return

def update_subscription_watermark(db, subscription, id):
  raise Exception("not implemented")



def denormalize_message(orig, dest, msgid, header, body, echodest):
  (origdom, origaddr) = orig
  (destdom, destaddr) = dest

  if origdom!="node":
    raise FTNFail("message source must be node not %s"%origdom)

  msg=ftn.msg.MSG()
  print(orig, dest)
  fname=header.find("sendername").text
  tname=header.find("recipientname").text
  subj=header.find("subject").text
  date=header.find("date").text
  print(fname, tname, subj, date)

  if destdom=="echo":
    msg.body=[""]
  msg.body = body.split("\n")
  msg.kludge = {}
  msg.via = []
  msg.path = []
  msg.seenby = []
  msg.orig=(fname, ftn.addr.str2addr(origaddr))
  if destdom=="node":
    msg.dest=(tname, ftn.addr.str2addr(destaddr))
  elif destdom=="echo":
    print("packing echomail msg to "+echodest)
    msg.dest=(tname, ftn.addr.str2addr(echodest))
  else:
    raise FTNFail("do not know how to pack message to "+destdom)
  msg.subj=subj
  msg.date=date
  msg.attr=0
  msg.cost=0
  msg.readcount=0
  msg.replyto=0
  msg.nextreply=0


  raise Exception("not implemented")
  return msg


