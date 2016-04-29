##Full Archive Search##
  - Tested with Python 2.7
  - Depends on `requests` library located at [Requests: HTTP for Humans](http://docs.python-requests.org/en/master/)

###Install Directions###
  - Copy all files to a directory
  - Modify `gnip.cfg` with appropriate account information
  - set an environment variable (`GNIP_CFG`) to point to the directory where gnip.cfg is stored.
  - It may be necessary to `chmod +x FAS.py` to make the script executable
  - Execute `./FAS.py` to see command line options.

###Usage###
  FAS.py - Retrieve Gnip Full Archive Search results
  
  Usage: FAS.py
  
    -e OR --endpoint=["Counts" | "Data"*] (optional)
    
    -q OR --query="Escaped Query Here" (required)
    
    -o OR --output="filename"
    
    -b OR --bucket=["day"* | "minute" | "second"]  (only used for counts, optional)
    
    -f OR --fromdate="YYYYMMDDHHSS" (optional)
    
    -t OR --todate="YYYYMMDDHHMMSS" (optional)
    
    -m OR --max=[maximum number of records to return] (all if omitted)
    
    * denotes default option if omitted
    
  
###Example:###
`./FAS.py -e Counts -q "gnip" -o Results.json -b minute -f 201601010000 -t 201602010000'`
 
