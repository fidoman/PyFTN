#!/bin/env python3

# connect to daemon and push incoming file
# connect to daemon and get outbound

import socket

from socketutil import *

s = socket.socket(socket.AF_INET)

s.connect(("127.0.0.1", 24555))
try:
  print(readline(s))

  s.send(b"ADDRESS 2:5020/12000.1\n")
  s.send(b"PASSWORD ABNM\n")

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
    print(repr(l))
    if l.startswith("FILENAME"):
      fn=l[9:]
      print(l)
      f=open("test/"+fn, "wb")
    elif l.startswith("BINARY"):
      fl=int(l[7:])
      for d in readdata(s, fl):
        f.write(d)
      f.close()
      s.send(("DONE "+fn+"\n").encode("utf-8"))

    elif l=="QUEUE EMPTY":
      break
    else:
      print(l)

  s.send(b"END SESSION\n")

finally:
  s.close()
