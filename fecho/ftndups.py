#!/usr/bin/python3

import hashlib
import sys
import ftnconfig

db=ftnconfig.connectdb()

Q1="select files.id, files.names, files.sha512, file_post.id, file_post.destination, to_char(to_timestamp(file_post.post_time), 'YYYY-MM-DD HH:MM:SS') as ts from file_post, files where file_post.filedata=files.id and files.sha512=$1 order by ts"


if len(sys.argv)>1:
    ffullname = sys.argv[1]

    sha512 = hashlib.new("sha512")
    f=open(ffullname, "rb")
    while(True):
      z=f.read(262144)
      if not z:
        break
      sha512.update(z)
    f.close()
    print(sha512.hexdigest())

#    print(help(db.prepare(Q1)))

    res=1
    for r in db.prepare(Q1).rows(sha512.digest()):
      print(r)
      res=0

    exit(res)

exit(2)
