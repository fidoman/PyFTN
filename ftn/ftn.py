#!/usr/bin/python

#import pgdb, sys

class FTNFail (Exception):
  def __init__(self, text):
    Exception.__init__(self, "FTN error: %s"%text)

class FTNSubscribeFailed (FTNFail):
  pass

class FTNDupMSGID(FTNFail):
  def __init__(self, text):
    FTNFail.__init__(self, "MSGID %s already in base"%text)

class FTNNoMSGID(FTNFail):
  def __init__(self):
    FTNFail.__init__(self, "Message without MSGID")

class FTNNoOrigin(FTNFail):
  def __init__(self):
    FTNFail.__init__(self, "Message without Origin")

class FTNNotSubscribed(FTNFail):
  def __init__(self, src, dst):
    FTNFail.__init__(self, "Address %s not subscribed to %s"%(src, dst))

class FTNAlreadySubscribed(FTNFail):
  def __init__(self, target, subscriber):
    FTNFail.__init__(self, "Address %s already subscribed to %s"%(str(subscriber), str(target)))


def logprint(s):
  sys.stderr.write(s+"\n")

log=logprint

class FTNBase:
  def __init__(self, db):
    self.db = db
    self.db.cursor().execute("commit")
    log("init")
    
  def populate(self, table, values):
    log("pop. begin")
    a=self.db.cursor()
    a.execute("begin")
    strval=[["'%s'"%str(a),"NULL"][a is None] for a in values]
    try:
      a.execute("insert into %s values (%s)"%(table, ", ".join(strval)))
      a.execute("commit")
    except:
      print("!", "insert into %s values (%s)"%(table, ", ".join(strval)))
      a.execute("rollback")
    log("pop. end")

  def subscr_status(self, link):
    a=self.db.cursor()
    a.execute("select * from subscribe where ftna='%s'"%link)
    res=a.fetchall()
    a.close()
    return res

  def subscr_add(self, link, area):
    log("add. begin")
    a=self.db.cursor()
    a.execute("begin")
    try:
      log(" 1st")
      a.execute("insert into subscribe values ('%s','%s')"%(link,area))
      a.execute("commit")
    except:
      log(" fail")
      a.execute("rollback")
      
      self.populate("address", [link])
      self.populate("areas", [area,None,None])
      
      a.execute("begin")
      try:
        log(" 2nd")
        a.execute("insert into subscribe values ('%s','%s')"%(link,area))
        a.execute("commit")
      except:
        log(" fail")
        a.execute("rollback")
        raise FTNSubscribeFailed
    log("add. end")
    
#def del( link, area ):

#ftnbase=FTNBase()
#ftnbase.subscr_status("2:5020/12000")
#ftnbase.subscr_add("2:5020/12000","fluid.local")

#hold - when sent to all, hol msg locally
#flush - purge message on timeout, even if unsent
# add - msg_seenby (indicator that message sent to link)
#   used as in echomail, as in netmail (but not exports)
