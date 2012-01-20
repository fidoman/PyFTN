"""
Message flow from database to links and users
"""

import xml.etree.ElementTree

from ftnconfig import suitable_charset, get_link_password
import ftn.msg
from ftn.ftn import FTNWrongPassword

def export_file(address, password, mailclass):
  """ mailclass is set of values netmail, echomail or any """
  raise Exception("not implemented")

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

    Q_get_subscription_messages = db.Q_get_subscription_messages = db.prepare(
        "select m.id, s.domain, s.text, m.msgid, m.header, m.body, m.receivedfrom "
        "from messages m, addresses s "
        "where m.id>$2 and m.destination=$1 and (m.processed is NULL or m.processed<>5)"
        "and m.source=s.id")

  for m in Q_get_subscription_messages(dest_id, lastsent):
    yield m[0], db.FTN_backdomains[m[1]], m[2], m[3], m[4], m[5], m[6]

  return


def update_subscription_watermark(db, subscription, id):
  db.prepare("update subscriptions set lastsent=$1 where id=$2")(id, subscription)



def denormalize_message(orig, dest, msgid, header, body, echodest=None, addvia=None, addseenby=None, addpath=None):
  (origdom, origaddr) = orig
  (destdom, destaddr) = dest

  charset = suitable_charset(None, "encode", origdom, origaddr, destdom, destaddr)
  #print(charset)

  if origdom!="node":
    raise FTNFail("message source must be node not %s"%origdom)

  msg=ftn.msg.MSG()

  fname=(header.find("sendername").text or '').encode(charset)
  tname=(header.find("recipientname").text or '').encode(charset)
  msg.subj=(header.find("subject").text or '').encode(charset)
  msg.date=(header.find("date").text or '').encode(charset)
  #print(fname, tname, subj, date)

  nltail=len(body)
  while(nltail>0 and body[nltail-1]=="\n"):
    nltail-=1
  msg.body = body[:nltail].encode(charset).split(b"\n")

  #print(xml.etree.ElementTree.tostring(header, encoding="utf-8").decode("utf-8"))
  ftnheader=header.find("FTN")
#  print(xml.etree.ElementTree.tostring(ftnheader).decode("utf-8"))


  msg.kludge = {} # overwrite CHRS kludge
  for kludge in ftnheader.findall("KLUDGE"):
    #print(kludge.get("name"), kludge.get("value"))
    msg.kludge[kludge.get("name").encode(charset)] = kludge.get("value").encode(charset)

  if charset=="ascii":
    if b"CHRS:" in msg.kludge:
      del msg.kludge[b"CHRS:"]
  else:
    msg.kludge[b"CHRS:"] = (charset.upper() + " 2").encode("ascii")

#  print(msg.kludge)

  msg.via = [] # netmail only
  for via in ftnheader.findall("VIA"):
    1/0
    #print(kludge.get("name"), kludge.get("value"))
    msg.kludge[kludge.get("name").encode(charset)] = kludge.get("value").encode(charset)
    

  msg.path = []
  msg.seenby = set() # echomail only

  if destdom=="echo":

    dest_zone=ftn.addr.str2addr(echodest)[0]
    my_zone=ftn.addr.str2addr(addpath)[0] # addpath should be this node's address

    if my_zone==dest_zone:
      for path in ftnheader.findall("PATH"):
        #print(path.get("record"))
        msg.add_path(path.get("record"))

      if addpath:
        #print("additional path", addpath)
        msg.add_path(addpath)

    else:
      pass # empty path
  
    if my_zone==dest_zone:

      for seenby in ftnheader.findall("SEEN-BY"):
        seenbyaddr = (seenby.get("zone"), seenby.get("net"), seenby.get("node"), seenby.get("point"))
        #print(seenbyaddr)
        msg.add_seenby(ftn.addr.addr2str(seenbyaddr))
    else:
      pass # drop old seen-by's
  
    for seenby in addseenby or []:
      #print("additional seenby", seenby)
      seenby_zone=ftn.addr.str2addr(seenby)[0]
      if seenby_zone==dest_zone:
        msg.add_seenby(seenby)


  msg.orig=(fname, ftn.addr.str2addr(origaddr))
  if destdom=="node":
    msg.dest=(tname, ftn.addr.str2addr(destaddr))
    msg.area=None
  elif destdom=="echo":
    #print("packing echomail msg to "+echodest)
    msg.dest=(tname, ftn.addr.str2addr(echodest))
    msg.area=destaddr.encode(charset)
  else:
    raise FTNFail("do not know how to pack message to "+destdom)


  msg.attr=0
  if destdom=="node":
    raise NotImplementedError("attr for netmail")

  msg.cost=0
  msg.readcount=0
  msg.replyto=0
  msg.nextreply=0

  #print(msg.__dict__)

  return msg


class file_export:
  def __init__(self, db, address, password, what):
    # first netmail
    # then requested file
    # then echoes
    # then filebox
    # and at last fileechoes
    self.db = db
    self.address = address
    if password != get_link_password(db, address):
      raise FTNWrongPassword()
    self.what = what

  def __enter__(self):
    return outbound_iterator(self.db, self.address, self.what)

  def __exit__(self, et, ev, tb):
    if et:
      print("cancel export")
      return False
    else:
      raise Excption("update last sent marks")
      return True

  
