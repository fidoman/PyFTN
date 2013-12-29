#!/usr/local/bin/python3 -bb

LOG="/tank/home/fido/tic.log"
OLDLOG="/tank/home/fido/tic.log.old"

import re
import os
import ftnconfig
import ftnimport

spc=re.compile("\s+")

if not os.path.exists(LOG):
    exit()

byarea={}

lines=[]
for l in open(LOG, encoding="cp866"): # data from tics is copied as is though it is bad way
    lines.append(l)
    a=list(map(str.strip, spc.split(l)))
    date=a[0]
    time=a[1]
    a=a[2:]
    src=None
    file=None
    area=None
    while len(a):
        if a[0]=="from":
            src=a[1]
        elif a[0]=="file":
            file=a[1]
        elif a[0]=="area":
            area=a[1]
        a=a[2:]
    byarea.setdefault(area, []).append((file, src))


areas=list(byarea.keys())
areas.sort()

outp = []

for area in areas:
#  outp.append ("AREA: "+ area+"\n")
  for file, src in byarea[area]:
    outp.append ("%-20s %-32s %-23s\n"%(area, file, src))
  outp.append("\n")

db=ftnconfig.connectdb()

with ftnimport.session(db) as sess:
  sess.send_message("Sergey Dorofeev", ("echo", "FLUID.REPORTS"), "All", None, "файлэхи",
"""
%s
"""%("".join(outp)))

fo=open(OLDLOG, "a")
for l in lines:
    fo.write(l)
fo.close
os.unlink(LOG)


#2012-02-21 08:30:12 from 2:5020/1200 file PNT5025.ZIP area PNTLIST replaces PNT5025.ZIP


