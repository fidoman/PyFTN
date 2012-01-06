#!/usr/local/bin/python3

import shlex, sys
import fileinput
import traceback

import ftnimport

nodes={}

for l in fileinput.input("import/bforce.subst"):
  x=shlex.split(l, "#")
  if not x:
    continue
  if x[0]=="override":
    node=x[1]
    x=x[2:]
#    print node,
    info={}
    while len(x):
#      print x[0]+"="+x[1],
      if x[0].lower()=="ipaddr":
        if not x[1].endswith("fidonet.net"):
          info["addr"]=x[1]
      elif x[0].lower()=="worktime":
        info["time"]=x[1]
      elif x[0].lower()=="flags":
        for fl in x[1].lower().split(","):
          if fl=="cm":
            info["time"]="00:00-24:00"
          elif fl=="binkp":
            #info.setdefault("conn", []).append((binkp, info["addr"]))
            info["binkp"]=True
          elif fl=="ifc":
            info["ifcico"]=True
          else:
            raise Exception("unknown flag %s"%repr(fl))
      else:
        raise Exception("unknown parameter %s"%repr(x[0]))

      x=x[2:]
    nodes[node]=info

  else:
    raise Exception("bad - %s"%repr(l))

for l in fileinput.input("import/binkd.nl"):
  x=shlex.split(l, "#")
  if not x:
    continue
  if not x[2].endswith("fidonet.net"):
    nodes.setdefault(x[1], {})["addr"]=x[2]
    nodes.setdefault(x[1], {})["binkp"]=True
    nodes.setdefault(x[1], {})["time"]="00:00-24:00"

with ftnimport.session(ftnimport.db) as sess:
 counter=0
 for n, i in nodes.items():
  sys.stdout.write("%d[%d]\r"%(counter,len(nodes)))
  sys.stdout.flush()
  counter+=1
  if "addr" not in i:
    continue
  for proto in ["binkp", "ifcico"]:
    if proto in i:
      sess.import_link_conn(n, (proto, i["addr"], i["time"]))
