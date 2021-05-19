import mmh3
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

headerfile = sys.argv[2]
headerstxt = ""
lookfordocs = sys.argv[3]
ratelimittests = int(sys.argv[4])
pathregression = sys.argv[5]
#githubapikey = sys.argv[5]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def pathregressiontest():
    urlbase = urlparse(url).scheme + "://" +  urlparse(url).netloc
    urlpaths = urlparse(url).path.split('/')
    newpath = ""
    for testpath in urlpaths:
        newpath = newpath + "/" + testpath
        testingurl = urlbase + newpath
        testurl(testingurl.replace("//","/").replace(":/","://"),1)
        time.sleep(3)
        #extra test to make sure we get with and without slash
        if (testingurl[-1:] != "/"):
            testingurl = urlbase + newpath + "/"
            testurl(testingurl.replace("//","/").replace(":/","://"),1)
            time.sleep(3)

def swaggercheck(url):
    swagger_endpoints = [
    "/api/swagger-ui.html","/swagger-ui.html","/swagger/index.html",
    "/swagger/swagger-ui.html","/swagger.json","/swagger/v1/swagger.json",
    "/swagger-config.yaml","/application.wadl","/application.wadl?detail=true",
    "/services?wsdl","/service?wsdl","?wsdl","/v2/swagger.json",
    "/v2/api-docs","/rest/services?_wadl","/services?_wadl"
    ]
    for endpoint in swagger_endpoints:
        urlbase = urlparse(url).scheme + "://" +  urlparse(url).netloc
        urlpaths = urlparse(url).path.split('/')
        newpath = ""
        for testpath in urlpaths:
            newpath = newpath + "/" + testpath
            testingurl = urlbase + newpath + endpoint
            testurl(testingurl.replace("//","/").replace(":/","://"))
            time.sleep(6)

def testurl(url, showresponse=0, responseheaders=0):
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
                print(responsebody[:300])
                print("REGULAR")
                #print(responsebody.decode("utf8", 'ignore')[:300])
                if re.search(r'\S+@\S+', responsebody.decode("utf8", 'ignore')):
                    piiList = piiList + " email |"
                if re.search('(lastname|firstname|first.name|last.name)', responsebody.decode("utf8", 'ignore'), re.IGNORECASE):
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
            print(Fore.WHITE + "HTTP Status: " + str(e.reason))
            responsebody = e.read()
            try:
                print(gzip.decompress(responsebody)[:300])
            except:
                print(e.read(300).decode("utf8", 'ignore'))
            #response = str(e.read().decode("utf8", 'ignore'))
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

def request_time():
    start_time = time.time()
    try:
        headerdict = json.loads(headerstxt)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
        rqobj = urlreq.Request(url, None, headers)
        if (headerstxt != ""):
            for key in headerdict:
                rqobj.add_header(key, headerdict[key])
        result = urlreq.urlopen(rqobj)
        end_time = time.time()
        return end_time - start_time
    except urllib.error.URLError as e:
        print(Fore.RED + "Error Returned1:" + e.reason)
        end_time = time.time()
        return end_time - start_time
        pass
    except:
        print(Fore.RED + "Error Returned2:")
        end_time = time.time()
        return end_time - start_time
        pass

def ratelimitcheck(n):
    print("Testing for rate limit with " + str(ratelimittests) + " requests against URL: " + url)
    experiment_start = time.time()
    for i in range(n):
        t = request_time()
        print(Fore.WHITE + "Request " + str(i) + " took " + str(t) + " ms")
    print('Testing Complete')
    #t = request_time()

def getfavicons():
    print("Looking for favicon.ico:")
    favicons = set()
    urlbase = urlparse(url).scheme + "://" +  urlparse(url).netloc
    urlpaths = urlparse(url).path.split('/')
    newpath = ""
    response = ""
    for testpath in urlpaths:
        newpath = newpath + "/" + testpath
        testingurl = urlbase + newpath + "/favicon.ico"
        testingurl = testingurl.replace("//","/").replace(":/","://")
        try:
            response = requests.get(testingurl)
            favicon = codecs.encode(response.content,"base64")
            hash = mmh3.hash(favicon)
        except:
            hash = ""
            response.content = ""
            return (False, '')
        if (str(response.content).find("x00") != -1):
            favicons.add(hash)
            print(testingurl)
    for icon in favicons:
        print("FavIcon Hash: " + str(icon))
        try:
            lookupurl = "https://raw.githubusercontent.com/panch0r3d/scrapts/master/shodan-favicon-hashes.csv"
            rqobj = urlreq.Request(lookupurl)
            result = urlreq.urlopen(rqobj)
            regex = str(icon) + "(.*)\n"
            searchresult = re.search(regex, str(result.read().decode("utf8", 'ignore')))
            if (searchresult.group(0)):
                print("Hash        |Product/Application        |Example http.title        |Example header(s) / ssl string        |More Info")
                splitresult = searchresult.group(0).split(',')
                spacer = "                                                                     "
                print((splitresult[0] + spacer)[:12] + "|" + (splitresult[1] + spacer)[:27] + "|" + (splitresult[2] + spacer)[:26] + "|" + (splitresult[3] + spacer)[:38] + "|" + splitresult[4])
        except urllib.error.URLError as e:
            regex = ""
            return (False, '')
        except:
            regex = ""
            return (False, '')
        print("Shodan Search Dork:")
        print("https://www.shodan.io/search?query=http.favicon.hash%3A" + str(icon))

def githubsearch():
    urlbase = urlparse(url).netloc
    urlpaths = urlparse(url).path.split('/')
    newpath = ""
    for testpath in urlpaths:
        newpath = newpath + "/" + testpath
        testingurl = urlbase + newpath
        testingurl = testingurl.replace("//","/").replace(":/","://")
        page = 1
        try:
            rungithubsearch(testingurl, page)
            return True
        except:
            return False

def rungithubsearch(search, page):
    #print("Searching Github for API references")
    #headers = { "Authorization":"token " + githubapikey }
    #url = 'https://api.github.com/search/code?q=' + search + '&page=' + str(page)
    url = 'https://github.com/search?q="' + search + '"&page=' + str(page) + '&type=code'
    print(url)
    try:
        #r = requests.get( url, headers=headers, timeout=5 )
        #json = r.json()
        rqobj = urlreq.Request(url, None, headers)
        #result = urlreq.urlopen(rqobj)
        #regexmatch = re.findall(r'data.hydro.click.hmac', str(result.read()))
        #regexmatch = re.findall(r'data-hydro-click-hmac.*?href.*?>',result.read())
        #rqblob = str(result.read())
        #print(regexmatch)
        #return json
    except Exception as e:
        #print( "%s[-] error occurred: %s%s" % (fg('red'),e,attr(0)) )
        rqblob = ""
        return False
    #print("Matches: " + re.findall(r'data.hydro.click.hmac.*?href.*?[>]', rqblob, re.MULTILINE))

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
        #headerstxt = json.load(hdrfile)
else:
    headerstxt = "0"
print("")
if (filemode == 0):
    print("Baseline Test:")
    testurl(url, 1, 1)
    ipresult = list( map( lambda x: x[4][0], socket.getaddrinfo(urlparse(url).netloc,22,type=socket.SOCK_STREAM)))
    for ipval in ipresult:
        ipurl = urlparse(url).scheme + "://" + ipval + urlparse(url).path + urlparse(url).params + "?" + urlparse(url).query
        testurl(ipurl, 1, 1)
    print(Fore.CYAN + "")
    try:
        getfavicons()
    except:
        print("Unable to retrieve favicon")
    print("")
    print("Github Search Dork:")
    githubsearch()
    print("Google Search Dork:")
    print("site:api-docs.io \"" + urlparse(url).netloc + "\"")
    print("site:documenter.getpostman.com \"" + urlparse(url).netloc + "\"")
print("----------------------------------------------------------------")
print(Fore.WHITE + "")

if (filemode == 1):
    for currurl in urllines:
        url = currurl
        ipresult = list( map( lambda x: x[4][0], socket.getaddrinfo(urlparse(currurl).netloc,22,type=socket.SOCK_STREAM)))
        #for ipval in ipresult:
        #    ipurl = "http://" + ipval + urlparse(currurl).path + urlparse(currurl).params + "?" + urlparse(currurl).query
        #    #urlparse(url).scheme
        #    testurl(ipurl, 1, 1)
        if (pathregression[:1] == "Y" or pathregression[:1] == "y"):
            print("Path regression results: ")
            pathregressiontest()
        else:
            testurl(url, 1, 1)
        if (lookfordocs[:1] == "Y" or lookfordocs[:1] == "y" ):
            print("Looking for Swagger documents (this may take a few minutes)")
            swaggercheck(url)
        if (ratelimittests > 0):
            ratelimitcheck(ratelimittests)
        if (path.isfile(headerfile)):
            hdrfile.close()
        time.sleep(1)
else:
    if (pathregression[:1] == "Y" or pathregression[:1] == "y"):
        print("Path regression results: ")
        pathregressiontest()
    if (lookfordocs[:1] == "Y" or lookfordocs[:1] == "y" ):
        print("Looking for Swagger documents (this may take a few minutes)")
        swaggercheck(url)
    if (ratelimittests > 0):
        ratelimitcheck(ratelimittests)
    if (path.isfile(headerfile)):
        hdrfile.close()
