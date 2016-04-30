#!/usr/local/bin/python3 -bb

import sys

import ftnconfig
import ftnimport
db=ftnconfig.connectdb()

def get_link(lid):
  pass
  
def set_link(lid, data):
  pass

cmd=sys.argv[1]

if cmd=="list":
  for lid, addr in db.prepare("select l.id, a.text from links l, addresses a where a.id=l.address"):
    print (lid, addr)

elif cmd=="add":
  addr = sys.argv[2]
  lid = ftnconfig.find_link(db, addr)
  if lid is not None:
    print("already exists")
    exit()
  pasw = sys.argv[3]
  input("confirm add "+addr+" pw "+pasw)
  with ftnimport.session(db) as sess:
    sess.import_link_auth(myaddr, addr, pasw, pasw)

#authentication = <FTNAUTH><ConnectPassword>pwd</ConnectPassword><RobotsPassword>pwd</RobotsPassword></FTNAUTH>
# my = 160 (myaddr_id)
# lastsent = time.time()
