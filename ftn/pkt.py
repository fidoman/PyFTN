import struct
#import mmap
import io
from .msg import MSG
from .addr import *
#import os

debug=False

# FSC-0048 Type 2+ support

def read_asciiz(fo, maxlen=None):
  buf=io.BytesIO()
  count=0
  while (maxlen is None) or (count<maxlen):
    c=fo.read(1)
    if len(c)==0:
      raise FTNFail("EOF reading mandatory packet field")
    if c==b"\0":
      break
    buf.write(c)
    count+=1

  buf.seek(0)
  return buf.read()


class PKT:
  def read_pkt2(self, fo):
      #read packet header
      #read messages

      h=fo.read(58)
      if len(h)<58:
        raise FTNFail("packet is too short (%d bytes): header incomplete"%len(h))

    # fsc-0001 PKT format
    # fsc-0039 PKT format capability word
    # http://www.ftsc.org/docs/fsc-0048.002 2+ extensions

      (fnode,tnode,year,month,day,hour,minute,second,        # 00-0F
       baud,sig,fnet,tnet, prod_l,rev_h, password,        # 10-21
       qfzone,qtzone,auxnet,CW_xchgcopy, prod_h,rev_l,   # 22-2B
       capability,fzone,tzone,fpoint,tpoint             # 2C-35
       ) = struct.unpack("<12H2B8s4H2B5H4x",h)

      if sig!=2:
        raise Exception("bad PKT signature in %s"%repr(fo))

      #print fnet,fnode,tnet,tnode,password

      self.password = password
      self.source = (fzone or qfzone,fnet,fnode,fpoint)
      self.destination = (tzone or qtzone,tnet,tnode,tpoint)
      self.auxnet = auxnet
      if year<1900:
        year+=1900
      self.date = (year,month+1,day,hour,minute,second)

      #print self.source, self.destination

      #print "now reading messages"
      msg_n=0
      while True: 
        if debug:
          print("message %d at 0x%08X"%(msg_n, fo.tell()))
        sigdata=fo.read(2)
        if len(sigdata)<2:
          print("packet without correct \0\0 terminator")
          break # for packets without 00 00 terminator

        try:
          (sig,)=struct.unpack("<H",sigdata)
        except:
          if ignore_err:
            break
          else:
            raise Exception("Unexpected end of packet")

        #pos+=2

        if sig!=2:
          if sig!=0:
            if ignore_err:
              break
            else:
                raise Exception("bad signature (message %d pos 0x%08X)"%(msg_n, fo.tell()))
          else:
            break

        hdata=fo.read(32)
        if len(hdata)<32:
          raise FTNFail("Unexpected end of packet")

        (fnode,tnode,fnet,tnet,attr,cost,date)=struct.unpack("<6H20s", hdata)
        #pos+=32

        date=date.strip(b"\0")

        tname=read_asciiz(fo, 36)
        if debug: print("tname end %08X"%fo.tell())
        fname=read_asciiz(fo, 36)
        if debug: print("fname end %08X"%fo.tell())
        subj=read_asciiz(fo, 72)
        if debug: print("subj end %08X"%fo.tell())
        body=read_asciiz(fo)
        if debug: print("body end %08X"%fo.tell())
        
        #print "load msg", msg_n, tnet, tnode
        msg=MSG()
        msg.load( (fname,(0,fnet,fnode,0)),
                (tname,(0,tnet,tnode,0)),subj,date,attr,cost,body )
        
        self.msg.append(msg)
        msg_n+=1

  def read_utf8z(self, fo):
    self.msg = []
    header = True
    for l in fo.readlines():
      l=l.rstrip(b"\n")
      if header:
        h=l.split(b"\0")
        if h[0]!=b"UTF8":
          raise FTNFail("Invalid header")
        self.source = str2addr(h[1].decode("utf-8"))
        self.destination = str2addr(h[2].decode("utf-8"))
        self.creator = h[3]
        self.password = h[4]
        #try:
        #print(os.fstat(fo).st_mtime)
        self.date = None
        header = False
      else:
        date, toname, fromname, subj, body, x = l.split(b"\0")
#        print ("From:", fromname)
#        print ("To  :", toname)
#        print ("Subj:", subj)
#        print ("Date:", date)
#        print ("X   :", repr(x))
#        print (body.replace("\r", "\n").replace("\1", "@"))
        msg = MSG()
        msg.load( (fromname, self.source), (toname, self.destination),
                subj, date, 0, 0, body)
        msg.kludge["CHRS:"] = "UTF-8 4"

        #print (msg.as_str().decode("utf-8"))
        self.msg.append(msg)

  def __init__(self, fo=None, ignore_err=False, format='pkt2'):
    self.msg = []
    if fo:
      self.fn=None
      if type(fo) in [str, str]:
        self.fn=fo
        fo=open(self.fn,"rb")

      if format=='pkt2':
        self.read_pkt2(fo)
      elif format=='utf8z':
        self.read_utf8z(fo)
      else:
        raise FTNFail("cannot load such PKT (%s)"%format)

      if self.fn:
        fo.close()

      #if msg_n==10000:
      #  raise Exception("paket too large (10000 messages is maximum limit)")

    else:
      pass

  def __str__(self):
    return "SRC: %s\n"%addr2str(self.source) + \
      "DST: %s\n"%addr2str(self.destination) + \
      "PASS %s\n"%self.password + \
      "DATE %04d-%02d-%02d %02d:%02d:%02d\n"%self.date + \
      "Messages: %d\n"%len(self.msg) + \
"===============================================================================\n".join([""]+list(map(str,self.msg))+[""])

  def save(self, file, format='pkt2'):

    def cut(s, l):
      if len(s)<l:
        return s+b"\0"
      else:
        return s[:l]

    if type(file) is str:
      f=open(file, "wb")
    else:
      f=file
    #print(repr(self.source), repr(self.destination))
    #print(repr(self.date),repr(self.password))
    f.write(struct.pack("<13H8s10H4s",self.source[2],self.destination[2],
      self.date[0],self.date[1]-1,self.date[2],self.date[3],
      self.date[4],self.date[5],0,2,self.source[1],self.destination[1],0xFE,
       self.password,
       self.source[0],self.destination[0],
       0,0x0100,0,0x0001,self.source[0],self.destination[0],
       self.source[3],self.destination[3],b"\0\0\0\0")) # b"XPKT"
    for m in self.msg:
      f.write(struct.pack("<7H20s", 2, m.orig[1][2], m.dest[1][2],
        m.orig[1][1], m.dest[1][1], m.attr, m.cost, m.date) +
        cut(m.dest[0], 36) + cut(m.orig[0], 36) + cut(m.subj, 72)+
        m.make_body()+b"\0")

    f.write(b"\0\0")

    if type(file) is str:
      f.close()

if __name__=="__main__":
  from glob import glob
  j=0
  for file in glob("*.pkt"):
    print(file)
    p=PKT(file)
#    for m in p.msg:
#      m.add_seenby("5020/9999")
#      m.add_path("5020/9999")

#    p.save(file+"_")
    #i=0
    #print len(p.msg)
    #while i<len(p.msg):
    #  msg=`p.msg[i]`
    #  if( len(msg)>50000 ):
    #    open("%04d.msg"%j,"wb").write(msg)
    #    del p.msg[i]
    #    j+=1
    #  else:
    #    i+=1
    #print len(p.msg)
    #p.save(file)
