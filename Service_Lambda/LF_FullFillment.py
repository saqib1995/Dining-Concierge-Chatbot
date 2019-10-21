import json
import boto3

def lambda_to_sqs(samp):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='test')
    print("printig from bot:" , samp)
    queue.send_message(MessageBody=json.dumps(samp))
	
def lambda_handler(event, context):
    samp=event['currentIntent']['slots']
    lambda_to_sqs(samp)
    response = {
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                  "contentType": "PlainText",
                  "content": "Your request is being Processed. We'll be in touch." 
                },
            }
        }
    return response