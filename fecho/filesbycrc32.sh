#!/bin/bash

find . -maxdepth 1 -type f -not -iname '*.tic' \
-not -iname '*.mo?' -not -iname '*.tu?' -not -iname '*.we?' -not -iname '*.th?' -not -iname '*.fr?' -not -iname '*.sa?' -not -iname '*.su?' \
-not -iname '*.mo?-*' -not -iname '*.tu?-*' -not -iname '*.we?-*' -not -iname '*.th?-*' -not -iname '*.fr?-*' -not -iname '*.sa?-*' -not -iname '*.su?-*' \
-not -iname '*.bad' -not -iname '*.dup' -not -iname '*.status' -not -iname '*.pkt' -not -iname '*.pkt-*' | while read x
#
do
    x=`basename "$x"`
    csum=`crc32 "$x"`
    mkdir -p $csum
    mod=0
    src="$x"
    while [[ -f $csum/$x ]]
    do
      x="${x%___*}___$mod"
      mod=$((mod+1))
    done
    echo [$x] $csum
    mv -n "$src" "$csum/$x"
done
