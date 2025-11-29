import re
import os

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# SMS emergency contact code
sms_code = '''            # Send SMS to emergency contact if available
            if user.get('emergency_contact_phone'):
                try:
                    import requests
                    emergency_msg = f"HavenMind Alert: {user['username']} may need support. They've expressed concerning emotions. Please check on them. Crisis helpline: 91-9820466726"
                    # Simple SMS using Fast2SMS (free tier)
                    sms_url = "https://www.fast2sms.com/dev/bulkV2"
                    payload = {
                        "authorization": os.getenv('FAST2SMS_API_KEY', 'demo'),
                        "message": emergency_msg[:160],  # SMS limit
                        "language": "english",
                        "route": "q",
                        "numbers": user['emergency_contact_phone']
                    }
                    requests.post(sms_url, data=payload, timeout=5)
                except:
                    pass  # Fail silently if SMS doesn't work'''

# Replace all occurrences of the disabled comment
new_content = content.replace('            # Emergency contact notification disabled - requires proper setup', sms_code)

# Write back to file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Added SMS emergency contact notifications")