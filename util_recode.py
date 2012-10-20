#!/usr/local/bin/python3 -bb

import ftnconfig

db=ftnconfig.connectdb()

MID=1262410
newc="cp850"

h,b,c=db.prepare("select header, body, origcharset from messages where id=$1").first(MID)

print(c)
h.find("sendername").text   = h.find("sendername").text.encode(c).decode(newc)
h.find("recipientname").text= h.find("recipientname").text.encode(c).decode(newc)
h.find("subject").text      = h.find("subject").text.encode(c).decode(newc)
b                           = b.encode(c).decode(newc)

print (b)

db.prepare("update messages set (header, body, origcharset) = ($2, $3) where id=$1")(MID, h, b, news)
