#!/usr/bin/python3 -bb

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

logname, logext = os.path.splitext(sys.argv[1])

logfile = open(logname+logext, "a")

sys.stdout = logfile

def log(s):
  logfile.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + ": " + 
                str(s).replace("\n", " + ") + "\n")
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
    os.system("~/unpack quick >> ~/log/quick.log")
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
  db = None
  try:
    db = connectdb()
    log(str(a)+" connected to database from %s:%d"%(db.client_address, db.client_port))
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
        # if no password sent and link does not have password, export only direct netmail
        #  - arranged in ftnexport
        classesstr = val.lower().split(",")
        classes = set()
        allclasses = set(("netmail", "echomail", "fileecho", "filebox", "direct"))
#        allclasses = set(("echomail", "fileecho", "filebox", "direct"))
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
              if outbfile is not None:
                log(str(a)+" outbound file "+outbfile.filename)
                s.send(b"FILENAME " + outbfile.filename.encode("utf-8") + b"\n")
                s.send(b"BINARY " + str(outbfile.length).encode("utf-8") + b"\n")

                while True:
                  d = outbfile.data.read(16384)
                  if len(d)==0:
                    break
                  log(str(a)+" %d"%s.send(d))

                confirmstr = readline(s).rstrip(b"\r")
                log(str(a)+" RECV: "+repr(confirmstr))
                log(str(a)+ " SHOULD: "+repr(b"DONE " + outbfile.filename.encode("utf-8")))
                if confirmstr != b"DONE " + outbfile.filename.encode("utf-8"):
                  raise Exception("did not get good confirmation string")

                log(str(a)+" CONFIRMED")
              else:
                log(str(a)+" None file passed, just committing")

              committer.commit()


          except FTNWrongPassword:
            log(str(a)+"address %s excluded due to wrong password"%address)
          except:
            log(str(a)+" exception in GET on address %s: %s"%(address, traceback.format_exc()))

        # "QUEUE EMPTY" must be sent only after all addresses are processed
        log(str(a)+" that's all")
        s.send(b"QUEUE EMPTY\n")

      else:
        raise Exception("unknown keyword %s"%arg)


  except Exception:
    log(str(a)+"\nexception\n"+traceback.format_exc())

  finally:
    log(str(a)+" end")
    s.close()
    if db:
      db.close()
      log(str(a)+" connection from %s:%d is closed: %s "% \
            (db.client_address, db.client_port, str(db.closed)))
    else:
      log(str(a)+" not database connection")


sockets=[]

for af, addr, proto in DAEMONBIND:
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
