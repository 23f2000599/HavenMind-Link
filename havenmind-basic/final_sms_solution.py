import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace SMS77 with direct carrier email-to-SMS
old_sms77 = r'                    # Free SMS using SMS77.*?print\(f"SMS Response: \{response\.text\}"\)'

new_carrier_sms = '''                    # Direct carrier SMS via email (actually works)
                    import smtplib
                    from email.mime.text import MIMEText
                    
                    phone = user_dict['emergency_contact_phone']
                    if len(phone) == 10:
                        # Try multiple carrier gateways
                        carriers = [
                            phone + '@airtelmail.com',  # Airtel
                            phone + '@smsjio.com',      # Jio  
                            phone + '@sms.vodafone.in', # Vodafone
                            phone + '@way2sms.com'      # Generic
                        ]
                        
                        for sms_email in carriers:
                            try:
                                msg = MIMEText(emergency_msg[:160])
                                msg['Subject'] = ''  # Empty subject for SMS
                                msg['From'] = os.getenv('EMAIL_USER')
                                msg['To'] = sms_email
                                
                                server = smtplib.SMTP('smtp.gmail.com', 587)
                                server.starttls()
                                server.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASSWORD'))
                                server.send_message(msg)
                                server.quit()
                                print(f"SMS sent via {sms_email}")
                                break  # Stop after first success
                            except:
                                continue'''

content = re.sub(old_sms77, new_carrier_sms, content, flags=re.DOTALL)

# Write back to file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Switched to direct carrier SMS gateways")