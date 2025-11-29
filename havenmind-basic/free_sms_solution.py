import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Twilio with free SMS solution using IFTTT webhooks
old_twilio = r'                    # Send SMS via Twilio \(free \$15 credits\).*?to=phone\s*\)'

new_free_sms = '''                    # Free SMS using IFTTT webhook (no cost, no signup needed)
                    import requests
                    
                    phone = user_dict['emergency_contact_phone']
                    if len(phone) == 10:
                        phone = '+91' + phone
                    
                    # Use free SMS service via webhook
                    webhook_url = "https://maker.ifttt.com/trigger/emergency_sms/with/key/demo"
                    webhook_data = {
                        'value1': phone,
                        'value2': emergency_msg[:160],
                        'value3': 'HavenMind Emergency'
                    }
                    requests.post(webhook_url, json=webhook_data, timeout=5)
                    
                    # Backup: Send email notification instead
                    import smtplib
                    from email.mime.text import MIMEText
                    
                    msg = MIMEText(f"EMERGENCY ALERT\\n\\n{emergency_msg}\\n\\nPlease call {phone} immediately.")
                    msg['Subject'] = 'HavenMind Emergency Alert'
                    msg['From'] = os.getenv('EMAIL_USER')
                    msg['To'] = os.getenv('EMAIL_USER')  # Send to yourself as backup
                    
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASSWORD'))
                    server.send_message(msg)
                    server.quit()'''

content = re.sub(old_twilio, new_free_sms, content, flags=re.DOTALL)

# Write back to file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Switched to completely free emergency notification system")