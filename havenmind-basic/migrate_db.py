import sqlite3

def migrate_database():
    conn = sqlite3.connect('havenmind.db')
    c = conn.cursor()
    
    # Add all missing columns one by one
    columns_to_add = [
        ('first_name', 'TEXT'),
        ('last_name', 'TEXT'),
        ('university', 'TEXT'),
        ('major', 'TEXT'),
        ('phone', 'TEXT'),
        ('year_of_study', 'TEXT'),
        ('daily_checkins', 'BOOLEAN DEFAULT 1'),
        ('mood_reminders', 'BOOLEAN DEFAULT 1'),
        ('peer_notifications', 'BOOLEAN DEFAULT 0'),
        ('ai_insights', 'BOOLEAN DEFAULT 1'),
        ('appointment_reminders', 'BOOLEAN DEFAULT 1'),
        ('support_type', 'TEXT DEFAULT "self_help"'),
        ('emergency_alerts', 'BOOLEAN DEFAULT 1'),
        ('share_location', 'BOOLEAN DEFAULT 0'),
        ('auto_professional_escalation', 'BOOLEAN DEFAULT 0'),
        ('emergency_contact_name', 'TEXT'),
        ('emergency_contact_phone', 'TEXT'),
        ('emergency_contact_relationship', 'TEXT'),
        ('notification_method', 'TEXT DEFAULT "email"'),
        ('notification_time', 'TEXT DEFAULT "morning"'),
        ('share_research', 'BOOLEAN DEFAULT 0'),
        ('ai_analysis', 'BOOLEAN DEFAULT 1'),
        ('share_counselors', 'BOOLEAN DEFAULT 0')
    ]
    
    for column_name, column_type in columns_to_add:
        try:
            c.execute(f'ALTER TABLE users ADD COLUMN {column_name} {column_type}')
            print(f'Added column: {column_name}')
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e):
                print(f'Column {column_name} already exists')
            else:
                print(f'Error adding {column_name}: {e}')
    
    conn.commit()
    conn.close()
    print('Database migration completed!')

if __name__ == '__main__':
    migrate_database()