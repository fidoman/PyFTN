#!/usr/bin/python

import sys, getopt, os
import struct, mmap
import ftn.pkt
import ftn.msg
import ftn.attr
from xml.dom.minidom import Document
import psycopg2
import psycopg2.errorcodes
import traceback
import re
import time
import locale
locale.setlocale(locale.LC_ALL, 'C')

from ftnimport import import_message
from badwriter import badmsgs

SQFRAME_NORMAL = 0
SQFRAME_FREE = 1
SQFRAME_LZSS = 2
SQFRAME_TRANSIENT = 3

def sqdate(v):
  day=v&0x1F
  v=v>>5
  month=v&0xF
  year=1980+(v>>4)
  return year, month, day

def sqtime(v):
  second=(v&0x1F)*2
  v=v>>5
  minute=v&0x3F
  hour=v>>6
  return hour, minute, second


def sq_message_extractor(f):
  """ iterator for messages in Squish base """
  fd=file(f, "r+b")
  fmap=mmap.mmap(fd.fileno(), 0)
  
  area=None
  if areabyname:
    area, _=os.path.splitext(os.path.split(f)[-1])
  
  Squish_header="<HHLLLLL80sLLLLLLHH124s"
  Squish_SQHDR="<LLLLLLHH"
  Squish_XMSG="<L36s36s72s4H4H2H2HhL9LL20s"
  header_len=struct.calcsize(Squish_header)
  sqhdr_len=struct.calcsize(Squish_SQHDR)
  xmsg_len=struct.calcsize(Squish_XMSG)
  
  hlen, rsv, num_msg, high_msg, skip_msg, high_water, uid, base, begin_frame, \
    last_frame, free_frame, last_free_frame, end_frame, max_msg, keep_days, \
    sz_sqhdr, rsv2 = struct.unpack_from(Squish_header, fmap)
    
  if sz_sqhdr != sqhdr_len: 
    raise Exception("SQHDR format changed")
  
  #print "length:", len

  frame = begin_frame
  
  while frame:
    print "%10d %s"%(frame, "="*69)
    try:
      id, next_frame, prev_frame, frame_length, msg_length, clen, frame_type, rsv = \
        struct.unpack_from(Squish_SQHDR, fmap, frame)
    except Exception, e:
      print "file info:", hlen, rsv, num_msg, high_msg, skip_msg, high_water, uid, `base`, begin_frame, \
        last_frame, free_frame, last_free_frame, end_frame, max_msg, keep_days, sz_sqhdr, `rsv2`, "$"
      print "error reading header of frame at offset %d"%frame
      raise e
      
    print id, "n%d"%next_frame,  "p%d"%prev_frame,  "fl%d"%frame_length,  "ml%d"%msg_length,  "clen%d"%clen, frame_type, rsv
    if frame_type == SQFRAME_NORMAL:
     try:
      msg=ftn.msg.MSG()

      mattr, mfrom, mto, msubject, morigz, morign, morigf, morigp, \
    				   mdestz, mdestn, mdestf, mdestp,\
    				   mdate_written, mtime_written,\
    				   mdate_arrived, mtime_arrived, mutc_ofs, \
        mreply_to, mreplies1, mreplies2,  mreplies3,  mreplies4,  mreplies5,  \
        mreplies6,  mreplies7,  mreplies8,  mreplies9, mumsgid, mftsc_date = \
           struct.unpack_from(Squish_XMSG, fmap, frame+sqhdr_len)
           
      fromaddr="%d:%d/%d.%d"%((morigz, morign, morigf, morigp))
      toaddr="%d:%d/%d.%d"%((mdestz, mdestn, mdestf, mdestp))
      #print "attr", mattr
      #print "from", mfrom.strip("\0").decode("cp866").encode("utf-8"), fromaddr
      #print "to", mto.strip("\0").decode("cp866").encode("utf-8"), toaddr
      #print "subject", msubject.strip("\0").decode("cp866").encode("utf-8")
      #print "date created", sqdate(mdate_written), sqtime(mtime_written)
      #print "date received", sqdate(mdate_arrived), sqtime(mtime_arrived)
      #print "reply:", mreply_to, mreplies1, mreplies2,  mreplies3,  mreplies4,  mreplies5,  \
    #    mreplies6,  mreplies7,  mreplies8,  mreplies9
      #print mumsgid, mftsc_date
      #if area:
      #  print "force AREA:", area

      header=fmap[frame+sqhdr_len+xmsg_len:frame+sqhdr_len+xmsg_len+clen]
      #print header.split("\x01")
      body=fmap[frame+sqhdr_len+xmsg_len+clen:frame+sqhdr_len+msg_length]
      #print body.replace("\x0d","\n").decode("cp866").encode("utf-8")

      if area:
        cbody="\x02\x00AREA:%s\n"%area.upper()
      else:
        cbody=""

      cbody+=reduce(str.__add__, map(lambda x: "\x01"+x+"\n", filter(lambda x: x, header.split("\x01"))), "")
      cbody+=body

      #print `cbody`

      msg.load( (mfrom.strip("\0"), (morigz, morign, morigf, morigp)), (mto.strip("\0"), (mdestz, mdestn, mdestf, mdestp)),
    		msubject.strip("\0"), mftsc_date.strip("\0"), mattr, 0, cbody )
    		
      yield msg
     except Exception, e:
      print "Exception in message at offset %d"%frame
      raise e

    else:
      print "frame type", frame_type

    frame = next_frame
  
  fd.close()
  return

def jam_message_extractor(f):
  """ iterator for messages in JAM base """
  if areabyname:
    raise Exception("area by name not implemented for JAM")

  filebase=os.path.splitext(f)[0]
  hfile=filebase+".jhr" # assume lowercase is required
  dfile=filebase+".jdt" # assume lowercase is required
  hf=file(hfile, "r+b")
  df=file(dfile, "r+b")
  hmap=mmap.mmap(hf.fileno(), 0)
  dmap=mmap.mmap(df.fileno(), 0)
  bSignature, bdatecreated, bmodcounter, bactivemsgs, bpasswordcrc, basemsgnum, _ = \
	struct.unpack_from("<4sLLLLL1000s", hmap, 0)
#  print bSignature

  pos=1024

  while pos<len(hmap):
    #print "*"*79
    ignore=False
    Signature, Revision, ReservedWord, \
    SubfieldLen, TimesRead, MSGIDcrc, REPLYcrc, \
    ReplyTo, Reply1st, Replynext, DateWritten, \
    DateReceived,   DateProcessed, MessageNumber, Attribute, \
    Attribute2, Offset, TxtLen, PasswordCRC, Cost = struct.unpack_from("<LHH17L", hmap, pos)
    pos+=struct.calcsize("<LHH17L")
#    print "Subfields:", SubfieldLen
    #print "date", "unknown" if DateWritten==0xffffffff else time.strftime("%d %b %y %H:%M:%S", time.localtime(DateWritten))
    #print "attr", ftn.attr.binary_to_text(Attribute)
    #print "attr2", Attribute2

    msgattr={}
    msgattr["date"] = "01 Jan 1970 00:00:00" if DateWritten==0xffffffff else time.strftime("%d %b %Y %H:%M:%S", time.localtime(DateWritten))
    msgattr["attr"] = ftn.attr.binary_to_text(Attribute)
    msgkludge=[]

    subpos=0
    while subpos<SubfieldLen:
      LoID, HiID, datlen=struct.unpack_from("<HHL", hmap, pos+subpos)
      subpos+=struct.calcsize("<HHL")
      if HiID!=0:
	raise Exception("JAM HiID not supported")
#      print "subheader", LoID, datlen, "bytes"
      val=hmap[pos+subpos:pos+subpos+datlen]
      if LoID==0:
	#print "senderaddress", val
	msgattr["senderaddress"]=val
      elif LoID==1:
	#print "recipientaddress", val
	msgattr["recipientaddress"]=val
      elif LoID==2:
	#print "sendername", val
	msgattr["sendername"]=val
      elif LoID==3:
	#print "recipientname", val
	msgattr["recipientname"]=val
      elif LoID==4:
	#print "msgid", val
	msgkludge.append(("MSGID:", val))
      elif LoID==5:
	#print "reply", val
	msgkludge.append(("REPLY:", val))
      elif LoID==6:
	#print "subject", val.decode("cp866")
	msgattr["subject"]=val
      elif LoID==7:
	#print "PID", val.decode("cp866")
	msgkludge.append(("PID:", val))
      elif LoID==8:
	print "Via", val.decode("cp866")
      elif LoID==9:
	print "File", val.decode("cp866")
	ignore=True
      elif LoID==11:
	print "FREQ", val.decode("cp866")
	ignore=True
      elif LoID==2000:
	#print "KLUGE", val.decode("cp866")
	kv=val.split(" ",1)
	if len(kv)==1:
	  kv.append("")
	msgkludge.append(kv)
      elif LoID==2003:
	#print "FLAG", 
	#for f in val.split(" "):
	#  print f,
	#  print ftn.attr.short_to_long(f),
	pass
      elif LoID==2004:
	#print "TZ", val.decode("cp866")
	msgkludge.append(("TZUTC:", val))
      else:
	raise Exception("unknown LoID %d"%LoID)

      subpos+=datlen
      if subpos>SubfieldLen: # must be strict equal at end of last subheader
        raise Exception("subheader overlaps next header %d %d"%(pos, subpos))

    if not ignore:

      try:
        bhead=reduce(str.__add__, map(lambda x: "\01"+x[0]+" "+x[1]+"\n", msgkludge), "")
      except Exception, e:
        print `msgkludge`
        raise e

      body=dmap[Offset:Offset+TxtLen]

      msg=ftn.msg.MSG()
      msg.load( (msgattr.get("sendername", "Sysop"), ftn.addr.str2addr(msgattr["senderaddress"])), 
	      (msgattr["recipientname"], ftn.addr.str2addr(msgattr["recipientaddress"])),
	      msgattr.get("subject", ""), msgattr["date"], Attribute, 0, bhead+body )

      #print unicode(msg).encode("utf-8")
      yield msg


    {
    10: "ENCLOSEDFILEWALIAS",
    12: "ENCLOSEDFILEWCARD",
    13: "ENCLOSEDINDIRECTFILE",
    1000: "EMBINDAT",
    2001: "SEENBY2D",
    2002: "PATH2D",
	}

    pos+=SubfieldLen

  hf.close()
  df.close()
  return

def pkt_message_extractor(f):
  """ iterator for messages in pkt file """
  pkt=ftn.pkt.PKT(f, True)
  return pkt.msg

def msg_message_extractor(f):
  """ iterator for a message in msg file """
  yield ftn.msg.MSG(f)
  return





if __name__ == "__main__":
    
  args, files = getopt.getopt(sys.argv[1:], 'pf:e')

  if len(files)==0:
    print "No input files"
    print " [-p /import as processed/] [-e /get echo name from filename/] -f format /msg|pkt|sq|jam/ file1..."
    sys.exit(-1)

  format=None
  processed=False
  areabyname=False
  for arg, v in args:
    if arg=='-f':
      if format:
        raise Exception('duplicate format specifier')
      format=v
    elif arg=='-p':
      processed=True
    elif arg=='-e':
      areabyname=True
    
  print format, processed, files

  if not format:
    raise Exception('format not specified')

  extractor = {"sq": sq_message_extractor, 
	     "jam": jam_message_extractor,
	     "msg": msg_message_extractor,
	     "pkt": pkt_message_extractor}[format]

  for f in files:
    print f
    for msg in extractor(f):
      #print unicode(msg).encode("utf-8")
      try:
        import_message(msg, None, processed=5, bulkload=True)
      except:
        traceback.print_exc()
        badmsgs.write(`msg`, traceback.format_exc())
    # no exception, all fine
    os.unlink(f)
