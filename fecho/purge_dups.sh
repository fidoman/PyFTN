find . -type f | while read f ; do echo -n "$f "; /tank/fido/home/PyFTN/fecho/ftndups.py "$f" && echo dup && rm "$f" ; done
