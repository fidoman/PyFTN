#!/usr/local/bin/python3

# convert files.bbs to .desc files

import os, re

for x in os.listdir():
  if os.path.isdir(x):
    print (x)
    bbsfile = os.path.join(x, "FILES.BBS")
    if not os.path.exists(bbsfile):
      continue
    b = {}
    f = None
    for l in open(bbsfile, encoding="cp866"):
      if l[0]==" ":
        b[f]+=l.strip()+"\n"
      elif l[0]=="\n":
        continue
      else:
        f, d = (l+" ").split(" ", 1)
        b[f] = d.strip()+"\n"

    files = {}
    for f in os.listdir(x):
      files[f.upper()] = f

    for k, v in b.items():
      if k.upper() in files:
        print (k, files[k.upper()], v)
        open(os.path.join(x, files[k.upper()]+".desc"), "w").write(v)
