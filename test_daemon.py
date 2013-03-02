#!/bin/env python3

# connect to daemon and push incoming file
# connect to daemon and get outbound

address = "1:123/500"
encoding = "utf-8"


import socket
import os

from socketutil import *

try:
  os.mkdir("test")
except:
  pass

if not os.path.isdir("test"):
  print ("please make dir test")
  exit()

s = socket.socket(socket.AF_INET)

import ftnconfig
db=ftnconfig.connectdb()
password = ftnconfig.get_link_password(db, address)
print (address, password)

do_send = False

s.connect(("127.0.0.1", 24555))
try:
  print(readline(s))

  s.send(b"ADDRESS "+address.encode(encoding)+b"\n")
  s.send(b"PASSWORD "+password.encode(encoding)+b"\n")

  if do_send:
    s.send(b"FILENAME test1.dat\n")
    s.send(b"BINARY 100\n")
    s.send(b"*"*100)
    print(readline(s))

    s.send(b"FILENAME test2.dat\n")
    s.send(b"BINARY 300\n")
    s.send(b"*"*300)
    print(readline(s))

  s.send(b"GET ALL\n")
  while True:
    l = readline(s).decode("utf-8")
    print("recv:",repr(l))
    if l.startswith("FILENAME"):
      fn=l[9:]
      print("filename:",fn)
      f=open("test/"+fn, "wb")
    elif l.startswith("BINARY"):
      fl=int(l[7:])
      print("length:",fl)
      for d in readdata(s, fl):
        f.write(d)
      f.close()
      input("commit - if you do it, messages will be marked as send (Ctrl-C to abort)")
      s.send(("DONE "+fn+"\n").encode("utf-8"))

    elif l=="QUEUE EMPTY":
      print ("queue empty")
      break
    else:
      print("unknown sentence")

  s.send(b"END SESSION\n")

finally:
  s.close()
