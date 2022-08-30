#!/usr/bin/python3

import sys
import os
import ftnconfig
import lo

db = ftnconfig.connectdb()

def save(db, filedata, outf):
  size, lo_id, content = db.prepare("select length, lo, content from files where id=$1").first(filedata)
  if lo_id is None:
        print ("in-line data", len(content))
        if len(content)!=size:
          raise Exception("content size mismatch")
        outf.write(content)
  else:
        print ("read lo", lo_id)
        lo_len = lo.lo_save(db, lo_id, outf)
        if lo_len!=size:
          raise Exception("large object size mismatch")


# 1. read link, get area and file name
# 2. select freshest file with specified name in area (from file_post)
# 3. save data under link

def restore_fechoes():
 base_dir = ftnconfig.DOUTBOUND
 for addr in os.listdir(base_dir):
  addr_dir = os.path.join(base_dir, addr)
  for f in os.listdir(addr_dir):
    fname=os.path.join(addr_dir, f)
    if os.path.islink(fname):
      target = os.readlink(fname)
      if os.path.exists(target):
        print ("good link")
        continue

      target_dir, target_file = os.path.split(target)
      _, fecho = os.path.split(target_dir)
      dest_id = ftnconfig.get_addr_id(db, db.FTN_domains["fileecho"], fecho.upper())

      newest_post = db.prepare("select max(post_time) from file_post where destination=$1 and filename ilike $2").first(dest_id, target_file)
      file_id = db.prepare("select filedata from file_post where destination=$1 and filename ilike $2 and post_time=$3").first(dest_id, target_file, newest_post)

      print (addr, f, fecho, dest_id, target_file, file_id)

      tmpf = fname+"_"

      tmpfd=open(tmpf, "wb")
      save(db, file_id, tmpfd)
      tmpfd.close()

      os.rename(fname, fname+"--badlink")
      os.rename(tmpf, fname)

def q_file(db, area, name):
  return db.prepare("select filedata from file_post"
    " where destination=(select id from addresses where text=$2 and domain=$1) and filename ilike $3"
    " order by post_time desc").first(db.FTN_domains["fileecho"], area, name)

def nodelist():
  f_id = q_file(db, 'NODELIST', 'NODELIST.___')
  print (f_id)
  save(db, f_id, open(ftnconfig.NODELIST+".zip", "wb"))
  base = os.path.split(ftnconfig.NODELIST)[0]
  save(db, q_file(db, 'R50ROUTE', 'R50.ROU'), open(os.path.join(base, 'R50.ROU'), "wb"))
  save(db, q_file(db, 'R50ROUTE', 'R50.TRU'), open(os.path.join(base, 'R50.TRU'), "wb"))
  save(db, q_file(db, 'NET5020', 'N5020.ROU'), open(os.path.join(base, 'N5020.ROU'), "wb"))
  save(db, q_file(db, 'NET5020', 'N5020.TRU'), open(os.path.join(base, 'N5020.TRU'), "wb"))
  save(db, q_file(db, 'DAILYUTF', 'DAILYUTF.Z__'), open(os.path.join(base, 'DAILYUTF.ZIP'), "wb"))
#  save(db, q_file(db, 'R50ECHOLST', 'ECHO50.LST'), open(os.path.join(base, 'ECHO50.LST'), "wb"))

if sys.argv[1] == "nodelist":
  nodelist()

elif sys.argv[1] == "outbound":
  restore_fechoes()

else:
  f_id = int(sys.argv[1])
  save(db, f_id, open(sys.argv[2], "wb"))
