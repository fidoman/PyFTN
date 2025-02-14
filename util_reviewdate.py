#!/usr/local/bin/python3 -bb

import ftnconfig

db=ftnconfig.connectdb()

for mid in db.prepare("select id from messages where id>100 and id<=110 order by id"):
  mid = mid[0]
  header = db.prepare("select header from messages where id=$1").first(mid)

  ftn=header.find("FTN")
  date=header.find("date")
  tz=None
  for kl in ftn.findall("KLUDGE"):
    kln=kl.get("name")
    if kln=="TZUTC:":
      if tz:
        print ("TZ dup")
        exit()
      tz=kl.get("value")
  print ("%10d   [%s] %s"%(mid, tz, date.text))
