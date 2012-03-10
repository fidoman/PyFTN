#!/usr/local/bin/python3

link = '2:5020/1042'
list = 'lists/GFD.txt'
orphans = list #'upl'
domain = 'fileecho'
oldlink = ['2:5020/758', '2:5020/1200']

robotname = ftnconfig.robotnames[domain]

import ftnconfig
import ftnimport

db=ftnconfig.connectdb()
pw = ftnconfig.get_link_password(db, link, forrobots=True)

pwold = {}
for ol in oldlink: 
  pwold[ol] = ftnconfig.get_link_password(db, ol, forrobots=True)


avail = set()
for l in open(list):
  avail.add(l.strip().upper())

orphan = set()
for l in open(orphans):
  orphan.add(l.strip().upper())

print (len(orphan), len(avail), len(orphan.intersection(avail)))

with ftnimport.session(db) as sess:

  subs=[]
  unsubs=[]
  for area in orphan.intersection(avail):
    print (area)
    sess.check_addr(domain, area)
    for ol in oldlink: 
      sess.remove_subscription(domain, area, ol)
    sess.add_subscription(True, domain, area, link)
    subs.append("+"+area+"\n")
    unsubs.append("-"+area+"\n")

  sess.send_message(ftnconfig.SYSOP, ("node", link), robot, None, pw, "".join(subs))
  for ol in oldlink: 
    sess.send_message(ftnconfig.SYSOP, ("node", ol), robot, None, pwold[ol], "".join(unsubs))
