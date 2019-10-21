import json
import requests
import boto3

sqsClient = boto3.resource('sqs')
smsClient = boto3.client('sns')
queue = sqsClient.get_queue_by_name(QueueName = "test")

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("yelp-restaurants")

def lambda_handler(event=None, context=None):

    for message in queue.receive_messages(MaxNumberOfMessages=1):
        sqs_data = message.body
        sqs_json = json.loads(sqs_data)
		
        cuisine = sqs_json['Cuisine']
        location = sqs_json['Location']
        diningtime = sqs_json['timetogo']
        numberofpeople = sqs_json['people']
        mobile = sqs_json['contact']
       
        host = 'https://search-myrestaurantdomain-dbofzx7lzmkociljgv3hxlfmre.us-east-1.es.amazonaws.com'
        index = 'restaurants'
        type = 'Restaurant'
        url = host + '/' + index + '/' + type + '/'
        url = url + '_search?q=cuisine:' + cuisine + '&size=5'
        r = requests.get(url)
    
        data = r.text
        json_data = json.loads(data)
        json_list = json_data['hits']['hits']

        messageToUser = "Hello, here are your restaurant suggestions, "
    
        count = 1
        for my_data in json_list:
            key = {'id':my_data['_source']['id']}
            response = table.get_item(Key=key)
            res_address = response['Item']['address1']
            res_name = response['Item']['name']
            messageToUser += str(count) + '.'
            messageToUser += res_name + ':'
            messageToUser += res_address + ' '
            count += 1
           
        sendSmsToUser(mobile, messageToUser)
        message.delete()
    
def sendSmsToUser(number, message_customer):
    smsClient.publish(PhoneNumber="+1"+number,Message=message_customer)