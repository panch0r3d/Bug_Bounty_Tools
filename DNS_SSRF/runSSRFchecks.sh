#!/bin/bash
#Get input and output files
input=`echo "$1"`
output=`echo "$2"`
echo '[*] Start getSSRFResponses.py'
pingaddr=`curl -IL http://pingb.in | grep -i "Location: " | sed 's/Location: //g' | cut -b 2-999999 | sed 's/\r//g'`
python ./getSSRFResponses.py ${input} ${pingaddr}.REPLACE.${pingaddr}.ns.pingb.in > ${output}
echo "" >> ${output}
echo "" >> ${output}
echo "[*] ping results" >> ${output}
echo "" >> ${output}
echo "${pingaddr}"
echo "http://pingb.in/${pingaddr}/history" >> ${output}
curl -v "http://pingb.in/${pingaddr}/history" >> ${output}
echo '[*] getSSRFResponses.py Complete'
