#!/usr/local/bin/python3 -bb

import glob
import os
import magic
import zipfile
import rarfile
import traceback
import io
import time
import tempfile

import ftnimport
import ftn.msg
import ftn.pkt
import ftn.addr
from ftn.ftn import FTNFail, FTNDupMSGID, FTNNoMSGID, FTNNoOrigin, FTNNotSubscribed, ispkt, ismsg, istic, isbundle, FTNExcessiveMessageSize
from ftnconfig import *

from badwriter import badmsgs, dupmsgs, secmsgs


def import_msg(sess, m, recv_from, bulk):
  # if m has flag ARQ, create a message with audit info and pack to recv_from then save to dsend to recv_from

  if not bulk and ('AuditRequest' in ftn.attr.binary_to_text(m.attr)):
      print ("Sending audit reply to", m.orig[0].decode("ascii"), ftn.addr.addr2str(m.orig[1]), "via", recv_from)
      # create message to m.source
      # pack into packet to revc_from

      #print(repr(), m.orig, recv_from, m.date.decode("ascii"))
      audit_m = ftn.msg.MSG()
      audit_m.load((b"Audit Tracker", ftn.addr.str2addr(ADDRESS)), m.orig, b"Audit tracking responce",
       time.strftime("%d %b %y  %H:%M:%S").encode("ascii"), 0, 0, 
       ("\nThis reply confirms that your message is received by node "+ADDRESS+".\n"
"In case of import errors the reply may be sent again when import will be retried. "
"If the message must be routed to next FIDO system on the way, the export confirmation will also be sent.\n"
"\n"
"If you have received this message for any echomail, please be sure that your system does not "
"export echomail messages with ARq flag turned on.\n"
"\n"
"In case of any issues please contact sysop "+SYSOP+" "+ADDRESS+"\n"
"\n" +
""" === < MESSAGE BEGIN > ===\n""").encode("ascii") +
m.as_str(shorten=True) +
b""" === < MESSAGE END > ===

--- PyFTN
\1Via """+ADDRESS.encode("ascii")+b""" ImmediateARqReply """+time.asctime().encode("ascii")+b"\n")


      link_pkt_format = get_link_pkt_format(sess.db, recv_from)

      audit_p = ftn.pkt.PKT(format=link_pkt_format)
      audit_p.msg = [audit_m]
      audit_p.password = get_link_password(db, recv_from).encode("ascii")
      audit_p.source = ftn.addr.str2addr(ADDRESS)
      audit_p.destination = ftn.addr.str2addr(recv_from)
      audit_p.date = time.localtime()[:6]
      destdir = addrdir(DOUTBOUND, recv_from)
      os.makedirs(destdir, exist_ok = True)
      pkth, pktfn = tempfile.mkstemp(prefix="arq", suffix='.pkt', dir=destdir)
      pktf = os.fdopen(pkth, "wb")
      audit_p.save(pktf)
      pktf.close()
      #open("/tmp/arq.msg", "wb").write(audit_m.pack())


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
  except postgresql.exceptions.XMLContentError as e:
    badmsgs.write(m.pack(), "inadequate XML escaping in message received from %s"%recv_from+"\n"+traceback.format_exc())
  except FTNExcessiveMessageSize as e:
    badmsgs.write(m.pack(), "Big message received from %s"%recv_from+"\n"+traceback.format_exc())



def import_pkt(sess, fo, recv_from, bulk):
  """ imports FTN incoming file as one transaction.
      returns True if file is successfully imported
        (if some msgs refused, they are saved separately)
      returns False and rollbacks transaction if import 
        failed for some reason
      file type: msg, pkt, tic, other (tic or msg attached file)
      orig_name is optional (for saving 'other' files) """

  link_pkt_format = get_link_pkt_format(sess.db, recv_from)
#  print (recv_from, link_pkt_format)

  x=ftn.pkt.PKT(fo, format=link_pkt_format)
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
  if fo:
        raise Exception("unable to use file object with rarfile")

  if fo is None:
        fo = open(fname, "rb")
        doclose = True
  else:
        doclose = False

  try:

    if ismsg(fname):
            print("msg")
            import_msg(sess, ftn.msg.MSG(fo), recv_from, bulk)

    elif ispkt(fname):
            print("pkt")
            # pktformat = ..get from database..
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
            print("rar file: reopening fname")
            z=rarfile.RarFile(fname)
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

  finally:
    if doclose:
        fo.close()




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
  destinations = set()

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
          #fo = open(f, "rb")
          import_file(sess, f, None, node, False)
          #fo.close()
          #os.unlink(f)
          os.rename(f, f+"-"+str(time.time()))
          destinations.update(sess.touched_addresses())

      except Exception as e:
        print("error on file %s"%repr(f))
        #os.rename(f, f+".bad")
        fx=open(f+".status", "w")
        fx.write(traceback.format_exc())
        fx.close()

        #exit()

  print("Destinations:", repr(destinations))
