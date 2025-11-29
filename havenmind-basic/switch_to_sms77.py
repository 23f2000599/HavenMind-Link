import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace TextBelt with SMS77
old_textbelt = r'                    # Free SMS using TextBelt.*?print\(f"SMS Response: \{response\.text\}"\)'

new_sms77 = '''                    # Free SMS using SMS77 (works in India)
                    import requests
                    
                    phone = user_dict['emergency_contact_phone']
                    if len(phone) == 10:
                        phone = '91' + phone  # Add country code without +
                    
                    sms77_url = "https://gateway.sms77.io/api/sms"
                    sms77_data = {
                        'to': phone,
                        'text': emergency_msg[:160],
                        'p': 'demo',  # Free demo mode
                        'from': 'HavenMind'
                    }
                    
                    response = requests.post(sms77_url, data=sms77_data, timeout=10)
                    print(f"SMS Status: {response.status_code}")
                    print(f"SMS Response: {response.text}")'''

content = re.sub(old_textbelt, new_sms77, content, flags=re.DOTALL)

# Write back to file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Switched to SMS77 (works in India)")