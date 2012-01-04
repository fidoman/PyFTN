#!/bin/env python3 -bb

import glob
import os
import magic
import zipfile
import rarfile
import traceback
import io

import ftnimport
import ftn.msg
import ftn.pkt
from ftn.ftn import FTNFail, FTNDupMSGID, FTNNoMSGID, FTNNoOrigin, FTNNotSubscribed

def ispkt(f):
  return f[-4:].lower()==".pkt"

def ismsg(f):
  return f[-4:].lower()==".msg"

def istic(f):
  return f[-4:].lower()==".tic"

BUNDLEext=set((".mo",".tu",".we",".th",".fr",".sa",".su"))

def isbundle(f):
  return f[-4:-1].lower() in BUNDLEext


from badwriter import badmsgs, dupmsgs, secmsgs


def import_msg(sess, m, recv_from):
  try:
    sess.import_message(m, recv_from)
  except FTNDupMSGID as e:
    # move duplicate to dup-area
    dupmsgs.write(m.pack(), "Duplicate message received from %s"%recv_from+"\n"+traceback.format_exc())
    # and continue
  except UnicodeDecodeError as e:
    badmsgs.write(m.pack(), "Could not recognize charset in message received from %s"%recv_from+"\n"+traceback.format_exc())
  except FTNNoMSGID as e:
    badmsgs.write(m.pack(), "No MSGID in message received from %s"%recv_from+"\n"+traceback.format_exc())
  except FTNNoOrigin as e:
    badmsgs.write(m.pack(), "No Origin in message received from %s"%recv_from+"\n"+traceback.format_exc())
  except FTNNotSubscribed as e:
    secmsgs.write(m.pack(), "Cannot post message received from %s"%recv_from+"\n"+traceback.format_exc())


def import_pkt(sess, fo, recv_from):
  """ imports FTN incoming file as one transaction.
      returns True if file is successfully imported
        (if some msgs refused, they are saved separately)
      returns False and rollbacks transaction if import 
        failed for some reason
      file type: msg, pkt, tic, other (tic or msg attached file)
      orig_name is optional (for saving 'other' files) """

  x=ftn.pkt.PKT(fo)
  #..pass to messages address from PKT (it can match with session address or verify by password if differ)

  rc=ftn.addr.str2addr(recv_from)
  if x.source[1]==65535 and x.source[0]==rc[0]:
    print("fixup for network address %s"%repr(x.source))
    x.source = (x.source[0], rc[1], x.source[2], x.source[3])

  pktsrc=ftn.addr.addr2str(x.source)
  print("received from: %s, packet src: %s"%(recv_from, pktsrc))
  if recv_from!=pktsrc:
    raise FTNFail("packet source (%s) does not match node address from which it was received (%s)"%(pktsrc, recv_from))
  for m in x.msg:
    import_msg(sess, m, pktsrc)





# unpack inbound, keeping from whom message received (but ignore unauthenticated addresses)
# load messages, setting processd=False and specifying receivedfrom
# 1) PKT address matches source and destination is this node

BASE="/tank/home/sergey/fido/fidotmp/archive"

def find_all(b):
  for x in glob.glob(b+"/*"):
    if os.path.isdir(x):
      for z in find_all(x):
        yield z
    else:
      yield x
  return

for net_dir in glob.glob(BASE+"/*:*"):
  for node_dir in glob.glob(net_dir+"/*"):
    node=node_dir[len(BASE)+1:]
    print("source: "+node)
    for f in find_all(node_dir):
      #skip for a while
      if not ismsg(f) and not ispkt(f) and not isbundle(f):
        continue

      print("file: "+f)
      try:
        with ftnimport.session(ftnimport.db) as sess:

          if ismsg(f):
            print("msg")
            import_msg(sess, ftn.msg.MSG(f), node)
            os.unlink(f)

          elif ispkt(f):
            print("pkt")
            import_pkt(sess, f, node)
            os.unlink(f)

          elif isbundle(f):
            mime=magic.file(f)
            print("bundle (%s)"%mime)
            if mime=="application/zip":
              print("zip file")
              z=zipfile.ZipFile(f)
              for zf in z.namelist():
                if not ispkt(zf):
                  raise Exception("non-PKT file in bundle %s"%repr(zf))

              for zf in z.namelist():
                print(zf)
                zfo=z.open(zf)
                import_pkt(sess, zfo, node)
                zfo.close()

              del z
              os.unlink(f)

            elif mime=="application/x-rar":
              print("rar file")
              z=rarfile.RarFile(f)
              for zf in z.namelist():
                if not ispkt(zf):
                  raise Exception("non-PKT file in bundle %s"%repr(zf))

              for zf in z.namelist():
                print(zf)
                zfo = z.open(zf)
                import_pkt(sess, zfo, node)
                zfo.close()

              del z
              os.unlink(f)


            else:
              print("dont know how to unpack")
              #fo=open(f, "rb")
              #badbnds.write(fo.read(), "from: "+node+"\n"+"dont know how to unpack")
              #fo.close()
              #os.unlink(f)

          elif istic(f):
            pass #print("tic - ignore")

            #fo=file(f, "rb")
            #import_file(fo, f, "tic", node)
            #fo.close()
            #os.unlink(f)

          else:
            pass #print("unspecified file, ignore")
            #fo=file(f, "rb")
            #import_file(fo, f, "other", node)
            #fo.close()
            #os.unlink(f)


      except Exception as e:
        print("error on file %s"%repr(f))
        #traceback.print_exc()
        os.rename(f, f+".bad")
        fx=open(f+".status", "w")
        fx.write(traceback.format_exc())
        fx.close()

        exit()
