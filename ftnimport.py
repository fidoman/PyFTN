"""
Import messages and files to local database
"""

import traceback
import sys
import xml.etree.ElementTree
import ftn.pkt
import ftn.attr
from ftn.ftn import FTNFail, FTNDupMSGID, FTNNoMSGID, FTNNoOrigin, FTNNotSubscribed
import re
from hashlib import sha1

import postgresql
db=postgresql.open("pq://fido:xxxyzt@192.168.0.3/fido")

def clean_str(s):
  return re.sub("[\0-\31]", lambda x: "\\x%02X"%ord(x.group(0)), s.replace("\0", "").replace("\\","\\\\"))

# changed at id=897897

class NoAddressInBaseException(FTNFail):
  def __init__(self, dom, addr):
    FTNFail.__init__(self, "no address %d %s"%(dom,addr))

RE_russian=re.compile(b"RU\.|SU\.|MO\.|R50\.|N50|HUMOR\.|TABEPHA$|XSU\.|ESTAR\.|FLUID\.|SURVIVAL\.GUIDE$|STARPER\.|VGA\.PLANETS|OBEC\.|SPB\.|"
            b"CTPAHHOE\.MECTO|PVT\.|1072\.|ADINF\.|ZX\.SPECTRUM|\$CRACK\$|BOCHAROFF\.|ZONE7|MISTRESS\.|FAR\.SUPPORT|FIDONET\.HISTORY|MINDO\.|"
            b"TYT\.BCE\.HACPEM|PUSHKIN\.|715\.|XPEHOBO\.MHE|CKA3KA\.CTPAHHOE\.MECTO|UZ\.|FREUD|GUITAR\.SONGS|RUSSIAN\.|LOTSMAN\.|AVP\.|1200\.|"
            b"MU\.|REAL\.SIBERIAN\.VALENOK|KAZAN\.|BRAKE\'S\.MAILER\.SUPPORT|\$HACKING\$|GERMAN\.RUS|GSS\.PARTOSS|NODEX\.|380\.|SMR\.|"
            b"TESTING$|ESPERANTO\.RUS|RUS\.|BEL\.|MOLDOVA\.|UKR\.|UA\.|RUS_|RUSSIAN_|KAK\.CAM-TO|DEMO.DESIGN|FTNED\.RUS|REAL\.SPECCY|"
            b"TAM\.HAC\.HET|T-MAIL|1641\.|DN\.|TVER\.|ASCII_ART|GER\.RUS|KHARKOV\.|XCLUDE\.|CB\.RADIO")

RE_latin=re.compile(b"IC$|ENET\.|FN_|FTSC_|PASCAL|BLUEWAVE")

RE_ukrainian=re.compile(b"ZZUKR\.|ZZUA\.")

class session:
  def __init__(self, db):
    self.db=db
    self.Q_msginsert = None
    self.Q_getlinkid = None
    self.address_cache = {}
    for domain_id, domain_name in db.prepare("SELECT id, name FROM domains;"):
      #print(domain_id, domain_name)
      if domain_name=="fidonet node": self.FIDOADDR=domain_id
      elif domain_name=="fidonet fileecho": self.FIDOFECHO=domain_id
      elif domain_name=="fidonet echo": self.FIDOECHO=domain_id
    self.Q_find_addr=db.prepare("select id from addresses where domain=$1 and text=$2")

  def find_addr(self, dom, addr):
      if (dom, addr) in self.address_cache:
        return self.address_cache[(dom, addr)]

      res=self.Q_find_addr(dom, addr)
      if len(res)==1:
        self.address_cache[(dom, addr)]=res[0][0]
        return res[0][0]
      if len(res)>1:
        raise Exception("multiple address records found (%d)"%len(res))
      raise NoAddressInBaseException(dom, addr)

  def add_addr(self, dom, addr):
      self.db.prepare("insert into addresses (domain, text) values($1, $2)")(dom, addr)

  def check_addr(self, dom, addr):
      try:
        return self.find_addr(dom, addr)
      except NoAddressInBaseException:
        self.add_addr(dom, addr)
      return self.find_addr(dom, addr)

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
    self.x=db.xact()
    self.x.start()
    return self

  def __exit__(self, et, ev, tb):
    if et:
      print("ROLLBACK")
      self.x.rollback()
      return False
    else:
      print("COMMIT")
      self.x.commit()
      return True

  def add_subscription(self, vital, target_domain, target_addr, subscriber_addr):
    target=check_addr(target_domain, target_addr)
    subscriber=check_addr(FIDOADDR, subscriber_addr)
    op=self.db.prepare("insert into subscriptions (vital, target, subscriber, lastsent) values ($1, $2, $3, NULL)")
    op(vital, target, subscriber)


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

  def import_message(self, msg, recvfrom, charset="ascii", processed=None, bulkload=False):
    """import msg as part of transaction.
       if msg is correct then it is stored in base.
       if msg fails validation then it will be saved in bad messages' directory """

    header = xml.etree.ElementTree.Element("header")
    ftnel = xml.etree.ElementTree.SubElement(header, "FTN")

    if b"CHRS:" in msg.kludge and msg.kludge[b"CHRS:"]==b"CP866 2": # can trust
      charset="cp866"

#      charset=msg.kludge[b"CHRS:"].rsplit(b" ", 1)[0].decode("ascii")
      #if charset in set(("IBMPC", "+7 FIDO", "ALT", "+7_FIDO", "CP-866", 
      #      "RUSSIAN", "RUS_FTN", "FIDO", "UKR", "R_FIDO", "TABLE", "IBMPC2", "R FIDO", 
      #      "FTN", "JK", "KOI", "CP808", "RUFIDO", "Russian", "IBM", "+7FIDO")):
      #    charset="cp866"

    # hacks
    if msg.area:
      msg.area = msg.area.upper()
      print("area for charset [%s]"%repr(msg.area))
      if RE_russian.match(msg.area):
        charset="cp866"
      elif RE_latin.match(msg.area):
        charset="latin-1"
      elif RE_ukrainian.match(msg.area):
        charset="cp1125"

    else:
      # netmail default charset
      charset="cp866"

    #print("charset:", charset)


    #print ("MSGID", msgid)
  
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
  


    # get message originator and recipient addresses

    if b"MSGID:" in msg.kludge:
      msgid=msg.kludge[b"MSGID:"].decode("ascii")
    else:
      msgid=None # try to generate


    if msg.area:

      # get originator address from Origin or MSGID
      origdom = self.FIDOADDR
      origname, _ = msg.orig[0], ftn.addr.addr2str(msg.orig[1])

      origaddr = None
      for b1 in msg.body:
        try:
          a=ftn.msg.decode_origin(b1).decode(charset)
          origaddr = ftn.addr.addr2str(ftn.addr.str2addr(a))
        except ftn.msg.DecodeError:
          pass

      if not origaddr:
        try:
          origaddr=ftn.addr.addr2str(ftn.addr.str2addr(msg.kludge[b"MSGID:"].decode(charset).split(" ")[0].split("@")[0]))
          print ("got from msgid:", origaddr)
        except:
          pass

      if not origaddr:
        raise FTNNoOrigin # No Origin, no MSGID with FTN address

      # destination is echo
      destdom = self.FIDOECHO
      destaddr = msg.area.decode(charset)
      destname, _ = msg.dest

    else:
      # netmail
      origdom = self.FIDOADDR
      origname, origaddr = msg.orig[0], ftn.addr.addr2str(msg.orig[1])

      destdom = self.FIDOADDR
      destname, destaddr = msg.dest[0], ftn.addr.addr2str(msg.dest[1])
  
  
    guessed=False
    mayusezone=None
    if origdom==self.FIDOADDR and origaddr[0]=='0':
      print("MSG with from = '%s': guess zone..."%origaddr)
      if msgid:
        guessfrom=ftn.addr.str2addr(msgid.split(" ")[0].split("@")[0])
        knownfrom=ftn.addr.str2addr(origaddr)
        if guessfrom[1]==knownfrom[1] and guessfrom[2]==knownfrom[2]:
          print (origaddr,"->",ftn.addr.addr2str(guessfrom))
          origaddr=ftn.addr.addr2str(guessfrom)
          guessed=True
          mayusezone=guessfrom[0]
  
      if not guessed:
        print ("AREA:", repr(msg.area))
        raise FTNFail("Zone in sender address is empty and cannot guess from MSGID %s\n"
          		"guess: %s known: %s"%(repr(msg.kludge.get(b"MSGID:")), guessfrom, knownfrom))
  
  
    guessed=False
    replyzone=None
    if destdom==self.FIDOADDR and destaddr[0]=='0':
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


    sendernameel = xml.etree.ElementTree.SubElement(header, "sendername")
    sendernameel.text = clean_str(origname.decode(charset))

    recipientnameel = xml.etree.ElementTree.SubElement(header, "recipientname")
    recipientnameel.text = clean_str(destname.decode(charset))

    dateel = xml.etree.ElementTree.SubElement(header, "date")
    dateel.text = clean_str(msg.date.decode(charset))

    subjel=xml.etree.ElementTree.SubElement(header, "subject")
    subjel.text = clean_str(msg.subj.decode(charset))
    
    body = (b"\n".join(msg.body)+b"\n").decode(charset)

    if msgid is None:
      # make hash of originator+date+subject+body - date to allow repeating posts
      hashdata = "\n".join((origname.decode(charset), origaddr, destname.decode(charset), destaddr,
            msg.date.decode(charset), msg.subj.decode(charset), body))
      msgid = origaddr + " " + sha1(hashdata.encode(charset)).hexdigest()
      print("generated MSGID", repr(msgid))
      msg.kludge[b"MSGID:"] = msgid.encode("ascii")
      #raise Exception("No MSGID, src=%s"%repr(origaddr))
      #raise FTNNoMSGID()


    #print "-"*79
    #sys.stdout.write(body.encode("utf-8"))
    #print "="*79

    #  raise Exception("Verify senderaddress and destination address are listed. (area autocreate, destination is listed, ...)")

    origid = self.check_addr(origdom, origaddr) # allow autocreate for source
    destid = self.check_addr(destdom, destaddr) # check node in nodelist and area exists
    # no autocreate. only on request and if exists in uplink lists

    # database must have trigger to check address to be created for nodelist and area for echolist and uplinks

    if not bulkload:
      recvfrom_id = self.find_addr(self.FIDOADDR, recvfrom)

      # check domain's "verifysubscription" and if true refuse if not subscribed
      r=self.db.prepare("select verifysubscriptions from domains where id=$1")(destdom)
      if len(r) == 0:
        raise Exception("invalid domain after checkaddress ??? %d"%destdom)
      verify_subscription = r[0][0]
  
      if verify_subscription:
        # check if message received from subscribed to the destination's address
        r=self.db.prepare("select count(id) from subscriptions where subscriber=$1 and target=$2")(recvfrom_id, destid)
        if r[0][0]==0:
          raise FTNNotSubscribed("%d/%s (id=%d)"%(self.FIDOADDR, recvfrom, recvfrom_id), "%d/%s (id=%d)"%(destdom, destaddr, destid))
        print("posting allowed for %d (%d/%s) to %d/%s"%(recvfrom_id, self.FIDOADDR, recvfrom, destdom, destaddr))

    else:
       recvfrom_id=None
  
    if len(self.db.prepare("select id from messages where msgid=$1")(msgid)):
      raise FTNDupMSGID(msgid)

    if not self.Q_msginsert:
      self.Q_msginsert = self.db.prepare("insert into messages (source, destination, msgid, header, body, processed, receivedfrom)"
          " values ($1, $2, $3, $4, $5, $6, $7)")

    self.Q_msginsert(origid, destid, msgid, header, body, processed, recvfrom_id)




  def import_link_auth(self, node, connectpassword, robotpassword, echolevel, fecholevel, echogroups, fechogroups):
    addr_id=check_addr(self.FIDOADDR, node)
  
    doc = xml.dom.minidom.Document()
    authel = doc.createElement("FTNAUTH")
  
    connectpwel = doc.createElement("ConnectPassword")
    authel.appendChild(connectpwel)
    connectpwtext = doc.createTextNode(connectpassword)
    connectpwel.appendChild(connectpwtext)
  
    for name, val in [("RobotsPassword", [robotpassword]),("EchoLevel", [echolevel]), 
          	    ("FileEchoLevel", [fecholevel]), 
          	    ("EchoGroup",list(echogroups or "")), ("FileEchoGroup",list(fechogroups or ""))]:
      for v1 in val:
        if v1:
          itemel=doc.createElement(name)
          authel.appendChild(itemel)
          itemtext=doc.createTextNode(v1)
          itemel.appendChild(itemtext)
  
    c=conn.cursor()
    try:
      c.execute("insert into links (address, authentication) values (%s, %s)", (addr_id, authel.toxml()))
      conn.commit()
    except psycopg2.IntegrityError as exc:
      if psycopg2.errorcodes.lookup(exc.pgcode)!='UNIQUE_VIOLATION':
        raise exc
      conn.rollback()
      c.execute("update links set (authentication) = (%s) where address=%s", (authel.toxml(), addr_id))
      conn.commit()
  
  


#print( db.prepare("select e.domain, e.text from subscriptions s, addresses a, addresses e where s.subscriber=a.id and e.id=s.target and a.text='2:5020/12000.1'")() )
