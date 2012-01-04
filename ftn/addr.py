#!/usr/bin/python

import re
from .ftn import FTNFail

def str2addr( s, addr=(None,None,None,0) ):
  """ String to separate numbers
   .1, 12000.1, 5020/12000.1, 2:5020/12000.1 - point address
   12000, 5020/12000, 2:5020/12000 - node address
   5020/, 2:5020, 2:5020/ - net address
   2: - zone address
  """
  zone,net,node,point=addr

  uho=s.find("@")
  if uho!=-1:
    s=s[:uho]

  x=re.match("^\.(\d+)$",s)
  if x: return zone, net, node, int(x.group(1))
  x=re.match("^(\d+)\.(\d+)$",s)
  if x: return zone, net, int(x.group(1)), int(x.group(2))
  x=re.match("^(\d+)\/(\d+)\.(\d+)$",s)
  if x: return zone, int(x.group(1)), int(x.group(2)), int(x.group(3))
  x=re.match("^(\d+)\:(\d+)\/(\d+)\.(\d+)$",s)
  if x: return int(x.group(1)), int(x.group(2)), int(x.group(3)), int(x.group(4))
  x=re.match("^(\d+)$",s)
  if x: return zone, net, int(x.group(1)), point
  x=re.match("^(\d+)\/(\d+)$",s)
  if x: return zone, int(x.group(1)), int(x.group(2)), point
  x=re.match("^(\d+)\:(\d+)\/(\d+)$",s)
  if x: return int(x.group(1)), int(x.group(2)), int(x.group(3)), point
  x=re.match("^(\d+)\/$",s)
  if x: return zone, int(x.group(1)), node, point
  x=re.match("^(\d+)\:(\d+)\/?$",s)
  if x: return int(x.group(1)), int(x.group(2)), node, point
  x=re.match("^(\d+)\:$",s)
  if x: return int(x.group(1)), net, node, point
  raise FTNFail("invalid FTN address '%s'"%s)



def addr2str(addr=(None,None,None,None)):
  zone,net,node,point=addr
  s=""
  if not (zone is None):
    s+=str(zone)+":"
  if not (net is None):
    s+=str(net)+"/"
  if not (node is None):
    s+=str(node)
  if not (point is None) and point!=0:
    s+="."+str(point)
  return s

def addr_expand(l, defaddr):
  r=[]
  for a in l:
    #print "expanding", a
    defaddr=str2addr(a,(defaddr[0],defaddr[1],defaddr[2],0))
    #print defaddr
    r+=[defaddr]
  #print r
  return r

def addr_dif(a, def_a):
  stop=0
  r=[None,None,None,None]
  for i in [0,1,2,3]:
    if( a[i]!=def_a[i] or stop ):
      stop=1
      r[i]=a[i]
  return tuple(r)

def addr_shrink(l):
  r=[]
  paddr=(None,None,None,None)
  for a in l:
    addr=str2addr(a)
    r+=[addr2str(addr_dif(addr,paddr))]
    paddr=addr

  return r

def addr_makelist(l, prefix, eol="\r", defknown=(None,None,None,None), maxlen=78):
  if len(l)==0:
    return ""
  s=""
  ss=defss=prefix
  known=defknown
  for a in l:
    a_current=str2addr(a)
    a_shrinked=addr_dif(a_current,known)
    a_str=addr2str(a_shrinked)
    if( len(ss)+len(a_str)>78 ):
      s+=ss+eol
      known=defknown
      ss=defss+" "+addr2str(addr_dif(a_current,known))
    else:
      ss+=" "+a_str
    known=a_current
  return s+ss+eol

def addr_cmp(x,y):
  for i in [0,1,2,3]:
    if x[i]<y[i]:
      return -1
    if x[i]>y[i]:
      return 1
  return 0

if __name__ == "__main__":
  for a in ".1 12000.1 5020/12000.1 2:5020/12000.1 12000 5020/12000 2:5020/12000 5020/ 2:5020 2:5020/ 2:".split():
    b=str2addr(a)
    c=addr2str(b)
    print(a, b, c)
