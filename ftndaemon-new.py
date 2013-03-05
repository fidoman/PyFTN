#!/usr/local/bin/python3 -bb

""" listen for incoming connection:
    processes received files 
    and generates outbound files on request

    Initialization:
    ADDRESS address
    ADDRESS address2
    ...
    PASSWORD password

    Outbound:
    on session mailer establishes connection to daemon and send request:
    > GET NETMAIL
    > GET ECHOMAIL
    > GET FILES
    > GET ALL

    daemon answers
    < QUEUE estimated_size
    < FILENAME filename
    < LENGTH length
    < binary file content
    mailer sends after file is sent to remote:
    > DONE filename
    demons commits exported file
    then daemon starts new file or sends:
    < QUEUE EMPTY

    Inbound:
    > FILENAME filename
    > BINARY length
    > (data)
    < DONE
    then repeat or close connection if done or go to outbound processing


"""

import socket
import select
import threading
import traceback
import sys
import time
import os
import importlib

import ftnconfig

logfile = open(ftnconfig.DAEMONLOG, "a")

sys.stdout = logfile

def log(s):
  logfile.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + ": " + 
                str(s).replace("\n", " + ") + "\n")
  logfile.flush()



log("start")

sockets=[]

for af, addr, proto in ftnconfig.DAEMONBIND:
  sockets.append((socket.socket(af), addr, proto))

for s, a, proto in sockets:
  ok = False
  while not ok:
    try:
      s.bind(a)
      s.listen(3)
      log("socket "+str(s)+" listen on "+str(a))
      ok = True
    except:
      log(traceback.format_exc())
      time.sleep(5)

#threads = []

modules = {}

def start_answer(proto, args):
  if proto not in modules:
    modules[proto] = importlib.import_module("daemon."+proto)

  t=threading.Thread(target = modules[proto].session, args=args)
  #threads.append(t)
  t.start()

try:
  while True:
    (incoming_connections, _, _) = select.select([x[0] for x in sockets], [], [])
    for ic in incoming_connections:
      ls, peer = ic.accept()
      log("socket %s peer %s on %s"%(str(ls), str(peer), str(ic)))
      for x in sockets:
        if x[0]==ic:
          log("protocol=%s"%x[2])
          start_answer(x[2], (log,ls,peer))
          break
      else:
        log("socket's protocol not found, it is very strange")
        ls.close()
finally:
  for s, a, _ in sockets:
    log("closing "+str(a))
    s.close()
  log("process will terminate after all threads finished")

log("end")
