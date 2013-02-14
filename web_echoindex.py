#!/usr/local/bin/python3 -bb

import ftnconfig
import ftnexport

db=ftnconfig.connectdb()

echoes = ftnexport.get_all_targets(db, "echo")

for echo in echoes:
  addr=ftnconfig.get_addr_id(db, db.FTN_domains["echo"], echo)
  print (echo, ftnexport.count_messages_to(db, addr))

