#!/usr/bin/python

import struct
from .addr import *
from .ftn import FTNFail
import os
import re
import traceback

class DecodeError(Exception):
  pass

attrs=[        "Private",
        "Crash",
        "Recd",
        "Sent",
        "FileAttached",
        "InTransit",
        "Orphan",
        "KillSent",
        "Local",
        "HoldForPickup",
        "unused",
        "FileRequest",
        "ReturnReceiptRequest",
        "IsReturnReceipt",
        "AuditRequest",
        "FileUpdateReq"
      ]

class MSG:
  """ FTN message
  Init methods:
    read_from(file) - read
    write_to(file) - write
  Fields: 
    from - (name,addr)
    to - (name,addr)
    subj
    date
    area - defined if echomail
    kludge - dict
    body
    path
    seenby
    via
  """  
  def __init__(self,file=None):
    if( file != None ):
      f=open(file,"rb")
      h=f.read(190)
      if len(h)<190:
        raise FTNFail("msg header incomplete")
      try:
        fn,tn,subj,date,readcount,tnode,fnode,cost,fnet,tnet,\
          tzone,fzone,tpnt,fpnt,replyto,attr,nextreply \
          = struct.unpack("<36s36s72s20s13H",h)
      except:
        raise FTNFail("msg - failed to unpack header of " + file)
      while len(fn) and (fn[-1]==0): fn=fn[:-1]
      while len(tn) and (tn[-1]==0): tn=tn[:-1]
      while len(subj) and (subj[-1]==0): subj=subj[:-1]
      while len(date) and (date[-1]==0): date=date[:-1]

      tpnt=fpnt=tzone=fzone=0 # these fields garbaged with golded

      self.load((fn,(fzone,fnet,fnode,fpnt)),
                (tn,(tzone,tnet,tnode,tpnt)),
                subj,date,attr,cost,f.read())

      self.readcount=readcount
      self.replyto=replyto
      self.nextreply=nextreply

    else:
      pass

  def load(self,src,dst,subj,date,attr,cost,body):
    while len(body) and (body[-1]==0): body=body[:-1]
    text=body.replace(b"\r\n",b"\r").replace(b"\n",b"\r").split(b"\r")
    if len(text) and (text[-1]==b''):
      del text[-1]

    self.body = []
    self.kludge = {}
    self.via = []
    self.path = []
    self.seenby = set()

    (fname,(fzone,fnet,fnode,fpnt)) = src
    (tname,(tzone,tnet,tnode,tpnt)) = dst

    self.area=None
    
    #print '****************', `text[0]`
    if len(text) and (text[0][0:7]==b"\02\0AREA:" or text[0][0:7]==b"\0\0AREA:"):
      #print "echomail"
      self.area=text[0][7:]
      del text[0]
    elif len(text) and (text[0][0:5]==b"AREA:"):
      #print "echomail"
      self.area=text[0][5:]
      del text[0]
      
#    self.area=os.path.split(self.area)[-1]
# ---
      
    for l in text:
      if l and l[0]==1:
        spc=l.find(b" ")
        name = l[1:spc]
        value = l[spc+1:]
        if name.upper()==b"FMPT":
          try: 
            fpnt = int(value)
          except:
            raise FTNFail("MSG: bad FMPT "+repr(value))
        elif name.upper()==b"TOPT":
          try:
            tpnt = int(value)
          except:
            raise FTNFail("MSG: bad TOPT "+value)
        elif name.upper()==b"INTL":
          try:
            to,frm=value.decode("ascii").split(" ")
            tzone,tnet,tnode,xpnt=str2addr(to)
            fzone,fnet,fnode,xpnt=str2addr(frm)
          except:
            raise FTNFail("MSG: bad INTL "+repr(value))
        elif name.upper()==b"VIA" or name.upper()==b"FORWARDED":
          self.via+=[(name,value)]
        elif name.upper()==b"PATH:":
          try:
           self.path.extend(map(
            addr2str, addr_expand(list(filter(bool, value.decode("ascii").split(" "))), (None, None, None, None))))
          except:
            raise FTNFail("MSG: bad PATH "+value)
        else:
          if name in self.kludge:
            if type(self.kludge[name]) is list:
              self.kludge[name]+=[value]
            else:
              self.kludge[name]=[self.kludge[name], value]
          else:
            self.kludge[name]=value
      else:
        self.body += [l]

    while len(self.body) and (self.body[-1][:8] == b"SEEN-BY:"):
      self.seenby.update(addr_expand(list(filter(bool,self.body[-1][9:].decode("ascii").split(" "))),(None,None,None,None)))
      del self.body[-1]

    self.orig=(fname, (fzone,fnet,fnode,fpnt))
    self.dest=(tname, (tzone,tnet,tnode,tpnt))
    self.subj=subj
    self.date=date
    self.attr=attr
    self.cost=cost
    self.readcount=0
    self.replyto=0
    self.nextreply=0

  def make_body(self, invalidate=0):
    if invalidate:
      c=b"@"
      eol=b"\n"
    else:
      c=b"\1"
      eol=b"\r"

    s=b""

    if self.area:
#      s+=b"\x02\x00AREA:"+self.area+eol
      s+=b"AREA:"+self.area+eol

    else:
      if self.orig[1][0]!=0: # zone
        s+=c+b"INTL "+\
          addr2str((self.dest[1][0],self.dest[1][1],self.dest[1][2],None)).encode("ascii")+b" "+\
          addr2str((self.orig[1][0],self.orig[1][1],self.orig[1][2],None)).encode("ascii")+eol

      if self.orig[1][3]!=0: # fmpt
        s+=c+b"FMPT "+str(self.orig[1][3]).encode("ascii")+eol

      if self.dest[1][3]!=0: # topt
        s+=c+b"TOPT "+str(self.dest[1][3]).encode("ascii")+eol

    for k in self.kludge.keys():
      v=self.kludge[k]
      if type(v) is list:
        for x in v:
          s+=c+k+b" "+x+eol
      else:
        s+=c+k+b" "+v+eol
        
    if invalidate:
      s+=(eol.join(self.body)+eol).replace(b"\n---", b"\n-+-").replace(b"\n * Origin", b"\n + Origin")
    else:
      s+=eol.join(self.body)+eol
      

    if invalidate:
      s+=b"".join([b"@"+x[0]+b" "+x[1]+eol for x in self.via])
    else:
      s+=b"".join([b"\1"+x[0]+b" "+x[1]+eol for x in self.via])

    seenbylist=list(self.seenby)
    seenbylist.sort()
    
    if invalidate:
      s+=addr_makelist(list(map(addr2str, seenbylist)), "SEEN+BY:", eol.decode("ascii")).encode("ascii")
    else:
      s+=addr_makelist(list(map(addr2str, seenbylist)), "SEEN-BY:", eol.decode("ascii")).encode("ascii")

    s+=addr_makelist(self.path, c.decode("ascii")+"PATH:", eol.decode("ascii")).encode("ascii")
    return s

  def as_str(self):
    s = b"From: "+self.orig[0]+b", "+addr2str(self.orig[1]).encode("ascii")+b"\n"
    s+= b"To  : "+self.dest[0]+b", "+addr2str(self.dest[1]).encode("ascii")+b"\n"
    s+= b"Subj: "+self.subj+b"\n"
    s+= b"Date: "+self.date+b"\n"
    s+= b"Attr: "+str(self.readcount).encode("ascii")+b" reads " + \
          b" ".join([x[1].encode("ascii") for x in [x for x in zip(list(range(16)),attrs) if self.attr&(1<<x[0])]]) + b"\n"
    s+= b"\n" + self.make_body(invalidate=1)
    return s

  def pack(self):
    faddr=self.orig[1]
    taddr=self.dest[1]
    return struct.pack("<36s36s72s20s13H",self.orig[0],self.dest[0],self.subj,
      self.date, self.readcount, taddr[2], faddr[2], self.cost, faddr[1],
      taddr[1], taddr[0], faddr[0] ,taddr[3], faddr[3], self.replyto, 
      self.attr, self.nextreply)+self.make_body()

  def add_seenby(self, a):
    addr=str2addr(a)
    self.seenby.add((None,addr[1],addr[2],None))

  def add_path(self, a):
    addr=str2addr(a)
    self.path.append(addr2str((None,addr[1],addr[2],None)))

ORIGIN=re.compile(b" \* Origin:(.*)\((.* )?(\d+\:\d+/\d+(\.\d+)?(\@.*)?)\)$")

def decode_origin(s):
  m=ORIGIN.match(s)
  if m:
    return m.group(3)
  else:
    raise DecodeError("Invalid origin %s"%repr(s))


if __name__ == "__main__":
#  x=MSG("1.msg")
#  open("x.msg","wb").write(`x`)
#  print x
  origins = [
" * Origin: test1 (2:5020/12000)",
" * Origin: test2 (2:5020/12000.1)",
" * Origin: test3 (text 2:5020/12000.1)",
" * Origin: test4 (shitty text 2:5020/12000.1)",
" * Origin: test5 (shitty text 2:5020*12000.1)",
" * Origin: test6 (WTF)"
]
  for o1 in origins:
    print(o1)
    try:
      print(decode_origin(o1))
    except:
      traceback.print_exc()
