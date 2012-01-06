#!/usr/bin/python

import shlex, sys

import ftnimport

nodes={}

for l in file("import/fidogate-passwd"):
 try:
  x=shlex.split(l, "#")
  if not x:
    continue
  node=x[1]
  nodeinfo=nodes.setdefault(node, {})
  if x[0]=="packet":
    nodeinfo["pktpasswd"]=x[2]

  elif x[0]=="af":
    if nodeinfo.has_key("robotpasswd"):
      if nodeinfo["robotpasswd"]!=x[2]:
        raise Exception("different robot pwd for %s"%node)
    else:
      nodeinfo["robotpasswd"]=x[2]
    nodeinfo["echolevel"]=x[3]
    nodeinfo["echogroups"]=x[4]

  elif x[0]=="ff":
    if nodeinfo.has_key("robotpasswd"):
      if nodeinfo["robotpasswd"]!=x[2]:
        raise Exception("different robot pwd for %s"%node)
    else:
      nodeinfo["robotpasswd"]=x[2]
    nodeinfo["fecholevel"]=x[3]
    nodeinfo["fechogroups"]=x[4]

  else:
    raise Exception("unknown record type %s"%x[0])

 except Exception as e:
  print "error on %s"%`l`
  raise e

counter=0
for n, i in nodes.items():
  sys.stdout.write("%-23s %d/%d\r"%(n, counter, len(nodes)))
  sys.stdout.flush()
  ftnimport.import_link_auth(n, i["pktpasswd"], i.get("robotpasswd", i["pktpasswd"]), i.get("echolevel"), i.get("fecholevel"), i.get("echogroups"), i.get("fechogroups"))
  counter+=1
