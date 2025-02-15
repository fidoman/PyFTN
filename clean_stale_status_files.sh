for a in *.status ; do b=${a%.status} ; if [ ! -e $b.msg ] ; then echo $a banadoned ; rm $a ; fi ; done
