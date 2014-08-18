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

def check_link(db, address, password, forrobots):
  "returns local address that is linked with remote address and verified with specified password"
  matching = []
  link_exists = False

  password = password or ""
  for my, authinfo in db.prepare("select ma.text, l.authentication from links l, addresses a, addresses ma "
                    "where l.address=a.id and a.domain=$1::integer and a.text=$2::varchar and ma.id=l.my")(db.FTN_domains["node"], address):
    link_exists = True

    pw = ""
    if forrobots:
      if authinfo.find("RobotsPassword") is not None:
        pw = authinfo.find("RobotsPassword").text
    else:
      if authinfo.find("ConnectPassword") is not None:
        pw = authinfo.find("ConnectPassword").text

    if check_pw(pw, password):
      matching.append(my)

  if len(matching)>2:
    raise Exception("two links for %s with same local address and password in database"%address)

  if link_exists:
    if len(matching)==0:
      print ("no match for specified password") # log bad password
      return link_exists, None
    return link_exists, matching[0] # checked link with known local address

  return link_exists, ftnconfig.ADDRESS # no link, use default address
