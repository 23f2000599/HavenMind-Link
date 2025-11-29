import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

# Get your Twilio phone numbers
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')

try:
    client = Client(account_sid, auth_token)
    
    # List all phone numbers in your account
    phone_numbers = client.incoming_phone_numbers.list()
    
    print("Your Twilio phone numbers:")
    for number in phone_numbers:
        print(f"Phone: {number.phone_number}")
        print(f"Friendly Name: {number.friendly_name}")
        print(f"SID: {number.sid}")
        print("---")
    
    if not phone_numbers:
        print("No phone numbers found. You need to buy a phone number from Twilio console.")
        print("Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/search")
        
except Exception as e:
    print(f"Error: {e}")