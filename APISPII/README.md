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

tamper.py  -  tries various http methods, api versioning, addition of parameters, and auth bypasses to see what changes
* options (Base URL or input file, header file, time in seconds between requests, optional tests to include (see below)
 * Optional tests:
  * flag v - versioning check looks for some type of numerical version in the url to do search and replace on 
  * flag m - HTTP methods tests 16 valid and 1 invalid HTTP method
  * flag i - test for JSON includes
  * flag s - test some interesting strings
Examples
* python3 tamper.py 'https://api.example.com/12345/user' header.txt 1 msiv
* python3 tamper.py 'https://api.example.com/12345/user' header.txt .5 NA
