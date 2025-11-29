"""
Daily Schedule Sender for HavenMind
Automatically sends daily calendar schedules via email and Telegram
"""

import sqlite3
from datetime import datetime, timedelta
from notification_system import notification_system
import threading
import time

def get_daily_schedule(user_id, date=None):
    """Get user's schedule for a specific date"""
    if date is None:
        date = datetime.now().date()
    
    conn = sqlite3.connect('havenmind.db')
    conn.row_factory = sqlite3.Row
    
    # Get events for the specified date
    events = conn.execute(
        '''SELECT * FROM calendar_events 
           WHERE user_id = ? AND date(event_date) = ? 
           ORDER BY event_date''',
        (user_id, date.strftime('%Y-%m-%d'))
    ).fetchall()
    
    conn.close()
    return events

def format_schedule_message(events, date):
    """Format schedule into a readable message"""
    date_str = date.strftime('%A, %B %d, %Y')
    
    if not events:
        return f"""
📅 Daily Schedule - {date_str}

🎉 No events scheduled for today! 
Enjoy your free day and consider:
• Taking a wellness break
• Journaling your thoughts
• Connecting with friends
• Working on personal projects

Have a great day! 🌟
"""
    
    message = f"📅 Daily Schedule - {date_str}\n\n"
    
    for event in events:
        event_time = datetime.strptime(event['event_date'], '%Y-%m-%dT%H:%M')
        time_str = event_time.strftime('%I:%M %p')
        
        # Add stress level emoji
        stress_emoji = {
            'minimal': '😌',
            'low': '🙂', 
            'medium': '😐',
            'high': '😰',
            'critical': '🚨'
        }.get(event['stress_level'], '📝')
        
        message += f"{stress_emoji} {time_str} - {event['title']}\n"
        if event['description']:
            message += f"   📝 {event['description']}\n"
        message += "\n"
    
    message += "💡 Tips for today:\n"
    message += "• Take breaks between events\n"
    message += "• Stay hydrated and eat well\n"
    message += "• Practice mindfulness if stressed\n"
    message += "• Journal about your day\n\n"
    message += "Have a productive day! 🌟"
    
    return message

def send_daily_schedules():
    """Send daily schedules to all users who have daily check-ins enabled"""
    conn = sqlite3.connect('havenmind.db')
    conn.row_factory = sqlite3.Row
    
    # Get users who have daily check-ins enabled
    users = conn.execute(
        'SELECT * FROM users WHERE daily_checkins = 1'
    ).fetchall()
    
    conn.close()
    
    today = datetime.now().date()
    
    for user in users:
        try:
            # Get user's schedule
            events = get_daily_schedule(user['id'], today)
            
            # Format message
            schedule_message = format_schedule_message(events, today)
            
            # Send notification
            notification_system.send_notification(
                user['id'],
                "Daily Schedule",
                schedule_message,
                f"Your Schedule for {today.strftime('%B %d, %Y')}"
            )
            
            print(f"Daily schedule sent to {user['username']}")
            
        except Exception as e:
            print(f"Error sending schedule to {user['username']}: {e}")

def schedule_daily_sender():
    """Run daily schedule sender at 8 AM every day"""
    while True:
        now = datetime.now()
        
        # Check if it's 8 AM
        if now.hour == 8 and now.minute == 0:
            print("Sending daily schedules...")
            send_daily_schedules()
            
            # Wait 60 seconds to avoid sending multiple times
            time.sleep(60)
        else:
            # Check every minute
            time.sleep(60)

def start_daily_scheduler():
    """Start the daily scheduler in a background thread"""
    scheduler_thread = threading.Thread(target=schedule_daily_sender, daemon=True)
    scheduler_thread.start()
    print("Daily scheduler started - will send schedules at 8 AM daily")

# Manual trigger for testing
def send_schedule_now(user_id):
    """Manually send today's schedule to a specific user"""
    try:
        events = get_daily_schedule(user_id)
        schedule_message = format_schedule_message(events, datetime.now().date())
        
        notification_system.send_notification(
            user_id,
            "Daily Schedule",
            schedule_message,
            f"Your Schedule for {datetime.now().strftime('%B %d, %Y')}"
        )
        
        return True
    except Exception as e:
        print(f"Error sending manual schedule: {e}")
        return False

if __name__ == "__main__":
    # Test the scheduler
    print("Testing daily schedule sender...")
    send_daily_schedules()