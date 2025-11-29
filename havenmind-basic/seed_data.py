import sqlite3
from datetime import datetime, timedelta

def seed_database():
    conn = sqlite3.connect('havenmind.db')
    c = conn.cursor()
    
    # Add sample user
    c.execute('INSERT OR IGNORE INTO users (id, username, email) VALUES (1, "demo_user", "demo@havenmind.com")')
    
    # Add sample journal entries
    sample_entries = [
        ("Feeling overwhelmed with assignments today. Too much work and not enough time.", 0.2, "negative"),
        ("Had a good study session. Feeling more confident about the upcoming exam.", 0.8, "positive"),
        ("Stressed about the presentation tomorrow. Need to practice more.", 0.3, "negative"),
        ("Great day! Finished my project early and had time to relax.", 0.9, "positive"),
        ("Feeling anxious about deadlines. Need to organize my schedule better.", 0.3, "negative")
    ]
    
    for content, sentiment, emotion in sample_entries:
        c.execute('INSERT OR IGNORE INTO journal_entries (user_id, content, sentiment_score, emotion_tags) VALUES (1, ?, ?, ?)', 
                 (content, sentiment, emotion))
    
    # Add sample calendar events
    today = datetime.now()
    sample_events = [
        ("Math Assignment Due", "Complete calculus homework", today + timedelta(days=1), "high"),
        ("Study Group Meeting", "Physics study session", today + timedelta(days=2), "medium"),
        ("Wellness Break", "Take a walk in the park", today + timedelta(hours=2), "low"),
        ("Project Presentation", "Present final project to class", today + timedelta(days=3), "high"),
        ("Lunch with Friends", "Social time at cafeteria", today + timedelta(days=1, hours=5), "low")
    ]
    
    for title, desc, event_date, stress in sample_events:
        c.execute('INSERT OR IGNORE INTO calendar_events (user_id, title, description, event_date, stress_level) VALUES (1, ?, ?, ?, ?)', 
                 (title, desc, event_date, stress))
    
    conn.commit()
    conn.close()
    print("Sample data added successfully!")

if __name__ == '__main__':
    seed_database()