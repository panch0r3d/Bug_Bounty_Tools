#!/bin/bash
#Get input file
input=`echo "$1"`
output=`echo "$2"`
i="1"
rndnum=$RANDOM
totrows=`wc -l < $input`
touch $output
if [ $# -ne 2 ];then
  echo "Usage: ./brokenlinkcrawl.sh [Input URL File] [Output File]"
else
  for line in $(cat $input)
  do
    echo "[*] Processing ($i of $totrows)"

    echo "URL:   $line " 
    timeout 1800s blc $line -ro --filter-level 3 --exclude twitter.com --exclude facebook.com --exclude google.com --exclude instagram.com --exclude youtube.com --exclude linkedin.com --exclude vimeo.com | tee -a $output
    echo "-----------------------------------------------------" >> $output
    sleep 1
  ((i=i+1))
  done < "$input"
fi
