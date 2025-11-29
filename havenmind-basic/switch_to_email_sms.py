import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace MSG91 with Email-to-SMS
old_sms = '''                    # Simple SMS using MSG91 (free tier)
                    sms_url = "https://api.msg91.com/api/sendhttp.php"
                    payload = {
                        "authkey": os.getenv('MSG91_API_KEY', 'demo'),
                        "mobiles": user_dict['emergency_contact_phone'],
                        "message": emergency_msg[:160],
                        "sender": "HAVMND",
                        "route": "4"
                    }
                    requests.post(sms_url, data=payload, timeout=5)'''

new_sms = '''                    # Send SMS via email gateway (free)
                    import smtplib
                    from email.mime.text import MIMEText
                    
                    # Most Indian carriers support email-to-SMS
                    carriers = {
                        '91': '@sms.airtel.in',  # Airtel
                        '92': '@sms.vodafone.in',  # Vodafone
                        '93': '@sms.idea.in',  # Idea
                        '94': '@sms.bsnl.in',  # BSNL
                        '95': '@sms.jio.in',  # Jio
                        '96': '@sms.airtel.in',  # Default to Airtel
                        '97': '@sms.airtel.in',
                        '98': '@sms.airtel.in',
                        '99': '@sms.airtel.in'
                    }
                    
                    phone = user_dict['emergency_contact_phone']
                    if len(phone) == 10:
                        carrier_code = phone[:2]
                        email_gateway = carriers.get(carrier_code, '@sms.airtel.in')
                        sms_email = phone + email_gateway
                        
                        msg = MIMEText(emergency_msg[:160])
                        msg['Subject'] = 'HavenMind Alert'
                        msg['From'] = os.getenv('EMAIL_USER')
                        msg['To'] = sms_email
                        
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASSWORD'))
                        server.send_message(msg)
                        server.quit()'''

content = content.replace(old_sms, new_sms)

# Write back to file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Switched to Email-to-SMS (completely free)")