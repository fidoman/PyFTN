#!/usr/bin/python3

import ftnconfig
import time

db=ftnconfig.connectdb()

counts = {}
safecount= 0
safelimit=15000
safedelay=20

def get_duplicate_addresses():
  q=db.prepare("select domain, text, array_agg(id) from addresses group by (domain, text) having count(*)>1")
  for d, t, ids in q():
    ids=list(ids)
    ids.sort()
    good_id=ids[0]
    bad_ids=ids[1:]
    print(d,t,good_id,bad_ids)
    for bad_id in bad_ids:
      print("renumber", bad_id, "after", good_id)
      renumber_dest(good_id, bad_id)
      print("replace dest",bad_id, "with", good_id, "in messages")
      print(db.prepare("update messages set id=DEFAULT, destination=$1 where destination=$2")(good_id, bad_id))
      print("replace dest",bad_id, "with", good_id, "in subscriptions")
      for s_id, s_s in db.prepare("select id, subscriber from subscriptions where target=$1")(bad_id):
        print(s_s,"subscribed to bad", bad_id)
        if len(db.prepare("select id, subscriber from subscriptions where subscriber=$1 and target=$2")(s_s, good_id))>0:
          print(s_s, "already subscribed to", good_id)
          print(db.prepare("delete from subscriptions where id=$1")(s_id))
        else:
          print(db.prepare("update subscriptions set target=$1 where target=$2")(good_id, bad_id))

      print("delete", bad_id)
      exit()
      print(db.prepare("delete from addresses where id=$1")(bad_id))
      exit()



# renumber NEW as continue of OLD

def get_last_numberfordestination_of(dest_id):
  return db.prepare("select max(numberfordestination) from messages where destination=$1").first(dest_id)


def renumber_dest(OLD,NEW):
  """ OLD - good valid id
      NEW - id to merge """

  if OLD>=NEW:
    print("go fuck yourself")
    exit(1)

  print("start from:", get_last_numberfordestination_of(OLD))

  number_from=get_last_numberfordestination_of(OLD)+1

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

get_duplicate_addresses()
exit()

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
