#!/usr/local/bin/python3 -bb

import glob
import os
import magic
import zipfile
import rarfile
import traceback
import io
import time

import ftnimport
import ftn.msg
import ftn.pkt
import ftn.addr
from ftn.ftn import FTNFail, FTNDupMSGID, FTNNoMSGID, FTNNoOrigin, FTNNotSubscribed
from ftnconfig import *

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


def import_msg(sess, m, recv_from, bulk):
  # if m has flag ARQ, create a message with audit info and pack to recv_from then save to dsend to recv_from

  try:
    sess.import_message(m, recv_from, bulk)
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


def import_pkt(sess, fo, recv_from, bulk):
  """ imports FTN incoming file as one transaction.
      returns True if file is successfully imported
        (if some msgs refused, they are saved separately)
      returns False and rollbacks transaction if import 
        failed for some reason
      file type: msg, pkt, tic, other (tic or msg attached file)
      orig_name is optional (for saving 'other' files) """

  x=ftn.pkt.PKT(fo)
  #..pass to messages address from PKT (it can match with session address or verify by password if differ)

  #rc=ftn.addr.str2addr(recv_from)
  if x.source[1]==65535 and x.source[0]==rc[0]:
    print("fixup for pointnet network address %s, NOT TESTED"%repr(x.source))
    x.source = (x.source[0], x.auxnet, x.source[2], x.source[3])

  pktsrc=ftn.addr.addr2str(x.source)
  #print("received from: %s, packet src: %s"%(recv_from, pktsrc))
  if recv_from!=pktsrc:
    raise FTNFail("packet source (%s) does not match node address from which it was received (%s)"%(pktsrc, recv_from))
  for m in x.msg:
    import_msg(sess, m, pktsrc, bulk)


def import_file(sess, fname, fo, recv_from, bulk):
    if ismsg(fname):
            print("msg")
            import_msg(sess, ftn.msg.MSG(fo), recv_from, bulk)

    elif ispkt(fname):
            print("pkt")
            import_pkt(sess, fo, recv_from, bulk)

    elif isbundle(fname):
        sample = fo.read(8192)
        fo.seek(-len(sample), io.SEEK_CUR)
        mime=magic.whatis(sample)
        print("bundle (%s)"%mime)
        if mime=="application/zip":
            print("zip file")
            z=zipfile.ZipFile(fo)
            for zf in z.namelist():
                if not ispkt(zf):
                  raise Exception("non-PKT file in bundle %s"%fname)

            for zf in z.namelist():
                print(zf)
                zfo=z.open(zf)
                import_pkt(sess, zfo, recv_from, bulk)
                zfo.close()

            
            z.close()

        elif mime=="application/x-rar":
            print("rar file")
            z=rarfile.RarFile(fo)
            for zf in z.namelist():
                if not ispkt(zf):
                  raise Exception("non-PKT file in bundle %s"%fname)

            for zf in z.namelist():
                print(zf)
                zfo = z.open(zf)
                import_pkt(sess, zfo, recv_from, bulk)
                zfo.close()

            z.close()

        else:
            raise Exception("dont know how to unpack bundle %s"%fname)

    else:
        raise Exception("file %s is not FIDO mail file")

#   elif istic(f):
#           pass #print("tic - ignore")
#
#           #fo=file(f, "rb")
#           #import_file(fo, f, "tic", recv_from)
#           #fo.close()
#           #os.unlink(f)




# unpack inbound, keeping from whom message received (but ignore unauthenticated addresses)
# load messages, setting processd=False and specifying receivedfrom
# 1) PKT address matches source and destination is this node

def find_all(b):
  for x in glob.glob(b+"/*"):
    if os.path.isdir(x):
      for z in find_all(x):
        yield z
    else:
      yield x
  return


if __name__ == "__main__":

  db=connectdb()

  print(time.asctime(), "start ftnpush")

  for pnode_dir in glob.glob(INBOUND+"/*"):

    node = ftn.addr.addr2str(map(int, pnode_dir[len(INBOUND)+1:].split(".")))
    #print("source: "+node)

    for f in find_all(pnode_dir+"/pwd-in"):
      #skip non-mail
      if not ismsg(f) and not ispkt(f) and not isbundle(f):
        continue

      print("file:", f)
      try:
        with ftnimport.session(db) as sess:
          fo = open(f, "rb")
          import_file(sess, f, fo, node, False)
          fo.close()
          os.unlink(f)

      except Exception as e:
        print("error on file %s"%repr(f))
        os.rename(f, f+".bad")
        fx=open(f+".status", "w")
        fx.write(traceback.format_exc())
        fx.close()

        exit()
