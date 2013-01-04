#!/usr/local/bin/python3 -bb

import ftn.addr
import ftn.msg
import ftn.pkt

msgfrom=(b"Point", "2:5020/12000.1")
msgto=(b"AreaFix", "2:5020/12000")
msgsubj=b"********"
msgdate=b"04 Jan 13  14:19:00"
msgattr=0
msgcost=0
msgbody=b"""%QUERY
"""

outmsg="test.msg"

m=ftn.msg.MSG()
m.load((msgfrom[0],ftn.addr.str2addr(msgfrom[1])),
       (msgto[0],  ftn.addr.str2addr(msgto[1]  )),
        msgsubj,msgdate,msgattr,msgcost,msgbody)

if outmsg:
  f=open(outmsg, "wb")
  f.write(m.pack())
  f.close()

p=ftn.pkt.PKT()
