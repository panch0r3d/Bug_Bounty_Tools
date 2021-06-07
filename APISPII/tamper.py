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
alertHighset = set()
alertMedset = set()
alertLowset = set()
checkedlist = set()
foundpaths = set()
foundsecrets = set()
foundhash = set()

try:
    fileoutput = sys.argv[5]
    outputmode = 2
    if (path.isfile(fileoutput)):
        outfile = open(fileoutput,'w')
        outfile.close()
except:
    outputmode = 1

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def dualprint(printstring):
    print(printstring)
    if (outputmode == 2):
        outfile = open(sys.argv[5],'a')
        newprintstring = printstring.replace('\033[32m','').replace('\033[37m','').replace('\033[34m','').replace('\033[36m','').replace('\033[31m','')
        outfile.write(newprintstring + "\r\n")
        outfile.close()

def regexchecks(responsebody, url):
    #regex results to check for some particular frameworks in debug mode
    #print("Regex: " + responsebody)
    piiList = ""
    alertname = ""
    if re.search(r'DEBUG...True', responsebody):
        alertname = " Alert:HIGH - Possible Django Debug Page Found" + "\r\n"
        dualprint(Fore.RED + alertname)
        alertHighset.add(str(url.rstrip('\n') + alertname))
    if re.search(r'Whoops..There was an error', responsebody):
        alertname = " Alert:HIGH - Possible Laravel Debug Page Found" + "\r\n"
        dualprint(Fore.RED + alertname)
        alertHighset.add(str(url.rstrip('\n') + alertname))
    if re.search(r'Action Controller..Exception caught', responsebody):
        alertname = " Alert:HIGH - Possible Ruby Debug Page Found" + "\r\n"
        dualprint(Fore.RED + alertname)
        alertHighset.add(str(url.rstrip('\n') + alertname))
    if re.search(r'JBWEB0000', responsebody):
        alertname = " Alert:LOW - Possible JBOSS Error Page Found" + "\r\n"
        dualprint(Fore.RED + alertname)
        alertHighset.add(str(url.rstrip('\n') + alertname))
    if re.search(r'apikey', responsebody.replace("hapikey%3D1xx39x89","").replace("hapikey=1xx39x89","").replace("hapikey%253D1xx39x89","").replace("apikey%3Dx278fxx0xx046723","").replace("apikey%253Dx278fxx0xx046723","").replace("apikey=x278fxx0xx046723",""), re.IGNORECASE):
        alertname = " Alert:HIGH - Possible API Key Found" + "\r\n"
        regresult = re.search(r'apikey', responsebody.replace("hapikey%3D1xx39x89","").replace("hapikey=1xx39x89","").replace("hapikey%253D1xx39x89","").replace("apikey%3Dx278fxx0xx046723","").replace("apikey%253Dx278fxx0xx046723","").replace("apikey=x278fxx0xx046723",""), re.IGNORECASE)
        regexsecret = regresult.group(0)
        if regexsecret in foundsecrets:
            foundsecrets.add(regexsecret)
        else:
            dualprint(Fore.RED + alertname)
            foundsecrets.add(regexsecret)
            alertHighset.add(str(url.rstrip('\n') + alertname))
    if re.search(r'(secret|_key|token)(=| |:|\")+', responsebody, re.IGNORECASE):
        alertname = " Alert:MEDIUM - Possible secret Found" + "\r\n"
        regresult = re.search(r'(secret|_key|token)(=| |:|\")+\S+(=| |:|\")+', responsebody, re.IGNORECASE)
        regexsecret = regresult.group(0)
        if regexsecret in foundsecrets:
            foundsecrets.add(regexsecret)
        else:
            dualprint(Fore.RED + alertname)
            foundsecrets.add(regexsecret)
            alertMedset.add(str(url.rstrip('\n') + alertname))
            dualprint(regexsecret)
    if re.search(r'(404 |not found|route|No \S+ resource \S+ found)', responsebody, re.IGNORECASE):
        if re.search(r'(=| |:|\")+[/]\S+(=| |:|\")+', responsebody, re.IGNORECASE):
            regresult = re.search(r'(=| |:|\")+[/]\S+(=| |:|\")+', responsebody, re.IGNORECASE)
            #print(regresult.group(0).strip())
            if regresult.group(0).strip().replace("\"","").replace(":","").replace("=","")[:-1] in url:
                alertname = ""
            else:
                if len(responsebody) <= 1000:
                    alertname = " Alert:MEDIUM - Possible backend API route" + "\r\n"
                    if regresult.group(0) in foundpaths:
                        foundpaths.add(regresult.group(0))
                    else:
                        dualprint(Fore.RED + alertname)
                        alertMedset.add(str(url.rstrip('\n') + alertname))
                        foundpaths.add(regresult.group(0))
                        dualprint(regresult.group(0).strip().replace("\"","").replace(":","").replace("=","")[:-1])
    #if re.search(r'\S+@\S+', responsebody):
    if re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', responsebody):
        piiList = piiList + " email |"
    if re.search('(lastname|firstname|first.name|last.name)', responsebody, re.IGNORECASE):
        piiList = piiList + " name |"
    # need to add social media links
    #if re.search(r"www\.linkedin\.com%2Fin%2F([^-]+)-", responsebody, re.IGNORECASE):
    #    piiList = piiList + " social media |"
    # need to add phone number
    if re.search(r"(phone|phonenum|phone.num)(=| |:|\")+(\d{3}[-\.\s]\d{3}[-\.\s]\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]\d{4}|\d{3}[-\.\s]\d{4})", responsebody, re.IGNORECASE):
        piiList = piiList + " phone number |"
    # need to add credit card
    #if re.search(r"(card|cc|credit|visa)(=| |:|\")+(?:[0-9]{4}-){3}[0-9]{4}|[0-9]{16}(=| |:|\")+", responsebody, re.IGNORECASE):
    if re.search(r"(card|cc|credit|visa)(=| |:|\")+[0-9]{4}(-| |)[0-9]{4}(-| |)[0-9]{4}(-| |)[0-9]{4}(-| |)(=| |:|\")+", responsebody, re.IGNORECASE):
        piiList = piiList + " credit card |"
    # need to add hash
    if re.search(r"(\"|\s|:|$)+([a-f0-9]{32})", responsebody, re.IGNORECASE):
        piiList = piiList + " hash |"
    if (piiList != ""):
        alertname = str(" Alert:LOW - Possible PII ( |" + piiList + ") Found" + "\r\n")
        dualprint(Fore.RED + alertname)
        alertLowset.add(str(url.rstrip('\n') + alertname))

def testurl(url, showresponse=0, responseheaders=0, baseline=0):
    if url in checkedlist:
        return (False, '')
    else:
        checkedlist.add(url)
    global respsize
    global respstatus
    try:
        headerdict = json.loads(headerstxt)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
        rqobj = urlreq.Request(url, None, headers)
        if (headerstxt != ""):
            for key in headerdict:
                rqobj.add_header(key, headerdict[key])
        result = urlreq.urlopen(rqobj, context=ctx, timeout=10)
        responsebody = result.read()
        if (baseline == 1):
            respsize = len(responsebody)
            respstatus = str(result.status)
            #print("Set Baseline: " + str(len(responsebody)))
            #print("Set Baseline: " + str(result.status))
        else:
            #print("New: " + str(len(responsebody)) + " Baseline: " + str(respsize))
            #print("New: " + str(result.status) + " Baseline: " + str(respstatus))
            if (str(len(responsebody)) == str(respsize) and str(result.status) == str(respstatus)):
                #print("Matched so should skip")
                return (False, '')
        dualprint(Fore.WHITE + "------------------------------------------------------------------------------------------------")
        dualprint(Fore.GREEN + str("URL: " + url))
        dualprint(Fore.WHITE + str("HTTP Status: " + str(result.status)))
        dualprint("Response Size:" + str(len(responsebody)))
        piiList = ""
        if (showresponse == 1):
            dualprint("Response Sample:")
            try:
                dualprint(str(gzip.decompress(responsebody)[:300]))
                #if re.search(r'\S+@\S+', gzip.decompress(responsebody)):
                #    piiList = piiList + " email |"
                #if re.search('(lastname|firstname|first.name|last.name)', gzip.decompress(responsebody), re.IGNORECASE):
                #    piiList = piiList + " name |"
                regexchecks(str(gzip.decompress(responsebody)), url)
            except:
                dualprint(str(responsebody.decode("UTF-8", 'strict')[:300]))
                #if re.search(r'\S+@\S+', responsebody.decode("utf8", 'ignore')):
                #    piiList = piiList + " email |"
                #if re.search('(lastname|firstname|first.name|last.name)', responsebody.decode("UTF-8", 'strict'), re.IGNORECASE):
                #    piiList = piiList + " name |"
                regexchecks(str(responsebody.decode("utf8", 'ignore')), url)
        if (responseheaders == 1):
            dualprint(Fore.WHITE + "")
            dualprint("Response Headers:")
            respheaders = result.info()
            dualprint(Fore.WHITE + str(respheaders))
        if (piiList != ""):
            dualprint(Fore.RED + str(" Possible PII ( |" + piiList + ") Found"))
        return (True, result.url)
    except urllib.error.URLError as e:
        dualprint(Fore.GREEN + "URL: " + url)
        try:
            dualprint(Fore.RED + str("HTTP Status: " + str(e.reason)))
            responsebody = str(e)
            try:
                dualprint(str(Fore.WHITE + gzip.decompress(responsebody)[:300]))
                regexchecks(gzip.decompress(responsebody), url)
            except:
                responsebody = str(e.read().decode("utf8", 'ignore'))
                dualprint(Fore.WHITE + str(responsebody)[:300])
                regexchecks(responsebody, url)
                regexchecks(str(e.reason), url)
            #regex results to check for some particular frameworks in debug mode
            #if re.search(r'DEBUG...True', responsebody):
            #    dualprint(Fore.RED + " Possible Django Debug Page Found")
            #if re.search(r'Whoops..There was an error', responsebody):
            #    dualprint(Fore.RED + " Possible Laravel Debug Page Found")
            #if re.search(r'Action Controller..Exception caught', responsebody):
            #    dualprint(Fore.RED + " Possible Ruby Debug Page Found")
            #if re.search(r'apikey', responsebody.lower().replace("hapikey%3D1xx39x89-c39f-465a-b278-fxx0xx046723","").replace("hapikey=1xx39x89-c39f-465a-b278-fxx0xx046723","").replace("apikey%3Dx278fxx0xx046723","").replace("apikey=x278fxx0xx046723","")):
            #    dualprint(Fore.RED + " Possible API Key Found")
            #if re.search(r'secret', responsebody, re.IGNORECASE):
            #    dualprint(Fore.RED + " Possible secret Found")
            #regexchecks(gzip.decompress(responsebody), url)
        except:
            dualprint(Fore.RED + "An error occurred")
        dualprint(Fore.WHITE + "")
        return (False, '')
    except:
        return (False, '')

def testversion(url):
    dualprint(Fore.WHITE + "------------------------------------------------------------------------------------------------")
    dualprint("Try to identify API versioning if any")
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
    ".","1.0","2.0","3.0","4.0"
    ]
    regexresult = ""
    hasversioning = 0
    if re.search(r'/v[0-9]/', url):
        regexresult = re.search(r'/v[0-9]/', url)
        dualprint(Fore.BLUE + "")
        dualprint(str("Found versioning: " + regexresult.group(0)))
        hasversioning = 1
        dualprint(Fore.WHITE + "")
    if re.search(r'/v/', url):
        regexresult = re.search(r'/v/', url)
        dualprint(Fore.BLUE + "")
        dualprint(str("Found versioning: " + regexresult.group(0)))
        hasversioning = 1
        dualprint(Fore.WHITE + "")
    if re.search(r'/v[0-9][.][0-9]+/', url):
        regexresult = re.search(r'/v[0-9][.][0-9]+/', url)
        dualprint(Fore.BLUE + "")
        dualprint(str("Found versioning: " + regexresult.group(0)))
        hasversioning = 1
        dualprint(Fore.WHITE + "")
    if re.search(r'/api-[0-9.]+/', url):
        regexresult = re.search(r'/api[0-9_\-.]+/', url)
        dualprint(Fore.BLUE + "")
        dualprint(str("Found versioning: " + regexresult.group(0)))
        hasversioning = 1
        dualprint(Fore.WHITE + "")
    if re.search(r'/[0-9][.][0-9]+/', url):
        regexresult = re.search(r'/[0-9][.][0-9]+/', url)
        dualprint(Fore.BLUE + "")
        dualprint(str("Found versioning: " + regexresult.group(0)))
        hasversioning = 1
        dualprint(Fore.WHITE + "")
    if (hasversioning == 1):
        for version in apiverions:
            newurl = url.replace(regexresult.group(0), "/" + version + "/")
            testurl(newurl, 1)
            time.sleep(sleepamt)
    else:
        dualprint(Fore.RED + "No versioning identified")
        dualprint(Fore.WHITE)

def testmethod(url):
    dualprint(Fore.WHITE + "------------------------------------------------------------------------------------------------")
    dualprint("Testing HTTP Methods")
    dualprint("")
    httpverbs = [
    "GET","POST","PUT","PATCH",
    "DELETE","COPY","HEAD","OPTIONS",
    "LINK","UNLINK","PURGE","LOCK",
    "UNLOCK","PROPFIND","VIEW","CONNECT",
    "TRACE","GARBAGE"
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
            dualprint(Fore.GREEN + str("Trying " + verb))
            result = urlreq.urlopen(rqobj, context=ctx, timeout=10)
            dualprint(Fore.WHITE + "------------------------------------------------------------------------------------------------")
            dualprint(Fore.GREEN + str("URL: " + url))
            try:
                dualprint(Fore.WHITE + str("HTTP Status: " + str(result.status)))
            except:
                dualprint("")
            responsebody = result.read()
            dualprint(str("Response Size:" + str(len(responsebody))))
            dualprint("Sample data returned: ")
            try:
                dualprint(str(gzip.decompress(responsebody)[:300]))
                regexchecks(str(gzip.decompress(responsebody)), url)
                dualprint(str(newdata))
            except:
                dualprint(str(responsebody[:300]))
                regexchecks(str(responsebody), url)
                dualprint(str(newdata))
            return (True, result.url)
        except urllib.error.URLError as e:
            dualprint(Fore.WHITE + "------------------------------------------------------------------------------------------------")
            dualprint(Fore.RED + "Error Returned:" + str(e.reason))
            try:
                responsebody = e
                #.read()
            except:
                responsebody = ""
            try:
                dualprint(str(responsebody.decode("utf8", 'ignore'))[:300])
                regexchecks(str(responsebody), url)
                regexchecks(str(e.reason), url)
                dualprint(str(newdata))
            except:
                dualprint(Fore.WHITE + "")
        except:
            dualprint(Fore.WHITE + "")
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
                    dualprint(Fore.GREEN + str("Trying " + test + " with " + override + " " + verb))
                    result = urlreq.urlopen(rqobj, context=ctx, timeout=10)
                    dualprint(Fore.WHITE + "------------------------------------------------------------------------------------------------")
                    dualprint(Fore.GREEN + str("URL: " + url))
                    try:
                        dualprint(Fore.WHITE + str("HTTP Status: " + str(result.status)))
                    except:
                        dualprint("")
                    responsebody = result.read()
                    dualprint(Fore.WHITE + str("Response Size:" + str(len(responsebody))))
                    dualprint("Sample data returned: ")
                    try:
                        dualprint(str(gzip.decompress(responsebody)[:300]))
                        regexchecks(str(gzip.decompress(responsebody)), url)
                        dualprint(str(newdata))
                    except:
                        dualprint(str(responsebody[:300]))
                        regexchecks(str(responsebody), url)
                        dualprint(str(newdata))
                    return (True, result.url)
                except urllib.error.URLError as e:
                    dualprint(Fore.WHITE + "------------------------------------------------------------------------------------------------")
                    dualprint(Fore.RED + str("Error Returned:" + str(e.reason)))
                    try:
                        responsebody = e
                        #.read()
                    except:
                        responsebody = ""
                    try:
                        dualprint(str(responsebody.decode("utf8", 'ignore'))[:300])
                        regexchecks(str(responsebody), url)
                        regexchecks(str(e.reason), url)
                        dualprint(str(newdata))
                    except:
                        dualprint(Fore.WHITE + "")
                except:
                    dualprint(Fore.WHITE + "")
            time.sleep(sleepamt)

def testincludes(url):
    dualprint(Fore.WHITE + "------------------------------------------------------------------------------------------------")
    dualprint("Testing for JSON includes")
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
        testurl(newurl, 1, 0, 0)
        time.sleep(sleepamt)
    dualprint(Fore.WHITE)

def badstrings(url):
    dualprint(Fore.WHITE + "------------------------------------------------------------------------------------------------")
    dualprint("Testing some bad strings")
    bad_strings = [
    "test","\"","|","'",
    "#","-","_","\\",
    "&","..","%","???",
    "*","%2e%2e%2f%23","%23","%3Fcanary%3Dx%26",
    ".json",".xml","../","%0d%0a","////////../../../etc/passwd",
    "1\'%20OR%20\'1\'=\'1","%3Fhapikey%3D1xx39x89-c39f-465a-b278-fxx0xx046723%3D",
    "%3Fapikey%3Dx278fxx0xx046723%3D","NULL","%C9","%252e%252e%252f"
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
            testingurl = urlbase + newpath + "/" + badstring
            newurl = testingurl.replace("//","/").replace(":/","://")
            testurl(newurl, 1, 0, 0)
            time.sleep(sleepamt)
        testingurl = url + badstring
        newurl = testingurl.replace("//","/").replace(":/","://")
        testurl(newurl, 1, 0, 0)
        time.sleep(sleepamt)

def testparams(url):
    dualprint(Fore.WHITE + "------------------------------------------------------------------------------------------------")
    dualprint("Testing query parameters")
    test_params = [
    "admin=true","test=1","environment=debug",
    "environment=dev","debug=true","url=http%3A%2F%2Fwww.example.com"
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
    for params in test_params:
        newurl = url + connector + params
        testurl(newurl, 1)
        time.sleep(sleepamt)
    #param tampering
    parsed = urlparse(url)
    currparams = parsed.query.split("&")
    if (parsed.query!=""):
        for params in currparams:
            newurl = url + connector + params + "x"
            testurl(newurl, 1)
            time.sleep(sleepamt)
        for params in currparams:
            newurl = url.replace(params,params.replace("=","=../"))
            testurl(newurl, 1)
            time.sleep(sleepamt)
    dualprint(Fore.WHITE)

url = sys.argv[1]
if (path.isfile(url)):
    filemode = 1
    urlfile = url
    urlfileobj = open(urlfile,'r')
    urllines = urlfileobj.readlines()
else:
    filemode = 0

def testheaders(url):
    dualprint(Fore.WHITE + "------------------------------------------------------------------------------------------------")
    dualprint("Testing HTTP Headers")
    dualprint("")
    test_headers = ["X-Forward-Proto","X-Original-URL","X-Custom-IP-Authorization","token","Max-Forwards0","Max-Forwards1","Max-Forwards2"
    ]
    #Check for responses with some intersting headers
    try:
        headerdict = json.loads(headerstxt)
    except:
        headerdict = ""
    for test in test_headers:
        try:
            rqobj = urlreq.Request(url, None)
            if (headerstxt == ""):
                #Add a default user agent to help things go well
                rqobj.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)')
            else:
                for key in headerdict:
                    rqobj.add_header(key, headerdict[key])
            #logic to determine header value
            parsed = urlparse(url)
            newurl = url
            if (test == "X-Forward-Proto"):
                if (parsed.scheme == "https"):
                    test_value = "http"
                else:
                    test_value = "https"
            if (test == "X-Original-URL"):
                test_value = parsed.path
                newurl = parsed.scheme + "://" + parsed.netloc
                print(newurl)
            if (test == "X-Custom-IP-Authorization"):
                test_value = "127.0.0.1"
            if (test == "token"):
                test_value = "NULL"
            if (test == "Max-Forwards0"):
                test_value = "0"
                test = "Max-Forwards"
            if (test == "Max-Forwards1"):
                test_value = "1"
                test = "Max-Forwards"
            if (test == "Max-Forwards2"):
                test_value = "2"
                test = "Max-Forwards"
            rqobj = urlreq.Request(newurl, None)
            rqobj.add_header(test, test_value)
            dualprint(Fore.GREEN + str("Trying " + test + " with " + test_value + " "))
            dualprint(Fore.WHITE + "------------------------------------------------------------------------------------------------")
            dualprint(Fore.GREEN + str("URL: " + newurl))
            result = urlreq.urlopen(rqobj, context=ctx, timeout=10)
            try:
                dualprint(Fore.WHITE + str("HTTP Status: " + str(result.status)))
            except:
                dualprint("")
            responsebody = result.read()
            dualprint(Fore.WHITE + str("Response Size:" + str(len(responsebody))))
            dualprint("Sample data returned: ")
            try:
                dualprint(str(gzip.decompress(responsebody)[:300]))
                regexchecks(str(gzip.decompress(responsebody)))
                dualprint(str(newdata))
            except:
                dualprint(str(responsebody[:300]))
                regexchecks(str(responsebody))
                dualprint(str(newdata))
            return (True, result.url)
        except urllib.error.URLError as e:
            dualprint(Fore.WHITE + "------------------------------------------------------------------------------------------------")
            dualprint(Fore.RED + str("Error Returned:" + str(e.reason)))
            responsebody = e
            #.read()
            try:
                dualprint(str(responsebody.decode("utf8", 'ignore'))[:300])
                regexchecks(str(responsebody.decode.decode("utf8", 'ignore')))
                dualprint(str(newdata))
            except:
                dualprint(Fore.WHITE + "")
        except:
            dualprint(Fore.WHITE + "")
    time.sleep(sleepamt)



dualprint(Fore.BLUE + "")
dualprint(".S_SSSs     .S_sSSs     .S          sSSs   .S_sSSs     .S   .S  ")
dualprint(".SS~SSSSS   .SS~YS%%b   .SS         d%%SP  .SS~YS%%b   .SS  .SS  ")
dualprint("S%S   SSSS  S%S   `S%b  S%S        d%S'    S%S   `S%b  S%S  S%S  ")
dualprint("S%S    S%S  S%S    S%S  S%S        S%|     S%S    S%S  S%S  S%S  ")
dualprint("S%S SSSS%S  S%S    d*S  S&S        S&S     S%S    d*S  S&S  S&S  ")
dualprint("S&S  SSS%S  S&S   .S*S  S&S        Y&Ss    S&S   .S*S  S&S  S&S  ")
dualprint("S&S    S&S  S&S_sdSSS   S&S        `S&&S   S&S_sdSSS   S&S  S&S  ")
dualprint("S&S    S&S  S&S~YSSY    S&S          `S*S  S&S~YSSY    S&S  S&S  ")
dualprint("S*S    S&S  S*S         S*S           l*S  S*S         S*S  S*S  ")
dualprint("S*S    S*S  S*S         S*S          .S*P  S*S         S*S  S*S  ")
dualprint("S*S    S*S  S*S         S*S        sSS*S   S*S         S*S  S*S  ")
dualprint("SSS    S*S  S*S         S*S        YSS'    S*S         S*S  S*S  ")
dualprint("       SP   SP          SP                 SP          SP   SP   ")
dualprint("       Y    Y           Y                  Y           Y    Y    ")
dualprint("                                                                 ")
dualprint(Fore.CYAN + "                                                                ")
dualprint("----------------------------------------------------------------")
dualprint("Imported Headers: ")
if (path.isfile(headerfile)):
    hdrfile = open(headerfile,'r')
    hdrlines = hdrfile.readlines()
    for line in hdrlines:
        dualprint(str(line))
        headerstxt = headerstxt + line
else:
    headerstxt = "0"
if (outputmode == 2):
    dualprint("Output File: " + fileoutput)
#print("Brute Force Style: " + definition + " length: " + sys.argv[3])
dualprint("----------------------------------------------------------------")
dualprint(Fore.WHITE + "")

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
        if "p" in testoptions:
            testparams(url.rstrip('\n'))
        if "h" in testoptions:
           testheaders(url.rstrip('\n'))
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
    if "p" in testoptions:
        testparams(url.rstrip('\n'))
    if "h" in testoptions:
        testheaders(url.rstrip('\n'))
    if (path.isfile(headerfile)):
        hdrfile.close()
print("")
print("")
dualprint("------------------------------------------------------------------------------------------------")
print("")
print(Fore.RED + "High Priority Alerts:")
print(Fore.WHITE + "")
print(*alertHighset)
print("")
print("")
dualprint("------------------------------------------------------------------------------------------------")
print("")
print(Fore.CYAN + "Medium Priority Alerts:")
print(Fore.WHITE + "")
print(*alertMedset)
print("")
print("")
dualprint("------------------------------------------------------------------------------------------------")
print("")
print(Fore.GREEN + "Low Priority Alerts:")
print(Fore.WHITE + "")
print(*alertLowset)
print(Fore.GREEN + "Found secrets:")
print(Fore.WHITE + "")
print(*foundsecrets)
print(Fore.GREEN + "Found path traversals:")
print(Fore.WHITE + "")
print(*foundpaths)
