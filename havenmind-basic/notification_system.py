"""
Notification System for HavenMind
Handles SMS, Email, and Emergency Alerts
"""

import os
from datetime import datetime
import sqlite3

class NotificationSystem:
    def __init__(self):
        # Email configuration (using Gmail SMTP)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_user = os.getenv('EMAIL_USER')  # Your Gmail address
        self.email_password = os.getenv('EMAIL_PASSWORD')  # Your Gmail app password
        
        # Free Telegram configuration
        from dotenv import load_dotenv
        load_dotenv()  # Ensure .env is loaded
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.sms_via_email = os.getenv('SMS_VIA_EMAIL', 'true').lower() == 'true'
        print(f"Loaded Telegram config: token={self.telegram_token[:10] if self.telegram_token else 'None'}..., chat_id={self.telegram_chat_id}")
    
    def send_email(self, to_email, subject, message):
        """Send email using simple SMTP with timeout"""
        try:
            if not self.email_user or not self.email_password:
                print(f"Email simulated for {to_email}: {subject} - {message}")
                return True
            
            # Try using yagmail (simpler library)
            try:
                import yagmail
                yag = yagmail.SMTP(self.email_user, self.email_password)
                yag.send(to_email, subject, message)
                print(f"Email sent to {to_email}")
                return True
            except ImportError:
                print("yagmail not installed. Install with: pip install yagmail")
            
            # Fallback: Use requests to send via web API
            import requests
            
            # Use a free email service API
            url = "https://formspree.io/f/xpznvqpb"  # Replace with your Formspree endpoint
            data = {
                "email": to_email,
                "subject": subject,
                "message": message,
                "_replyto": self.email_user
            }
            
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                print(f"Email sent via API to {to_email}")
                return True
            else:
                print(f"API email failed: {response.status_code}")
                
        except Exception as e:
            print(f"Email error: {e}")
        
        print(f"Email simulated for {to_email}: {subject} - {message}")
        return True
    
    def send_telegram(self, message):
        """Send Telegram notification"""
        try:
            # Debug output removed since we print in __init__ now
            
            if not self.telegram_token or not self.telegram_chat_id:
                print(f"Telegram credentials missing - simulating: {message}")
                return True
            
            import requests
            
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message
            }
            
            print(f"Sending to Telegram: {url}")
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            
            print(f"Telegram response: {result}")
            
            if result.get('ok'):
                print(f"Telegram message sent successfully to chat {self.telegram_chat_id}")
                return True
            else:
                print(f"Telegram error: {result.get('description', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"Telegram error: {e}")
            print(f"Telegram would be sent: {message}")
            return True
    
    def _send_textbelt_sms(self, to_phone, message):
        """Send SMS via TextBelt (1 free per day)"""
        try:
            import requests
            
            url = "https://textbelt.com/text"
            data = {
                'phone': to_phone,
                'message': message,
                'key': self.textbelt_key
            }
            
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            
            if result.get('success'):
                print(f"SMS sent via TextBelt to {to_phone}")
                return True
            else:
                print(f"TextBelt error: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"TextBelt SMS error: {e}")
            return False
    
    def _send_sms_via_email(self, to_phone, message):
        """Send SMS via carrier email gateway (completely free)"""
        try:
            # Indian carriers and international gateways
            carriers = {
                'airtel': 'airtelap.com',
                'jio': 'jiomsg.com', 
                'vi': 'vimsg.com',
                'bsnl': 'bsnlmsg.com',
                'idea': 'ideacellular.net',
                # International fallbacks
                'verizon': 'vtext.com',
                'att': 'txt.att.net',
                'tmobile': 'tmomail.net'
            }
            
            # Clean phone number
            clean_phone = to_phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            
            # Try multiple carriers (since we don't know which one)
            success = False
            for carrier, gateway in carriers.items():
                try:
                    sms_email = f"{clean_phone}@{gateway}"
                    result = self.send_email(sms_email, "HavenMind", message)
                    if result:
                        print(f"SMS sent via {carrier} gateway to {to_phone}")
                        success = True
                        break
                except:
                    continue
            
            return success
            
        except Exception as e:
            print(f"SMS via email error: {e}")
            return False
    
    def _send_whatsapp_business(self, to_phone, message):
        """Send via WhatsApp Business API"""
        import requests
        
        url = f"https://graph.facebook.com/v18.0/{self.whatsapp_phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.whatsapp_token}",
            "Content-Type": "application/json"
        }
        data = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "text",
            "text": {"body": message}
        }
        
        response = requests.post(url, json=data, headers=headers)
        return response.status_code == 200
    
    def _send_callmebot(self, to_phone, message):
        """Send via CallMeBot (Free)"""
        import requests
        import urllib.parse
        
        encoded_message = urllib.parse.quote(message)
        url = f"https://api.callmebot.com/whatsapp.php?phone={to_phone}&text={encoded_message}&apikey={self.callmebot_key}"
        
        response = requests.get(url)
        return response.status_code == 200
    
    def send_sms(self, to_phone, message):
        """Send SMS using Twilio"""
        try:
            from twilio.rest import Client
            
            account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            twilio_phone = os.getenv('TWILIO_PHONE_NUMBER', '+13203228495')
            
            print(f"SMS Debug: SID={account_sid[:10] if account_sid else 'None'}..., from={twilio_phone}, to={to_phone}")
            
            if not account_sid or not auth_token:
                print(f"Twilio credentials missing - SMS simulated for {to_phone}: {message}")
                return False
            
            client = Client(account_sid, auth_token)
            
            # Format phone number
            if len(to_phone) == 10:
                to_phone = '+91' + to_phone
            elif not to_phone.startswith('+'):
                to_phone = '+91' + to_phone
            
            message_obj = client.messages.create(
                body=message[:160],  # SMS limit
                from_=twilio_phone,
                to=to_phone
            )
            
            print(f"SMS sent successfully to {to_phone}: {message_obj.sid}")
            return True
            
        except Exception as e:
            print(f"SMS error: {e}")
            return False
    
    def send_notification(self, user_id, notification_type, message, subject=None):
        """Send notification based on user preferences"""
        conn = sqlite3.connect('havenmind.db')
        conn.row_factory = sqlite3.Row
        
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        
        if not user:
            return False
        
        notification_method = user['notification_method'] if user['notification_method'] else 'email'
        
        success = False
        
        if notification_method in ['email', 'both']:
            if user['email']:
                success = self.send_email(user['email'], subject or f"HavenMind - {notification_type}", message)
        
        if notification_method in ['telegram', 'both']:
            telegram_message = f"<b>HavenMind - {notification_type}</b>\n\n{message}"
            success = self.send_telegram(telegram_message)
        
        return success
    
    def send_emergency_alert(self, user_id, crisis_message):
        """Send emergency alert to emergency contact"""
        conn = sqlite3.connect('havenmind.db')
        conn.row_factory = sqlite3.Row
        
        user_row = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        
        if not user_row:
            return False
            
        # Convert sqlite3.Row to dict to avoid .get() issues
        user = dict(user_row)
        
        if not user.get('emergency_alerts'):
            return False
        
        emergency_contact_phone = user.get('emergency_contact_phone')
        emergency_contact_name = user.get('emergency_contact_name')
        
        if not emergency_contact_phone:
            return False
        
        # Create emergency message with journal content (shorter for SMS)
        journal_preview = crisis_message[:30] + "..." if len(crisis_message) > 30 else crisis_message
        alert_message = f"🚨 EMERGENCY: {user['username']} needs help. Journal: '{journal_preview}' Call them NOW. Crisis: 91-9820466726"
        
        # Send SMS to emergency contact
        print(f"Sending emergency SMS to {emergency_contact_phone}")
        print(f"Emergency message: {alert_message}")
        sms_sent = self.send_sms(emergency_contact_phone, alert_message)
        print(f"Emergency SMS result: {sms_sent}")
        
        # Also send email if we have emergency contact email
        if user.get('email'):
            email_message = f"""
Your emergency contact ({emergency_contact_name}) has been notified about your crisis indicators.

If you're in immediate danger, please:
- Call emergency services
- Go to your nearest emergency room
- Call crisis helpline: 91-9820466726
- Reach out to your emergency contact: {emergency_contact_name}

You are not alone. Help is available.
"""
            self.send_email(user['email'], "Emergency Alert Sent", email_message)
        
        return sms_sent
    
    def send_daily_checkin(self, user_id):
        """Send daily wellness check-in reminder"""
        message = """
🌟 Daily Wellness Check-in - HavenMind

How are you feeling today? Take a moment to journal your thoughts and emotions.

Your mental health matters. Even a few minutes of reflection can make a difference.

Visit: [Your HavenMind Link]
"""
        return self.send_notification(user_id, "Daily Check-in", message, "Time for your daily wellness check-in")
    
    def send_mood_reminder(self, user_id):
        """Send mood tracking reminder"""
        message = """
💭 Mood Check - HavenMind

It's time for your weekly mood check-in. How has your week been?

Tracking your mood helps identify patterns and improve your mental wellness.

Visit: [Your HavenMind Link]
"""
        return self.send_notification(user_id, "Mood Tracking", message, "Weekly mood check-in reminder")
    
    def send_appointment_reminder(self, user_id, appointment_details):
        """Send appointment reminder"""
        message = f"""
📅 Appointment Reminder - HavenMind

You have an upcoming counseling session:
{appointment_details}

Remember:
- Be on time
- Bring any questions or concerns
- Your mental health is a priority

If you need to reschedule, please contact us as soon as possible.
"""
        return self.send_notification(user_id, "Appointment Reminder", message, "Upcoming counseling appointment")
    
    def send_peer_response_alert(self, user_id, peer_name):
        """Send notification when peer supporter responds"""
        message = f"""
💬 Peer Support Response - HavenMind

{peer_name} has responded to your support request.

Check your messages to continue the conversation.

Visit: [Your HavenMind Link]
"""
        return self.send_notification(user_id, "Peer Response", message, "Peer supporter has responded")

# Global notification system instance
notification_system = NotificationSystem()

def send_crisis_alert(user_id, crisis_content):
    """Helper function to send crisis alerts"""
    return notification_system.send_emergency_alert(user_id, crisis_content)

def send_daily_reminder(user_id):
    """Helper function to send daily reminders"""
    return notification_system.send_daily_checkin(user_id)

def send_peer_notification(user_id, peer_name):
    """Helper function to send peer response notifications"""
    return notification_system.send_peer_response_alert(user_id, peer_name)