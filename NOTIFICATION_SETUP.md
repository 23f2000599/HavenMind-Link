# HavenMind Notification System Setup

## Overview
The profile update system now includes a comprehensive notification system that can send:
- **SMS notifications** for urgent alerts and reminders
- **Email notifications** for regular updates
- **Emergency alerts** to designated emergency contacts
- **Crisis detection** with automatic emergency contact notification

## Fixed Issues
✅ **Profile Update Not Working**: Added proper backend routes and form handling
✅ **Missing Contact Information**: Added phone number and emergency contact fields
✅ **No Notification System**: Built complete SMS/Email notification system
✅ **Emergency Alerts Without Contacts**: Added emergency contact validation

## New Features Added

### 1. Contact Information Fields
- **Phone Number**: Required for SMS notifications
- **Emergency Contact Name**: Person to notify during crisis
- **Emergency Contact Phone**: Phone number for emergency alerts
- **Emergency Contact Relationship**: Relationship to emergency contact

### 2. Notification Preferences
- **Notification Method**: Email, SMS, or Both
- **Notification Time**: Morning, Afternoon, Evening, or Custom
- **Daily Check-ins**: SMS/Email reminders to journal
- **Mood Reminders**: Weekly mood tracking notifications
- **Peer Notifications**: Alerts when peer supporters respond
- **AI Insights**: Weekly wellness insights
- **Appointment Reminders**: SMS reminders for counseling sessions

### 3. Crisis Support Features
- **Emergency Contact Alerts**: SMS to emergency contact during crisis
- **Location Sharing**: GPS location sent during crisis (if enabled)
- **Auto-Professional Escalation**: Immediate professional intervention
- **Crisis Detection**: AI detects crisis language and triggers alerts

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your credentials:

```bash
# For Email Notifications (Gmail)
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password

# For SMS Notifications (Twilio)
TWILIO_SID=your_twilio_sid
TWILIO_TOKEN=your_twilio_auth_token
TWILIO_PHONE=+1234567890

# Gemini AI (existing)
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Gmail Setup (for Email Notifications)
1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account Settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
   - Use this password in `EMAIL_PASSWORD`

### 4. Twilio Setup (for SMS Notifications)
1. Create a Twilio account at https://www.twilio.com
2. Get your Account SID and Auth Token from the dashboard
3. Purchase a phone number for sending SMS
4. Add credentials to `.env` file

### 5. Test the System
1. Update your profile with phone number and emergency contact
2. Click "Save & Test Notifications" to verify setup
3. Check that you receive the test notification

## How It Works

### Profile Updates
- Students can now update personal information, contact details, and preferences
- All forms properly submit to backend routes
- Success/error messages are displayed
- Database automatically adds new columns as needed

### Notification Flow
1. **User Action**: Student journals, requests support, etc.
2. **AI Analysis**: System analyzes content for crisis indicators
3. **Notification Decision**: Based on user preferences and urgency
4. **Delivery**: SMS/Email sent using Twilio/Gmail
5. **Emergency Escalation**: If crisis detected, emergency contact notified

### Crisis Detection
- AI analyzes journal entries and chat messages
- Keywords: "die", "suicide", "kill myself", "end it", etc.
- Automatic emergency contact notification
- Professional escalation if enabled
- Crisis resources provided immediately

### Emergency Alerts
When crisis is detected:
```
🚨 EMERGENCY ALERT - HavenMind 🚨

[Student Name] may be in crisis and needs immediate support.

Crisis indicators detected: [specific content]

Please reach out to them immediately:
- Call them now
- Check on their wellbeing
- Consider professional help if needed

Time: 2024-01-15 14:30:25

If this is a medical emergency, call 911.
Crisis Hotline: 988
```

## Usage Examples

### For Students
1. **Setup Profile**: Add phone number and emergency contact
2. **Choose Preferences**: Select notification methods and timing
3. **Enable Crisis Support**: Configure emergency alerts
4. **Test System**: Use "Save & Test Notifications" button

### For Emergency Contacts
- Will receive SMS alerts during student crisis
- Clear instructions on what to do
- Emergency resources provided
- Time-stamped for reference

### For Administrators
- Monitor notification delivery in logs
- Configure system-wide notification settings
- Access emergency alert history
- Manage crisis response protocols

## Technical Details

### Database Schema Updates
New columns added to `users` table:
- `phone`, `emergency_contact_name`, `emergency_contact_phone`
- `notification_method`, `notification_time`
- `daily_checkins`, `mood_reminders`, `peer_notifications`
- `emergency_alerts`, `share_location`, `auto_professional_escalation`

### Notification System Architecture
- `notification_system.py`: Core notification logic
- Email: SMTP with Gmail
- SMS: Twilio REST API
- Emergency: Immediate delivery with fallbacks
- Logging: All notifications logged for audit

### Security Considerations
- Environment variables for sensitive credentials
- User consent required for all notifications
- Emergency contact validation
- Opt-out available for all notification types
- Data encryption for sensitive information

## Troubleshooting

### Common Issues
1. **No notifications received**: Check phone number format and credentials
2. **Email not working**: Verify Gmail app password and 2FA
3. **SMS not working**: Check Twilio balance and phone number verification
4. **Emergency alerts not sent**: Verify emergency contact information

### Testing
- Use "Save & Test Notifications" button
- Check console logs for error messages
- Verify credentials in `.env` file
- Test with different notification methods

## Future Enhancements
- Push notifications for mobile app
- Integration with campus emergency systems
- Geofencing for location-based alerts
- Machine learning for better crisis detection
- Multi-language support for notifications