#!/usr/local/bin/python3 -bb

import re
import os
import ftnconfig
import ftnimport

import datetime

today=datetime.datetime.now(datetime.timezone.utc)
h=today.hour
m=today.minute
s=today.second
mks=today.microsecond
x=datetime.timedelta(seconds=h*3600+m*60+s, microseconds=mks)

today = today-x

yesterday=today-datetime.timedelta(1)

#print(today)
#print(yesterday)

lines=[]

prv_area=None

db=ftnconfig.connectdb()
for area, fname, fsize, recv_timestamp, recv_from in db.prepare(
    "select (select text from addresses where id=fp.destination), fp.filename, "
           "(select length from files where id=fp.filedata), "
           "fp.recv_timestamp, "
           "(select text from addresses where id=fp.recv_from) "
    "from file_post fp, addresses a "
    "where a.id=fp.destination and fp.recv_timestamp>=$1 and fp.recv_timestamp<$2 "
    "order by a.text, fp.filename")(yesterday, today):

    if prv_area is not None and prv_area!=area:
      lines.append("\n")
      prv_area = area

    lines.append("%-20s %-22s %-9d %-23s\n"%(area, fname, fsize, recv_from))

#    print(lines[-1])
#exit()

with ftnimport.session(db) as sess:
  sess.send_message(("node", ftnconfig.ADDRESS), "Sergey Dorofeev", ("echo", "FLUID.REPORTS"), "All", None, "файлэхи",
"""
%s
"""%("".join(lines)))
