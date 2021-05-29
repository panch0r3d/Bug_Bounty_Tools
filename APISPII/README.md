Usage:

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

bruteforce.py  -  replaces a canary {APISPII} in either the URL or data file
* options (Base URL or input file, type (see list), length of object, max iterations), header file, data file and method for non GET requests)
  * types: 
    * numbers - numbers 0-9
    * alphanumlower - letters a-z and numbers 0-9
    * alphanumupper - letters A-Z and numbers 0-9
    * alphamixed - letters a-z and letters A-Z 
    * alphanummixed - letters a-z and letters A-Z and numbers 0-9
    * alphanummixedchars - letters a-z and letters A-Z and numbers 0-9 and characters !"#$%&'()*+, -./:;<=>?@[\]^_`{|}~
    * hex - letters a-f and numbers 0-9
    * numberseq - numbers increasing sequentially by 1 starting from the number specified in the url with {APISPII,1}

Examples
* python3 bruteforce.py 'https://api.example.com/{APISPII}/user' 'numbers' 6 2 header.txt None
* python3 bruteforce.py 'https://app.example.com/v1/public/task/{APISPII}' 'alphanumlower' 6 2 NA NA
* python3 bruteforce.py /tmp/listofurls.txt 'numberseq' 6 2 header.txt {/tmp/datafile.txt,PUT}

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

api_info.py  -  returns data about the api as well as running some basic tests like path regression, rate limiting, and exposed documentation
* options (Base URL or input file, header file, brute force for documentation, number of requests to test rate limiting, test path regression)

Examples
* python3 api_info.py 'https://api.example.com/12345/user' header.txt N 0 Y
* python3 api_info.py 'https://api.example.com/12345/user' header.txt Y 0 N
* python3 api_info.py 'https://api.example.com/12345/user' header.txt Y 1000 Y
* python3 api_info.py /tmp/listofurls.txt N N 0 N

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Tamper - this tools tries to do all the things that I was trying to remember to do manually for API endpoints. The tool keeps track of what url's have already been checked to avoid hitting the same ones multiple times. It also gets a baseline from the initial GET request for response size and response code so that anything that returns the exact same isn't shown over and over. All of the responses are checked via some pretty simple regexes for PII as well as tokens/keys/secrets and any framework debug pages. A summary of anything interesting found via the regexes is printed before the tool exits. The header file is JSON and can include your cookies or any needed headers. I typically just use the basic one here in this repository first and then add cookies / tokens etc as needed. 

tamper.py  -  tries various http methods, api versioning, addition of parameters, and auth bypasses to see what changes
* options (Base URL or input file, header file, time in seconds between requests, optional tests to include (see below), optional output file
 * Optional tests:
  * flag v - versioning check looks for some type of numerical version in the url to do search and replace on 
  * flag m - HTTP methods tests 16 valid and 1 invalid HTTP method
  * flag i - test for JSON includes
  * flag s - test some interesting strings
  * flag p - tests query parameters by adding a few potentaially interesting ones and duplicating any existing ones with an x appended to the value
  * flag h - tests some potential auth bypassing headers

Examples
* python3 tamper.py 'https://api.example.com/12345/user' header.txt 1 msiv
* python3 tamper.py 'https://api.example.com/12345/user' header.txt .5 NA
* python3 tamper.py /tmp/listofendpoints.txt header.txt 1 msivph /tmp/outputfile.txt
