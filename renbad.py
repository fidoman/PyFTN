#!/usr/local/bin/python3

# run within directory!!!

import os

good=["MO", 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']

def mkext(counter):
  inc='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
  day=int(counter/len(inc))
  if day>=len(good): 
    print("no more exts")
    exit(-1)
  pos=counter%len(inc)
  return good[day] + inc[pos]

c=0

for z in os.listdir('.'):
  if z.endswith(".PKT"): continue
  if z[8]!='.': continue
  if len(z) not in [12,21,20,19,18]: continue
  if len(z)==12 and z[9:11] in good: continue
  new='FFFFFFFF.'+mkext(c)
  print(z, new)
  while 1:
    try:
      if not os.path.exists(new):
        os.rename(z, new)
      break
    except Exception as e:
      print(e)
    finally:
     c+=1

#c=0
#while 1:
#  print mkext(c)
#  c+=1
