import urllib2
import ssl
import sys
#import re
#import time
from socket import error as SocketError

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headerbase = sys.argv[4]
header = headerbase
try:
 getbody = int(sys.argv[5])
except:
 getbody = 500

i = 0

while (i < int(sys.argv[3])):
  header = header + headerbase
  i += 1
  #print i
  #print header

opener = urllib2.build_opener(urllib2.HTTPSHandler(context=ctx))
opener.addheaders = [(sys.argv[2], header)]
try:
 response = opener.open(sys.argv[1], timeout=4)
except SocketError as e:
 response =  e.errno
 title = ""
 length = "0"
 respheaders = ""
 data = ""
except urllib2.HTTPError as e:
 data = e.read()
 #match = re.search('<title>(.*?)</title>', data)
 #title = match.group(1) if match else 'No title'
 title = ""
 respheaders = ""
 response = e.code
 length = "1"
except urllib2.URLError as e:
 print 'urllib2.URLError'
 data = response.read()
 #match = re.search('<title>(.*?)</title>', data)
 #title = match.group(1) if match else 'No title'
 title = ""
 respheaders = response.info()
 response = e.reason
 length = "0"
else:
 data = response.read()
 #match = re.search('<title>(.*?)</title>', data)
 #title = match.group(1) if match else 'No title'
 respheaders = response.info()
 response = response.getcode()
 length = len(data)
#print str(title).strip()
print "content-Length: ",str(length).strip()
print "Response Code: ",str(response).strip()
print "Response Headers: "
print respheaders
print data[0:getbody]
