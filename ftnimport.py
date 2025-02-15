"""
Import messages and files to local database
"""

import traceback
import sys
import xml.etree.ElementTree
import ftn.pkt
import ftn.attr
from ftn.ftn import FTNFail, FTNDupMSGID, FTNNoMSGID, FTNNoOrigin, FTNNotSubscribed, FTNAlreadySubscribed, FTNWrongPassword, FTNNoAddressInBase
from ftn.ftn import FTNExcessiveMessageSize
import re
import os
import time, datetime
from hashlib import sha1
from ftnconfig import suitable_charset, find_link, ADDRESS, get_addr_id, MSGSIZELIMIT, IMPORTLOCK
import ftnaccess
from stringutil import *
import ftnpoll
import postgresql.alock

def modname(n, m):
  return n if m==0 else "%s.%d"%(n, m)

class file_import:
  def __init__(self, db, address, password, filename, length):
    print("from",address,"pw",password,"recv",filename,"len",length)

    # based on length choose to process data in memory (check received data length)
    # or save to disk
    # packets
    # bundles
    # freqs
    # tics
    # files

    self.db = db
    self.address = address

    link_id, addr_id, myaddr_id = ftnaccess.check_link(db, address, password, False)
    if myaddr_id is None:
        raise FTNWrongPassword()
    self.protected = link_id is not None

    savedir = inbound_dir(address, self.protected, True)
    if not os.path.exists(savedir):
      os.makedirs(savedir)
    mod = 0
    while True:
      try:
        self.file = os.path.join(savedir, modname(filename, mod))
        self.fo = os.fdopen(os.open(self.file, os.O_CREAT | os.O_EXCL | os.O_WRONLY), "wb") # should add  | os.O_BINARY
        break
      except OSError as e:
        if e.args[0]!=17:
          raise e

      mod += 1

  def __enter__(self):
    return self

  def add_data(self, d):
    self.fo.write(d)

  def __exit__(self, et, ev, tb):
    self.fo.close()
    if et:
      print("cancel file")
      os.unlink(self.file)
      return False
    else:
      return True


# clean_str changed at id=897897



def normalize_message(msg, charset="ascii"):

    header = xml.etree.ElementTree.Element("header")
    ftnel = xml.etree.ElementTree.SubElement(header, "FTN")

    # begin addresses
    # get message originator and recipient addresses

    # - MSGID
    msgid = msg.kludge.get(b"MSGID:")
    if type(msgid) is list:
      raise FTNFail("Multiple MSGID")
    if msgid is not None:
      try:
        msgid = msgid.decode("ascii")
      except:
        raise FTNFail("MSGID is not ASCII string")
    # if no MSGID kludge, MSGID will be generated

    # - plain
    if msg.area:

      msg.area = msg.area.upper()

      # get originator address from Origin or MSGID
      origdom = "node"
      origname, _ = msg.orig[0], ftn.addr.addr2str(msg.orig[1])

      origaddr = None
      for b1 in msg.body:
        try:
          a=ftn.msg.decode_origin(b1).decode(charset)
          origaddr = ftn.addr.addr2str(ftn.addr.str2addr(a))
        except ftn.msg.DecodeError:
          pass

      if not origaddr or origaddr[0]=='0':

        print ("no origin, msgid:", repr(msgid))
        try:
          origaddr=ftn.addr.addr2str(ftn.addr.str2addr(msgid.split(" ")[0].split("@")[0]))
          print ("got from msgid:", origaddr)
        except:
          pass

        if not origaddr or origaddr[0]=='0':
          try:
            print("SYNC?")
            origaddr=ftn.addr.addr2str(ftn.addr.str2addr(msgid.split(" ")[0].split("@")[1]))
            print ("got from msgid (syncbbs):", origaddr)
          except:
            pass


      if not origaddr:
        raise FTNNoOrigin # No Origin, no MSGID with FTN address

      # destination is echo
      destdom = "echo"
      destaddr = msg.area.decode(charset) # ascii 
      destname, _ = msg.dest

    else:
      # netmail
      origdom = "node"
      origname, origaddr = msg.orig[0], ftn.addr.addr2str(msg.orig[1])

      destdom = "node"
      destname, destaddr = msg.dest[0], ftn.addr.addr2str(msg.dest[1])

    # - guess
    guessed=False
    mayusezone=None
    if origdom=="node" and origaddr[0]=='0':
      print("MSG with from = '%s': guess zone..."%origaddr)
      knownfrom=ftn.addr.str2addr(origaddr)
      if msgid:
        guessfrom=ftn.addr.str2addr(msgid.split(" ")[0].split("@")[0])
        if guessfrom[1]==knownfrom[1] and guessfrom[2]==knownfrom[2]:
          print (origaddr,"->",ftn.addr.addr2str(guessfrom))
          origaddr=ftn.addr.addr2str(guessfrom)
          guessed=True
          mayusezone=guessfrom[0]
      else:
        guessfrom = None

      if not guessed:
        print ("AREA:", repr(msg.area))
        raise FTNFail("Zone in sender address is empty and cannot guess from MSGID %s\n"
          		"guess: %s known: %s"%(repr(msg.kludge.get(b"MSGID:")), guessfrom, knownfrom))
    
    guessed=False
    replyzone=None
    if destdom=="node" and destaddr[0]=='0':
      print ("MSG with to = '%s': guess zone..."%destaddr)
      if b"REPLY:" in msg.kludge:
       try:
        guessto=ftn.addr.str2addr(msg.kludge[b"REPLY:"].decode(charset).split(" ")[0].split("@")[0])
        replyzone=guessto[0]
        knownto=ftn.addr.str2addr(destaddr)
        if guessto[1]==knownto[1] and guessto[2]==knownto[2]:
          print("use REPLYTO",destaddr,"->",ftn.addr.addr2str(guessto))
          destaddr=ftn.addr.addr2str(guessto)
          guessed=True
       except FTNFail:
         pass # could not parse replyto id
 
      if not guessed and mayusezone and ((replyzone is None) or replyzone==mayusezone):
        guessto=list(ftn.addr.str2addr(destaddr))
        guessto[0]=mayusezone
        destaddr=ftn.addr.addr2str(guessto)
        print("take destination zone from source")
        guessed=True

#      if not guessed: # caution
#        guessto=list(ftn.addr.str2addr(destaddr))
#        if guessto[1]==5020:
#          guessto[0]=2
#        destaddr=ftn.addr.addr2str(guessto)
#        guessed=True

      if not guessed:
        raise FTNFail("Zone in recepient address is empty and cannot guess from REPLY")

    # end addresses


    charset = suitable_charset(msg.kludge.get(b"CHRS:"), msg.kludge.get(b"CHARSET:"), "decode", origdom, origaddr, destdom, destaddr) or charset
    #print("charset:", charset)


    if msg.seenby:
      for seenby1 in msg.seenby:
        seenbyel=xml.etree.ElementTree.SubElement(ftnel, "SEEN-BY")
        if seenby1[0]:
          seenbyel.set("zone", str(seenby1[0]))
        seenbyel.set("net", str(seenby1[1]))
        seenbyel.set("node", str(seenby1[2]))
        if seenby1[3]:
          seenbyel.set("point", str(seenby1[3]))
  
    if msg.via:
      for via1 in msg.via:
        viael = xml.etree.ElementTree.SubElement(ftnel, "VIA")
        viael.set(via1[0].decode(charset), via1[1].decode(charset))
  
    for attr1 in ftn.attr.binary_to_text(msg.attr):
      xml.etree.ElementTree.SubElement(ftnel, "ATTR", id = attr1)
  
    for kname, kval in msg.kludge.items():
      if type(kval)!=list:
        kval=[kval]
      for v1 in kval:
        xml.etree.ElementTree.SubElement(ftnel, "KLUDGE", 
          name = clean_str(kname.decode(charset)), 
          value = clean_str(v1.decode(charset)))
            # TZUTC sometimes filled with zeroes...
            # and special chars sometimes encountered

    for path1 in msg.path:
      #print(path1)
      pathel=xml.etree.ElementTree.SubElement(ftnel, "PATH", record = clean_str(path1))

    for zpth1 in msg.zpth:
      #print(zpth1)
      zpthel=xml.etree.ElementTree.SubElement(ftnel, "ZPTH", record = clean_str(zpth1))
  


    sendernameel = xml.etree.ElementTree.SubElement(header, "sendername")
    sendernameel.text = clean_str(origname.decode(charset))

    recipientnameel = xml.etree.ElementTree.SubElement(header, "recipientname")
    recipientnameel.text = clean_str(destname.decode(charset))

    dateel = xml.etree.ElementTree.SubElement(header, "date")
    dateel.text = clean_str(msg.date.decode(charset))

    subjel=xml.etree.ElementTree.SubElement(header, "subject")
    subjel.text = clean_str(msg.subj.decode(charset))
    
    # may be autodetect is needed
    body = (b"\n".join(msg.body)+b"\n").decode(charset)

    if msgid is None:
      # make hash of originator+date+subject+body - date to allow repeating posts
      hashdata = "\n".join((origname.decode(charset), origaddr, destname.decode(charset), destaddr,
            msg.date.decode(charset), msg.subj.decode(charset), body))
      msgid = origaddr + " " + sha1(hashdata.encode(charset)).hexdigest()
      print("generated MSGID", repr(msgid))

    #xml.etree.ElementTree.dump(header)

    return (origdom, origaddr), (destdom, destaddr), msgid, header, body, charset

import re

RE_ftnsign = re.compile("(\r|\n|\r\n|\n\r)(---| \* Origin)", re.I)
def sign_invalidate(s):
    n=s.group(1)+s.group(2)[0]+"+"+s.group(2)[2:]
    #print("!!!",s.group(0),"->", n)
    return n


def compose_message(db, sender, sendername, recipient, recipientname, replyto, subject, body, flags):

    header = xml.etree.ElementTree.Element("header")
    ftnel = xml.etree.ElementTree.SubElement(header, "FTN")

    sendernameel = xml.etree.ElementTree.SubElement(header, "sendername")
    sendernameel.text = sendername

    recipientnameel = xml.etree.ElementTree.SubElement(header, "recipientname")
    recipientnameel.text = recipientname

    dateel = xml.etree.ElementTree.SubElement(header, "date")
    dateel.text = time.strftime("%d %b %y  %H:%M:%S")

    tzoffs = -time.timezone//60
    tzhours = tzoffs//60
    tzmins = tzoffs%60
    xml.etree.ElementTree.SubElement(ftnel, "KLUDGE", name = "TZUTC:", value = "%02d%02d"%(tzhours, tzmins))

    subjel=xml.etree.ElementTree.SubElement(header, "subject")
    subjel.text = subject

    if replyto:
      xml.etree.ElementTree.SubElement(ftnel, "KLUDGE", name = "REPLY:", value = replyto)

    msgid = "%s %08x"%(sender[1], db.prepare("SELECT nextval('msgid_seq')").first())
    print("generated MSGID", repr(msgid))

    xml.etree.ElementTree.SubElement(ftnel, "KLUDGE", name = "MSGID:", value = msgid)


    for attr1 in flags:
      xml.etree.ElementTree.SubElement(ftnel, "ATTR", id = attr1)

    body = RE_ftnsign.sub(sign_invalidate, body) + "\n--- PyFTN\n" + \
        ((" * Origin: fluid.fidoman.ru ("+sender[1]+")\n") if recipient[0]=="echo" else "")

    return sender, recipient, msgid, header, body



# ---------------------------------------------

class session:
  def __init__(self, db):
    self.db=db
    self.Q_msginsert = None
    self.Q_getlinkid = None
    self.address_cache = {}
    self.domains = {}
    self.last_message_for_address = {}
    self.Q_update_addr_msg = None
    self.Q_get_max_numfordest = None
    for domain_id, domain_name in db.prepare("SELECT id, name FROM domains;"):
      #print(domain_id, domain_name)
      if domain_name=="fidonet node": 
        self.FIDOADDR=domain_id
        self.domains["node"]=domain_id
      elif domain_name=="fidonet echo": 
        self.FIDOECHO=domain_id
        self.domains["echo"]=domain_id
      elif domain_name=="fidonet fileecho": 
        self.FIDOFECHO=domain_id
        self.domains["fileecho"]=domain_id
#    self.Q_find_addr=db.prepare("select id from addresses where domain=$1 and text=$2")

#  def find_addr(self, dom, addr):
#      if (dom, addr) in self.address_cache:
#        return self.address_cache[(dom, addr)]
#
#      res=self.Q_find_addr(dom, addr)
#      if len(res)==1:
#        self.address_cache[(dom, addr)]=res[0][0]
#        return res[0][0]
#      if len(res)>1:
#        raise Exception("multiple address records found (%d)"%len(res))
#      raise FTNNoAddressInBase(dom, addr)

  def add_addr(self, dom, addr):
      timestamp = datetime.datetime.now(datetime.timezone.utc)
      self.db.prepare("insert into addresses (domain, text, created) values($1, $2, $3)")(dom, addr, timestamp)

  def forget_address(self, dom, addr):
      self.db.prepare("delete from addresses where domain=$1 and text=$2")(self.db.FTN_domains[dom], addr)

  def check_addr(self, domain, addr):
      dom = self.db.FTN_domains[domain]
      try:
        return get_addr_id(self.db, dom, addr)
      except FTNNoAddressInBase:
        self.add_addr(dom, addr)
      return get_addr_id(self.db, dom, addr)

  def get_linkid(self, dom, addr):
      if not self.Q_getlinkid:
        self.Q_getlinkid = self.db.prepare("select links.id from links, addresses where links.address=addresses.id and addresses.domain=$1 and addresses.text=$2")
      r = self.Q_getlinkid(dom, addr)
      if len(r)==0:
        raise FTNFail("No link with %d %s"%(dom,addr))
      if len(r)>1:
        raise FTNFail("Duplicate link in base for %d %s"%(dom,addr))
      return r[0][0]


  def __enter__(self):
    self.x=self.db.xact()
    self.x.start()
    print ("START")
    self.poller = ftnpoll.poller(self.db)
    return self

  def __exit__(self, et, ev, tb):
    if et:
      print ("ROLLBACK")
      self.x.rollback()
      return False
    else:
      print ("COMMIT")
      self.x.commit()
      self.poller.do()
      return True


  def save_watermark(self, target, lastsent):
        createwatermark = True
        updatewatermark = False
        # get removed subscription watermark and update or create it
        for check_id, check_msg in self.db.prepare(
            "select id, message from deletedvitalsubscriptionwatermarks where target=$1")(target):
          createwatermark = False
          if check_msg>lastsent:
            updatewatermark = True
        if createwatermark:
          print ("create watermark as %d"%lastsent)
          self.db.prepare("insert into deletedvitalsubscriptionwatermarks (target, message) values ($1, $2)")(target, lastsent)
        if updatewatermark:
          print ("update watermark %d as %d"%(check_id, lastsent))
          self.db.prepare("update deletedvitalsubscriptionwatermarks set message=$1 where id=$2")(check_id, lastsent)

  def remove_watermark(self, target):
    print("#remove_watermark target=%d"%target)
    self.db.prepare("delete from deletedvitalsubscriptionwatermarks where target=$1")(target)

  def get_watermark(self, target):
    """ get from saved or if there are nothing there get from current vital subscriptions and as last resort the oldest message """
    for check_id, check_msg in self.db.prepare(
            "select id, message from deletedvitalsubscriptionwatermarks where id = (select min(id) from deletedvitalsubscriptionwatermarks where target=$1)"
            )(target):
      print ("#get_watermark: saved watermark", check_msg)
      return check_msg # any exists

    oldest_vital = self.db.prepare("select min(lastsent) from subscriptions where target=$1 and vital=true").first(target)
    if oldest_vital is not None:
      print ("#get_watermark: oldest sent vital", oldest_vital)
      return oldest_vital

    # no vital subscriptions
    oldest_msg = self.db.prepare("select min(id) from messages where destination=$1").first(target)
    if oldest_msg is not None:
      print ("#get_watermark: oldest message to", target, oldest_msg)
      return oldest_msg

    # no messages to this destination, start subscriptions at current
    print ("#get_watermark: return max from all messages")
    return self.db.prepare("select max(id) from messages").first()


  def add_subscription(self, vital, target_domain, target_addr, subscriber_addr, start=None):
    """ vital: True, False - set new value; None - leave old or add False """
    target=get_addr_id(self.db, self.db.FTN_domains[target_domain], target_addr)
    subscriber=self.check_addr("node", subscriber_addr)
    if start is None:
      start=self.db.prepare("select max(id) from messages").first()

    check = self.db.prepare("select id, vital, lastsent from subscriptions where target=$1 and subscriber=$2")(target, subscriber)

    if len(check):
      print ("#add_subscription: subscription exists")
      oldid, oldvital, lastsent = check[0]

      if vital is None or vital==oldvital:
        print ("#add_subscription: nothing changed")
        return "already subscribed"

      if vital:
        print ("#add_subscription: convert to vital")
        self.db.prepare("update subscriptions set vital=true where id=$1")(oldid)
        self.remove_watermark(target)
        return "converted to vital"
      else:
        print ("#add_subscription: convert to non-vital")
        self.save_watermark(target, lastsent)
        self.db.prepare("update subscriptions set vital=false where id=$1")(oldid)
        return "converted to non-vital"

    else:
      print ("#add_subscription: new subscription")
      if vital:
        start = self.get_watermark(target)
        self.remove_watermark(target)

      op=self.db.prepare("insert into subscriptions (vital, target, subscriber, lastsent) values ($1, $2, $3, $4)")(vital or False, target, subscriber, start)
      return "subscribed from %d"%start


  def remove_subscription(self, target_domain, target_addr, subscriber_addr):
    target=get_addr_id(self.db, self.db.FTN_domains[target_domain], target_addr)
    subscriber=get_addr_id(self.db, self.db.FTN_domains["node"], subscriber_addr)

    check = self.db.prepare("select vital, lastsent from subscriptions where target=$1 and subscriber=$2")(target, subscriber)
    if len(check):
      if check[0][0]:
        print ("removing vital subscription")
        lastsent = check[0][1]
        self.save_watermark(target, lastsent)

    else:
      return "not subscribed"

    op=self.db.prepare("delete from subscriptions where target=$1 and subscriber=$2")
    op(target, subscriber)
    return "unsubscribed"

  def reset_subscription(self, target_domain, target_addr, subscriber_addr, timestamp):
    target=get_addr_id(self.db, self.db.FTN_domains[target_domain], target_addr)
    subscriber=get_addr_id(self.db, self.db.FTN_domains["node"], subscriber_addr)
    reset_id=self.db.prepare("select min(id) from messages where destination=$1 and receivedtimestamp>=$2::text::timestamptz").first(target, timestamp)
    if reset_id is None:
      return "no messages after specified date"
    try:
      self.db.prepare("update subscriptions set lastsent=$3 where subscriber=$1 and target=$2")(subscriber, target, reset_id)
      return "reset to %d"%reset_id
    except:
      print ("Exception in reset_subscription")
      traceback.print_exc()
      return "failed"


  def import_link_conn(self, node, conninfo):
    """ match database records with given table """

    ps=self.db.prepare("select links.id, links.connection from links, addresses where links.address=addresses.id "
            "and addresses.domain=$1::bigint and addresses.text=$2::varchar for update of links")

    links=ps(FIDOADDR, node)
    if len(links)==0:
      raise Exception("cannot set connection info for non-existent link")
    if len(links)>1:
      raise Exception("multiple links with same address %s"%node)

    link_id, link_connection = links[0]
    if link_connection is None:
      connel = xml.etree.cElementTree.Element("FTNConnection")
    else:
      connel= link_connection

    #print ((link_id), connel.tag, connel.attrib, connel.text, connel.tail)
    #print (connel.find("DoPoll"), conninfo)

    #print(conninfo)
    if conninfo[0]=="binkp":
      n=xml.etree.ElementTree.SubElement(connel, "Binkp", Address=conninfo[1], Time=conninfo[2])
    elif conninfo[0]=="ifcico":
      n=xml.etree.ElementTree.SubElement(connel, "Ifcico", Address=conninfo[1], Time=conninfo[2])
    else:
      raise Exception("unknown protocol %s"%(conninfo[0]))

    self.db.prepare("update links set connection=$2 where id=$1")(link_id, connel)
    #xml.etree.ElementTree.dump(connel)


  def import_link_polling(self, node_polls):
    """ match database records with given table """

    c=self.db.prepare("select links.id, links.connection, addresses.text from links, addresses where links.address=addresses.id for update of links")()
    u=self.db.prepare("update links set (connection) = ($1) where id=$2")
    for row_id, row_connection, row_address in c:
      print (row_id, row_connection, row_address)
      if row_connection is None:
        if row_address in node_polls:
          print ("add poll for node %s (new connection)", row_address)
          connel = xml.etree.ElementTree.Element("FTNConnection")
          xml.etree.ElementTree.SubElement(connel, "DoPoll")
          u(connel, row_id)
        else:
          print ("no conn info and no autopoll - skipping")
      else:
        connel=row_connection
        pollels=connel.findall("DoPoll")
        xdopoll=len(pollels)>0
        if xdopoll and not (row_address in node_polls):
          print ("disable polls")
          for pollel in pollels:
            connel.remove(pollel)
          u(connel, row_id)

        elif (row_address in node_polls) and not xdopoll:
          print ("enable polls")
          xml.etree.ElementTree.SubElement(connel, "DoPoll")
          u(connel, row_id)
  
        else:
          print ("OK")


  def send_message(self, sender, sendername, recipient, recipientname, replyto, subj, body, flags = [], sendmode=None):
    orig, dest, msgid, header, body = compose_message(self.db, sender, sendername, recipient, recipientname, replyto, subj, body, flags)
    #print ("msg from:", orig)
    #print ("msg to  :", dest)
    #print ("msgid   :", msgid)
    #print ("header  :")
    #xml.etree.ElementTree.dump(header)
    #print ("body    :", body)
    if sendmode is not None and sendmode.count("direct"):
      processed=8
    else:
      processed=0
    return self.save_message(orig, dest, msgid, header, body, None, ADDRESS, processed=processed)

  def import_message(self, msg, recvfrom, bulk):
    orig, dest, msgid, header, body, origcharset = normalize_message(msg)
    return self.save_message(orig, dest, msgid, header, body, origcharset, recvfrom, processed=5 if bulk else 0, bulkload=bulk)

  def save_message(self, sender, recipient, msgid, header, body, origcharset, recvfrom,  processed=0, bulkload=False):
    """import msg as part of transaction.
       if msg is correct then it is stored in base.
       if msg fails validation then it will be saved in bad messages' directory """

    if (len(body)+len(repr(header))) > MSGSIZELIMIT:
      raise FTNExcessiveMessageSize(len(body)+len(repr(header)), MSGSIZELIMIT)

    origdomname, origaddr = sender
    destdomname, destaddr = recipient

    #origdom=self.domains[origdomname]
    destdom=self.domains[destdomname]

    #print "-"*79
    #sys.stdout.write(body.encode("utf-8"))
    #print "="*79

    #  raise Exception("Verify senderaddress and destination address are listed. (area autocreate, destination is listed, ...)")

    origid = self.check_addr(origdomname, origaddr) # allow autocreate for source
    # no autocreate. only on request and if exists in uplink lists

    # database must have trigger to check address to be created for nodelist and area for echolist and uplinks

    if recvfrom:
      recvfrom_id = get_addr_id(self.db, self.FIDOADDR, recvfrom)
    else:
      recvfrom_id = None

    if not bulkload:

      # check domain's "verifysubscription" and if true refuse if not subscribed
      r=self.db.prepare("select verifysubscriptions from domains where id=$1")(destdom)
      if len(r) == 0:
        raise Exception("invalid domain after checkaddress ??? %d"%destdom)
      verify_subscription = r[0][0]

      if verify_subscription: # move to ftnaccess
        # check if message received from subscribed to the destination's address
        maypost, do_create = ftnaccess.may_post(self.db, recvfrom_id, (destdomname, destaddr))
        if maypost:
          print("posting allowed for %d (%d/%s) to %d/%s"%(recvfrom_id, self.FIDOADDR, recvfrom, destdom, destaddr))
          destid = self.check_addr(destdomname, destaddr) # check node in nodelist and area exists
          if do_create:
            print ("subscribe %s to %s %s as uplink"%(recvfrom, destdomname, destaddr))
            self.add_subscription(True, destdomname, destaddr, recvfrom)
        else:
          raise FTNNotSubscribed("%d/%s (id=%d)"%(self.FIDOADDR, recvfrom, recvfrom_id), "%d/%s"%(destdom, destaddr))
      else:
            # flaw: allow to flood with messages to non-existent addresses. should be checked with trigger in database
        #  (allow create node/point only if nodelisted, area only if listed on bone/uplinks)
        destid = self.check_addr(destdomname, destaddr) # check node in nodelist and area exists

    if len(self.db.prepare("select id from messages where msgid=$1 and destination=$2")(msgid, destid)):
      raise FTNDupMSGID(msgid)

    if not self.Q_msginsert:
      self.Q_msginsert = self.db.prepare("insert into messages (source, destination, msgid, header, body, "
            "origcharset, processed, receivedfrom, receivedtimestamp, numberfordestination) "
            "values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) returning id")

    if not self.Q_update_addr_msg:
      self.Q_update_addr_msg = self.db.prepare("update addresses set last=$2 where id=$1")

    if not self.Q_get_max_numfordest:
      self.Q_get_max_numfordest = self.db.prepare("select last from addresses where id=$1")

    with postgresql.alock.ExclusiveLock(self.db, IMPORTLOCK): # lock per all table messages
      # begin insert-lock
      # guarantees that for greater id greater timestamp
      timestamp = datetime.datetime.now(datetime.timezone.utc)
      print ("Transaction state", self.x.state, str(timestamp))
      if destdomname=="echo":
        numfordest = (self.Q_get_max_numfordest.first(destid) or 0) + 1
      else:
        numfordest = None
      new_msg=self.Q_msginsert(origid, destid, msgid, header, body, origcharset, processed, recvfrom_id, timestamp, numfordest)[0][0]
      print ("insert msg #", new_msg, "to address", destid, "number", numfordest)
      self.Q_update_addr_msg(destid, new_msg)
      # end insert-lock

    self.last_message_for_address[destid] = new_msg
    self.poller.add_one(destid)

  def touched_addresses(self):
    return self.last_message_for_address.keys()

  def import_link_auth(self, myaddr, node, connectpassword, robotpassword, echolevel=None, fecholevel=None, echogroups=None, fechogroups=None):
    addr_id = self.check_addr("node", node)
    my_id = self.check_addr("node", myaddr)

    authel = xml.etree.ElementTree.Element("FTNAuth")
    connectpwel = xml.etree.ElementTree.SubElement(authel, "ConnectPassword")
    connectpwel.text = connectpassword

    for name, val in [("RobotsPassword", [robotpassword]),("EchoLevel", [echolevel]), 
          	    ("FileEchoLevel", [fecholevel]), 
          	    ("EchoGroup",list(echogroups or "")), ("FileEchoGroup",list(fechogroups or ""))]:
      for v1 in val:
        if v1:
          itemel = xml.etree.ElementTree.SubElement(authel, name)
          itemel.text = v1

    exists = int(self.db.prepare("select count(*) from links where address=$1").first(addr_id))>0

    if not exists:
      self.db.prepare("insert into links (my, address, authentication) values ($1, $2, $3)")(my_id, addr_id, authel)
    else:
      self.db.prepare("update links set (authentication) = ($2) where address=$1")(addr_id, authel)

if __name__=="__main__":
  pass
