#!/bin/sh
sed -i \
         -e 's/#ffffff/rgb(0%,0%,0%)/g' \
         -e 's/#44537f/rgb(100%,100%,100%)/g' \
    -e 's/#ffffff/rgb(50%,0%,0%)/g' \
     -e 's/#87bdff/rgb(0%,50%,0%)/g' \
     -e 's/#ffffff/rgb(50%,0%,50%)/g' \
     -e 's/#3a3432/rgb(0%,0%,50%)/g' \
	$@
