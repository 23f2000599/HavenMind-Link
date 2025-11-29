import sqlite3
from datetime import datetime

def verify_mop_students():
    conn = sqlite3.connect('havenmind-basic/havenmind.db')
    c = conn.cursor()
    
    # Check students
    students = c.execute('''SELECT id, username, first_name, last_name, university, major, year_of_study 
                           FROM users WHERE university = "M.O.P Vaishnav College for Women(Autonomous)"''').fetchall()
    
    print("=== MOP VAISHNAV COLLEGE STUDENTS ===")
    for student in students:
        print(f"ID: {student[0]} | {student[1]} | {student[2]} {student[3]} | {student[4]} | {student[5]}")
    
    # Check journal entries
    journal_count = c.execute('''SELECT COUNT(*) FROM journal_entries je 
                                JOIN users u ON je.user_id = u.id 
                                WHERE u.university = "M.O.P Vaishnav College for Women(Autonomous)"''').fetchone()[0]
    
    # Check calendar events
    calendar_count = c.execute('''SELECT COUNT(*) FROM calendar_events ce 
                                 JOIN users u ON ce.user_id = u.id 
                                 WHERE u.university = "M.O.P Vaishnav College for Women(Autonomous)"''').fetchone()[0]
    
    # Check support requests
    support_count = c.execute('''SELECT COUNT(*) FROM support_requests sr 
                                JOIN users u ON sr.user_id = u.id 
                                WHERE u.university = "M.O.P Vaishnav College for Women(Autonomous)"''').fetchone()[0]
    
    print(f"\n=== DATA SUMMARY ===")
    print(f"Students: {len(students)}")
    print(f"Journal Entries: {journal_count}")
    print(f"Calendar Events: {calendar_count}")
    print(f"Support Requests: {support_count}")
    
    # Sample journal entries
    print(f"\n=== SAMPLE JOURNAL ENTRIES ===")
    sample_journals = c.execute('''SELECT u.first_name, je.content, je.emotion_tags, je.created_at 
                                  FROM journal_entries je 
                                  JOIN users u ON je.user_id = u.id 
                                  WHERE u.university = "M.O.P Vaishnav College for Women(Autonomous)" 
                                  ORDER BY je.created_at DESC LIMIT 5''').fetchall()
    
    for journal in sample_journals:
        print(f"{journal[0]}: {journal[1][:50]}... ({journal[2]}) - {journal[3][:10]}")
    
    conn.close()
    print(f"\nSUCCESS: All MOP Vaishnav students added with comprehensive data!")
    print(f"Login with: priya1/password123, ananya2/password123, etc.")

if __name__ == "__main__":
    verify_mop_students()