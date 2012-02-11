#!/bin/env python3

from ftnconfig import *
import ftnimport

db=connectdb()

with ftnimport.session(db) as sess:
  sess.send_message("Sergey Dorofeev", ("echo", "N5020.SYSOP"), "All", None, "test", 
"""Привет All!

2:5020/12000 переехал на новый софт.
Просьба сообщать о глюках.
Сейчас главная проблема с завершением binkp сессий.
""")
