#!/bin/env python3 -bb

""" listen for incoming connection:
    processes received files 
    and generates outbound files on request

    Outbound:
    on session mailer establishes connection to daemon and send request:
    GET NETMAIL FOR address
    GET ECHOMAIL FOR address
    GET FILES FOR address
    GET ALL FOR address
    daemon answers
    QUEUE EMPTY
    if there is no outbound
    or
    FILE filename LENGTH length
    then sends binary file content
    after receiving file mailer transfers it and sends
    OK
    then demons commits export and sends next file or signals that queue empty
    if no OK is received exported data is not get removed
    from database and will be sent again

    Inbound:
    > FILE file FROM address LENGTH length
    > (data)
    < OK
    then repeat or close connection if done or go to outbound processing
"""

import socket
import select
import threading

from ftnconfig import *

def readline(s):
  l=b""
  while True:
    c=s.recv(1)
    if c==b"\n":
      break
    l+=c
  return l

def session(s, a):
  s.send(b"hi "+str(a).encode("utf-8")+b"\n")
  print(readline(s).decode("utf-8"))
  s.close()

sockets=[]

for af, addr in DAEMONBIND:
  sockets.append((socket.socket(af), addr))

for s, a in sockets:
  s.bind(a)
  s.listen(3)

threads = []

while True:
  (incoming_connections, _, _) = select.select([x[0] for x in sockets], [], [])
  for ic in incoming_connections:
    ls, peer = ic.accept()
    print(ls, peer)
    t=threading.Thread(target=session, args=(ls,peer))
    threads.append(t)
    t.start()
