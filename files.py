
import os
import hashlib

from ftnconfig import FILEDIR, GROUPFILESBY, connectdb

def get_folder(id):
  minid = id//GROUPFILESBY
  maxid = minid+GROUPFILESBY-1
  return os.path.join(FILEDIR, "%d-%d"%(minid, maxid))

def import_file(db, path, recvfrom):
  # calc length, crc32, sha256
  # if already in base return id
  # if not in base
  # create recrd and move to storage (in the transaction)
  pass

db=connectdb()

x=db.xact()
x.start()
db.prepare("select * from files")()
db.prepare("insert into files values (10, 10, 'a', 'b', 'c')")()
db.prepare("select * from files")()
x.commit()

