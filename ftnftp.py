#!/usr/local/bin/python3 -bb

import ftnconfig
import ftplib
import ast
import io
import ftn.pkt
import os
import ftnimport

from ftn.ftn import ismail
from ftnpush import import_file
from ftnexport import file_export

class FTPFile():
  def __init__(self, b):
    self.b = b

  def feed(self, d):
    self.b.write(d)
    print (len(d), "bytes added")


db = ftnconfig.connectdb()

for lid, addr, conn in db.prepare("select id, address, connection from links"):
  if conn is not None:
    ftp = conn.find("FTP")
    if ftp is not None:
      #print (addr, ftp.keys(), ftp.get("host"))
      domain, address = ftnconfig.get_addr(db, addr)
      link_pkt_format = ftnconfig.get_link_pkt_format(db, address)
      password = ftnconfig.get_link_password(db, address)

      print (ftp.get("username"), ftp.get("password"), ftp.get("host"), ftp.get("port", 0))

      with ftplib.FTP() as ftpc:
        ftpc.connect(host=ftp.get("host"), port=int(ftp.get("port", 0)))
        ftpc.login(user=ftp.get("username"), passwd=ftp.get("password"))
        #print (ftpc.getwelcome())
        ftpc.set_pasv(ast.literal_eval(ftp.get("passive", "False")))

        path = ftp.get("getfrom")
        print (path)
        if path: 
          ftpc.cwd(path)

        print (ftpc.nlst())

        for rfile in ftpc.nlst():
          print ("Remote file", rfile, "size", ftpc.size(rfile))
          if "/" in rfile:
            raise Exception("Slash in remote file name")

          if False: # ismail(rfile):
            # in-memory import is disabled until rarfile will start working with file objects
            print ("ismail")
            # download
            data = io.BytesIO()
            recipient = FTPFile(data)
            ftpc.retrbinary('RETR '+rfile, recipient.feed)

            data.seek(0)
            with ftnimport.session(db) as sess:
              import_file(sess, rfile, data, address, False)
              #ftpc.delete(rfile)

          else:
            savedir = ftnconfig.addrdir(ftnconfig.INBOUND, address)
            print("save", savedir)
            if not os.path.exists(savedir):
              os.makedirs(savedir)
            fd = os.open(os.path.join(savedir, "pwd-in", rfile), os.O_CREAT|os.O_WRONLY)
            fo = os.fdopen(fd, "wb")
            recipient = FTPFile(fo)
            ftpc.retrbinary('RETR '+rfile, recipient.feed)
            fo.close()
            ftpc.delete(rfile)

        ftpc.cwd("~")
        path = ftp.get("putto")
        if path:
          ftpc.cwd(path)
    
          
          for outbfile, committer in file_export(db, address, password, ["netmail", "echomail"]):
            print("outbound file "+outbfile.filename)

            existing = ftpc.nlst()
            while outbfile.filename in existing:
              outbfile.filename = "_" + outbfile.filename

#            ff=open("/tmp/test.zip", "wb")
#            while True:
#              x=outbfile.data.read(1000)
#              if not x:
#                break
#              ff.write(x)
#            ff.close()

            ftpc.storbinary("STOR "+outbfile.filename, outbfile.data)

            committer.commit()
