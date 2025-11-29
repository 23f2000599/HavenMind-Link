import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Twilio with Telegram for emergency contacts
old_twilio = r'                    # Send SMS via Twilio \(free \$15 credits\).*?to=phone\s*\)'

new_telegram = '''                    # Send Telegram message to emergency contact
                    import requests
                    
                    # Use your bot to send message to emergency contact's Telegram
                    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
                    emergency_chat_id = user_dict.get('emergency_contact_telegram_id')
                    
                    if bot_token and emergency_chat_id:
                        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                        telegram_data = {
                            'chat_id': emergency_chat_id,
                            'text': f"🚨 *HavenMind Emergency Alert*\\n\\n{emergency_msg}",
                            'parse_mode': 'Markdown'
                        }
                        requests.post(telegram_url, data=telegram_data, timeout=5)'''

content = re.sub(old_twilio, new_telegram, content, flags=re.DOTALL)

# Write back to file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Switched to Telegram for emergency contacts")