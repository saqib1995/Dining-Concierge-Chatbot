from yelpapi import YelpAPI
import json
import boto3
from decimal import Decimal
import requests
from requests_aws4auth import AWS4Auth
import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("yelp-restaurants")
print(table.table_status)

region = 'us-east-1'
service = 'es'

host = 'https://search-myrestaurantdomain-dbofzx7lzmkociljgv3hxlfmre.us-east-1.es.amazonaws.com'

index = 'restaurants'
type = 'Restaurant'
url = host + '/' + index + '/' + type + '/'
headers = { "Content-Type": "application/json" }
api_key = ''    #left blank on purpose
yelp_api = YelpAPI(api_key)
data = ['id', 'name', 'review_count', 'rating', 'coordinates', 'address1', 'zip_code', 'display_phone']
es_data = ['id']

cuisines = [ "italian", "indian", "american","mexican", "thai" , "chinese"]

def fill_in_dataframe(response, c):
    new_response = json.loads(json.dumps(response), parse_float=Decimal)
    for t in new_response["businesses"]:

        dict1 = { key:value for (key,value) in t.items() if key in data}
        dict2 = {key:value for (key,value) in t["location"].items() if key in data}
        dict1.update(dict2)
        dict1.update(cuisine=c)
        final_dict = {key: value for key, value in dict1.items() if value}
        timeStamp = str(datetime.datetime.now())
        final_dict.update(insertedAtTimestamp=timeStamp)        
        my_es_id  = final_dict['id']
        es_dict = {key: final_dict[key] for key in final_dict.keys() 
                               & {'id', 'cuisine'}} 
        es_document = json.loads(json.dumps(es_dict))
        r = requests.put(url+str(my_es_id), json=es_document, headers=headers)
        table.put_item(Item=final_dict)
      
def get_data(event=None, context=None):
    for c in cuisines:
        for x in range(0, 1000, 50):
            response = yelp_api.search_query(term=c, location='manhattan, newyork, ny', limit=50, offset=x)
            fill_in_dataframe(response, c)