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

logfile = open(sys.argv[1], "ab")

def log(s):
  logfile.write((time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + ": " + 
                str(s).replace("\n", " + ") + "\n").encode("utf-8"))
  logfile.flush()


L_unpack = threading.Lock()

def rununpack():
  global L_unpack

  log("rununpack")
  is_free = L_unpack.acquire(False)
  if not is_free: 
    log("waiting another process")
    L_unpack.acquire()

  if is_free:
    log("start to unpack")
    os.system("./unpack quick >> log/quick.log")
  else:
    log("already unpacked")

  L_unpack.release()

log("start")


from ftnconfig import *
from ftnimport import file_import
from ftnexport import file_export
from ftn.ftn import FTNWrongPassword

from socketutil import *

def session(s, a):
  try:
    db = connectdb()
    addresses = []
    password = None
    filename = None
    length = None
    s.send(b"hi "+str(a).encode("utf-8")+b"\n")
    while True:
      l=readline(s).decode("utf-8")
      while l[-1] in ("\n", "\r"):
        l = l[:-1]

      log(str(a)+" got %s"%repr(l))
      arg, val = l.split(" ", 1)
      #log(arg+" is "+val)
      if arg=="ADDRESS":
        if password:
          raise Exception("password already established")
        #log(str(a)+" ADDRESS "+val)
        addresses.append(val)
      elif arg=="PASSWORD":
        if password:
          raise Exception("password already established")
        if len(addresses) == 0:
          raise Exception("password without address")
        #log("PASSWORD "+val)
        password = val
      elif arg=="FILENAME":
        if filename:
          raise Exception("filename already established")
        if not address:
          raise Exception("filename without address")
        #log("FILENAME "+val)
        filename = val
      elif arg=="BINARY":
        if not filename:
          raise Exception("binary data without filename")
        length = int(val)
        log(str(a)+" receive %d bytes of file %s from address %s password %s"%(length, filename, address[0], password))

        with file_import(db, address[0], password, filename, length) as sess:
          for data in readdata(s, length):
            sess.add_data(data)

        s.send(b"DONE\n")
        filename = None

      elif arg=="END":
        log(str(a)+" session end "+val)
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

        rununpack()

        log(str(a)+" sending "+", ".join(list(classes)))

        for address in addresses:
         try:
          log(str(a)+" export for address "+address)

          for outbfile, committer in file_export(db, address, password, classes):
            log(str(a)+" outbound file "+outbfile.filename)
            s.send(b"FILENAME " + outbfile.filename.encode("utf-8") + b"\n")
            s.send(b"BINARY " + str(outbfile.length).encode("utf-8") + b"\n")

            while True:
              d = outbfile.data.read(16384)
              if len(d)==0:
                break
              log(str(a)+" %d"%s.send(d))

            confirmstr = readline(s)
            log(str(a)+" RECV: "+repr(confirmstr))
            log(str(a)+ " SHOULD: "+repr(b"DONE " + outbfile.filename.encode("utf-8")))
            if confirmstr != b"DONE " + outbfile.filename.encode("utf-8"):
              raise Exception("did not get good confirmation string")

            log(str(a)+" CONFIRMED")
            committer.commit()

         except FTNWrongPassword:
            log("address %s excluded due to wrong password"%address)
         except:
            log(str(a)+" exception on addess %s: %s"%(address, traceback.format_exc()))

        log(str(a)+" that's all")
        s.send(b"QUEUE EMPTY\n")

      else:
        raise Exception("unknown keyword %s"%arg)

  except Exception:
    log(str(a)+"\nexception\n"+traceback.format_exc())

  finally:
    log(str(a)+" end")
    s.close()


sockets=[]

for af, addr in DAEMONBIND:
  sockets.append((socket.socket(af), addr))

for s, a in sockets:
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

try:
  while True:
    (incoming_connections, _, _) = select.select([x[0] for x in sockets], [], [])
    for ic in incoming_connections:
      ls, peer = ic.accept()
      log("socket %s peer %s"%(str(ls), str(peer)))
      t=threading.Thread(target=session, args=(ls,peer))
      #threads.append(t)
      t.start()
finally:
  for s, a in sockets:
    log("closing "+str(a))
    s.close()
  log("process will terminate after all threads finished")
