#!/usr/bin/python3

import ftnconfig
import time

db=ftnconfig.connectdb()

counts = {}
safecount= 0
safelimit=15000
safedelay=20

OLD=17240
NEW=18022

if OLD>=NEW:
  print("go fuck yourself")
  exit(1)
# renumber NEW as continue of OLD

def get_last_numberfordestination_of(dest_id):
  return db.prepare("select max(numberfordestination) from messages where destination=$1").first(dest_id)

print("start from:", get_last_numberfordestination_of(OLD))

number_from=get_last_numberfordestination_of(OLD)+1

if True:

  dest_to_renumber=NEW

  xact=db.xact()
  xact.start()
  for mid, mdest, mnum in db.prepare("select id, destination, numberfordestination from messages where destination=$1 order by id")(dest_to_renumber):
    ordernum = number_from
    if mnum>ordernum:
      ordernum=mnum

    number_from = ordernum + 1
    if mnum != ordernum:
      print ("update message %d (to %d) change numberfordestination %d->%d"%(mid, mdest, mnum, ordernum))
      db.prepare("update messages set numberfordestination=$2 where id=$1")(mid, ordernum)
#      safecount+=1
  xact.commit()


exit()

#echo = 'PUSHKIN.LOCAL'
#dest = db.prepare("select id from addresses where domain=$1 and text=$2").first(db.FTN_domains["echo"], echo)


for dest, destname in db.prepare("select id, text from addresses where domain=$1")(db.FTN_domains["echo"]):
  prv=time.mktime(time.gmtime())
  print (destname)

  xact=db.xact()
  xact.start()
  for mid, mdest, mnum in db.prepare("select id, destination, numberfordestination from messages where destination=$1 order by id")(dest):
    ordernum = counts.get(mdest, 0) + 1
    counts[mdest] = ordernum
    if mnum != ordernum:
      print ("update message %d (to %d) set num=%d"%(mid, mdest, ordernum))
      db.prepare("update messages set numberfordestination=$2 where id=$1")(mid, ordernum)
      safecount+=1
  xact.commit()

  current=time.mktime(time.gmtime())
  print ("time=%d"%(current-prv))
  prv=current

  if safecount>safelimit:
    print("relax...")
    time.sleep(safedelay)
    safecount=0
