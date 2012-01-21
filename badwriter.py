import os

from ftnconfig import *

CNT="counter"

class BadWriter:
  def __init__(self, folder, counterfile, ext):
    self.folder=folder
    try:
      os.makedirs(folder)
    except OSError as e:
      if e.args[0]!=17: # not File Exists error
        raise e

    self.counterfile=counterfile
    self.ext=ext
    try:
      self.badcounter=eval(open(counterfile).read())
    except:
      self.badcounter=1

  def write(self, data, status):
    f=open(os.path.join(self.folder, "%012X.%s"%(self.badcounter, self.ext)), "wb")
    f.write(data)
    f.close()

    if status:
      f=open(os.path.join(self.folder, "%012X.status"%self.badcounter), "w")
      f.write(status)
      f.close()

    self.badcounter+=1

  def __del__(self):
    open(self.counterfile,"w").write(str(self.badcounter))

badmsgs=BadWriter(BADDIR, os.path.join(BADDIR,CNT), "msg")
#badpkts=BadWriter("badpkt", "badpkt/counter", "pkt")
#badbnds=BadWriter("badbnd", "badbnd/counter", "mo0")
dupmsgs=BadWriter(DUPDIR, os.path.join(DUPDIR,CNT), "msg")
secmsgs=BadWriter(SECDIR, os.path.join(SECDIR,CNT), "msg")
