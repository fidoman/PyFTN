#!/usr/local/bin/python3 -bb

from ftnconfig import connectdb, get_link_password

db=connectdb()

fareas={}

for a, b in db.prepare("select t.text, sr.text from subscriptions s, addresses sr, addresses t "
            "where s.subscriber=sr.id and s.target=t.id and t.domain=3")():
  fareas.setdefault(a, set()).add(b)

fa=open("/tank/home/fido/fareas.bbs", "w")
fa.write("*****\n")
for k, v in fareas.items():
  fa.write("/tank/home/fido/fareas/"+k.lower()+" "+k+" "+" ".join(v)+"\n")
fa.close()

pw=open("/tank/home/fido/passwd", "w")
for a in db.prepare("select a.text from links l, addresses a "
            "where l.address=a.id and a.domain=$1 order by a.text")(db.FTN_domains["node"]):
  #print (a[0])
  pw.write("password %-23s %s\n"%(a[0], get_link_password(db, a[0])))
pw.close()