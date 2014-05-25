#!/usr/local/bin/python3 -bb

import ftnexport
import ftnconfig
import os

db=ftnconfig.connectdb()
address="2:5020/4441"
password="TIW229LQ"
classes=["echomail"]
outdir=os.path.join("static", address.replace("/", ".").replace(":","."))
os.makedirs(outdir, exist_ok=True)

def log(s):
  print("fileexport:", s)

for outbfile, committer in ftnexport.file_export(db, address, password, classes):
    if outbfile is not None:
        log("outbound file "+outbfile.filename+ " " + str(outbfile.length) + " bytes")
        outf=open(os.path.join(outdir,outbfile.filename), "xb")

        while True:
            d = outbfile.data.read(16384)
            if len(d)==0:
                break
            written = outf.write(d)
            if written != len(d):
                raise Exception("error on write %d of %d"%(written, len(d)))

        outf.close()

    committer.commit()
