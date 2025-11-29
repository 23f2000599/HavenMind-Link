import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace WhatsApp with Twilio SMS
old_whatsapp = r'                    # Send WhatsApp message \(free via CallMeBot\).*?requests\.get\(whatsapp_url, timeout=5\)'

new_twilio = '''                    # Send SMS via Twilio (free $15 credits)
                    from twilio.rest import Client
                    
                    account_sid = os.getenv('TWILIO_ACCOUNT_SID', 'demo')
                    auth_token = os.getenv('TWILIO_AUTH_TOKEN', 'demo')
                    twilio_phone = os.getenv('TWILIO_PHONE_NUMBER', '+1234567890')
                    
                    if account_sid != 'demo':
                        client = Client(account_sid, auth_token)
                        phone = user_dict['emergency_contact_phone']
                        if len(phone) == 10:
                            phone = '+91' + phone  # Add India country code
                        
                        client.messages.create(
                            body=emergency_msg[:160],
                            from_=twilio_phone,
                            to=phone
                        )'''

content = re.sub(old_whatsapp, new_twilio, content, flags=re.DOTALL)

# Write back to file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Switched to Twilio SMS (free $15 credits)")