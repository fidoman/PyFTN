#!/bin/env python3

from ftnconfig import *
import ftnimport
import os

db=connectdb()

DESTDOM,DESTTXT, DESTNAME = "node", "2:5020/715", "Alex Barinov"
REPLY = None
SUBJ = "fluid.local"
BODY = "В ответе %QUERY выдаётся сабж маленькими буквами. Это глюк какой-то?"

#DESTDOM,DESTTXT, DESTNAME = "echo", "FLUID.LOCAL", "All"
#REPLY = None
#SUBJ = "MSGID"
#BODY = "тест генератора MSGID, использующего Postgresql sequence. Старт с текущего unixtime."


with ftnimport.session(db) as sess:
    sess.send_message("Sergey Dorofeev", (DESTDOM, DESTTXT), 
                DESTNAME, REPLY, SUBJ, 
"""Hello %s,

%s

"""%(DESTNAME.split(" ")[0], BODY))
