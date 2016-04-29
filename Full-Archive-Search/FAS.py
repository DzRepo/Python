#!/usr/bin/env python

import json
import FullArchiveSearch
from locate import locate, clear
import ConfigFile
import sys, getopt


ActivityCount=0
db=None
table=None
FileHandle = None
Output = None

def print_help():
    print "FAS.py - Retrieve Gnip Full Archive Search results"
    print 'Usage: FAS.py'
    print '          -e OR --endpoint=["Counts" | "Data"*] (optional)'
    print '          -q OR --query="Escaped Query Here" (required)'
    print '          -o OR --output="filename"'
    print '          -b OR --bucket=["day"* | "minute" | "second"]  (only used for counts, optional)'
    print '          -f OR --fromdate="YYYYMMDDHHSS" (optional)'
    print '          -t OR --todate="YYYYMMDDHHMMSS" (optional)'
    print '          -m OR --max=[maximum number of records to return] (all if omitted)'
    print '    * denotes default option if omitted'
    print ''
    print 'Example'
    print './FAS.py -e Counts -q "gnip" -o Results.json -b minute -f 201601010000 -t 201602010000'
    print ''

def main(argv):
	SearchType = "Data"
	Query = None
	Bucket = "day"
	FromDate = None
	ToDate = None
	Database = None
	Document = None
	MAX = -1
	
	global db
	global table

	global ActivityCount
	ActivityCount = 0
	global File
	global Output
	global FileHandle

	try:
		opts, args = getopt.getopt(argv,"e:q:o:b:f:t:m:h",["endpoint=","query=","output=","bucket=","fromdate=","todate=","max=","help"])
	except getopt.GetoptError as err:
		print (err)
		print_help()
		sys.exit(2)
		
	for opt, arg in opts:
		if opt in ( '-e','--endpoint'):
			SearchType = arg.lower()
		elif opt in ('-q', '--query'):
			Query = arg
		elif opt in ('-o', '--output'):
			Output = arg
		elif opt in ('-b', '--bucket'):
			Bucket = arg
		elif opt in ('-f', '--fromdate'):
			FromDate = arg
		elif opt in ('-t', '--todate'):
			ToDate = arg
		elif opt in ('-m', '--max'):
			MAX = int(arg)
		else:
			print_help()
			sys.exit(2)
			
	if (Query is None):
		print_help()
		sys.exit(2)
	else:
		# don't print if no Output set, in case output is routed via pipe
		if Output is not None:
			clear()
			print "Full Archive Search"
			print "Search Type:", SearchType
			print "Query:", Query
			print "Output:", Output
			print "Bucket:", Bucket
			print "FromDate:", FromDate
			print "ToDate:", ToDate
			print "Max records to return:", MAX

	

		if SearchType == 'data':
			if Output is not None:
				FileHandle = open(Output, "a")
		
			AllResults = FullArchiveSearch.GetData(Query, FromDate, ToDate, MAX)
			if Output is not None:
				print "Total Activities retrieved:", ActivityCount
			

		elif SearchType == 'counts':
			Results = FullArchiveSearch.GetCounts(Query, Bucket, FromDate, ToDate)
			if Output is not None:
				FileHandle = open(Output, "a")
				if FileHandle is not None:
					FileHandle.write(json.dumps(Results))
					FileHandle.close()
					print "Total Activity count:", Results['totalCount']
			else:
				sys.stdout.write(json.dumps(Results))

# Process data coming back from FAS Data endpoint 
def ActivityHandler(activity):
	global ActivityCount
	global FileHandle
	global Output
	
	if Output is not None:
		FileHandle = open(Output, "a")

	if FileHandle is None:
		sys.stdout.write(json.dumps(activity))
	else:		
		locate( activity['id'], 1, 10)
		FileHandle.write(json.dumps(activity) + "\n")
		FileHandle.close()
    	
	ActivityCount += 1
	
#Initialize and process
if __name__ == "__main__":
    FullArchiveSearch.SetCallback(ActivityHandler)
    main(sys.argv[1:])
