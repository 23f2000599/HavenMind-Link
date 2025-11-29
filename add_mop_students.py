import sqlite3
import hashlib
from datetime import datetime, timedelta
import random

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_mop_students():
    conn = sqlite3.connect('havenmind-basic/havenmind.db')
    c = conn.cursor()
    
    # Student data
    students = [
        {'name': 'Priya Sharma', 'email': 'priya.sharma@mopvaishnav.edu.in', 'major': 'Computer Science', 'year': '3rd Year'},
        {'name': 'Ananya Krishnan', 'email': 'ananya.k@mopvaishnav.edu.in', 'major': 'Psychology', 'year': '2nd Year'},
        {'name': 'Divya Menon', 'email': 'divya.menon@mopvaishnav.edu.in', 'major': 'English Literature', 'year': '1st Year'},
        {'name': 'Shreya Patel', 'email': 'shreya.patel@mopvaishnav.edu.in', 'major': 'Business Administration', 'year': '3rd Year'},
        {'name': 'Kavya Reddy', 'email': 'kavya.reddy@mopvaishnav.edu.in', 'major': 'Mathematics', 'year': '2nd Year'},
        {'name': 'Meera Iyer', 'email': 'meera.iyer@mopvaishnav.edu.in', 'major': 'Chemistry', 'year': '3rd Year'},
        {'name': 'Riya Singh', 'email': 'riya.singh@mopvaishnav.edu.in', 'major': 'Economics', 'year': '1st Year'},
        {'name': 'Aishwarya Nair', 'email': 'aishwarya.nair@mopvaishnav.edu.in', 'major': 'Physics', 'year': '2nd Year'},
        {'name': 'Sneha Gupta', 'email': 'sneha.gupta@mopvaishnav.edu.in', 'major': 'History', 'year': '3rd Year'},
        {'name': 'Pooja Jain', 'email': 'pooja.jain@mopvaishnav.edu.in', 'major': 'Biotechnology', 'year': '2nd Year'}
    ]
    
    # Journal entries templates
    journal_templates = [
        {"content": "Today was overwhelming with so many assignments due. Feeling stressed about managing everything.", "sentiment": 0.3, "emotion": "negative"},
        {"content": "Had a great discussion in class today! Really enjoyed the lecture on {subject}.", "sentiment": 0.8, "emotion": "positive"},
        {"content": "Missing home and family. College life is harder than I expected.", "sentiment": 0.2, "emotion": "negative"},
        {"content": "Successfully completed my project presentation. Feeling accomplished!", "sentiment": 0.9, "emotion": "positive"},
        {"content": "Struggling to make friends here. Feeling quite lonely lately.", "sentiment": 0.25, "emotion": "negative"},
        {"content": "Exam stress is getting to me. Can't seem to focus on studies.", "sentiment": 0.3, "emotion": "negative"},
        {"content": "Joined the college cultural club today. Excited about upcoming events!", "sentiment": 0.85, "emotion": "positive"},
        {"content": "Had a fight with my roommate. Living away from home is challenging.", "sentiment": 0.2, "emotion": "negative"},
        {"content": "Got good marks in my mid-semester exam. All the hard work paid off!", "sentiment": 0.9, "emotion": "positive"},
        {"content": "Feeling anxious about my future career. So many decisions to make.", "sentiment": 0.35, "emotion": "negative"}
    ]
    
    # Calendar events templates
    calendar_templates = [
        {"title": "{major} Assignment Submission", "stress": "high"},
        {"title": "Mid-semester Exam - {major}", "stress": "critical"},
        {"title": "Group Project Meeting", "stress": "medium"},
        {"title": "Library Study Session", "stress": "low"},
        {"title": "Cultural Event Practice", "stress": "low"},
        {"title": "Career Counseling Session", "stress": "medium"},
        {"title": "Final Exam - {major}", "stress": "critical"},
        {"title": "Presentation Preparation", "stress": "high"},
        {"title": "Club Meeting", "stress": "minimal"},
        {"title": "Research Paper Deadline", "stress": "high"}
    ]
    
    # Support request templates
    support_templates = [
        {"message": "Feeling overwhelmed with academic pressure. Need someone to talk to.", "priority": "high"},
        {"message": "Having trouble adjusting to college life. Missing home a lot.", "priority": "medium"},
        {"message": "Anxiety about upcoming exams is affecting my sleep.", "priority": "high"},
        {"message": "Struggling with time management. Any tips would be helpful.", "priority": "medium"},
        {"message": "Feeling isolated and having difficulty making friends.", "priority": "medium"}
    ]
    
    user_ids = []
    
    # Create students
    for i, student in enumerate(students):
        first_name, last_name = student['name'].split(' ', 1)
        username = first_name.lower() + str(i+1)
        password_hash = hash_password('password123')
        
        c.execute('''INSERT INTO users 
                    (username, email, password_hash, role, first_name, last_name, 
                     university, major, year_of_study, phone, emergency_contact_name, 
                     emergency_contact_phone, emergency_contact_relationship) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (username, student['email'], password_hash, 'student', first_name, last_name,
                  'M.O.P Vaishnav College for Women(Autonomous)', student['major'], student['year'],
                  f'+91-98765{43210+i}', f'{first_name} Mother', f'+91-98765{54321+i}', 'Mother'))
        
        user_id = c.lastrowid
        user_ids.append(user_id)
        print(f"Created student: {student['name']} (ID: {user_id})")
    
    # Add journal entries (past 30 days)
    for user_id in user_ids:
        for day in range(30):
            if random.random() < 0.6:  # 60% chance of journal entry per day
                date = datetime.now() - timedelta(days=day)
                entry = random.choice(journal_templates)
                content = entry['content'].replace('{subject}', students[user_id-user_ids[0]]['major'])
                
                c.execute('''INSERT INTO journal_entries 
                            (user_id, content, sentiment_score, emotion_tags, created_at) 
                            VALUES (?, ?, ?, ?, ?)''',
                         (user_id, content, entry['sentiment'], entry['emotion'], date))
    
    # Add calendar events (next 30 days)
    for user_id in user_ids:
        student_major = students[user_id-user_ids[0]]['major']
        for week in range(4):
            for _ in range(random.randint(3, 6)):  # 3-6 events per week
                days_ahead = random.randint(week*7, (week+1)*7-1)
                event_date = datetime.now() + timedelta(days=days_ahead)
                event = random.choice(calendar_templates)
                title = event['title'].replace('{major}', student_major)
                
                c.execute('''INSERT INTO calendar_events 
                            (user_id, title, description, event_date, stress_level) 
                            VALUES (?, ?, ?, ?, ?)''',
                         (user_id, title, f'Academic event for {student_major}', 
                          event_date.strftime('%Y-%m-%d %H:%M:%S'), event['stress']))
    
    # Add support requests (some students)
    for user_id in random.sample(user_ids, 6):  # 6 out of 10 students have support requests
        for _ in range(random.randint(1, 3)):  # 1-3 requests per student
            days_ago = random.randint(1, 20)
            request_date = datetime.now() - timedelta(days=days_ago)
            support = random.choice(support_templates)
            
            c.execute('''INSERT INTO support_requests 
                        (user_id, message, priority, status, created_at) 
                        VALUES (?, ?, ?, ?, ?)''',
                     (user_id, support['message'], support['priority'], 
                      random.choice(['waiting', 'active', 'closed']), request_date))
    
    conn.commit()
    conn.close()
    print("\nSUCCESS: Created 10 MOP Vaishnav students with comprehensive data!")
    print("Data added:")
    print("- 10 students with complete profiles")
    print("- ~180 journal entries (past 30 days)")
    print("- ~140 calendar events (next 30 days)")
    print("- ~12 support requests")
    print("\nLogin credentials:")
    print("Username: priya1, ananya2, divya3, etc.")
    print("Password: password123")

if __name__ == "__main__":
    create_mop_students()