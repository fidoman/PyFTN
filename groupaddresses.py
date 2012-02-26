#!/bin/env python3 -bb

from ftnconfig import *
import ftnimport

# Part I. Nodes
# 1. Group points to nodes
# 2. Group nodes to hubs
# 3. Group hubs and free nodes to hosts
# 4. Group hosts and free nodes to regions
# 5. Group regions to zones

db=connectdb()

update_group=db.prepare("update addresses set \"group\" = $1 where id=$2")

def group_points():

  with db.xact():
    for n_id, n_text, p_id, p_text, p_group in db.prepare(
        "select n.id, n.text, p.id, p.text, p.group from addresses n, addresses p "
        "where n.domain=$1 and p.domain=$1 and p.text LIKE n.text || '.%'")(db.FTN_domains["node"]):
      if p_group!=n_id:
        print("update point:", n_text, "<-", p_text, p_group==n_id)
        update_group(n_id, p_id)

  with ftnimport.session(db) as sess:
    for p_id, p_text in db.prepare("""select id, text from addresses where "group" is NULL and text LIKE '%:%/%.%' and domain=$1""")(db.FTN_domains["node"]):
      newnode=p_text[:p_text.rfind(".")]
      print("point without node:", p_id, p_text, p_text[:p_text.rfind(".")])
      newid=sess.check_addr(db.FTN_domains["node"], newnode)
      print("addind new node and grouping to", newnode)
      update_group(newid, p_id)


print("grouping points...")
group_points()

print("grouping by nodelist")

groups = {0: None}
leveln = 1

zone = None
region = None
network = None
hub = None

with ftnimport.session(db) as sess:
 
 # load nodelist
 for l in open(NODELIST):
  l=l.split(";")[0].rstrip()
  if not l or len(l)==1: continue

  level, addr, name, loc, sysop, phone, flags = l.split(',', 6)

  if leveln == 0:
    print("top level")

  curr_leveln = leveln

  if level=='Zone':
    leveln = 1
    zone = addr
    region = '0'
    network = '0'
    node = '0'
  elif level=='Region':
    leveln = 2
    region = addr
    network = region
    node = '0'
  elif level=='Host':
    leveln = 3
    network = addr
    node = '0'
  elif level=='Hub':
    leveln = 4
    node = addr
  else:
    leveln = 5
    node = addr

  for ll in range(leveln, 6):
    groups[ll] = (zone, network, node)


  node_address = "%s:%s/%s"%(zone, network, node)
  if groups[leveln-1] is None:
    print(node_address + " not grouped")
    continue
  
  group_address = "%s:%s/%s"%groups[leveln-1]

  node_id = sess.check_addr(db.FTN_domains["node"], node_address)
  group_id = sess.check_addr(db.FTN_domains["node"], group_address)

  oldgroup_id = db.prepare("""select "group" from addresses where domain=$1 and text=$2""").first(db.FTN_domains["node"], node_address)

  #print("%s (%d) %s %s --> %s (%d)"%(node_address, node_id, name, str(oldgroup_id), group_address, group_id))
  if oldgroup_id != group_id:
    update_group(group_id, node_id)

  #....
  #print('|'.join((level, addr, name, loc, sysop, phone, flags)))
  


# Part II. Echoes
# 1. Group areas and fareas to respective "backbones"
# need trigger: notify subscriber of backbone of group membership change with sending
# subscribe/unsubscribe messages (if no subscription to individual area)
