#!/bin/sh
sed -i \
         -e 's/rgb(0%,0%,0%)/#ffffff/g' \
         -e 's/rgb(100%,100%,100%)/#44537f/g' \
    -e 's/rgb(50%,0%,0%)/#ffffff/g' \
     -e 's/rgb(0%,50%,0%)/#87bdff/g' \
 -e 's/rgb(0%,50.196078%,0%)/#87bdff/g' \
     -e 's/rgb(50%,0%,50%)/#ffffff/g' \
 -e 's/rgb(50.196078%,0%,50.196078%)/#ffffff/g' \
     -e 's/rgb(0%,0%,50%)/#3a3432/g' \
	$@
