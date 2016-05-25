#!/usr/bin/env python
from __future__ import print_function

import gnip_insights as insights
import json
import time
import requests

if __name__ == "__main__":

	GROUPINGS_WIRELESS = '{"groupings": {"By-Country-Network": {"group_by": ["user.location.country", "user.device.network"]},"By-Device":{"group_by":["user.device.os"]}}}'
	GROUPINGS_GENDER = '{"groupings": {"By-Gender": {"group_by": ["user.gender"]},"By-Gender-Interest":{"group_by":["user.gender", "user.interest"]}}}'
	GROUPINGS_TV_SHOWS = '{"groupings": {"By-TV-Shows": {"group_by": ["user.tv.show"]},"By-Country-TV-Shows":{"group_by":["user.location.country","user.tv.show"]}}}'
	GROUPINGS_BASICS = '{"groupings": {"By-Network": {"group_by": ["user.device.network"]},"By-Gender":{"group_by":["user.gender"]},"By-Region":{"group_by":["user.location.region"]},"By-Langage":{"group_by":["user.language"]}}}'

	consumer_key="CONSUMER_KEY_HERE"
	consumer_secret="CONSUMER_SECRET_HERE"
	token="TOKEN_HERE"
	token_secret="TOKEN_SECRET_HERE"

	SEGMENT_NAME="Segment-Name-Here"
	AUDIENCE_NAME="Audience-Name-Here"

	# A line delimited file of Twitter NUMERIC user ids
	USER_ID_FILENAME="UserHandles.txt"
	
	Segment_Create_Flag = True
	Segment_Append_Flag = True
	Audience_Create_Flag = True
	Audience_Query_Flag = True
	Audience_Delete_Flag = True
	Segment_Delete_Flag = True
	Audience_Usage_Flag = True

	# Create API access object
	audience=insights.Audience(consumer_key, consumer_secret, token, token_secret)
	
	if Segment_Create_Flag:
		print ("Creating Segment")
		segment_create_response = audience.create_segment(SEGMENT_NAME)
		if segment_create_response.status_code == requests.codes.created:
			print("  Create Response:", json.dumps(segment_create_response.json(), indent=3))
		else:
			if segment_create_response.status_code == requests.codes.unauthorized:
				print("  Create Segment Error - Unauthorized.  Check keys and tokens")
			else:
				print("  Create Segment Error - Status code:", segment_create_response.status_code)

	if Segment_Append_Flag:
		print("Append to Segment")
		id_list=[]
		append_to_id = None
		
		segments = audience.get_segments()
		if segments.status_code == requests.codes.ok:
			for segment in segments.json()['segments']:
				if segment['name'] == SEGMENT_NAME:
					append_to_id = segment['id']
			print("  Segment id:", append_to_id)
		elif segments.status_code == requests.codes.unauthorized:
			print("  Append Segment Error - (get_segments) - Unauthorized.  Check keys and tokens")
		else:
			print("  Append Segment Error - (get_segments):", segments.status_code)

		if 	append_to_id is not None:
			try:
				with open(USER_ID_FILENAME) as user_id_file:
					for user_id in user_id_file:
						id_list.append(user_id[:-1])
			except IOError:
				print("  Error - Cannot find or open:", USER_ID_FILENAME)
			
			loopFlag = True
			start_id = 0
			
			print("  Appending IDs")
			print("  ", segment['num_user_ids'], " users prior to append")
			
			while loopFlag:
				if len(id_list) < 100000:
					max_id = len(id_list)
				else:
					max_id = 100000
			
				segment_append_response = audience.append_to_segment(append_to_id,id_list[start_id:max_id])
				if segment_append_response.status_code == requests.codes.ok:
					print("  Append Response:", segment_append_response.json()['num_user_ids'], ' users after append')
					del id_list[start_id:max_id]
				if max_id < 100000:
				    loopFlag = False
				elif segment_append_response.status_code == requests.codes.unauthorized:
					print("  Append Segment Error - Unauthorized.  Check keys and tokens")
					loopFlag = False
				else:
					print("  Append Segment Error - Status code:", segment_append_response.status_code)
					loopFlag = False
	
	if Audience_Create_Flag:
		print("Creating Audience")
		segment_ids=[]
		segments = audience.get_segments()
		if segments.status_code == requests.codes.ok:
			for segment in segments.json()['segments']:
				if segment['name'] == SEGMENT_NAME: 
					segment_ids.append(segment['id'])
		else:
			if segments.status_code == requests.codes.unauthorized:
				print("  Audience Create Error - (get_segments) - Unauthorized.  Check keys and tokens")
			else:
				print("  Audience Create Error - (get_segments):", segments.status_code)
		
		audience_create_response = audience.create_audience(AUDIENCE_NAME, segment_ids)
		if audience_create_response.status_code == requests.codes.created:
			print("  Create Audience Response:", json.dumps(audience_create_response.json(), indent=3))
		elif audience_create_response.status_code == requests.codes.unauthorized:
			print("  Append Segment Error - Unauthorized.  Check keys and tokens")
		else:
			print("  Create Audience Error - Status code:", audience_create_response.status_code)
	
	if Audience_Query_Flag:
		print("Querying Audience")
		get_audiences_response = audience.get_audiences()
		if get_audiences_response.status_code == requests.codes.ok:
			for audience_item in get_audiences_response.json()['audiences']:
				print("  Querying audience:", audience_item['name'])
				audience_query_response = audience.get_audience_query(audience_item["id"],json.loads(GROUPINGS_BASICS))
				if audience_query_response.status_code == requests.codes.ok:
					print("  Audience Query Reponse:",  json.dumps(audience_query_response.json(), indent=3))
				elif segment_append_response.status_code == requests.codes.unauthorized:
					print("  Audience Query Error - Unauthorized.  Check keys and tokens")
				else:
					print("  Audience Query Error - Status code:", audience_query_response.status_code)
		else:
			if segments.status_code == requests.codes.unauthorized:
				print("  Query Audience Error - (get_segments) - Unauthorized.  Check keys and tokens")
			else:
				print("  Query Audience Error (get_audiences):", get_audiences_response.status_code)
			
	if Audience_Delete_Flag:
		print("Deleting Audiences")
		get_audiences_response = audience.get_audiences()
		if get_audiences_response.status_code == requests.codes.ok:
			for audience_item in get_audiences_response.json()['audiences']:
				print ("  Deleting Audience:", audience_item['id'])
				audience_delete_response = audience.delete_audience(audience_item['id'])
				if audience_delete_response.status_code == requests.codes.ok:
					print("  Audience Deleted")
				else:
					print("  Delete Audience Error:", audience_delete_response.status_code)
		elif get_audiences_response.status_code == requests.codes.unauthorized:
			print("  Delete Audience Error - (get_audiences) - Unauthorized.  Check keys and tokens")
		else:
			print("Delete Audience Error (get_audiences):", get_audiences_response.status_code)

	if Segment_Delete_Flag:	
		print("Deleting Segments")
		segments = audience.get_segments()
		if segments.status_code == requests.codes.ok:
			for segment in segments.json()['segments']:
				print("  Deleting Segment:", segment['id'])
				segment_delete_response = audience.delete_segment(segment['id'])
				if segment_delete_response.status_code == requests.codes.ok:
					print("  Segment Deleted")
				else:
					if segment_delete_response.status_code == requests.codes.unauthorized:
						print("  Delete Segment Error - Unauthorized.  Check keys and tokens")
					else:
						print("  Delete Segment Error: ", segment_delete_response.status_code)
		elif segments.status_code == requests.codes.unauthorized:
			print("  Delete Segment Error - (get_segments) - Unauthorized.  Check keys and tokens")
		else:
			print("  Delete Segment Error (get_segments): ", segments.status_code)

	if Audience_Usage_Flag:
		print ("Audience Usage")
		usage_response = audience.get_usage()
		if usage_response.status_code == requests.codes.ok:
			print("  Usage Response: ", json.dumps(usage_response.json(), indent=3))
		elif usage_response.status_code == requests.codes.unauthorized:
			print("  Usage Error - Unauthorized.  Check keys and tokens")
		else:
			print("  Get Usage Error: ", usage_response.status_code)
	