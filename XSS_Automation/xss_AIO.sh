#!/bin/bash
line=`echo $1`
rowstart="1"
rowend="100"
rndnum=$RANDOM
tmpfile=/tmp/$rndnum.crawllogs.txt
tmpout=/tmp/$rndnum.crawllogsout.txt
#Get domains from pi server
wget http://192.168.1.114:8000/domains/${line}subdomainscleaned.txt -O /usr/share/domains/${line}subdomainscleaned.txt
#Crawl links for domains
/usr/share/scripts/brokenlinkcrawl.sh /usr/share/domains/${line}subdomainscleaned.txt /usr/share/crawllogs/${line}.txt
#clean crawled links file
grep -o 'http[s]\?://[^"]\+$' /usr/share/crawllogs/${line}.txt | grep -v '[ ]' | grep -v '\.svg$' | grep -v '\.jpeg$' | grep -v '\.jpg$' | grep -v '\.png$' |sort -u > /usr/share/crawllogs/${line}cleaned.txt
totrows=`wc -l < /usr/share/crawllogs/${line}cleaned.txt`
touch /usr/share/crawllogs/xsslogs/${line}.txt &> /dev/null
while [ $rowstart -lt $totrows ]
  do
    eval "sed -n '$rowstart,$rowend""p' /usr/share/crawllogs/${line}cleaned.txt > $tmpfile"
    echo "[*] Processing rows $rowstart through $rowend of $totrows rows in file "
    #run Dalfox with XSS hunter blind payloads and parameter list
    cat $tmpfile | timeout 1200s dalfox pipe -b "https://YOURUSERNAME.xss.ht" --silence --mining-dict-word /usr/share/wordlists/parameters_500.txt | tee -a $tmpout
    cat $tmpout >> /usr/share/crawllogs/xsslogs/${line}.txt
    rowstart=$[rowstart+100]
    rowend=$[rowend+100]
    sleep 1
  done
#Update common files
grep -r '\.js' /usr/share/crawllogs/ | grep 'http[s]\?://[^"]\+$' | grep -v '[ ]' | grep -v '\.svg$' | grep -v '\.jpeg$' | grep -v '\.jpg$' | grep -v '\.png$' | grep -v '\.jsp' | sed 's/\/usr\/share\/crawllogs\/.*txt://g' | sort -u > /usr/share/scripts/allcrawledjs.txt
grep -r '\.js' /usr/share/crawllogs/ | grep "BROKEN" | grep 'http[s]\?://[^"]\+$' | grep -v '\.svg$' | grep -v '\.jpeg$' | grep -v '\.jpg$' | grep -v '\.png$' | grep -v '\.jsp' | sort -u > /usr/share/scripts/allbrokencrawledjs.txt
grep -r '\.js' /usr/share/crawllogs/ | grep "ERR" | grep 'http[s]\?://[^"]\+$' | grep -v '\.svg$' | grep -v '\.jpeg$' | grep -v '\.jpg$' | grep -v '\.png$' | grep -v '\.jsp' | sort -u >> /usr/share/scripts/allbrokencrawledjs.txt
grep -r 'ENOTFOUND' /usr/share/crawllogs/ | grep "BROKEN" | grep -v '\.jpeg ' | grep -v '\.jpg ' | grep -v '\.png ' | grep -v '\.gif ' | grep -v '\.ico ' | sort -u > /usr/share/scripts/allbrokencrawledlinks.txt
grep -r '\[POC\]' /usr/share/crawllogs/xsslogs | sort -u > /usr/share/scripts/allPOClogs.txt
grep -r 'http' /usr/share/crawllogs/ | grep 'http[s]\?://[^"]\+$' | grep -v '[ ]' | grep -v '\.svg$' | grep -v '\.jpeg$' | grep -v '\.jpg$' | grep -v '\.png$' | sed 's/\/usr\/share\/crawllogs\/.*txt://g'| sort -u > /usr/share/scripts/allcrawledlinks.txt
grep -r 'http' /usr/share/crawllogs/ | grep 'http[s]\?://[^"]\+$' | grep -v '[ ]' | grep -v '\.svg$' | grep -v '\.jpeg$' | grep -v '\.jpg$' | grep -v '\.png$' | sort -u > /usr/share/scripts/allcrawledlinksreference.txt
