#!/usr/local/bin/python3

import sys
import os
import ftnconfig
import lo

db = ftnconfig.connectdb()

# 1. read link, get area and file name
# 2. select freshest file with specified name in area (from file_post)
# 3. save data under link

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

      size, lo_id, content = db.prepare("select length, lo, content from files where id=$1").first(file_id)

      print (addr, f, fecho, dest_id, target_file, file_id, size, lo_id)

      tmpf = fname+"_"
    
      if lo_id is None:
        print ("data", len(content))
        if len(content)!=size:
          raise Exception("content size mismatch")
        tmpfd=open(tmpf, "wb")
        tmpfd.write(content)
        tmpfd.close()
        del content
      else:
        print ("read lo", lo_id)
        lo_len = lo.lo_save(db, lo_id, tmpf)
        if lo_len!=size:
          raise Exception("large object size mismatch")

      os.rename(fname, fname+"--badlink")
      os.rename(tmpf, fname)
