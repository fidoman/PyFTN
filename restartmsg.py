#!/bin/env python3

import sys
import glob
import re
import os
import shutil
import ftnconfig

RE_from=re.compile("from(\:)? (\d+\:\d+\/\d+(\.d+)?)")

directory = sys.argv[1]

for stfile in glob.glob(directory+"/*.status"):
  f=RE_from.search(open(stfile).readline())
  if f:
    msgfile = stfile[:-7]+".msg"
    dstdir="/tank/home/sergey/fido/fidotmp/archive/"+f.group(2)+"/pwd-in/"
    try:
      os.makedirs(dstdir)
    except:
      pass
    shutil.move(msgfile, dstdir)
    shutil.move(stfile, dstdir)
