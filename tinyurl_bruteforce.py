import random
import string
import urllib.request as urlreq
import csv
import sys
import time

filename = sys.argv[2]
i = 0
exclude = sys.argv[4]

def random_string(stringLength=sys.argv[3]):
    letters = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(stringLength))

def resolve_tinyurl(url):
    try:
        result = urlreq.urlopen(url)
        if(result.url == exclude):
            return (False, '')
        else:
            return (True, result.url)
    except:
        return (False, '')

def random_tinyurl(quiet=False, prefixs = ['']):
        link_not_valid = True
        link_base = sys.argv[1]
        while(link_not_valid):
            prefix = random.choice(prefixs)
            link = link_base + prefix + random_string(8 - len(prefix))
            result = resolve_tinyurl(link)
            if(result[0]):
                link_not_valid = False
                if(not quiet):
                    print(link + ' = ' + result[1])
                return (link, result[1])
            else:
                link_not_valid = True
                if(not link_not_valid):
                    print(link + ' is not valid...')

while(i < 99999):
    link = random_tinyurl(prefixs=['x','y'])  # x and y appear to be the only valid ones

    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(link)

    print('Saved to ' + filename)
    i = i + 1
    time.sleep(.25)
