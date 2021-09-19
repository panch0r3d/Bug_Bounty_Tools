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
from datetime import date

i = 0
quiet = "false"
url = sys.argv[1]
headerfile = sys.argv[2]
sleepamt = float(sys.argv[3])
testheaders = sys.argv[4]
headervalue = sys.argv[5]
if (path.isfile(url)):
    filemode = 1
    urlfile = url
    urlfileobj = open(urlfile,'r')
    urllines = urlfileobj.readlines()
else:
    filemode = 0

headertestfile = testheaders
headertestfileobj = open(headertestfile,'r')
headertestlines = headertestfileobj.readlines()
headerstxt = ""
respsize = 0
respstatus = ""
testheader = ""
alertHighset = set()
alertMedset = set()
alertLowset = set()
checkedlist = set()
foundpaths = set()
foundsecrets = set()
foundhash = set()
foundemails = set()
foundlrgdata = set()

try:
    fileoutput = sys.argv[6]
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
        outfile = open(sys.argv[6],'a')
        newprintstring = printstring.replace('\033[32m','').replace('\033[37m','').replace('\033[34m','').replace('\033[36m','').replace('\033[31m','')
        outfile.write(newprintstring + "\r\n")
        outfile.close()

def regexchecks(responsebody, url):
    #regex results to check for some particular frameworks in debug mode
    #print("Regex: " + responsebody)
    piiList = ""
    alertname = ""
    if re.search(headervalue, responsebody):
        alertname = " Alert:HIGH - Possible header reflection" + "\r\n"
        dualprint(Fore.RED + alertname)
        alertHighset.add(str(url.rstrip('\n') + alertname))
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
    if re.search(r'Index Of', responsebody, re.IGNORECASE):
        alertname = " Alert:HIGH - Directory Listing" + "\r\n"
        if re.search(r'parent dir', responsebody, re.IGNORECASE):
            dualprint(Fore.RED + alertname)
            alertHighset.add(str(url.rstrip('\n') + alertname))
    if len(responsebody) > respsize and len(responsebody) > 300000:
        if "doctype html" in responsebody[:50]:
            alertname = " Alert:HIGH - Large amount of non html data returned" + "\r\n"
            dualprint(Fore.RED + alertname)
            alertHighset.add(str(url.rstrip('\n') + alertname))
            foundlrgdata.add(str(url.rstrip('\n')))
        else:
            alertname = " Alert:MEDIUM - Large amount of data returned" + "\r\n"
            dualprint(Fore.RED + alertname)
            alertMedset.add(str(url.rstrip('\n') + alertname))
            foundlrgdata.add(str(url.rstrip('\n')))
    if re.search(r'JBWEB0000', responsebody):
        alertname = " Alert:LOW - Possible JBOSS Error Page Found" + "\r\n"
        dualprint(Fore.RED + alertname)
        alertHighset.add(str(url.rstrip('\n') + alertname))
    if re.search(r'apikey', responsebody.replace("hapikey%3D1xx39x89","").replace("hapikey=1xx39x89","").replace("hapikey%253D1xx39x89","").replace("apikey%3Dx278fxx0xx046723","").replace("apikey%253Dx278fxx0xx046723","").replace("apikey=x278fxx0xx046723",""), re.IGNORECASE):
        alertname = " Alert:HIGH - Possible API Key Found" + "\r\n"
        regresult = re.search(r'apikey(=| |:|\")+\S+(=| |:|\")+', responsebody.replace("hapikey%3D1xx39x89","").replace("hapikey=1xx39x89","").replace("hapikey%253D1xx39x89","").replace("apikey%3Dx278fxx0xx046723","").replace("apikey%253Dx278fxx0xx046723","").replace("apikey=x278fxx0xx046723",""), re.IGNORECASE)
        regexsecret = regresult.group(0)
        if regexsecret in foundsecrets:
            foundsecrets.add(regexsecret)
        else:
            dualprint(Fore.RED + alertname)
            dualprint(regexsecret)
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
    if re.search(r'(404 |not found|route|No \S+ resource \S+ found|Problem accessing|Cannot(=| |:|\")+Get)', responsebody, re.IGNORECASE):
        #print("Match Not Found")
        if re.search(r'(=| |:|\")+[/]\S+(=| |:|\"|<)+', responsebody, re.IGNORECASE):
            regresult = re.search(r'(=| |:|\")+[/]\S+(=| |:|\"|<)+', responsebody, re.IGNORECASE)
            #print(regresult.group(0).strip())
            if regresult.group(0).strip().replace("\"","").replace(":","").replace(" ","")[:-1] in url:
                alertname = ""
            else:
                if len(responsebody) <= 1000:
                    alertname = " Alert:MEDIUM - Possible backend API route" + "\r\n"
                    if regresult.group(0).strip().replace("\"","").replace(":","").replace(" ","")[:-1] in foundpaths:
                        foundpaths.add(regresult.group(0))
                    else:
                        dualprint(Fore.RED + alertname)
                        alertMedset.add(str(url.rstrip('\n') + alertname))
                        foundpaths.add(regresult.group(0))
                        dualprint(regresult.group(0).strip().replace("\"","").replace(":","").replace(" ","")[:-1])
    #if re.search(r'\S+@\S+', responsebody):
    if re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', responsebody):
        piiList = piiList + " email |"
        regresult = re.findall('([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', responsebody)
        print(Fore.RED)
        emailcounter = 0
        for email in regresult:
            if (emailcounter < 5):
                dualprint(email)
            emailcounter = emailcounter + 1
            #dualprint(*regresult)
            #dualprint(regresult.group(0))
            foundemails.add(email)
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
    #if re.search(r"(\"|\s|:|$)+([a-f0-9]{32})", responsebody, re.IGNORECASE):
    #    piiList = piiList + " hash |"
    if (piiList != ""):
        alertname = str(" Alert:LOW - Possible PII ( |" + piiList + ") Found" + "\r\n")
        dualprint(Fore.RED + alertname)
        alertLowset.add(str(url.rstrip('\n') + alertname))

def testurl(url, showresponse=0, responseheaders=0, baseline=0, addheader=0):
    #if url in checkedlist:
    #    return (False, '')
    #else:
    #    checkedlist.add(url)
    global respsize
    global respstatus
    try:
        headerdict = json.loads(headerstxt)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
        rqobj = urlreq.Request(url, None, headers)
        if (headerstxt != ""):
            for key in headerdict:
                rqobj.add_header(key, headerdict[key])
        if (addheader == 1):
            rqobj.add_header(testheader, headervalue)
        result = urlreq.urlopen(rqobj, context=ctx, timeout=5)
        responsebody = result.read()
        if (baseline == 1):
            respsize = len(responsebody)
            respstatus = str(result.status)
        else:
            #if (str(len(responsebody)) == str(respsize) and str(result.status) == str(respstatus)):
            if (len(responsebody) >= (respsize - 10) and len(responsebody) <= (respsize + 10) and str(result.status) == str(respstatus)):
                return (False, '')
        dualprint(Fore.WHITE + "------------------------------------------------------------------------------------------------")
        if (addheader == 1):
            dualprint("Header: " + testheader)
            dualprint("Value: " + headervalue)
            dualprint("Timestamp: " + str(date.today()))
        dualprint(Fore.GREEN + str("URL: " + url))
        dualprint(Fore.WHITE + str("HTTP Status: " + str(result.status)))
        dualprint("Response Size:" + str(len(responsebody)))
        piiList = ""
        if (showresponse == 1):
            dualprint("Response Sample:")
            try:
                dualprint(str(gzip.decompress(responsebody)[:300]))
                regexchecks(str(gzip.decompress(responsebody)), url)
            except:
                dualprint(str(responsebody.decode("UTF-8", 'strict')[:300]))
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
        if (baseline == 1):
            respsize = len(str(e))
            respstatus = str(e.reason)
        if (len(str(e)) >= (respsize - 10) and len(str(e)) <= (respsize + 10) and str(e.reason) == str(respstatus) and baseline == 0):
            return (False, '')
        dualprint(Fore.WHITE + "------------------------------------------------------------------------------------------------")
        if (addheader == 1):
            dualprint("Header: " + testheader)
            dualprint("Value: " + headervalue)
            dualprint("Timestamp: " + str(date.today()))
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
        except:
            dualprint(Fore.RED + "An error occurred")
        dualprint(Fore.WHITE + "")
        return (False, '')
    except:
        return (False, '')



dualprint(Fore.BLUE + "")
dualprint(" ___________  ______    _______       __    __       __  ___________  ")
dualprint("('     _   ')/    ' \  |   __ '\     /' |  | '\     /''\('     _   ') ")
dualprint(" )__/  \\__/ /, ____  \ (. |__) :)    |: (__) :|    /    \)__/  \\__/  ")
dualprint("    \__ /  /  /    ) :)|:  ____/     |/      \|   /' /\  \  \__ /     ")
dualprint("    |.  | (: (____/ :/ (   /         |/  __  \|  //  __'  \ |.  |     ")
dualprint("    |:  |  \        / /   /          |: (  ) :| /   /  \   \|:  |     ")
dualprint("     \__|   \'_____/   \__/           \__|  |__/(___/    \___)\__|     ")
dualprint("                                                                       ")
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
dualprint("----------------------------------------------------------------")
dualprint(Fore.WHITE + "")

if (filemode == 1):
    for currurl in urllines:
        url = currurl
        testurl(url, 1, 1, 1, 0)
        for allheaders in headertestlines:
            #print("------------------------------------------------------------------------------------------------")
            testheader = allheaders.rstrip('\n')
            testurl(url, 1, 0, 0, 1)
        if (path.isfile(headerfile)):
            hdrfile.close()
        #if (path.isfile(headertestfile)):
        #    hdrtestfile.close()
        time.sleep(sleepamt)
else:
    testurl(url, 1, 1, 1, 0)
    for allheaders in headertestlines:
        #print("------------------------------------------------------------------------------------------------")
        testheader = allheaders.rstrip('\n')
        testurl(url, 1, 0, 0, 1)
    if (path.isfile(headerfile)):
        hdrfile.close()
    #if (path.isfile(headerfile)):
    #    hdrfile.close()
print("")
print("")
dualprint("------------------------------------------------------------------------------------------------")
