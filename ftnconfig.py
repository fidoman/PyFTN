
import postgresql
import postgresql.alock
import re
import socket
import os
import ftn.addr
from ftn.ftn import FTNNoAddressInBase

# ---------------------------------------------------------------------------------------

def connectdb(dbstring = open("/home/sergey/PyFTN/database.cfg").read().strip()):
  # pq://user:password@hostname/databasename
  db = postgresql.open(dbstring)
  init_domains(db)
  init_commuter(db)
  return db

# system-specific settings

FIDODIR="/tank/home/fido"
ADDRESS="2:5020/12000"
SYSOP="Sergey Dorofeev"
HOSTNAME="fluid.fidoman.ru"

NETMAIL_uplinks = ["2:5020/758", "2:5020/715"] # default route
NETMAIL_peers = [] #"2:5020/274", "2:5020/545", "2:5020/1042", "2:5020/3274"] # bone
# 2:6090/1

#NETMAIL_peers += ["2:5020/181", "2:5020/1453", "2:50/10", "2:5059/37"] # downliks
NETMAIL_peers += ["2:5020/4441"] # echomail uplink
NETMAIL_peers += ["2:5020/1200"]
NETMAIL_peers += ["2:5020/614"] # fileecho uplinks

# only links must be here!
NETMAIL_peerhosts = [("2:5059/0", "2:5059/37"),
                     ("2:5051/0", "2:5020/1042"),
                     ("2:5097/0", "2:5097/31"),
                     ("2:5012/0", "2:5012/200"),
                     ("2:5040/0", "2:5040/2"),
]



# generally-acceptable defaults

NODELIST=os.path.join(FIDODIR, "nodelist/fido.ndl")
NODELISTENCODING="iso8859-1"

DUPDIR=os.path.join(FIDODIR, "refuse/dupmsg")
BADDIR=os.path.join(FIDODIR, "refuse/badmsg")
SECDIR=os.path.join(FIDODIR, "refuse/secmsg")
LOGDIR=os.path.join(FIDODIR, "log")
INBOUND = os.path.join(FIDODIR, "recv")
DINBOUND = os.path.join(FIDODIR, "drecv")
OUTBOUND = os.path.join(FIDODIR, "send")
BINKLEYSTYLE = os.path.join(FIDODIR, "outb")
DOUTBOUND = os.path.join(FIDODIR, "dsend")
MSGMARKESTAT = os.path.join(FIDODIR, "msgestat")
MSGMARKPOLL = os.path.join(FIDODIR, "msgpoll")
FILEDIR = os.path.join(FIDODIR, "files")
FAREASDIR = os.path.join(FIDODIR, "fareas")
GROUPFILESBY=5000

# routing files
format1files = [os.path.join(FAREASDIR, "r50route/R50.ROU"), os.path.join(FAREASDIR, "net5020/n5020.rou")]
format2files = [os.path.join(FAREASDIR, "r50route/R50.TRU"), os.path.join(FAREASDIR, "net5020/n5020.tru")]

# logging
DAEMONLOG="daemon.log"

UNPACK1=[os.path.join(FIDODIR, "unpack"), "quick"]
UNPACK1LOG="quick.log"
UNPACK2=[os.path.join(FIDODIR, "unpack")]
UNPACK2LOG="unpack.log"

robotnames = {
    "echo": "AreaFix",
    "fileecho": "FileFix"
}


FTNPORT=24555
NNTPPORT=11119
DAEMONBIND=[
    (socket.AF_INET, ('0.0.0.0', FTNPORT), "ftn"),
    (socket.AF_INET6, ('::', FTNPORT), "ftn"),
#    (socket.AF_INET, ('0.0.0.0', NNTPPORT), "nntp"),
#    (socket.AF_INET6, ('::', NNTPPORT), "nntp"),
]
# add binding with specifying session function

PACKETTHRESHOLD = 100*1024
BUNDLETHRESHOLD = 500*1024

MSGSIZELIMIT = 470000

BUNDLETIMELIMIT=30
PACKETTIMELIMIT=3

# never change it

PKTLOCK=1
BUNDLELOCK=2
TICLOCK=3
EXPORTLOCK={"netmail": 4, "echomail": 5, "fileecho": 6, "filebox": 7}
IMPORTLOCK=8

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
#  for id, comm in db.prepare("select id, commuter from subscriptions"):
#    if comm:
#      db.FTN_commuter[id] = comm


# -

RE_russian=re.compile("RU\.|SU\.|MO\.|R50\.|N50|HUMOR\.|TABEPHA$|XSU\.|ESTAR\.|FLUID\.|SURVIVAL\.GUIDE$|STARPER\.|VGA\.PLANETS|OBEC\.|SPB\.|"
            "CTPAHHOE\.MECTO|PVT\.|1072\.|ADINF\.|ZX\.SPECTRUM|\$CRACK\$|BOCHAROFF\.|ZONE7|MISTRESS\.|FAR\.SUPPORT|FIDONET\.HISTORY|MINDO\.|"
            "TYT\.BCE\.HACPEM|PUSHKIN\.|715\.|XPEHOBO\.MHE|CKA3KA\.CTPAHHOE\.MECTO|UZ\.|FREUD|GUITAR\.SONGS|RUSSIAN\.|LOTSMAN\.|AVP\.|1200\.|"
            "MU\.|REAL\.SIBERIAN\.VALENOK|KAZAN\.|BRAKE\'S\.MAILER\.SUPPORT|\$HACKING\$|GERMAN\.RUS|GSS\.PARTOSS|NODEX\.|380\.|SMR\.|"
            "TESTING$|ESPERANTO\.RUS|RUS\.|BEL\.|MOLDOVA\.|RUS_|RUSSIAN_|KAK\.CAM-TO|DEMO.DESIGN|FTNED\.RUS|REAL\.SPECCY|"
            "TAM\.HAC\.HET|T-MAIL|1641\.|DN\.|TVER\.|ASCII_ART|GER\.RUS|KHARKOV\.|XCLUDE\.|CB\.RADIO|1754\.|400\.|NSK\.|N463\.|"
            "614\.|6140\.|LUCKY\.GATE|DREAD'S\.|KIEV\.|HACKING|CASTLE\.THERRON|FIDO7\.|PC\.CODING|NICE\.SOURCES|TULA\.|2\.5083\.|"
            "CONCORD|TITANIC\.|ROO\.|DWAVE\.|RSS.BASH.ORG.RU|RSS.SECURITYLAB.RU|RSS.BUGTRAQ.RU|RSS.RU.NEWS|SIMBIRSK\.|HOUSTON\.|"
            "INTERBONE\.|RSS\.IBASH\.ORG\.RU|CHERKASSY\.|AT\.TALK|SMOLENSK\.|Z\.TAVSAR\.|WIT\.|STV\.|54\.|"
            "RSS\.IPFW\.RU\.BASH|RSS\.COMPULENTA\.RU|4441\.|KOENIG\.|ALTYN\.|NIKOLAEV\.|TSK\.|"
	"KN\.|XSTATION\.")


RE_cp437 = re.compile("BBS_ADS|IC$|ENET\.|FTSC_|PASCAL|BLUEWAVE|HOME_COOKING|FN_|WIN95|FIDOSOFT\.|OTHERNETS|FIDOTEST|"
            "ECHOLIST|STATS|COOKING|LINUX|HAM|GOLDED|OS2|ASIAN_LINK|WINDOWS|ARGUS|EASTSTAR|FIDO-REQ|FDN_ANNOUNCE|"
            "ALLFIX_|BBS_PROMOTION|KOFO_|FUNNY|SYNC_|SYNCHRONET|SYNCDATA|LORD|BBS_CARNIVAL|RSS\.DEALEXTREME\.COM|"
            "ALT-BBS-ADS|IPV6|MEMORIES|JAMNNTPD|AMATEUR_RADIO|FIDONEWS|.*?\.GER$|ESSNASA|MAKENL_NG|CFORSALE|IREX|"
            "MYSTIC|ZCC-PUBLIC|AUTOMOTIVE|DBRIDGE|INTERNET|CHATTER|FILEGATE|EC_UTIL|PCBOARD")

RE_cp850 = re.compile("no_such_echo")

RE_latin = re.compile("CBM|ESP\.")

RE_utf8 = re.compile("POLITICS|ALL-POLITICS|DEBATE|CONSPRCY|COFFEE_KLATSCH")

RE_ukrainian=re.compile("UKR\.|UA\.|R46\.|R46FE\.|LUGANSK\.")


def suitable_charset(chrs_kludge, charset_kludge, mode, srcdom, srcaddr, destdom, destaddr): # mode="encode"|"decode"

    charset = "fido_relics"

    if chrs_kludge is None and charset_kludge==b"LATIN-1":
      chrs_kludge=b"LATIN-1 2"

    if chrs_kludge==b"CP866 2":
      charset="cp866"
    elif chrs_kludge==b"CP1125 2":
      charset="cp1125"
    elif chrs_kludge==b"CP850 2":
      charset="cp850"
    elif chrs_kludge==b"CP858 2":
      charset="cp858"
    elif chrs_kludge==b"CP865 2":
      charset="cp865"
    elif chrs_kludge==b"CP861 2":
      charset="cp861"
    elif chrs_kludge==b"CP437 2":
      charset="cp437"
    elif chrs_kludge==b"CP1251 2":
      charset="cp1251"
    elif chrs_kludge==b"CP1250 2":
      charset="cp1250"
    elif chrs_kludge==b"CP1252 2":
      charset="cp1252"
    elif chrs_kludge==b"LATIN-1 2" or chrs_kludge==b"ISO-8859-1 2":
      charset="iso8859-1"
    elif chrs_kludge==b"LATIN-9 2":
      charset="iso8859-15"
    elif chrs_kludge==b"UTF-8 4":
      charset="utf-8"

#      charset=msg.kludge[b"CHRS:"].rsplit(b" ", 1)[0].decode("ascii")
      #if charset in set(("IBMPC", "+7 FIDO", "ALT", "+7_FIDO", "CP-866", 
      #      "RUSSIAN", "RUS_FTN", "FIDO", "UKR", "R_FIDO", "TABLE", "IBMPC2", "R FIDO", 
      #      "FTN", "JK", "KOI", "CP808", "RUFIDO", "Russian", "IBM", "+7FIDO")):
      #    charset="cp866"

    elif destdom=="echo":
      #print("area for charset [%s]"%repr(msg.area))
      if RE_utf8.match(destaddr):
        charset="utf-8"
      elif RE_russian.match(destaddr):
        charset="cp866"
      elif RE_cp437.match(destaddr):
        charset="cp437"
      elif RE_cp850.match(destaddr):
        charset="cp850"
      elif RE_latin.match(destaddr):
        charset="iso8859-1"
      elif RE_ukrainian.match(destaddr):
        charset="cp1125"
      else:
        # unknown echo, relax kludge checks
        if chrs_kludge==b"UTF-8 2":
          charset="utf-8"

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
    if len(x)==0 or x[0][0] is None:
      return None
    authinfo=pw[linkaddr]=x[0][0]

  if forrobots:
    return authinfo.find("RobotsPassword").text
  else:
    return authinfo.find("ConnectPassword").text



def get_link_polling(db, linkaddr):
  x=db.prepare("select l.connection from links l, addresses a "
                    "where l.address=a.id and a.domain=$1::integer and a.text=$2::varchar"
                )(db.FTN_domains["node"], linkaddr)

#SELECT address, xpath('/FTNAUTH/ConnectPassword/text()',authentication)
#  FROM links;


  if len(x)==0 or x[0][0] is None:
      return None
  conninfo=x[0][0]

  return conninfo.find("DoPoll") is not None


def get_link_pkt_format(db, linkaddr):
  try:
    pw=db.link_pkt_format
  except:
    pw=db.link_pkt_format={}

  try:
    pwq=db.link_pkt_format_q
  except:
    pwq=db.link_pkt_format_q=db.prepare("select l.pktformat from links l, addresses a "
                    "where l.address=a.id and a.domain=$1::integer and a.text=$2::varchar")

  pktformat = pw.get(linkaddr)
  if pktformat is None:
    x = pwq(db.FTN_domains["node"], linkaddr)
    if len(x)==0 or x[0][0] is None:
      return db.prepare("select pktformat from links where address IS NULL")()[0][0]
    pktformat=pw[linkaddr]=x[0][0]

  return pktformat

def get_link_bundler(db, linkaddr):
  try:
    pw=db.link_bundler
  except:
    pw=db.link_bundler={}

  try:
    pwq=db.link_bundler_q
  except:
    pwq=db.link_bundler_q=db.prepare("select l.bundle from links l, addresses a "
                    "where l.address=a.id and a.domain=$1::integer and a.text=$2::varchar")

  bundler = pw.get(linkaddr)
  if bundler is None:
    x = pwq(db.FTN_domains["node"], linkaddr)
    if len(x)==0: # no config for the link
      return db.prepare("select bundle from links where address IS NULL")()[0][0]
    bundler=pw[linkaddr]=x[0][0]

  return bundler



def get_link_id(db, linkaddr, withfailback=False):
  try:
    linkids=db.link_ids
  except:
    linkids=db.link_ids={}

  try:
    linkids_q=db.link_ids_q
  except:
    linkids_q=db.link_ids_q=db.prepare(
        "select l.id from links l, addresses a where l.address=a.id and a.domain=$1 and a.text=$2")

  link_id = linkids_q.first(db.FTN_domains["node"], linkaddr)
  if link_id:
    return linkids.setdefault(linkaddr, link_id)
  if withfailback:
    link_id=db.prepare("select id from links where address IS NULL")()[0][0]
  return link_id


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

# -

if __name__ == "__main__": 
  db=connectdb()
  for i in range(100):
#    print(get_link_password(db, "2:5020/2065"))
#    print(get_link_password(db, "2:5020/715"))
    print(get_link_password(db, "2:5020/1955"))
    print(get_link_password(db, "2:5020/1955", True))
