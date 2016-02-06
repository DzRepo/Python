#!/usr/bin/env python
from __future__ import ( division, absolute_import, print_function, unicode_literals )
import sys, os
import urlparse
import urllib2
import base64
import json
import gzip 

#  TODO: Convert these to settings file / command line args

UN = 'USER@DOMAIN.com'
ACCOUNT = 'ACCOUNTNAME'
PWD = 'PASSWORD'
UUID = 'JOB-UUID'
Keep = False
ProcessTweets = True
Start_File = 0
End_File = 999999999

valid_status = ['finished', 'delivered']

class RequestWithMethod(urllib2.Request):
    def __init__(self, url, method, headers={}):
        self._method = method
        urllib2.Request.__init__(self, url, headers)

    def get_method(self):
        if self._method:
            return self._method
        else:
            return urllib2.Request.get_method(self) 

def handle_error(error):
        print("Error: ", error)
        
def get_response(url, auth):
        req = RequestWithMethod(url, 'GET')
	req.add_header('Content-type', 'application/json')
	req.add_header("Authorization", "Basic %s" % auth)
	
	try:
	   request = urllib2.urlopen(req)
	   return request.read()
	except urllib2.HTTPError as e:
	    if e.code == 401:
	        handle_error(Exception("Authorization failed - Credentials invalid"))
	    elif e.code == 404:
	        handle_error(Exception("URL not found.  Check Job ID"))
	    elif e.code == 410:
	        handle_error(Exception("URL not found.  Job has expired"))
	    else:
	        handle_error(e)
	   	   
def decompress_file(filename):
    with gzip.open(filename, 'rb') as f:
        file_content = f.read()
        return file_content
     
def get_status(username, password, account, uuid):
        try:
            url = 'https://historical.gnip.com:443/accounts/' + account + '/publishers/twitter/historical/track/jobs/' + uuid + '.json'
    	    auth = base64.encodestring('%s:%s' % (UN, PWD)).replace('\n', '')
            status = get_response(url, auth)
            if status is not None:
   	        return json.loads(status)
   	except Exception as e:
   	    print("Error in get_status")
   	    handle_error(e)

def get_filelist(username, password, jobinfo):
    try:
        data_url = job_info['results']['dataURL']
        auth = base64.encodestring('%s:%s' % (UN, PWD)).replace('\n', '')
 
        results = get_response(data_url, auth)
        if results is not None:
            return json.loads(results)
    except Exception as e:
        print ("Error in get_filelist")
        handle_error(e)

def process_activity(activity):
    if 'id' in activity:
        print("ID:", activity['id'])
    elif 'info' in activity:
        print("Number of activities processed:", activity['activity_count'])
    else:
        print ("Unrecognized format: ", activity)

def get_files(urlList, uuid, keep=False, process=False, start=0, end=99999999):
    try:
        filecount = 0
        if len(urlList) < end:
            end = len(urlList)
            
        for url in urlList:
            filecount += 1
            if filecount > start and filecount < end + 1:
                filename = download_file(url, uuid)
                if process:
                    file_text = decompress_file(filename)
                    lines = file_text.splitlines()
                    print ("Number of rows:", len(lines))
                    for line in lines:
                        if (len(line) > 1):
                            try:
                                process_activity(json.loads(line))
                            except Exception as e:
                                handle_error(e)
                    if (not keep):
                        os.remove(filename)
    except Exception as e:
        print("Error in get_files")
        handle_error(e)
                            
def download_file(url, uuid):
    try:
        u = urllib2.urlopen(url)
        scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
        filename_start = path.find(uuid) + len(uuid) + 1
        filename = path[filename_start:]
        filename = filename.replace("/","_")
        print ("Downloading ", filename)
        output = open(filename,'wb')
        output.write(u.read())
        output.close()
        return filename
    except Exception as e:
        print("Error in download_file")
        handle_error("Error downloading:" + filename + " - " + e)
            
if __name__ == "__main__":
    
	# url = 'https://historical.gnip.com:443/accounts/steven-dzilvelis/publishers/twitter/historical/track/jobs/2v4yeqs3tw.json'
    try:
        job_info = get_status(UN, PWD, ACCOUNT, UUID)
        
        if job_info is not None:
            print ('Found job:', job_info['title'], 'with a status of', job_info['status'], " - ", job_info['statusMessage'])
            # print (job_info)
            
            if job_info['status'] not in valid_status:
                print('Status of job is', job_info)
            else:
                if job_info['percentComplete'] == 100:
                    print("Getting filelist")
                    results = get_filelist(UN, PWD, job_info)
                    if results is not None:
                        print ("Number of files:", results['urlCount'])
                        if results['urlCount'] == 0:
                            print(results)
                        else:
                            get_files(results['urlList'], UUID, Keep, ProcessTweets, Start_File, End_File)
    
    except Exception as e:
        print ("Error in main")
        handle_error(e)