# Bug_Bounty_Tools
Random tools I've made for bug bounty hunting

* DNS SSRF : Find dns ping backs from URLs sent in headers (Burp Collaborator Everywhere inspired but does not use Burp) finds potential SSRF's and header based redirects

* headerBlowupURL.py : Send a header of a specified size to tease out an error message that discloses backend server name / version. This works when header size limit lower on the backend server vs the frontend. So the header passes to the backend and triggers the error. See https://research.securitum.com/x-forwarded-for-header-security-problems/ for additional explanation
  Usage: python headerBlowupURL.py https://www.example.com 'X-Forwarded-For' 0 '%' 500
   python headerBlowupURL.py [URL to Test] [Name of the Header] [How many times to repeat the value specified] [The value to repeat in the header] [How much of the response to return (optional default is 500)]
   
* CheckPorts.sh - Banner grabbing using telnet through bash 
  Usage: CheckPorts.sh [Input File of URLs/IPs and Ports] &> [Output File]
  expected input format 123.123.123.123:8001 or www.example.com:8001
  
* tinyurl_bruteforce.py - A random brute forcer for shortened URLs (https://www.vanityurlshorteners.com/) *note* watch out for rate limiting
  Usage: python3 tinyurl_bruteforce.py 'https://tinyurl.com/' /tmp/tinyurl.txt 7 'https://www.example.com'
         tinyurl_bruteforce.py [base url] [output file to save reults to] [max length of random characters appended to base] [optional to filter out results that all
         point to the same url]

