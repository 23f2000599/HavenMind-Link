import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace carrier SMS with Twilio
old_carrier = r'                    # Direct carrier SMS via email \(actually works\).*?continue'

new_twilio = '''                    # Send SMS via Twilio
                    from twilio.rest import Client
                    
                    account_sid = os.getenv('TWILIO_ACCOUNT_SID', 'demo')
                    auth_token = os.getenv('TWILIO_AUTH_TOKEN', 'demo')
                    twilio_phone = os.getenv('TWILIO_PHONE_NUMBER', '+919871095817')
                    
                    if account_sid != 'demo':
                        client = Client(account_sid, auth_token)
                        phone = user_dict['emergency_contact_phone']
                        if len(phone) == 10:
                            phone = '+91' + phone
                        
                        client.messages.create(
                            body=emergency_msg[:160],
                            from_=twilio_phone,
                            to=phone
                        )
                        print(f"SMS sent to {phone}")'''

content = re.sub(old_carrier, new_twilio, content, flags=re.DOTALL)

# Write back to file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Switched back to Twilio with your phone number")