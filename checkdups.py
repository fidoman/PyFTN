#!/bin/env python

# check that messages in dupearea really the same as in database

import os
from ftnconfig import *
import ftn.msg

for f in os.listdir(DUPDIR):
  if f.endswith(".msg"):
    print f
