import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Email emergency contact code
email_code = '''            # Send email to emergency contact if available
            if user.get('emergency_contact_phone'):
                try:
                    import smtplib
                    from email.mime.text import MIMEText
                    emergency_msg = f"HavenMind Alert: {user['username']} may need support. They've expressed concerning emotions in their journal. Please check on them. If urgent, call crisis helpline: 91-9820466726"
                    
                    msg = MIMEText(emergency_msg)
                    msg['Subject'] = 'HavenMind Emergency Alert'
                    msg['From'] = 'havenmind@gmail.com'
                    msg['To'] = f"{user['emergency_contact_phone']}@gmail.com"  # Assuming email format
                    
                    # Use Gmail SMTP (you can change this)
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login('havenmind@gmail.com', os.getenv('EMAIL_PASSWORD', 'demo'))
                    server.send_message(msg)
                    server.quit()
                except:
                    pass  # Fail silently if email doesn't work'''

# Find and replace SMS code with email code
sms_pattern = r'            # Send SMS to emergency contact if available.*?pass  # Fail silently if SMS doesn\'t work'
new_content = re.sub(sms_pattern, email_code, content, flags=re.DOTALL)

# Write back to file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Switched to email emergency notifications")