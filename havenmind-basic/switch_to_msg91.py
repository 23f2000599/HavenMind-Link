import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Fast2SMS with MSG91
old_sms = '''                    # Simple SMS using Fast2SMS (free tier)
                    sms_url = "https://www.fast2sms.com/dev/bulkV2"
                    payload = {
                        "authorization": os.getenv('FAST2SMS_API_KEY', 'demo'),
                        "message": emergency_msg[:160],  # SMS limit
                        "language": "english",
                        "route": "q",
                        "numbers": user_dict['emergency_contact_phone']
                    }'''

new_sms = '''                    # Simple SMS using MSG91 (free tier)
                    sms_url = "https://api.msg91.com/api/sendhttp.php"
                    payload = {
                        "authkey": os.getenv('MSG91_API_KEY', 'demo'),
                        "mobiles": user_dict['emergency_contact_phone'],
                        "message": emergency_msg[:160],
                        "sender": "HAVMND",
                        "route": "4"
                    }'''

content = content.replace(old_sms, new_sms)

# Write back to file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Switched to MSG91 SMS")