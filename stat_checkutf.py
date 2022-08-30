#!/usr/bin/python3

import os
import zipfile

import ftnconfig
import ftnimport

base = os.path.split(ftnconfig.NODELIST)[0]

zippedfile=os.path.join(base, 'DAILYUTF.ZIP')
z = zipfile.ZipFile(zippedfile)

outp=[]

for zf in z.namelist():
  outp.append("Checking file %s"%zf)

  u = z.open(zf)
  l_pos=1
  ascii_count = 0
  utf8_count = 0
  error_count = 0

  for l in u:
    try:
      l.decode("ascii")
      ascii_count +=1
      l_pos+=1
      continue
    except:
      pass

    try:
      l.decode("utf-8")
      utf8_count +=1
      l_pos+=1
      continue
    except:
      pass

    l1=l.decode("utf-8", "replace")
    outp.append("Error on line %d"% l_pos)
    outp.append(l1.strip())
#    print(repr(l1))
    error_count +=1

    l_pos+=1


  u.close()

  outp.append("ASCII lines: %d"%ascii_count)
  outp.append("UTF-8 lines: %d"%utf8_count)
  outp.append("Error lines: %d"%error_count)


db = ftnconfig.connectdb()

with ftnimport.session(db) as sess:
  sess.send_message(("node", ftnconfig.ADDRESS), "Sergey Dorofeev", ("echo", "FLUID.REPORTS"), "All", None, "UTF-8 nodelist stats",
"""Привет All

%s

Вот так
"""%("\n".join(outp)))
