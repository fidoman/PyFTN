#!/bin/env python3

from ftnconfig import *
import ftnimport

db=connectdb()

exit()

with ftnimport.session(db) as sess:
  sess.send_message("Sergey Dorofeev", ("echo", "FLUID.LOCAL"), 
        "Eugene Palenock", None, "что с фидо?", 
"""Привет

MO.IZMAILOVO уже и так на /4441...

""")

exit()



with ftnimport.session(db) as sess:
  sess.send_message("Sergey Dorofeev", 
                    ("node", "2:5020/715"), "Alexey Barinov", 
                    None, "строчка для нодлиста", 
"""Привет 

Hub,12000,Fluid,Vidnoe,Sergey_Dorofeev,7-495-541-9688,33600,V34,XW,IBN,IFC,INA:fluid.fidoman.ru,U,TDL

""")

exit()
