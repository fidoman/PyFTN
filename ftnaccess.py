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

def check_link(db, address, password, forrobots):
  "returns local address that is linked with remote address and verified with specified password"
  # returns link_id, addr_id or None, myaddr_id or None
  matching = []
  link_exists = False

  password = password or ""
  for addr_id, myaddr_id, authinfo, link_id in db.prepare(
        "select a.id, l.my, l.authentication, l.id "
        "from links l, addresses a "
        "where l.address=a.id and a.domain=$1 and a.text=$2")(db.FTN_domains["node"], address):
    link_exists = True

    pw = ""
    if forrobots:
      if authinfo.find("RobotsPassword") is not None:
        pw = authinfo.find("RobotsPassword").text
    else:
      if authinfo.find("ConnectPassword") is not None:
        pw = authinfo.find("ConnectPassword").text

    if check_pw(pw, password):
      matching.append((link_id, addr_id, myaddr_id))

  if len(matching)>2:
    raise Exception("two links for %s with same local address and password in database"%address)

  if link_exists:
    if len(matching)==0:
      print ("no match for specified password") # log bad password
      return None, None, None
      # return None addr_id as remote link cannot prove address validity
    return matching[0][0], matching[0][1], matching[0][2] # checked link with known local address

  return None, \
    db.prepare("select id from addresses where domain=$1 and text=$2").first(db.FTN_domains["node"], address), \
    ftnconfig.get_addr_id(db, db.FTN_domains["node"], ftnconfig.ADDRESS) # no link, use default address

# Tests:
#  check valid link
#  check existing link with bad password
#  check non-existent link with known address
#  check non-existent link with UNknown address

# may_post
#   subscribed link
#   unsubscribed link
#   link with autocreate to existing but not subscribed echo
#   link without autocreate to non-existent echo

if __name__=="__main__":
  db = ftnconfig.connectdb()
  print("y",may_post(db, ftnconfig.get_addr_id(db, db.FTN_domains["node"], "2:5020/12000.1"), ("echo", "FLUID.LOCAL")))
  print("n",may_post(db, ftnconfig.get_addr_id(db, db.FTN_domains["node"], "2:5020/4441"), ("echo", "FLUID.LOCAL")))
  print("y",may_post(db, ftnconfig.get_addr_id(db, db.FTN_domains["node"], "2:5020/4441"), ("echo", "FLUID.KINO")))
  
  print("y", check_link(db, "2:5020/12000.1", "<real passw>", False))
  print("n", check_link(db, "2:5020/12000.1", "sfefe", False))
  print("ok", check_link(db, "2:5030/585", "", False))
  print("ok", check_link(db, "2:5011/1122", "", False))
