import requests
import datetime
import time



#Configurables
###Access Key
access_key = <Feedly Access Key goes here>
###How old until an article is considerd old###
age_threshold = 14 #Days
###How low does the engagement score need to be for an article to suck###
engagement_threshold = 100



#Init
###Build Authorization Header
headers = {'Authorization': 'OAuth ' + access_key}
###Lets get some counts
count_itemtoonew = 0
count_itemoldenough = 0
count_itemoldbutcool = 0
count_itemoldandboring = 0
###purge array
purge_array = []



#Get list of subscriptions
def get_subscriptions():
	url = 'http://cloud.feedly.com/v3/subscriptions'
	subscriptions = requests.get(url, headers=headers)
	
	#Show the result
	print(subscriptions.json())

	#Print just the titles
	for subscription in subscriptions.json():	
		print(subscription['title'].encode('utf-8').strip())

#Get list of streams and the unread counts
def get_unread_stream_counts():
	url = 'http://cloud.feedly.com/v3/markers/counts'									#Get unread counts of subscriptions
	unread_count = requests.get(url, headers=headers)
	return unread_count

#Determine the expire age in epoch
def get_expire_age_epoch():
	expire_date = (datetime.datetime.today() - datetime.timedelta(days=age_threshold))	#Get current time in epoch
	expire_date_epoch = time.mktime(expire_date.timetuple())							#Convert to epoch
	return expire_date_epoch

#Mark articles as read
def mark_articles_read(purge_array):
	body = {
	  "entryIds": purge_array,
	  "action": "markAsRead",
	  "type": "entries"
	}		
	url = 'http://cloud.feedly.com/v3/markers'
	response = requests.post(url, headers=headers , json=body)
	return response

#Get 1000 unread stream items
def get_unread_stream_items(streamid):
	url = 'http://cloud.feedly.com/v3/streams/contents?unreadOnly=true&count=1000&streamId=' + streamid
	unread_stream_contents = requests.get(url, headers=headers)
	return unread_stream_contents
	

#Print unread counts
for unread_record in get_unread_stream_counts().json()['unreadcounts']:
	print('Processing:')
	print(unread_record['id'].strip())
	if unread_record['count'] > 0 and "/global.all" in unread_record['id']:				#Process this Id
		for item in get_unread_stream_items(unread_record['id']).json()['items']:
			if item['published'] < long(get_expire_age_epoch() * 1000):
				count_itemoldenough += 1
				if item['engagement'] < engagement_threshold:
					count_itemoldandboring += 1
					purge_array += [item['id']]
				else:
					count_itemoldbutcool += 1
			else:
				count_itemtoonew += 1
	else:
		print('Stream has 0 unread count, moving on')

print(mark_articles_read(purge_array))
print("Item too new count:")
print(count_itemtoonew)
print("Item old enoughw and was processed:")
print(count_itemoldenough)
print("Item is old but cool, so wasn't touched:")
print(count_itemoldbutcool)
print("Item is old and shit, marked as read:")
print(count_itemoldandboring)
