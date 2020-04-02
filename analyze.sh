#!/bin/bash

FILE='cyber-dataset.csv'
#FILE='scifi-dataset.csv'
#FILE='best-scifi-dataset.csv'

# TOP 15

TOP_15_RATING=$(cat $FILE | cut -d\; -f6 | sed 's/,//g' | sort -rn | head -n 30)

for B in $(echo $TOP_15_RATING); do
	TITLE=$(grep $B $FILE | cut -d\; -f2 | sed 's/[(].*//')
	AUTHOR==$(grep $B $FILE | cut -d\; -f2 | sed 's/[(].*//')
	echo "$B $TITLE"
done



