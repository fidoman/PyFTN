#!/bin/env python3

from ftnconfig import *
import ftnimport

with ftnimport.session(db) as sess:
  sess.send_message("Sergey Dorofeev", ("echo", "FLUID.LOCAL"), "All", None, "test", 
"""Привет All!

Это тест.
Меня вообще видно?
""")
