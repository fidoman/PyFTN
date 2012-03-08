#!/usr/local/bin/python3

link = '2:5020/758'
list = 'lists/ech00758.lst'
orphans = 'upl'
domain = 'echo'
oldlink = None #'2:5020/758'

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
if oldlink: pwold = ftnconfig.get_link_password(db, oldlink, forrobots=True)


avail = set()
for l in open(list):
  avail.add(l.strip())

orphan = set()
for l in open(orphans):
  orphan.add(l.strip())

print (len(orphan), len(avail), len(orphan.intersection(avail)))

with ftnimport.session(db) as sess:

  subs=[]
  unsubs=[]
  for area in orphan.intersection(avail):
    print (area)
    if oldlink: sess.remove_subscription(domain, area, oldlink)
    sess.add_subscription(True, domain, area, link)
    subs.append("+"+area+"\n")
    unsubs.append("-"+area+"\n")

  sess.send_message(ftnconfig.SYSOP, ("node", link), robot, None, pw, "".join(subs))
  if oldlink: sess.send_message(ftnconfig.SYSOP, ("node", oldlink), robot, None, pwold, "".join(unsubs))
