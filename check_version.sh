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
	exit 0
else
	exit 1
fi
