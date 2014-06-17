#!/usr/local/bin/python3 -bb

import os

import ftnconfig

fareas = ftnconfig.FAREASDIR

for d in os.listdir(fareas):
  farea_dir = os.path.join(fareas, d)
  if not os.path.isdir(farea_dir):
    continue
  farea = d.upper()

  print (farea, farea_dir)

  files=set()
  infos=set()
  descs=set()
  for f in os.listdir(farea_dir):
    if f.endswith(".desc"):
      descs.add(f)
    elif f.endswith(".info"):
      infos.add(f)
    else:
      files.add(f)
  for f in files:
    if f+".info" not in infos:
      print (f)

# all files not having desc import as hatched 2001-01-01
# import and delete

# index all files stored in pwd-in-archive
# save index for restart, add to it new files

# make list of all files with .info
# order by received time from .info together with archive

# import in recv-time order by list and delete (excluding having symlinks in outboxes)

# stop old tic processing
# import newly appeared files
# for links that have files in outbox make lastrecv as before oldest file
# clean outboxes
# make all new files to get to database