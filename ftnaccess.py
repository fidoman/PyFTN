import ftnconfig

def may_subscribe(link, address):
  """ returns is the link allowed to subscribe to the address and 
      is it allowed to import by this subscription"""
  return True, True

#def may_create():

def may_post(db, node, address):
  node_id = ftnconfig.get_addr_id(db, db.FTN_domains["node"], node)
  addr_id = ftnconfig.get_addr_id(db, db.FTN_domains[address[0]], address[1])
  x=db.prepare("select id from subscriptions where subscriber=$1 and target=$2")(node_id, addr_id)
  return len(x)>0

def check_pw(genuine, provided):
  if provided==genuine:
    return True
  if len(provided)==8 and provided==genuine[:8]: # if genuine is shorter than 8 chrs provided also must have the same length
    # it can match only if provided passwd is equal to genuine (if genuine is shorter than 8) or if it is equal to first 8 chars
    return True
  if len(provided)==8 and provided==genuine[:8].upper():
    return True
  return False
