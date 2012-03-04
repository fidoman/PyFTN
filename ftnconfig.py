
import postgresql
import postgresql.alock
import re
import socket
import os
import ftn.addr
from ftn.ftn import FTNNoAddressInBase

# ---------------------------------------------------------------------------------------

def connectdb():
  db = postgresql.open("pq://fido:bgdis47wb@127.0.0.1/fido")
  init_domains(db)
  init_commuter(db)
  db.filen=FileNumbering(db)
  return db

FIDODIR="/tank/home/fido"
ADDRESS="2:5020/12000"
SYSOP="Sergey Dorofeev"
NODELIST=os.path.join(FIDODIR, "fareas/dailylst/NODELIST.064")

DUPDIR=os.path.join(FIDODIR, "refuse/dupmsg")
BADDIR=os.path.join(FIDODIR, "refuse/badmsg")
SECDIR=os.path.join(FIDODIR, "refuse/secmsg")
INBOUND = os.path.join(FIDODIR, "recv")
DINBOUND = os.path.join(FIDODIR, "drecv")
OUTBOUND = os.path.join(FIDODIR, "send")
DOUTBOUND = os.path.join(FIDODIR, "dsend")
MSGMARK = os.path.join(FIDODIR, "msgmark")
FILEDIR = os.path.join(FIDODIR, "files")
GROUPFILESBY=5000

# routing files
format1files = ["/tank/home/fido/fareas/r50route/R50.ROU", "/tank/home/fido/fareas/net5020/N5020.ROU"]
format2files = ["/tank/home/fido/fareas/r50route/R50.TRU", "/tank/home/fido/fareas/net5020/N5020.TRU"]

NETMAIL_uplinks = ["2:5020/758", "2:5020/715"] # default route
NETMAIL_peers = [] #"2:5020/274", "2:5020/545", "2:5020/1042", "2:5020/3274"] # bone
# 2:6090/1

#NETMAIL_peers += ["2:5020/181", "2:5020/1453", "2:50/10", "2:5059/37"] # downliks
NETMAIL_peers += ["2:5020/4441"] # echomail uplink

# only links must be here!
NETMAIL_peerhosts = [("2:5059/0", "2:5059/37"),
                     ("2:5051/0", "2:5020/845"),
                     ("2:5097/0", "2:5097/31")]

DAEMONPORT=24555
DAEMONBIND=[
    (socket.AF_INET, ('0.0.0.0', DAEMONPORT)),
    (socket.AF_INET6, ('::', DAEMONPORT)),
]

PACKETTHRESHOLD = 100*1024
BUNDLETHRESHOLD = 500*1024


PKTLOCK=1
BUNDLELOCK=2
TICLOCK=3

# ---------------------------------------------------------------------------------------

# - values configured in database

def init_domains(db):
  try:
    return db.FTN_domains, db.FTN_backdomains
  except AttributeError:
    db.FTN_domains = {}
    db.FTN_backdomains = {}
    for domain_id, domain_name in db.prepare("SELECT id, name FROM domains"):
      if domain_name=="fidonet node":
        db.FTN_domains["node"]=domain_id
        db.FTN_backdomains[domain_id]="node"
      elif domain_name=="fidonet echo":
        db.FTN_domains["echo"]=domain_id
        db.FTN_backdomains[domain_id]="echo"
      elif domain_name=="fidonet fileecho":
        db.FTN_domains["fileecho"]=domain_id
        db.FTN_backdomains[domain_id]="fileecho"
      elif domain_name=="fidonet backbone":
        db.FTN_domains["backbone"]=domain_id
        db.FTN_backdomains[domain_id]="backbone"
    return db.FTN_domains, db.FTN_backdomains


def init_commuter(db):
  db.FTN_commuter = {}
  for id, comm in db.prepare("select id, commuter from subscriptions"):
    if comm:
      db.FTN_commuter[id] = comm


# -

RE_russian=re.compile("RU\.|SU\.|MO\.|R50\.|N50|HUMOR\.|TABEPHA$|XSU\.|ESTAR\.|FLUID\.|SURVIVAL\.GUIDE$|STARPER\.|VGA\.PLANETS|OBEC\.|SPB\.|"
            "CTPAHHOE\.MECTO|PVT\.|1072\.|ADINF\.|ZX\.SPECTRUM|\$CRACK\$|BOCHAROFF\.|ZONE7|MISTRESS\.|FAR\.SUPPORT|FIDONET\.HISTORY|MINDO\.|"
            "TYT\.BCE\.HACPEM|PUSHKIN\.|715\.|XPEHOBO\.MHE|CKA3KA\.CTPAHHOE\.MECTO|UZ\.|FREUD|GUITAR\.SONGS|RUSSIAN\.|LOTSMAN\.|AVP\.|1200\.|"
            "MU\.|REAL\.SIBERIAN\.VALENOK|KAZAN\.|BRAKE\'S\.MAILER\.SUPPORT|\$HACKING\$|GERMAN\.RUS|GSS\.PARTOSS|NODEX\.|380\.|SMR\.|"
            "TESTING$|ESPERANTO\.RUS|RUS\.|BEL\.|MOLDOVA\.|UKR\.|UA\.|RUS_|RUSSIAN_|KAK\.CAM-TO|DEMO.DESIGN|FTNED\.RUS|REAL\.SPECCY|"
            "TAM\.HAC\.HET|T-MAIL|1641\.|DN\.|TVER\.|ASCII_ART|GER\.RUS|KHARKOV\.|XCLUDE\.|CB\.RADIO|1754\.|400\.|NSK\.")


RE_cp437 = re.compile("BBS_ADS|IC$|ENET\.|FTSC_|PASCAL|BLUEWAVE|HOME_COOKING|FN_|WIN95|FIDOSOFT\.|FIDONEWS")

RE_utf8 = re.compile("POLITICS")

RE_ukrainian=re.compile("ZZUKR\.|ZZUA\.")


def suitable_charset(chrs_kludge, mode, srcdom, srcaddr, destdom, destaddr): # mode="encode"|"decode"

    charset = "ascii"

    if chrs_kludge==b"CP866 2": # can trust
      charset="cp866"

#      charset=msg.kludge[b"CHRS:"].rsplit(b" ", 1)[0].decode("ascii")
      #if charset in set(("IBMPC", "+7 FIDO", "ALT", "+7_FIDO", "CP-866", 
      #      "RUSSIAN", "RUS_FTN", "FIDO", "UKR", "R_FIDO", "TABLE", "IBMPC2", "R FIDO", 
      #      "FTN", "JK", "KOI", "CP808", "RUFIDO", "Russian", "IBM", "+7FIDO")):
      #    charset="cp866"

    if destdom=="echo":
      #print("area for charset [%s]"%repr(msg.area))
      if RE_utf8.match(destaddr):
        charset="utf-8"
      elif RE_russian.match(destaddr):
        charset="cp866"
      elif RE_cp437.match(destaddr):
        charset="cp437"
      elif RE_ukrainian.match(destaddr):
        charset="cp1125"

    else:
      # netmail default charset
      #if destaddr.startswith("2:50")
      charset="cp866"

    return charset

# - 

def get_link_password(db, linkaddr, forrobots=False):
  try:
    pw=db.link_passwords
  except:
    pw=db.link_passwords={}

  try:
    pwq=db.link_passwords_q
  except:
    pwq=db.link_passwords_q=db.prepare("select l.authentication from links l, addresses a "
                    "where l.address=a.id and a.domain=$1::integer and a.text=$2::varchar")

#SELECT address, xpath('/FTNAUTH/ConnectPassword/text()',authentication)
#  FROM links;


  authinfo = pw.get(linkaddr)
  if authinfo is None:
    x = pwq(db.FTN_domains["node"], linkaddr)
    if len(x)==0:
      return None
    authinfo=pw[linkaddr]=x[0][0]

  if forrobots:
    return authinfo.find("RobotsPassword").text
  else:
    return authinfo.find("ConnectPassword").text

def get_link_id(db, linkaddr):
  try:
    linkids=db.link_ids
  except:
    linkids=db.link_ids={}

  try:
    linkids_q=db.link_ids_q
  except:
    linkids_q=db.link_ids_q=db.prepare(
        "select l.id from links l, addresses a where l.address=a.id and a.domain=$1 and a.text=$2")

  return linkids.setdefault(linkaddr, linkids_q.first(db.FTN_domains["node"], linkaddr))

def get_addr_id(db, dom, addr):
  try:
    ac=db.address_cache
  except:
    ac=db.address_cache={}

  try:
    ac_q=db.address_cache_q
  except:
    ac_q=db.address_cache_q = db.prepare("select id from addresses where domain=$1 and text=$2")

  if (dom, addr) in ac:
    return ac[(dom, addr)]

  res=ac_q(dom, addr)
  if len(res)==1:
    ac[(dom, addr)]=res[0][0]
    return res[0][0]
  if len(res)>1:
    raise Exception("multiple address records found (%d)"%len(res))
  raise FTNNoAddressInBase(dom, addr)

def get_addr(db, addr_id):
  try:
    addrs=db.addrs
    addrs_q=db.addrs_q
  except:
    addrs=db.addrs={}
    addrs_q=db.addrs_q=db.prepare("select domain, text from addresses where id=$1")

  if addr_id not in addrs:
    addrs[addr_id] = addrs_q.first(addr_id)

  return addrs[addr_id]


# -

def addrdir(base, addr):
  return os.path.join(base, ".".join(map(str, ftn.addr.str2addr(addr))))

#def inbound_dir(address, isprotected, isdaemon):
#  base = DINBOUND if isdaemon else INBOUND
#  if isprotected:
#    return os.path.join(base, ".".join(map(str, ftn.addr.str2addr(address))))
#  else:
#    return os.path.join(base, "unknown")

# -

class FileNumbering:
  def __init__(self, db):
    self.db = db

  def get_pkt_n(self, link_id):
    with postgresql.alock.ExclusiveLock(self.db, ((PKTLOCK, link_id))):
      r = self.db.prepare("select pktn from links where id=$1").first(link_id)
      self.db.prepare("update links set pktn=pktn+1 where id=$1")(link_id)
    return r

  def get_bundle_n(self, link_id):
    with postgresql.alock.ExclusiveLock(self.db, ((BUNDLELOCK, link_id))):
      r = self.db.prepare("select bundlen from links where id=$1").first(link_id)
      self.db.prepare("update links set bundlen=bundlen+1 where id=$1")(link_id)
    return r

  def get_tic_n(self, link_id):
    with postgresql.alock.ExclusiveLock(self.db, ((TICLOCK, link_id))):
      r = self.db.prepare("select ticn from links where id=$1").first(link_id)
      self.db.prepare("update links set ticn=ticn+1 where id=$1")(link_id)
    return r

# -

if __name__ == "__main__": 
  db=connectdb()
  for i in range(100):
    print(get_link_password(db, "2:5020/2065"))
    print(get_link_password(db, "2:5020/715"))
    print(get_link_password(db, "2:5020/570"))

#  print(filen.get_pkt_n(113))
#  print(filen.get_tic_n(113))
#  print(filen.get_pkt_n(114))
#  print(filen.get_bundle_n(114))
