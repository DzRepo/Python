#!/usr/bin/env python

import base64
import json
import xml
import sys
import requests
import json
import ConfigFile

ActivityCallBack = None

AllData=[]

def process_activity(activity):
	# print activity
	if ActivityCallBack is not None:
		ActivityCallBack(activity)

def SetCallback(callback):
	global ActivityCallBack
	ActivityCallBack = callback

def GetAuthHeader():
	credentials=ConfigFile.GetSettings("gnip.cfg", "credentials")
	base64string = base64.encodestring('%s:%s' % (credentials['username'],credentials['password'])).replace('\n', '')
	return {"Authorization":"Basic %s" % base64string}
    
def BuildQuery(SearchTerm, FromDate, ToDate):
	query={}
	query['query'] = SearchTerm

	if FromDate is not None:
		query['fromDate'] = FromDate
		    
	if ToDate is not None:
		query['toDate'] = ToDate
	return query

def GetCounts(SearchTerm, Bucket, FromDate, ToDate):
	search=ConfigFile.GetSettings("gnip.cfg", "FullArchiveSearch")
    
    # Build base query
	query=BuildQuery(SearchTerm, FromDate, ToDate)
    
    #Augment with counts only parameters
	query['bucket'] = Bucket
    
	Url = search['baseurl'] + '.json'
    
    # build header
	authHeader = GetAuthHeader()
	Url = search['baseurl'] + '/counts.json'
    
	IsNextToken = True
	Total_Count = 0
    
	results=[]
	totalCount = 0
    
	while IsNextToken:
		oldNext = ""
		req = requests.post(Url, headers=authHeader, data=json.dumps(query))
		if req.status_code != 200:
			print "Error.  Status code:", req.status_code
			print json.loads(req.text)['error']['message']
			IsNextToken = False
		else:
			jsonResponse = json.loads(req.text)
			for result in jsonResponse["results"]:
				results.append(result)
			totalCount += jsonResponse["totalCount"]
	    
		if "next" in jsonResponse:
			if oldNext == jsonResponse['next']:
				IsNextToken = False
				print "Duplicate next token detected"
			else:
				query['next'] = jsonResponse['next']
				oldNext = jsonResponse['next']
		else:
			IsNextToken = False

	allresults={}
	allresults['results']=results
	allresults['requestParameters']=jsonResponse["requestParameters"]
	allresults['totalCount']=totalCount
	return allresults
    
def GetData(SearchTerm, FromDate, ToDate, totalResults=-1):
    #Get Search config parameters
	search=ConfigFile.GetSettings("gnip.cfg", "FullArchiveSearch")
    
    # Build base query
	query=BuildQuery(SearchTerm, FromDate, ToDate)
    
    #Augment with data only parameters
	if totalResults > 0 and totalResults < 500:
		maxResults = totalResults
	else:
		maxResults = 500
	query['maxResults'] = maxResults
	    
	Url = search['baseurl'] + '.json'
	AllData = []
    
    # build header
	authHeader = GetAuthHeader()
    
	IsNextToken = True
	Activities_Count = 0
       
	while IsNextToken:
		oldNext = ""
		req = requests.post(Url, headers=authHeader, data=json.dumps(query))
		if req.status_code != 200:
			print json.loads(req.text)['error']['message']
			IsNextToken = False
		else:
			results = json.loads(req.text)
	    
		if len(results) > 0:
			if ActivityCallBack is None:
				AllData.extend(results['results'])
			else:
				for activity in results['results']:
					Activities_Count += 1
					process_activity(activity)
					if totalResults >0 and Activities_Count == totalResults:
						results.pop('next', None)
						break

		if "next" in results:
			if oldNext == results['next']:
				IsNextToken = False
				print "Duplicate next token detected"
			else:
				query['next'] = results['next']
				oldNext = results['next']
		else:
			IsNextToken = False

	if ActivityCallBack is None:
		return AllData
	else:
		return Activities_Count

#FASCount = GetData("gnip", "20160101000", "201603010000")
# print "Total Activities: ", FASCount

# FAS_Counts = GetCounts("Trump", "day", "20160101000", "201603010000")
# print json.dumps(FAS_Counts['totalCount'], indent=3)
