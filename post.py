#!/usr/local/bin/python3 -bb

from ftnconfig import *
import ftnimport
import os

db=connectdb()

with ftnimport.session(db) as sess:
    for echo in os.listdir("post"):
        echopath = os.path.join("post", echo)
        for msg in os.listdir(echopath):
            msgpath = os.path.join(echopath, msg)
            #print (msgpath, msg, echo)
            text = open(msgpath).read()
            #print (text)

            sess.send_message("Sergey Dorofeev", ("echo", echo), 
                "All", None, msg, text)

