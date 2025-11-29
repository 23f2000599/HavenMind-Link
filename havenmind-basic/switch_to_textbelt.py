import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace current system with TextBelt (free SMS)
old_system = r'                    # Free SMS using IFTTT webhook.*?server\.quit\(\)'

new_textbelt = '''                    # Free SMS using TextBelt (no signup needed)
                    import requests
                    
                    phone = user_dict['emergency_contact_phone']
                    if len(phone) == 10:
                        phone = '+91' + phone
                    
                    textbelt_url = "https://textbelt.com/text"
                    textbelt_data = {
                        'phone': phone,
                        'message': emergency_msg[:160],
                        'key': 'textbelt'  # Free quota
                    }
                    
                    response = requests.post(textbelt_url, data=textbelt_data, timeout=10)
                    print(f"SMS Status: {response.status_code}")
                    print(f"SMS Response: {response.text}")'''

content = re.sub(old_system, new_textbelt, content, flags=re.DOTALL)

# Write back to file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Switched to TextBelt free SMS")