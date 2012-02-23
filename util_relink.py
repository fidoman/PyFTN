#!/usr/local/bin/python3

area="MO.IZMAILOVO"

import ftnconfig
import ftnimport

db=ftnconfig.connectdb()

vital = db.prepare("select s.id, sr.domain, sr.text from subscriptions s, addresses t, addresses sr where s.target=t.id and t.domain=$1 and t.text=$2 and s.subscriber=sr.id and s.vital=true")

for subs, srd, srt in vital(db.FTN_domains["echo"], area):
    print (subs, "%d|%s"%(srd,srt))
