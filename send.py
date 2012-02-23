#!/bin/env python3

from ftnconfig import *
import ftnimport

db=connectdb()

with ftnimport.session(db) as sess:
  sess.send_message("Sergey Dorofeev", ("echo", "FLUID.LOCAL"), 
        "Eugene Palenock", None, "что с фидо?", 
"""Привет

Отправь тест убедиться что всё идёт и скажи мне путь который там увидишь. Я отравлю заново.
Если скажешь msgid последнего сообщения, которое там есть от 19-го, будет вообще отлично.

""")

exit()


with ftnimport.session(db) as sess:
  sess.send_message("Sergey Dorofeev", ("echo", "N5020.SYSOP"), "All", None, "",
"""Привет All

Так нормально?

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

