import mmh3
import random
import string
import urllib
import urllib.request as urlreq
import re
import json
import sys
import time
import os.path
import gzip
import requests
import codecs
import ssl
import socket
from urllib.parse import urlparse
from os import path
from colorama import Fore, Back

i = 0
quiet = "false"
headerfile = sys.argv[2]
sleepamt = float(sys.argv[3])
testoptions = sys.argv[4]
headerstxt = ""
respsize = 0
respstatus = ""

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def testurl(url, showresponse=0, responseheaders=0, baseline=0):
    try:
        headerdict = json.loads(headerstxt)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
        rqobj = urlreq.Request(url, None, headers)
        if (headerstxt != ""):
            for key in headerdict:
                rqobj.add_header(key, headerdict[key])
        result = urlreq.urlopen(rqobj, context=ctx)
        responsebody = result.read()
        print("------------------------------------------------------------------------------------------------")
        print(Fore.GREEN + "URL: " + url)
        print(Fore.WHITE + "HTTP Status: " + str(result.status))
        print("Response Size:" + str(len(responsebody)))
        if (baseline == 1):
            respsize = len(responsebody)
            respstatus = str(result.status)
            #print(respsize)
            #print(respstatus)
        else:
            respsize = 0
        piiList = ""
        if (showresponse == 1):
            print("Response Sample:")
            try:
                print(gzip.decompress(responsebody)[:300])
                if re.search(r'\S+@\S+', gzip.decompress(responsebody)):
                    piiList = piiList + " email |"
                if re.search('(lastname|firstname|first.name|last.name)', gzip.decompress(responsebody), re.IGNORECASE):
                    piiList = piiList + " name |"
            except:
                print(responsebody.decode("UTF-8", 'strict')[:300])
                if re.search(r'\S+@\S+', responsebody.decode("utf8", 'ignore')):
                    piiList = piiList + " email |"
                if re.search('(lastname|firstname|first.name|last.name)', responsebody.decode("UTF-8", 'strict'), re.IGNORECASE):
                    piiList = piiList + " name |"
        if (responseheaders == 1):
            print("")
            print("Response Headers:")
            respheaders = result.info()
            print(respheaders)
        if (piiList != ""):
            print(Fore.RED + " Possible PII ( |" + piiList + ") Found")
        return (True, result.url)
    except urllib.error.URLError as e:
        print(Fore.GREEN + "URL: " + url)
        try:
            print(Fore.RED + "HTTP Status: " + str(e.reason))
            #print(e.read(300).decode("utf8", 'ignore'))
            #response = str(e.read().decode("utf8", 'ignore'))
            responsebody = e.read()
            try:
                print(gzip.decompress(responsebody)[:300])
            except:
                print(e.read(300).decode("utf8", 'ignore'))
            #regex results to check for some particular frameworks in debug mode
            if re.search(r'DEBUG...True', responsebody):
                print(Fore.RED + " Possible Django Debug Page Found")
            if re.search(r'Whoops..There was an error', responsebody):
                print(Fore.RED + " Possible Laravel Debug Page Found")
        except:
            print(Fore.RED + "An error occurred")
        print(Fore.WHITE + "")
        return (False, '')
    except:
        return (False, '')

def testversion(url):
    print(Fore.WHITE + "------------------------------------------------------------------------------------------------")
    print("Try to identify API versioning if any")
    apiverions = [
    "v1","v2","v3","v4",
    "v5","v6","v7","v8",
    "v9","v10","v99","vtest",
    "vdev","dev","test","prod",
    "v1.0","v2.0","v3.0","v4.0",
    "v5.0","v6.0","v7.0","v8.0",
    "v9.0","v10.0","1","2",
    "3","4","5","6",
    "7","8","9","10",
    "api-1.0","api-2.0","api-3.0",
    "."
    ]
    regexresult = ""
    hasversioning = 0
    if re.search(r'/v[0-9]/', url):
        regexresult = re.search(r'/v[0-9]/', url)
        print(Fore.BLUE + "")
        print("Found versioning: " + regexresult.group(0))
        hasversioning = 1
        print(Fore.WHITE + "")
    if re.search(r'/v[0-9][.][0-9]+/', url):
        regexresult = re.search(r'/v[0-9][.][0-9]+/', url)
        print(Fore.BLUE + "")
        print("Found versioning: " + regexresult.group(0))
        hasversioning = 1
        print(Fore.WHITE + "")
    if re.search(r'/api-[0-9.]+/', url):
        regexresult = re.search(r'/api[0-9_\-.]+/', url)
        print(Fore.BLUE + "")
        print("Found versioning: " + regexresult.group(0))
        hasversioning = 1
        print(Fore.WHITE + "")
    if (hasversioning == 1):
        for version in apiverions:
            newurl = url.replace(regexresult.group(0), "/" + version + "/")
            #print(newurl)
            testurl(newurl, 1)
            time.sleep(sleepamt)
    else:
        print(Fore.RED + "No versioning identified")
        print(Fore.WHITE)

def testmethod(url):
    print(Fore.WHITE + "------------------------------------------------------------------------------------------------")
    print("Testing HTTP Methods")
    print("")
    httpverbs = [
    "GET","POST","PUT","PATCH",
    "DELETE","COPY","HEAD","OPTIONS",
    "LINK","UNLINK","PURGE","LOCK",
    "UNLOCK","PROPFIND","VIEW","CONNECT",
    "GARBAGE"
    ]
    overrideverbs = [
    "POST","PUT","PATCH","DELETE","GET"]
    overrideheaders = [
    "X-HTTP-Method-Override","X-HTTP-Method","X-Method-Override"]
    testverbs = [
    "GET","HEAD","OPTIONS"]
    try:
        headerdict = json.loads(headerstxt)
    except:
        headerdict = ""
    for verb in httpverbs:
        try:
            rqobj = urlreq.Request(url, None, method=verb)
            if (headerstxt == ""):
                #Add a default user agent to help things go well
                rqobj.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)')
            else:
                for key in headerdict:
                    rqobj.add_header(key, headerdict[key])
            print(Fore.GREEN + "Trying " + verb )
            result = urlreq.urlopen(rqobj, context=ctx)
            print(Fore.WHITE + "------------------------------------------------------------------------------------------------")
            print(Fore.GREEN + "URL: " + url)
            print(Fore.WHITE + "HTTP Status: ")
            print(result.status)
            responsebody = result.read()
            print("Response Size:" + str(len(responsebody)))
            print("Sample data returned: ")
            try:
                print(gzip.decompress(responsebody)[:300])
                print(newdata)
            except:
                print(responsebody[:300])
                print(newdata)
            return (True, result.url)
        except urllib.error.URLError as e:
            print(Fore.WHITE + "------------------------------------------------------------------------------------------------")
            print(Fore.RED + "Error Returned:" + str(e.reason))
            try:
                print(e.read(300).decode("utf8", 'ignore'))
                print(newdata)
            except:
                print(Fore.WHITE + "")
        except:
            print(Fore.WHITE + "")
        time.sleep(sleepamt)
    #Check for verb overrides
    for override in overrideheaders:
        for verb in overrideverbs:
            for test in testverbs:
                try:
                    rqobj = urlreq.Request(url, None, method=test)
                    if (headerstxt == ""):
                        #Add a default user agent to help things go well
                        rqobj.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)')
                    else:
                        for key in headerdict:
                            rqobj.add_header(key, headerdict[key])
                    rqobj.add_header(override, verb)
                    print(Fore.GREEN + "Trying " + test + " with " + override + " " + verb )
                    result = urlreq.urlopen(rqobj, context=ctx)
                    print(Fore.WHITE + "------------------------------------------------------------------------------------------------")
                    print(Fore.GREEN + "URL: " + url)
                    print(Fore.WHITE + "HTTP Status: ")
                    print(result.status)
                    responsebody = result.read()
                    print("Response Size:" + str(len(responsebody)))
                    print("Sample data returned: ")
                    try:
                        print(gzip.decompress(responsebody)[:300])
                        print(newdata)
                    except:
                        print(responsebody[:300])
                        print(newdata)
                    return (True, result.url)
                except urllib.error.URLError as e:
                    print(Fore.WHITE + "------------------------------------------------------------------------------------------------")
                    print(Fore.RED + "Error Returned:" + str(e.reason))
                    try:
                        print(e.read(300).decode("utf8", 'ignore'))
                        print(newdata)
                    except:
                        print(Fore.WHITE + "")
                except:
                    print(Fore.WHITE + "")
            time.sleep(sleepamt)

def testincludes(url):
    print(Fore.WHITE + "------------------------------------------------------------------------------------------------")
    print("Testing for JSON includes")
    include_endpoints = [
    "users","sessions","authors","errors",
    "listings","accounts","invoices",
    "items","reports","feeds","orders",
    "settings","notifications","locales",
    "subscriptions","payments","tokens",
    "user","session","author","error",
    "listing","account","invoice",
    "item","report","feed","order",
    "setting","notification","locale",
    "subscription","payment","token",
    "auth","config"
    ]
    regexresult = ""
    if ("?" in url):
        hasparams = 1
    else:
        hasparams = 0
    if (hasparams == 1):
        connector = "&"
    else:
        connector = "?"
    for endpoints in include_endpoints:
        newurl = url + connector + "include=" + endpoints
        #print(newurl)
        testurl(newurl, 1)
        time.sleep(sleepamt)
    print(Fore.WHITE)

def badstrings(url):
    print(Fore.WHITE + "------------------------------------------------------------------------------------------------")
    print("Testing some bad strings")
    bad_strings = [
    "test","\"","|","'",
    "#","-","_","\\",
    "&","..","%","???",
    "*","%2e%2e%2f%23","%23","%3Fcanary%3Dx%26",
    ".json",".xml"
    ]
    for badstring in bad_strings:
        urlbase = urlparse(url).scheme + "://" +  urlparse(url).netloc
        urlpaths = urlparse(url).path.split('/')
        newpath = ""
        for testpath in urlpaths:
            newpath = newpath + "/" + testpath
            testingurl = urlbase + newpath + badstring
            newurl = testingurl.replace("//","/").replace(":/","://")
            testurl(newurl, 1, 0, 0)
            time.sleep(sleepamt)
        testingurl = url + badstring
        newurl = testingurl.replace("//","/").replace(":/","://")
        testurl(newurl, 1, 0, 0)
        time.sleep(sleepamt)

url = sys.argv[1]
if (path.isfile(url)):
    filemode = 1
    urlfile = url
    urlfileobj = open(urlfile,'r')
    urllines = urlfileobj.readlines()
else:
    filemode = 0

print(Fore.BLUE + "")
print(".S_SSSs     .S_sSSs     .S          sSSs   .S_sSSs     .S   .S  ")
print(".SS~SSSSS   .SS~YS%%b   .SS         d%%SP  .SS~YS%%b   .SS  .SS  ")
print("S%S   SSSS  S%S   `S%b  S%S        d%S'    S%S   `S%b  S%S  S%S  ")
print("S%S    S%S  S%S    S%S  S%S        S%|     S%S    S%S  S%S  S%S  ")
print("S%S SSSS%S  S%S    d*S  S&S        S&S     S%S    d*S  S&S  S&S  ")
print("S&S  SSS%S  S&S   .S*S  S&S        Y&Ss    S&S   .S*S  S&S  S&S  ")
print("S&S    S&S  S&S_sdSSS   S&S        `S&&S   S&S_sdSSS   S&S  S&S  ")
print("S&S    S&S  S&S~YSSY    S&S          `S*S  S&S~YSSY    S&S  S&S  ")
print("S*S    S&S  S*S         S*S           l*S  S*S         S*S  S*S  ")
print("S*S    S*S  S*S         S*S          .S*P  S*S         S*S  S*S  ")
print("S*S    S*S  S*S         S*S        sSS*S   S*S         S*S  S*S  ")
print("SSS    S*S  S*S         S*S        YSS'    S*S         S*S  S*S  ")
print("       SP   SP          SP                 SP          SP   SP   ")
print("       Y    Y           Y                  Y           Y    Y    ")
print("                                                                 ")
print(Fore.CYAN + "                                                                ")
print("----------------------------------------------------------------")
print("Imported Headers: ")
if (path.isfile(headerfile)):
    hdrfile = open(headerfile,'r')
    hdrlines = hdrfile.readlines()
    for line in hdrlines:
        print(line)
        headerstxt = headerstxt + line
else:
    headerstxt = "0"
#print("Output File: " + output)
#print("Brute Force Style: " + definition + " length: " + sys.argv[3])
print("----------------------------------------------------------------")
print(Fore.WHITE + "")

if (filemode == 1):
    for currurl in urllines:
        url = currurl
        #ipresult = list( map( lambda x: x[4][0], socket.getaddrinfo(urlparse(currurl).netloc,22,type=socket.SOCK_STREAM)))
        testurl(url, 1, 1, 1)
        if "v" in testoptions:
            testversion(url.rstrip('\n'))
        if "m" in testoptions:
            testmethod(url.rstrip('\n'))
        if "i" in testoptions:
            testincludes(url.rstrip('\n'))
        if "s" in testoptions:
            badstrings(url.rstrip('\n'))
        if (path.isfile(headerfile)):
            hdrfile.close()
        time.sleep(sleepamt)
else:
    testurl(url, 1, 1, 1)
    if "v" in testoptions:
        testversion(url.rstrip('\n'))
    if "m" in testoptions:
        testmethod(url.rstrip('\n'))
    if "i" in testoptions:
        testincludes(url.rstrip('\n'))
    if "s" in testoptions:
        badstrings(url.rstrip('\n'))
    #time.sleep(sleepamt)
    if (path.isfile(headerfile)):
        hdrfile.close()
