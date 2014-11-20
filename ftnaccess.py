import ftnconfig

def may_subscribe(link, address):
  """ returns is the link allowed to subscribe to the address and 
      is it allowed to import by this subscription"""
  return True, True

def may_post(db, node_id, address):
  #print("*may post* check")
  print ("subscriber id", node_id)
  print ("address", address)
  domain_id = db.FTN_domains[address[0]]
  addr_id = db.prepare("select id from addresses where domain=$1 and text=$2").first(domain_id, address[1])
  if addr_id is None:
    print ("unknown address, checking autocreate")
    x=db.prepare("select count(id) from links where address=$1 and $2 = any(autocreate)").first(node_id, domain_id)
    if x!=1:
      print ("autocreate is not allowed")
      return False
    print ("autocreate is permitted")
    return True
  #print ("area id", addr_id)
  x=db.prepare("select id from subscriptions where subscriber=$1 and target=$2 and writable=true")(node_id, addr_id)
  #print ("subscriptions", x)
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

def check_link(db, addr_id, password, forrobots):
  "returns local address that is linked with remote address and verified with specified password"
  matching = []
  link_exists = False

  password = password or ""
  for myaddr_id, authinfo, link_id in db.prepare(
        "select l.my, l.authentication, l.id "
        "from links l where l.address=$1")(addr_id):
    link_exists = True

    pw = ""
    if forrobots:
      if authinfo.find("RobotsPassword") is not None:
        pw = authinfo.find("RobotsPassword").text
    else:
      if authinfo.find("ConnectPassword") is not None:
        pw = authinfo.find("ConnectPassword").text

    if check_pw(pw, password):
      matching.append((link_id, myaddr_id))

  if len(matching)>2:
    raise Exception("two links for %s with same local address and password in database"%address)

  if link_exists:
    if len(matching)==0:
      print ("no match for specified password") # log bad password
      return None, None
    return matching[0][0], matching[0][1] # checked link with known local address

  return None, ftnconfig.get_addr_id(db, db.FTN_domains["node"], ftnconfig.ADDRESS) # no link, use default address

