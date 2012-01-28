#!/bin/env python3 -bb

""" listen for incoming connection:
    processes received files 
    and generates outbound files on request

    Initialization:
    ADDRESS address
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

from ftnconfig import *
from ftnimport import file_import
from ftnexport import file_export

from socketutil import *

def session(s, a):
  address = None
  password = None
  filename = None
  length = None
  try:
    s.send(b"hi "+str(a).encode("utf-8")+b"\n")
    while True:
      l=readline(s).decode("utf-8").rstrip()
      print("got '%s'"%repr(l))
      arg, val = l.split(" ", 1)
      print(arg, val)
      if arg=="ADDRESS":
        if address:
          raise Exception("address already established")
        address = val
      elif arg=="PASSWORD":
        if password:
          raise Exception("password already established")
        if address is None:
          raise Exception("password without address")
        password = val
      elif arg=="FILENAME":
        if filename:
          raise Exception("filename already established")
        if not address:
          raise Exception("filename without address")
        filename = val
      elif arg=="BINARY":
        if not filename:
          raise Exception("binary data without filename")
        length = int(val)
        print("should receive %d bytes of file %s from address %s password %s"%(length, filename, address, password))

        with file_import(db, address, password, filename, length) as sess:
          for data in readdata(s, length):
            sess.add_data(data)

        s.send(b"DONE\n")
        filename = None

      elif arg=="END":
        print("session end "+val)
        break

      elif arg=="GET":
        if password is None:
          raise Exception("may not send data on unprotected incoming sessions")

        classesstr = val.lower().split(",")
        classes = set()
        allclasses = set(("netmail", "echomail", "fileecho", "filebox"))
        if ["all"]==classesstr:
          classes = allclasses
        else:
          for classstr in classesstr:
            if classstr in allclasses:
              classes.add(classstr)
            else:
              raise Excption("invalid mail class")
        print("sending "+", ".join(list(classes)))

        for outbfile, committer in file_export(db, address, password, classes):
          print(outbfile.filename)
          s.send(b"FILENAME " + outbfile.filename.encode("utf-8") + b"\n")
          s.send(b"BINARY " + str(outbfile.length).encode("utf-8") + b"\n")

          while True:
            d = outbfile.data.read(16384)
            if len(d)==0:
              break
            print(s.send(d))

          confirmstr = readline(s)
          print("RECV: "+repr(confirmstr))
          print("SHOULD: "+repr(b"DONE " + outbfile.filename.encode("utf-8")))
          if confirmstr != b"DONE " + outbfile.filename.encode("utf-8"):
            raise Exception("did not get good confirmation string")

          committer.commit()

        print("that's all")
        s.send(b"QUEUE EMPTY\n")

      else:
        raise Exception("unknown keyword %s"%arg)

  finally:
    print("end "+str(a))
    s.close()


sockets=[]

for af, addr in DAEMONBIND:
  sockets.append((socket.socket(af), addr))

for s, a in sockets:
  s.bind(a)
  s.listen(3)

#threads = []

try:
  while True:
    (incoming_connections, _, _) = select.select([x[0] for x in sockets], [], [])
    for ic in incoming_connections:
      ls, peer = ic.accept()
      print(ls, peer)
      t=threading.Thread(target=session, args=(ls,peer))
      #threads.append(t)
      t.start()
finally:
  for s, a in sockets:
    print("closing "+str(a))
    s.close()
  print("process will terminate after all threads finished")
  print("if after finish OS reports that already in use try just to telnet to all daemon's listened ports and wait")
