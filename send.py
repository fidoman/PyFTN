#!/bin/env python3

from ftnconfig import *
import ftnimport

db=connectdb()

#with ftnimport.session(db) as sess:
#  sess.send_message("Sergey Dorofeev", ("echo", "FLUID.LOCAL"), "All", None, "fluid.reports", 
#"""Привет All!
#
#Починить никак нельзя, новый надо делать.
#Тут же всё по-другому :) Только тикер старый пока остался.
#
#""")

with ftnimport.session(db) as sess:
  sess.send_message("Sergey Dorofeev", 
                    ("node", "2:50/10.27753"), "Mihail Yakovlev", 
                    "2:50/10.27753 4f37e5b5", "Re: 5012", 
"""Привет 

Прописал.

--- PyFTN""")
