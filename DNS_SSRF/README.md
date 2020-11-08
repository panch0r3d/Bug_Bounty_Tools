# SSRF via DNS Lookups

This is my poor mans version of Burp Collaborator using bash, python, and Pingb.in :)

The tool sends requests to all of the URLs in the input file. Each request will contain a request header with a unique value. After all of the requests are sent by the tool any DNS pings to the URLs it sent in the header values are pulled back and added to the output file. It's not very stealthy or fast but it appears to be working pretty reliably. The only thing it doesn't capture are pings that are very delayed, but the output conatins the URL to check back later for those.  

Usage: runSSRFchecks.sh /tmp/SomelistOfURLs.txt /tmp/FileToOutputResultsto.txt

The input file should be full URLs like this:

https://somewebsite.com

http://someotherwebsite.com

This is still sort of a work in progress so let me know if you have suggestions or issues.


Please use responsibly :) and I'd love to know if you have any luck getting bounties with these or if you have any feedback / requests.
