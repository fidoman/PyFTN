"""
Message flow from database to links and users
"""

import xml.etree.ElementTree

from ftnconfig import suitable_charset, get_link_password, ADDRESS
import ftn.msg
import ftn.attr
from ftn.ftn import FTNFail, FTNWrongPassword



def get_node_subscriptions(db, addr, msgdom):
  """ addr - address of subscriber node
      msgdom - destination domain of messages (no combining supported)
  """
  domains = db.FTN_domains
  try:
    Q_get_node_subscriptions = db.Q_get_node_subscriptions
  except AttributeError as e:
    # target: any with domain msgdom
    # subscriber: addr
    Q_get_node_subscriptions = db.Q_get_node_subscriptions = db.prepare("select s.id, t.id, s.lastsent from subscriptions s, addresses sr, addresses t "
        "where s.target=t.id and t.domain=$1 and s.subscriber=sr.id and sr.domain=$2 and sr.text=$3")

  return Q_get_node_subscriptions.rows(domains[msgdom], domains["node"], addr)




def get_subscriber_messages_n(db, subscriber, domain):
  """ get all subscribed addresses in specified domain and 
      fetch all messages with id>lastsent or if lastsent is None - with processed==0 """


#  if lastsent:

  query = db.prepare("""

    with recursive allsubscription(id, target, dir) as 
    (
        select id, target, 1 from subscriptions where subscriber=$1
      Union
        select s.id, a.id, 0 from allsubscription s, addresses a 
        where a.group = s.target
              and (select count(id) from subscriptions where target=a.id) = 0
    )

    select m.id, m.source, m.destination, m.msgid, m.header, m.body, m.receivedfrom
    from allsubscription alls, addresses sa, messages m
    where sa.id=alls.target and sa.domain=$2 and 
          m.processed=0 and m.destination=alls.target
    order by m.id
    ;

  """)

  for m in query(subscriber, domain):
    yield m


def get_subscriber_messages_e(db, subscriber, domain):
  """ get all subscribed addresses in specified domain and 
      fetch all messages with id>lastsent or if lastsent is None - with processed==0 """

  query = db.prepare("""

    with recursive allsubscription(id, lastsent, target, dir) as 
    (
        select id, lastsent, target, 1 from subscriptions where subscriber=$1
      Union
        select s.id, s.lastsent, a.id, 0 from allsubscription s, addresses a 
        where a.group = s.target
              and (select count(id) from subscriptions where target=a.id) = 0
    )

    select m.id, m.source, m.destination, m.msgid, m.header, m.body, m.receivedfrom, alls.id
    from allsubscription alls, addresses sa, messages m
    where sa.id=alls.target and sa.domain=$2 and 
          m.id>alls.lastsent and m.destination=alls.target
          m.receivedfrom<>$1
    order by m.id
    ;

  """)

  for m in query(subscriber, domain):
    yield m




def get_messages(db, dest_id, lastsent):
  """ use lastsent >= -1 for fetching echomail
      or lastsent = None for netmail """

  try:
    Q_get_subscription_messages_e = db.Q_get_subscription_messages_e
    Q_get_subscription_messages_n = db.Q_get_subscription_messages_n

  except AttributeError:

    Q_get_subscription_messages_e = db.Q_get_subscription_messages_e = db.prepare(
        "select m.id, s.domain, s.text, m.msgid, m.header, m.body, m.receivedfrom "
        "from messages m, addresses s "
        "where m.id>$2 and m.destination=$1"
        "and m.source=s.id")

    Q_get_subscription_messages_n = db.Q_get_subscription_messages_n = db.prepare(
        "select m.id, s.domain, s.text, m.msgid, m.header, m.body, m.receivedfrom "
        "from messages m, addresses s "
        "where m.destination=$1 and m.processed=0"
        "and m.source=s.id")


  if lastsent is not None:
    # echomail-style 

    for m in Q_get_subscription_messages_e(dest_id, lastsent):
      yield m[0], db.FTN_backdomains[m[1]], m[2], m[3], m[4], m[5], m[6]

  else:
    # netmail-style

    for m in Q_get_subscription_messages_n(dest_id):
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
    for viak, viav in via.attrib.items():
      msg.via.append((viak.encode(charset), viav.encode(charset)))
  for via in addvia:
    msg.via.append(("Via", via))

#  print(msg.via)

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
    attrs=[]
    for attr in ftnheader.findall("ATTR"):
      attrs.append(attr.get("id"))
    msg.attr = ftn.attr.text_to_binary(attrs)

  msg.cost=0
  msg.readcount=0
  msg.replyto=0
  msg.nextreply=0

  #print(msg.__dict__)

  return msg


class exported_file:
  def __init__(self):
    self

def commit_list(db, idlist):
  while len(idlist):
    db.prepare("update messages set processed=2 where id=$1")(idlist[0])
    del idlist[0]

def commit_lasts(db, lasts):
  for k, v in lasts.items():
    db.prepare("update subscriptions set lastsent=$1 where id=$2")(v, k)
    del lasts[k]

def file_export(db, address, password, what):
  """ This generator fetches messages from database and
      yields objects, that contain the file information
      and instructions how to commit to db inforamtion
      about successful message delivery """

    # first netmail
    # then requested file
    # then echoes
    # then filebox
    # and at last fileechoes
  if password != get_link_password(db, address):
      raise FTNWrongPassword()

  addr_id = db.prepare("select id from addresses where domain=$1 and text=$2").first(db.FTN_domains["node"], address)

  if "netmail" in what:
    p = packer(ADDRESS, address, False)
    p.msgids = []

    #..firstly send pkts in outbound
    for id_msg, src, dest, msgid, header, body, recvfrom in get_subscriber_messages_n(db, addr_id, db.FTN_domains["node"]):

      myvia = "PyFTN " + ADDRESS + " " + time.asctime()
      srca=db.prepare("select domain, text from addresses where id=$1").first(src)
      dsta=db.prepare("select domain, text from addresses where id=$1").first(dest)

      try:
        msg = denormalize_message(
            (db.FTN_backdomains[srca[0]], srca[1]),
            (db.FTN_backdomains[dsta[0]], dsta[1]), 
            msgid, header, body, address, addvia = [myvia])
      except:
        raise Exception("denormalization error on message id=%d"%m[0]+"\n"+traceback.format_exc())

      p.msgids.append(id_msg)
      if p.add_message(msg):
        p.file.commit = lambda: commit_list(db, p.msgids)
        yield p.file
        

    if p.flush():
      p.file.commit = lambda: commit_list(db, p.msgids)
      yield p.file
    del p

  if "echomail" in what:

    #..firstly send bundles in outbound


    p = packer(ADDRESS, address, True)
    p.lasts = {}
    subscache = {}
    for id_msg, src, dest, msgid, header, body, recvfrom, withsubscr in get_subscriber_messages_e(db, addr_id, db.FTN_domains["echo"]):
      print(id_msg)

      # check commuter
      subscriber_comm = db.FTN_commuter.get(withsubscr)
      if subscriber_comm is not None:
        # get subscription through what message was received
        recvfrom_subscription = db.prepare("select id from subscriptions where target=$1 and subscriber=$2").first(sub_tart, m_recvfrom)
        recvfrom_comm = db.FTN_commuter.get(recvfrom_subscription)
        if recvfrom_comm == subscriber_comm:
          continue # do not forward between subscriptions in one commuter group (e.g. two uplinks)

      if dest in subscache:
        subscribers = subscache[dest]
      else:
        subscribers = db.prepare("select a.domain, a.text from subscriptions s, addresses a where s.target=$1 and s.subscriber=a.id")(dest)

        if not all([x[0]==db.FTN_domains["node"] for x in subscribers]):
          raise FTNFail("subscribers from wrong domain for "+str(sub_targ))

        #    print(sub_id, sub_targ, "all subscribers:", [x[1] for x in subscribers])

        subscribers = subscriber_cache[dest] = [x[1] for x in subscribers]


      # modify path and seen-by
      # seen-by's - get list of all subscribers of this target; add subscribers list
      #... if go to another zone remove path and seen-by's and only add seen-by's of that zone -> ftnexport
      try:
        msg = denormalize_message(
            (db.FTN_backdomains[srca[0]], srca[1]),
            (db.FTN_backdomains[dsta[0]], dsta[1]), 
            m_msgid, m_header, m_body, address, addseenby=subscribers, addpath=ADDRESS)
      except:
        raise Exception("denormalization error on message id=%d"%m[0]+"\n"+traceback.format_exc())

      p.lasts.setdefault(withsubscr, id_msg)
      if p.add_message(msg):
        p.file.commit = lambda: commit_lasts(db, p.lasts)
        yield p.file
     
    if p.flush():
      p.file.commit = lambda: commit_lasts(db, p.lasts)
      yield p.file

  if "filebox" in what:
    # ..send freq filebox
    pass #1/0

  if "fileecho" in what:
    # ..send fileechoes
    pass #1/0

  if "filebox" in what:
    # ..send main filebox
    pass #1/0

  return


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
      return self.flush()

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
      if self.flush_packet():
        return True
    if self.bundle:
      if self.flush_bundle():
        return True
    return False

# no auto flush - only when correctly updating lastsent
#  def __del__(self):
#    self.flush()
