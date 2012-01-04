import os

class BadWriter:
  def __init__(self, folder, counterfile, ext):
    self.folder=folder
    self.counterfile=counterfile
    self.ext=ext
    self.badcounter=eval(open(counterfile).read())

  def write(self, data, status):
    f=open(os.path.join(self.folder, "%012X.%s"%(self.badcounter, self.ext)), "wb")
    f.write(data)
    f.close()
    f=open(os.path.join(self.folder, "%012X.status"%self.badcounter), "w")
    f.write(status)
    f.close()
    self.badcounter+=1

  def __del__(self):
    open(self.counterfile,"w").write(str(self.badcounter))

badmsgs=BadWriter("badmsg", "badmsg/counter", "msg")
#badpkts=BadWriter("badpkt", "badpkt/counter", "pkt")
#badbnds=BadWriter("badbnd", "badbnd/counter", "mo0")
dupmsgs=BadWriter("dupmsg", "dupmsg/counter", "msg")
secmsgs=BadWriter("secmsg", "secmsg/counter", "msg")
