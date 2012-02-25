#!/bin/env python3

from ftnconfig import *
import ftnimport

db=connectdb()

#exit()

with ftnimport.session(db) as sess:
  sess.send_message("Sergey Dorofeev", ("echo", "TESTING"), 
        "All", None, "test path", 
"""Hello All

Test2

""")
exit()





with ftnimport.session(db) as sess:
  sess.send_message("Sergey Dorofeev", 
                    ("node", "2:5020/4441"), "Yuri Myakotin", 
                     None, "прохождение почты", 
"""Привет 

Нашёл у себя один косяк - capability word с перестановленными
байтами не записывалось. Из-за этого может в бэды выпадать?
Сейчас ещё раз мо.измайлово отресканил.

""")
exit()


