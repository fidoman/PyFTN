import sys
import os

import ftn.pkt

n=sys.argv[1]
n2="_".join(os.path.splitext(n))

p=ftn.pkt.PKT(n)
p.save(n2)
