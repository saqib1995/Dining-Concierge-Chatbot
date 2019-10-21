import json
import boto3

client=boto3.client("lex-runtime")

def lambda_handler(event, context):
    response=client.post_text(botName='Yelp_chat_bot', botAlias='$LATEST', userId='admin',inputText=event['message'])
    return response['message']