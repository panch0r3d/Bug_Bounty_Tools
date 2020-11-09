# Bug_Bounty_Tools
Random tools I've made for bug bounty hunting

* DNS SSRF : Find dns ping backs from URLs sent in headers (Burp Collaborator inspired but does not use Burp) 
* headerBlowupURL.py : Send a header of a specified size to tease out an error message that discloses backend server name / version. This works when header size limit lower on the backend server vs the frontend. So the header passes to the backend and triggers the error. See https://research.securitum.com/x-forwarded-for-header-security-problems/ for additional explanation
  Usage: python headerBlowupURL.py https://www.example.com 'X-Forwarded-For' 0 '%' 500
   python headerBlowupURL.py [URL to Test] [Name of the Header] [How many times to repeat the value specified] [The value to repeat in the header] [How much of the response to return (optional default is 500)]
   
