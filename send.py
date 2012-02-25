#!/bin/env python3

from ftnconfig import *
import ftnimport

db=connectdb()

exit()

with ftnimport.session(db) as sess:
  sess.send_message("Sergey Dorofeev", ("echo", "FLUID.LOCAL"), 
        "All", None, "попытка #2", 
"""Привет Eugene!

В base64

4C5ZEdwHAgAXABIAGwAiAAAAAgCcE5wTAABLRDM4OUJUNQIAAgAAAAAAAAABAAIAAgAAAAAAWFBL
VAIA4C5ZEZwTnBMAAAAAMjMgRmViIDEyICAxODoyMzoxMABBbGwAU2VyZ2V5IERvcm9mZWV2AK/g
rqKl4KqgIOGi76eoAEFSRUE6TU8uSVpNQUlMT1ZPDQFNU0dJRDogMjo1MDIwLzEyMDAwIGI2MzU4
NTI4ODU5NzRkNzcxYTE0OTBjN2IyZDg2OTM0NTY0MzM0NGQNAUNIUlM6IENQODY2IDINj+CooqXi
IEFsbA0NnyCkqKquIKinoqit7+7h7Cwgra4g7eKuIJKFkZIuDYjioKogoq6v4K7hOiCspa3vIKKo
pK2uPyA6KQ0NDS0tLSBQeUZUTg0gKiBPcmlnaW46IGZsdWlkLmZpZG9tYW4ucnUgKDI6NTAyMC8x
MjAwMCkNU0VFTi1CWTogNTAyMC83NyA4NDggMTk1NSAyMDY1IDQ0NDEgMTIwMDANAVBBVEg6IDUw
MjAvMTIwMDANAAAA


""")
exit()





with ftnimport.session(db) as sess:
  sess.send_message("Sergey Dorofeev", 
                    ("node", "2:5020/4441"), "Yuri Myakotin", 
                     None, "прохождение почты", 
"""Привет 

Нашёл у себя один косяк - capability word с перестановленными
байтами не записывалось. Из-за этого может в бэды выпадать?
Сейчас ещё раз мо.измайлово отресканил.

""")
exit()


