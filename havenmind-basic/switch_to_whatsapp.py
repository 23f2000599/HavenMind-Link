import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace email SMS with WhatsApp
old_sms_block = r'                    # Send SMS via email gateway \(free\).*?server\.quit\(\)'

new_whatsapp = '''                    # Send WhatsApp message (free via CallMeBot)
                    import urllib.parse
                    phone = user_dict['emergency_contact_phone']
                    if phone.startswith('91'):
                        phone = phone[2:]  # Remove country code
                    elif len(phone) == 10:
                        phone = '91' + phone  # Add India country code
                    
                    whatsapp_msg = urllib.parse.quote(emergency_msg[:1000])
                    whatsapp_url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={whatsapp_msg}&apikey=demo"
                    requests.get(whatsapp_url, timeout=5)'''

content = re.sub(old_sms_block, new_whatsapp, content, flags=re.DOTALL)

# Write back to file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Switched to WhatsApp notifications (free)")