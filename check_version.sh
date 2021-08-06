#!/bin/bash

CURR_V=$(poetry version)
cd ..
git clone https://github.com/FANTM/devlprd devlprd-main
cd devlprd-main
MAIN_V=$(poetry version)
cd ..
rm -rf devlprd-main
if [[ $MAIN_V = $CURR_V ]]
then
	echo "Bump the version!"
	exit 1
else
	exit 0
fi
