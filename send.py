#!/bin/env python3

from ftnconfig import *
import ftnimport

with ftnimport.session(db) as sess:
  sess.send_message("robot", ("node", ADDRESS), "sysop", "test", "test message")
