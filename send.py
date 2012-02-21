#!/bin/env python3

from ftnconfig import *
import ftnimport

db=connectdb()

with ftnimport.session(db) as sess:
  sess.send_message("Sergey Dorofeev", ("echo", "N5020.SYSOP"), "All", None, "эхи",
"""Привет All

Что-то я туплю, где найти актуальную информацию об эхобоне?

""")

exit()

with ftnimport.session(db) as sess:
  sess.send_message("Sergey Dorofeev", 
                    ("node", "2:5020/758"), "Alexey Gerasimov", 
                    None, "бэды", 
"""Привет 

Посмотри плз, нет ли от меня бэдов и нераспакованной почты. Если есть, запакуй в архив и 
выложи мне на холд пожалуйста - буду разбираться.

""")

exit()

with ftnimport.session(db) as sess:
  sess.send_message("Sergey Dorofeev", ("echo", "FLUID.LOCAL"), "All", None, "$CRACK$", 
"""Привет All!

Кто на $CRACK$ подписан, посмотрите, есть мессага с MSGID="2:5020/1955.4 4f3b1a82"
(там что-то про nod32)

""")


