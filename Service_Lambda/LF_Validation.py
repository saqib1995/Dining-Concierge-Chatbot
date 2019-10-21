import json
import math
import dateutil.parser
import datetime
import time
import os
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']

def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }

def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }
    return response
	
def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }

def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }

def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False

def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')

def validate_restaurant(slots):
    city_Location = slots["Location"]
    food_type = slots["Cuisine"]
    num_people = slots['people']
    date = slots["Datepick"]
    dine_time = slots["timetogo"]
    
    available_locations=['manhattan','Manhattan']
    if city_Location is not None and city_Location.lower() not in available_locations:
        return build_validation_result(False,'Location','We do not support {} as a location for now. Manhattan is the only supported option for now.'.format(city_Location))
    
    available_food_types=['american','indian','mexican','italian','chinese','thai']
    if food_type is not None and food_type.lower() not in available_food_types:
        return build_validation_result(False,'Cuisine','We do not support {} as a Cuisine for now. Please choose from American,Indian,Chinese,Italian,Thai and Mexican'.format(food_type))
        
    if num_people is not None:  
        
        if int(num_people) < 1:
            return build_validation_result(False,'people','Minimum 1 person should be there to Dine.')
        
        elif int(num_people) > 6:
            return build_validation_result(False,'people','Maximum 10 people are supported.')

    if date is not None:
        if not isvalid_date(date):
            return build_validation_result(False, 'Datepick','Please select a valid Date.')
        
        if datetime.datetime.strptime(date, '%Y-%m-%d').date() < datetime.date.today():
            return build_validation_result(False, 'Datepick', 'You cannot choose a previous Date.')
    
    if dine_time is not None:
        hour, minute = dine_time.split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        current_hour =datetime.datetime.now().hour
        current_minute = datetime.datetime.now().minute
        
        if math.isnan(hour) or math.isnan(minute):
            return build_validation_result(False, 'timetogo', 'Enter Proper time')
        
        if(datetime.datetime.strptime(date, '%Y-%m-%d').date() == datetime.date.today()):
            if(hour < current_hour):
                return build_validation_result(False, 'timetogo', 'Invalid time. Please mention a valid time')
            
            elif((hour == current_hour) and minute<current_minute):
                return build_validation_result(False, 'timetogo', 'Invalid time. Please mention a valid time')     
        
    return {'isValid': True}

def restaurant_suggestion(intent_request):
    
    city_Location = intent_request['currentIntent']['slots']['Location']
    food_type = intent_request['currentIntent']['slots']['Cuisine']
    num_people = intent_request['currentIntent']['slots']['people']
    date = intent_request['currentIntent']['slots']['Datepick']
    dine_time = intent_request['currentIntent']['slots']['timetogo']
    
    source = intent_request['invocationSource']
    
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    
    if intent_request['invocationSource'] == 'DialogCodeHook':
        
        validation_result = validate_restaurant(intent_request['currentIntent']['slots'])
        if not validation_result['isValid']:
            slots = intent_request['currentIntent']['slots']
            slots[validation_result['violatedSlot']] = None

            return elicit_slot(session_attributes,intent_request['currentIntent']['name'],slots,validation_result['violatedSlot'],validation_result['message'])
        

        return delegate(session_attributes, intent_request['currentIntent']['slots'])
		
    return delegate(session_attributes, intent_request['currentIntent']['slots'])

def dispatch(intent_request):
    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))
    intent_name = intent_request['currentIntent']['name']
    if intent_name == 'Restaurant':
        return restaurant_suggestion(intent_request)
    raise Exception('Intent with name ' + intent_name + ' not supported')

def lambda_handler(event, context):
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    return dispatch(event)