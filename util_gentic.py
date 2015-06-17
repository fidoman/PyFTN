#!/usr/bin/python3

import ftnconfig
import ftntic
import json

files="""litg1336.rar
tropoi14.rar
tropoi18.rar
vert0001.rar
vert0104.rar
vert0203.rar
vert0204.rar
vert0301.rar
vert0303.rar""".split("\n")

db=ftnconfig.connectdb()

for f in files:
  print (f)
  for (fp,fp_origin,fp_destination,fp_filename, fp_other, f_size) in db.prepare("select fp.id, fp.origin, fp.destination, fp.filename, fp.other, f.length from file_post fp, files f where filename ilike $1 and fp.filedata=f.id")(f):
    print (fp)
    other= json.loads(fp_other)
    crc = other.pop("CRC", "00000000")[0]

    tic = ftntic.make_tic("2:5020/12000", "2:5059/37", "*", ftnconfig.get_addr(db, fp_destination)[1], ftnconfig.get_addr(db, fp_origin)[1] if fp_origin else None,
                fp_filename, f_size, crc, other)

    open("%d.tic"%fp, "wb").write(tic)
