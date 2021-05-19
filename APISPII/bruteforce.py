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
import uuid
from os import path
from colorama import Fore, Back

definition = sys.argv[2]
i = 0
quiet = "false"
stringLength = int(sys.argv[3])
maxreq = int(sys.argv[4])
headerfile = sys.argv[5]
datainfo = str(sys.argv[6]).replace("{","").replace("}","").split(",")
#print(len(datainfo))

headerstxt = ""

def random_string(stringLength):
    if (definition == "numbers"):
        letters = string.digits
    elif (definition == "alphanumlower"):
        letters = string.ascii_lowercase + string.digits
    elif (definition == "alphanumupper"):
        letters = string.ascii_uppercase + string.digits
    elif (definition == "alphamixed"):
        letters = string.ascii_uppercase + string.ascii_lowercase
    elif (definition == "alphanummixed"):
        letters = string.ascii_uppercase + string.ascii_lowercase + string.digits
    elif (definition == "alphanummixedchars"):
        letters = string.ascii_uppercase + string.ascii_lowercase + string.digits + string.punctuation
    elif (definition == "hex"):
        letters = string.hexdigits
    else:
        letters = string.ascii_lowercase + string.digits
    if (definition == "guid" or definition == "uuid"):
        return str(uuid.uuid4())
    else:
        return ''.join(random.choice(letters) for i in range(stringLength))

def resolve_url(url):
    try:
        headerdict = json.loads(headerstxt)
    except:
        headerdict = ""
    try:
        #Deal with data
        newdata = ""
        if (datalines != ""):
            if (definition == "numberseq"):
                newdata = datalines.replace(re.search(r'\{APISPII.[0-9].*?\}', datalines).group(0), str(numberseqint)).encode('utf-8')
                #print(newdata)
            else:
                newdata = datalines.replace("{APISPII}",  random_string(stringLength)).encode('utf-8')
                #print(newdata)
        if (len(datainfo) == 2):
            rqobj = urlreq.Request(url, data=newdata, method=datainfo[1])
        else:
            rqobj = urlreq.Request(url, None, method='GET')
        if (headerstxt == ""):
            #Add a default user agent to help things go well
            rqobj.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)')
        else:
            for key in headerdict:
                rqobj.add_header(key, headerdict[key].replace("{APISPII}",  random_string(stringLength)).encode('utf-8'))
        result = urlreq.urlopen(rqobj)
        print(Fore.WHITE + "------------------------------------------------------------------------------------------------")
        print(Fore.GREEN + "URL: " + url)
        print(Fore.WHITE + "HTTP Status: ")
        print(result.status)
        print("Sample data returned: ")
        responsebody = result.read()
        try:
            print(gzip.decompress(responsebody)[:500])
            print(newdata)
        except:
            print(responsebody[:500])
            print(newdata)
        return (True, result.url)
    except urllib.error.URLError as e:
        print(Fore.WHITE + "------------------------------------------------------------------------------------------------")
        print(Fore.RED + "Error Returned:" + e.reason)
        try:
            print(e.read(300).decode("utf8", 'ignore'))
            print(newdata)
        except:
            return (False, '')
    except:
        return (False, '')

def random_url(quiet=False):
        link_not_valid = True
        link_base = sys.argv[1]
        i = 0
        while(i < 1):
            if "APISPII" in link_base:
                if (definition == "numberseq"):
                    link = link_base.replace(re.search(r'\{APISPII.[0-9].*?\}', str(sys.argv[1])).group(0), str(numberseqint))
                    #print(link)
                else:
                    link = link_base.replace("{APISPII}",  random_string(stringLength))
            else:
                link = link_base
            result = resolve_url(link)
            #if(result[0]):
            #    link_not_valid = False
            #    return (link, result[1])
            #else:
            #    link_not_valid = True
            i = i + 1

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
if (path.isfile(headerfile)):
    print("Imported Headers: ")
    hdrfile = open(headerfile,'r')
    hdrlines = hdrfile.readlines()
    for line in hdrlines:
        print(line)
        headerstxt = headerstxt + line
        #headerstxt = json.load(hdrfile)
else:
    headerstxt = ""
datalines = ""
if (len(datainfo) == 2 and path.isfile(datainfo[0])):
    print("Imported Data File: ")
    datafile = open(datainfo[0],'r')
    datalines = datafile.read()
    print(datalines)
#print("Output File: " + output)
print("Brute Force Style: " + definition + " length: " + sys.argv[3])
print("Max Attempts: " + sys.argv[4])
numberseqint = 0
if (definition == "numberseq"):
    if "APISPII" in datalines:
        print("Numbers Starting Sequentially at: " + str(re.search(r'APISPII.[0-9].*?\}', datalines).group(0).replace("APISPII,","").replace("}","")))
        numberseqint = int(re.search(r'APISPII.[0-9].*?\}', datalines).group(0).replace("APISPII,","").replace("}",""))
    else:
        print("Numbers Starting Sequentially at: " + str(re.search(r'APISPII.[0-9].*?\}', str(sys.argv[1])).group(0).replace("APISPII,","").replace("}","")))
        numberseqint = int(re.search(r'APISPII.[0-9].*?\}', str(sys.argv[1])).group(0).replace("APISPII,","").replace("}",""))
print("----------------------------------------------------------------")
print(Fore.WHITE + "")
while(i < maxreq):
    link = random_url()
    i = i + 1
    if (definition == "numberseq"):
        numberseqint = numberseqint + 1
    time.sleep(.5)
if (path.isfile(headerfile)):
    hdrfile.close()
if (len(datainfo) == 2 and path.isfile(datainfo[0])):
    datafile.close()
