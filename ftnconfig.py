
import postgresql
import postgresql.alock
import re
import socket
import os
import ftn.addr

# ---------------------------------------------------------------------------------------

db=postgresql.open("pq://fido:bgdis47wb@127.0.0.1/fido")

DUPDIR="dupmsg"
BADDIR="badmsg"
SECDIR="secmsg"
ADDRESS="2:5020/12000"
INBOUND="/tank/home/fido/recv"
DINBOUND="/tank/home/fido/drecv"
OUTBOUND="/tank/home/fido/send"
NODELIST="/tank/home/fido/nodelist/fido.ndl"
LOCALNETMAIL="/tank/home/fido/netmail"

NETMAIL_uplinks = ["2:5020/758", "2:5020/715"] # default route
NETMAIL_peers = ["2:5020/274", "2:5020/545", "2:5020/1042", "2:5020/3274"] # bone
NETMAIL_peers += ["2:5020/181", "2:5020/1453"] # downliks

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

init_domains(db)

def init_commuter(db):
  db.FTN_commuter = {}
  for id, comm in db.prepare("select id, commuter from subscriptions"):
    db.FTN_commuter[id] = comm

init_commuter(db)

# -

RE_russian=re.compile("RU\.|SU\.|MO\.|R50\.|N50|HUMOR\.|TABEPHA$|XSU\.|ESTAR\.|FLUID\.|SURVIVAL\.GUIDE$|STARPER\.|VGA\.PLANETS|OBEC\.|SPB\.|"
            "CTPAHHOE\.MECTO|PVT\.|1072\.|ADINF\.|ZX\.SPECTRUM|\$CRACK\$|BOCHAROFF\.|ZONE7|MISTRESS\.|FAR\.SUPPORT|FIDONET\.HISTORY|MINDO\.|"
            "TYT\.BCE\.HACPEM|PUSHKIN\.|715\.|XPEHOBO\.MHE|CKA3KA\.CTPAHHOE\.MECTO|UZ\.|FREUD|GUITAR\.SONGS|RUSSIAN\.|LOTSMAN\.|AVP\.|1200\.|"
            "MU\.|REAL\.SIBERIAN\.VALENOK|KAZAN\.|BRAKE\'S\.MAILER\.SUPPORT|\$HACKING\$|GERMAN\.RUS|GSS\.PARTOSS|NODEX\.|380\.|SMR\.|"
            "TESTING$|ESPERANTO\.RUS|RUS\.|BEL\.|MOLDOVA\.|UKR\.|UA\.|RUS_|RUSSIAN_|KAK\.CAM-TO|DEMO.DESIGN|FTNED\.RUS|REAL\.SPECCY|"
            "TAM\.HAC\.HET|T-MAIL|1641\.|DN\.|TVER\.|ASCII_ART|GER\.RUS|KHARKOV\.|XCLUDE\.|CB\.RADIO")

RE_latin=re.compile("IC$|ENET\.|FN_|FTSC_|PASCAL|BLUEWAVE")

RE_ukrainian=re.compile("ZZUKR\.|ZZUA\.")


def suitable_charset(chrs_kludge, mode, srcdom, srcaddr, destdom, destaddr): # mode="encode"|"decode"

    charset = "ascii"

    if chrs_kludge=="CP866 2": # can trust
      charset="cp866"

#      charset=msg.kludge[b"CHRS:"].rsplit(b" ", 1)[0].decode("ascii")
      #if charset in set(("IBMPC", "+7 FIDO", "ALT", "+7_FIDO", "CP-866", 
      #      "RUSSIAN", "RUS_FTN", "FIDO", "UKR", "R_FIDO", "TABLE", "IBMPC2", "R FIDO", 
      #      "FTN", "JK", "KOI", "CP808", "RUFIDO", "Russian", "IBM", "+7FIDO")):
      #    charset="cp866"

    if destdom=="echo":
      #print("area for charset [%s]"%repr(msg.area))
      if RE_russian.match(destaddr):
        charset="cp866"
      elif RE_latin.match(destaddr):
        charset="latin-1"
      elif RE_ukrainian.match(destaddr):
        charset="cp1125"

    else:
      # netmail default charset
      #if destaddr.startswith("2:50")
      charset="cp866"

    return charset

# - 

def get_link_password(db, linkaddr):
  try:
    pw=db.link_passwords
  except:
    pw=db.link_passwords={}

  authinfo = pw.get(linkaddr)
  if authinfo is None:
    x = db.prepare("""select l.authentication from links l, addresses a 
                    where l.address=a.id and a.domain=$1 and a.text=$2""")(db.FTN_domains["node"], linkaddr)
    if len(x)==0:
      return None
    authinfo=pw[linkaddr]=x[0][0]

  return authinfo.find("ConnectPassword").text

def get_link_id(db, linkaddr):
  try:
    linkids=db.link_ids
  except:
    linkids=db.link_ids={}
  return linkids.setdefault(linkaddr, 
        db.prepare("select l.id from links l, addresses a where l.address=a.id and a.domain=$1 and a.text=$2").first(db.FTN_domains["node"], linkaddr))

def inbound_dir(address, isprotected, isdaemon):
  base = DINBOUND if isdaemon else INBOUND
  if isprotected:
    return os.path.join(base, ".".join(map(str, ftn.addr.str2addr(address))))
  else:
    return os.path.join(base, "unknown")

# -

class FileNumbering:
  def __init__(self, db):
    self.db = db

  def get_pkt_n(self, link_id):
    with postgresql.alock.ExclusiveLock(db, ((PKTLOCK, link_id))):
      r = db.prepare("select pktn from links where id=$1").first(link_id)
      db.prepare("update links set pktn=pktn+1 where id=$1")(link_id)
    return r

  def get_bundle_n(self, link_id):
    with postgresql.alock.ExclusiveLock(db, ((BUNDLELOCK, link_id))):
      r = db.prepare("select bundlen from links where id=$1").first(link_id)
      db.prepare("update links set bundlen=bundlen+1 where id=$1")(link_id)
    return r

  def get_tic_n(self, link_id):
    with postgresql.alock.ExclusiveLock(db, ((TICLOCK, link_id))):
      r = db.prepare("select ticn from links where id=$1").first(link_id)
      db.prepare("update links set ticn=ticn+1 where id=$1")(link_id)
    return r

filen=FileNumbering(db)

# -

if __name__ == "__main__": 
  print(get_link_password(db, "2:5020/2065"))
  print(get_link_password(db, "2:5020/715"))

#  print(filen.get_pkt_n(113))
#  print(filen.get_tic_n(113))
#  print(filen.get_pkt_n(114))
#  print(filen.get_bundle_n(114))
