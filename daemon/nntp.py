#!/usr/local/bin/python3 -bb

import socket
import traceback
import re
import time
import datetime

from socketutil import *
import ftnconfig
import ftnimport
import ftnexport

sessions=[]


# https://tools.ietf.org/html/rfc1036

spaces=re.compile(b"\s+")
msgrange=re.compile(b"(\d+)(-(\d*))?$")
digits=re.compile(b"\d+$")

def session(log, s, a):

  def prepare_not_pipelining_response():
    try:
      while s.recv(4096, socket.MSG_DONTWAIT):
        log(str(a)+" unexpected pipelining\n")
    except BlockingIOError:
      pass

  def ascii_arg(n):
    try:
      return cmd[n].decode("ascii").upper()
    except:
      return None

  def cmdConnection():
    nonlocal db, servicing
    try:
      db = ftnconfig.connectdb()
      servicing = True
      s.send(b"201 Read-only server intact\r\n")
    except:
      log(str(a)+"\nexception\n"+traceback.format_exc())
      servicing = False
      s.send(b"400 Database is unavailable\r\n")

  def cmdQuit():
    nonlocal servicing
    s.send(b"205 NNTP Service exits normally\r\n")
    servicing = False

  def cmdMode():
    if len(cmd)<2:
      s.send(b"501 No argument\r\n")
      return
    arg = ascii_arg(1)
    if arg is None:
      s.send(b"501 Non-ASCII argument\r\n")
      return
    if arg=="READER":
      s.send(b"201 Posting prohibited\r\n")
    else:
      s.send(b"501 Invalid argument\r\n")

  def cmdCapabilities():
    s.send(b"101 Capability list follows\r\n")
    for cap in ["VERSION 2","READER","MODE-READER","LIST ACTIVE NEWSGROUPS","IMPLEMENTATION PyFTN 1"]:
      s.send(cap.encode("ascii")+b"\r\n")
    s.send(b".\r\n")

  def cmdGroup():
    nonlocal currentgroup
    if len(cmd)<2:
      s.send(b"501 No argument\r\n")
      return
    try:
      arg = cmd[1].decode("utf-8")
    except:
      s.send(b"501 Bad argument\r\n")
      return
    x=ftnexport.nntp_group(db, arg)
    if x is None:
      s.send(b"411 No such group\r\n")
    else:
      s.send(("211 %d %d %d %s\r\n"%(x[0] or 0, x[1] or 0, x[2] or 0, arg)).encode("ascii"))
      currentgroup = arg
      log(str(a)+" group "+arg+" selected")


  def cmdListGroup():
    nonlocal currentgroup
    if len(cmd)==1:
      if currentgroup is None:
        s.send(b"412 No group selected\r\n")
        return
      group = currentgroup

    if len(cmd)>1:
      try:
        arg = cmd[1].decode("utf-8")
      except:
        s.send(b"501 Bad argument\r\n")
        return
      group = arg

    if len(cmd)>2:
      arg2=cmd[2]
      m=msgrange.match(arg2)
      if not m:
        s.send(b"501 Bad range\r\n")
        return

      try:
        gtethan=int(m.group(1))
        if m.group(2):
          if m.group(3):
            ltethan=int(m.group(3))
          else:
            ltethan=None
        else:
          ltethan=gtethan
      except:
        s.send(b"501 Bad range\r\n")
        return

    else:
      gtethan=None
      ltethan=None

    x=ftnexport.nntp_group(db, group)
    if x is None:
      s.send(b"411 No such group\r\n")
      return

    s.send(("211 %d %d %d %s\r\n"%(x[0] or 0, x[1] or 0, x[2] or 0, group)).encode("ascii"))
    currentgroup = group
    log(str(a)+" group "+currentgroup+" selected")

#    s.send((repr(gtethan)+" - "+repr(ltethan)).encode("ascii")+b"\r\n")

    for num in ftnexport.nntp_group_list(db, currentgroup, gtethan, ltethan):
      s.send(str(num).encode("ascii")+b"\r\n")
    s.send(b".\r\n")


  def cmdLast():
    nonlocal currentgroup, currentarticle
    if currentgroup is None:
      s.send(b"412 No newsgroup selected\r\n")
      return
    if currentarticle is None:
      s.send(b"420 Current article number is invalid\r\n")
      return
    newarticle = ftnexport.nntp_prev(db, currentgroup, currentarticle)
    if newarticle is None:
      s.send(b"422 No previous article in this group\r\n")
    currentarticle = newarticle
    msgid = ftnexport.nntp_msgid(db, currentgroup, newarticle)
    s.send(("223 %d %s\r\n"%(newarticle, msgid)).encode("ascii"))

  def cmdNext():
    nonlocal currentgroup, currentarticle
    if currentgroup is None:
      s.send(b"412 No newsgroup selected\r\n")
      return
    if currentarticle is None:
      s.send(b"420 Current article number is invalid\r\n")
      return
    newarticle = ftnexport.nntp_next(db, currentgroup, currentarticle)
    if newarticle is None:
      s.send(b"421 No next article in this group\r\n")
    currentarticle = newarticle
    msgid = ftnexport.nntp_msgid(db, currentgroup, newarticle)
    s.send(("223 %d %s\r\n"%(newarticle, msgid)).encode("ascii"))


  def cmdArticle():
    nonlocal currentgroup, currentarticle
    response,head,body={
        "ARTICLE": ("220", True, True),
        "HEAD": ("221", True, False),
        "BODY": ("222", False, True),
        "STAT": ("223", False, False)
    }

    # 1) demultiplex parameters
    msgid = None
    article = None

    if len(cmd)==1:
      if currentarticle is None:
        s.send(b"420 Current article number is invalid\r\n")
        return
      article=currentarticle

    if len(cmd)>1:
      arg=cmd[1]
      if digits.match(arg):
        try:
          article=int(arg)
        except:
          s.send(b"501 Invalig argument\r\n")
          return
      else:
        try:
          msgid=arg.decode("ascii")
        except:
          s.send("501 Non-ASCII MSGID\r\n")
          return
        log(str(a)+" fetch by msgid "+repr(msgid))

    # 2) fetching
    if msgid is not None:
      out = nntp_fetch(db, msgid=arg, head=head, body=body)
      if out is None:
        s.send(b"430 No article with that message-id\r\n")
        return
    elif article is not None:
      if currentgroup is None:
        s.send(b"412 No newsgroup selected\r\n")
        return
      group=currentgroup
      out = nntp_fetch(db, group=group, article=article, head=head, body=body)
      if out is None:
        s.send(b"423 No article with that number\r\n")
        return
    else:
      s.send("501 Could not interpret arguments\r\n")
      return

    s.send((response+" "+"0" if article is None else str(article)+" "+msgid+"\r\n").encode("ascii"))
    for l in out:
      s.send(l.encode("utf-8")+b"\r\n")
    s.send(b".\r\n")

    # 3) update
    if article is not None:
      currentarticle = article

  def cmdDate():
    nntpdate = time.strftime("%Y%m%d%H%M%S", time.gmtime()).encode("ascii")
    s.send(b"111 "+nntpdate+b"\r\n")

  def cmdHelp():
    s.send(b"100 Help text follows\r\n")
    s.send(b"NNTP access for PyFTN message database\r\n")
    s.send(b"See https://tools.ietf.org/html/rfc3977 for NNTP protocol specification\r\n")
    s.send(b"And https://tools.ietf.org/html/rfc1036 for article format\r\n")
    s.send(b"Please mail sergey@fidoman.ru if you believe this software has a bug\r\n")
    s.send(b".\r\n")


  def ListActive(newerthan=None):
    try:
      echolist = list(ftnexport.nntp_list_active(db, newerthan))
    except:
      s.send(b"403 error querying list of echoes\r\n")
      log(str(a)+" exception on ListActive %s"%(traceback.format_exc()))
      return

    if newerthan is None:
      s.send(b"215 list of newsgroups follows\r\n")
    else:
      s.send(b"231 list of new newsgroups follows\r\n")

    for e, mn, mx in echolist:
      if mn is None or mx is None:
        mn = mx = 0
      s.send(("%s %d %d n\r\n"%(e,mn,mx)).encode("ascii"))
    s.send(b".\r\n")


  def cmdList():
    if len(cmd)==1:
      ListActive()
      return
    arg = ascii_arg(1)
    if arg is None:
      s.send(b"501 Non-ASCII argument\r\n")
      return
    if arg == "ACTIVE":
      ListActive()
      return
    if arg == "NEWSGROUPS":
      s.send(b"215 descriptions not supported yet\r\n")
      s.send(b".\r\n")
      return

    s.send(b"501 Unsupported argument\r\n")


  def cmdNewGroups():
    if len(cmd)<3 or len(cmd[1])!=6 and len(cmd[1])!=8 or len(cmd[2])!=6:
      s.send(b"501 Bad argument\r\n")
      return
    try:
      year  = int(cmd[1][:-4])
      month = int(cmd[1][-4:-2])
      day   = int(cmd[1][-2:])
      hour   = int(cmd[2][:2])
      minute = int(cmd[2][2:4])
      second = int(cmd[2][4:])
      if len(cmd[1][:-4])==2:
        cyear=time.gmtime()[0]
        cyear_yy=cyear%100
        ccentury=cyear//100
        if year>cyear_yy:
          year+=(ccentury-1)*100
        else:
          year+=ccentury*100

      dt = datetime.datetime(year, month, day, hour, minute, second, tzinfo=datetime.timezone.utc)
    except:
      s.send(b"501 Bad argument\r\n")
      return

    ListActive(dt)


  commands={ # allow pipeline, function
None:	(False, cmdConnection),
"QUIT":	(True, cmdQuit),
"MODE":	(True, cmdMode), #READER
"CAPABILITIES": (True, cmdCapabilities),
"GROUP":	(True, cmdGroup),
"LISTGROUP":	(True, cmdListGroup), #multiline out
"LAST":	(True, cmdLast),
"NEXT":	(True, cmdNext),
"ARTICLE":	(True, cmdArticle), #multiline
"HEAD":	(True, cmdArticle), #multiline
"BODY":	(True, cmdArticle), #multiline
"STAT":	(True, cmdArticle),
#"POST":	(False, cmdPost),
"DATE": (True, cmdDate),
"HELP": (True, cmdHelp),
"NEWGROUPS": (True, cmdNewGroups),
"LIST": (True, cmdList),
  }

  def dispatch_command(c):
    procdata = commands.get(c)
    if procdata is None:
        s.send(b"500 Unknown command\r\n")
        return

    pipelining, procedure = procdata
    if not pipelining:
      prepare_not_pipelining_response()
    procedure()

  try:
    db = None
    servicing = None
    currentgroup = None
    currentarticle = None

    dispatch_command(None) # incoming connection greeting

    while servicing:
      cmd = spaces.split(readline(s).strip())
      log(str(a)+" command: "+repr(cmd))
      try:
        cmds=cmd[0].decode("ascii").upper()
      except:
        s.send(b"500 Non-ASCII command\r\n")
        continue
      dispatch_command(cmds)

  except Exception:
    log(str(a)+"\nexception\n"+traceback.format_exc())

  finally:
    log(str(a)+" end")
    s.close()


#protocol state variables:
#  group = None or value
#  article = None or value


