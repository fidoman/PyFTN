#!/usr/local/bin/python3 -bb

import ftnconfig

db=ftnconfig.connectdb()

MID=1607849
newc="cp437"

h,b,c=db.prepare("select header, body, origcharset from messages where id=$1").first(MID)

#print(c)
#print(repr(b.encode("koi8-r")))
#print(b.encode("koi8-r").decode("utf-8", "ignore"))
#exit()

h.find("sendername").text   = h.find("sendername").text.encode(c).decode(newc)
h.find("recipientname").text= h.find("recipientname").text.encode(c).decode(newc)
h.find("subject").text      = h.find("subject").text.encode(c).decode(newc)
b                           = b.encode(c).decode(newc)

print(c)
print(h.find("sendername").text)
print(h.find("recipientname").text)
print(h.find("subject").text)
print (b)

input("Ctrl-C to cancel or Enter to update")

db.prepare("update messages set (header, body, origcharset) = ($2, $3, $4) where id=$1")(MID, h, b, newc)
