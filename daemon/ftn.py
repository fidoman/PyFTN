import threading
import traceback

from socketutil import *
from ftnconfig import connectdb
from ftnimport import file_import
from ftnexport import file_export
from ftn.ftn import FTNWrongPassword

L_unpack = threading.Lock()


def session(log, s, a):

  def rununpack():
    global L_unpack

    log("rununpack aquiring lock")
#  is_free = L_unpack.acquire(False)
#  if not is_free: 
#    log("waiting another process")

  # always unpack as there is possibility that when other process started our data was not ready
    L_unpack.acquire()

#  if is_free:
    log("start to unpack")
  #--os.spawn(os.P_WAIT, UNPACK1[0], UNPACK1)

#  else:
#    log("just unpacked by parallel process")

    L_unpack.release()



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
        # if no password sent and link does not have password, export only direct netmail
        #  - arranged in ftnexport
        classesstr = val.lower().split(",")
        classes = set()
        allclasses = set(("netmail", "echomail", "fileecho", "filebox", "direct"))
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
            log("address %s excluded due to wrong password"%address)
          except:
            log(str(a)+" exception on addess %s: %s"%(address, traceback.format_exc()))

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
