#!/usr/local/bin/python3 -bb

import os
import re
import ftn.msg
import ftnimport
import ftnconfig

db=ftnconfig.connectdb()

def set_status(echostatus, e, s):
  if e in echostatus:
    raise Exception("duplicate echo")
  echostatus[e] = s



def process_4441():

  basedir="areafix/4441"
  UPLINK="2:5020/4441"

  RE_subscribed=re.compile("Эха (\S+) подписана")
  RE_alreadysubscribed=re.compile("Вы уже подписаны на (\S+)")
  RE_notfound=re.compile("Эха (\S+) не найдена")

  echostatus={}

  for mfile in os.listdir(basedir):
    m=ftn.msg.MSG(os.path.join(basedir,mfile))
    orig, dest, msgid, header, body, charset = ftnimport.normalize_message(m)
    print(orig, dest, msgid)
    if orig!=("node", UPLINK):
      continue

  #  print(repr(header.find("subject").text))
    lines = body.split("\n")
    for l in lines:
      if len(l)==0 or l[0]==">":
        continue
      m=RE_subscribed.match(l)
      if m:
          set_status(echostatus, m.group(1), "ok")
          continue
      m=RE_alreadysubscribed.match(l)
      if m:
          set_status(echostatus, m.group(1), "ok")
          continue
      m=RE_notfound.match(l)
      if m:
          set_status(echostatus, m.group(1), "absent")
          continue
      raise Exception("unrecognized: %s"%l)

  return echostatus


def process_758():

  basedir="areafix/758"
  UPLINK="2:5020/758"

  RE_subscribed=re.compile("(\S+) \.* Linked")
  RE_alreadysubscribed=re.compile("Area (\S+) is already linked")
  RE_notfound=re.compile("Area (\S+) doesn't exist")

  echostatus={}

  for mfile in os.listdir(basedir):
    m=ftn.msg.MSG(os.path.join(basedir,mfile))
    orig, dest, msgid, header, body, charset = ftnimport.normalize_message(m)
    print(orig, dest, msgid)
    if orig!=("node", UPLINK):
      continue

  #  print(repr(header.find("subject").text))
    lines = body.split("\n")
    for l in lines:
      if len(l)==0 or l[0]==">":
        continue
      m=RE_subscribed.match(l)
      if m:
          set_status(echostatus, m.group(1), "ok")
          continue
      m=RE_alreadysubscribed.match(l)
      if m:
          set_status(echostatus, m.group(1), "ok")
          continue
      m=RE_notfound.match(l)
      if m:
          set_status(echostatus, m.group(1), "absent")
          continue
    
      #raise Exception("unrecognized: %s"%l)

  return echostatus


# ---

process = [
("2:5020/758", process_758),
#("2:5020/4441", process_4441),
]

for link, func in process:

  with ftnimport.session(db) as sess:
    for k, v in func().items():
      if v=="absent":
          print (k)
          sess.remove_subscription("echo", k, link)
