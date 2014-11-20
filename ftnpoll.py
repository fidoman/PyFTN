#!/usr/local/bin/python3 -bb

import ftnconfig
import ftnexport
import ftn.addr
import os
import traceback

class poller:
  def __init__(self,db,exclude=set()):
    self.db=db
    self.dests=set()
    self.exclude=exclude
  def add_one(self,addr):
    self.dests.add(addr)
  def add_set(self,addrs):
    self.dests.update(addrs)

  def do(self):
    to_poll = set()
    for d in self.dests:
      to_poll.update(map(lambda x: x[0], ftnexport.get_subscribers(self.db,d)))
    self.dests=set()
    myzone=ftn.addr.str2addr(ftnconfig.ADDRESS)[0]
    #print (myzone)
    for a in to_poll:
      #print("poll", a)
      a=ftnconfig.get_addr(self.db, a)[1]
      #print (a)
      if ftnconfig.get_link_polling(self.db, a):
        print ("poll",a)
      else:
        #print ("not needed")
        continue
      addr=ftn.addr.str2addr(a)
      if addr[0]==myzone:
        zonepath=ftnconfig.BINKLEYSTYLE
      else:
        zonepath=ftnconfig.BINKLEYSTYLE+".%d"%addr[0]
      if addr[3]==0:
        pollfilename="%04x%04x.dlo"%(addr[1], addr[2])
        basepath=zonepath
      else:
        pollfilename="0000%04x.dlo"%addr[3]
        basepath=os.path.join(zonepath, "%04x%04x.pnt"%(addr[1], addr[2]))

      try:
        os.makedirs(basepath, exist_ok=True)
      except FileExistsError:
        pass
      except:
        print ("could not create outbound directory")
        return
      try:
        touch=open(os.path.join(basepath,pollfilename),"a")
        touch.close()
      except:
        print ("could not poll", a)
        traceback.print_exc()

if __name__=="__main__":

  db=ftnconfig.connectdb()
  p=poller(db)
  p.add_one(73)
  p.do()
