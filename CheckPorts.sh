#!/bin/bash
#Get input file
input=`echo "$1"`
#output=`echo "$2"`
i="1"
mkdir /tmp/CheckPort &> /dev/null
rndnum=$RANDOM
tmpfile=/tmp/CheckPort/$rndnum.CheckPort.txt
tmpscript=/tmp/CheckPort/$rndnum.script.txt
grep ':' $input | grep -v ':8443' | grep -v ':8080' | sort | uniq > $tmpfile
totrows=`wc -l < $tmpfile`
if [ $# -ne 1 ];then
  echo "Usage: ./CheckPorts.sh [Input Domains File] [Output File]"
else
  for line in $(cat $tmpfile)
  do
    echo "---------------------------------------------------------------------------------------"
    echo "|[*] Processing ($i of $totrows)"
    # Make script file for telnet
    rm $tmpscript &> /dev/null
    url_port="${line/':'/' '}"
    echo "|URL PORT $url_port"
    echo "echo 'open $url_port'" >> $tmpscript
    echo "sleep 4" >> $tmpscript
    echo "echo help" >> $tmpscript
    echo "sleep 2" >> $tmpscript
    echo "echo PWD" >> $tmpscript
    echo "sleep 1" >> $tmpscript
    echo "echo quit" >> $tmpscript
    echo "echo q" >> $tmpscript
    chmod +x $tmpscript
    #Process in Telnet
    echo "---------------------------------------------------------------------------------------"
    echo "|URL:   $line "
    echo "---------------------------------------------------------------------------------------"
    $tmpscript | telnet | tee -a /tmp/CheckPort/$rndnum.CheckPortOut.txt
    echo ""
    echo ""
  ((i=i+1))
  done < "$input"
  rm $tmpfile &> /dev/null
  rm $tmpscript &> /dev/null
  rm /tmp/CheckPort/$rndnum.CheckPortOut.txt &> /dev/null
fi
