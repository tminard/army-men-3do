#!/usr/bin/env bash

set -e

echo -n "Copy $PWD/output/sprites/*.png to /mnt/c/Users/Desktop/output/$1 (Y/n)? "
read conf

if [ $conf = "Y" ]; then
	mkdir /mnt/c/Users/adelp/Desktop/output/$1 && cp $PWD/output/sprites/*.png /mnt/c/Users/adelp/Desktop/output/$1
else
	echo "Aborted copy"
fi
