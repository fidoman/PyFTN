#!/usr/local/bin/python3

link = '2:5020/4441'
list = 'lists/ech04441.lst'
orphans = 'stat_upl'
domain = 'echo'

if domain=="echo":
  robot = "AreaFix"
elif domain=="fileecho":
  robot = "FileFix"
else:
  raise Exception("cannot manage subscriptions in domain", domain)



import ftnconfig
import ftnimport

db=ftnconfig.connectdb()
pw = ftnconfig.get_link_password(db, link, forrobots=True)


avail = set()
for l in open(list):
  avail.add(l.strip())

orphan = set()
for l in open(orphans):
  orphan.add(l.strip())

print (len(orphan), len(avail), len(orphan.intersection(avail)))

with ftnimport.session(db) as sess:
  for area in orphan.intersection(avail):
    print (area)
    sess.add_subscription(True, domain, area, link)
    #sess.remove_watermark(domain, area, subscriber)
    sess.send_message(ftnconfig.SYSOP, ("node", link), robot, None, pw, "+"+area)
