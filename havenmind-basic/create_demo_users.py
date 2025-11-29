import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_demo_users():
    conn = sqlite3.connect('havenmind.db')
    c = conn.cursor()
    
    # Demo users for each role
    demo_users = [
        ('student_demo', 'student@demo.com', 'demo123', 'student'),
        ('peer_demo', 'peer@demo.com', 'demo123', 'peer_supporter'),
        ('professional_demo', 'professional@demo.com', 'demo123', 'professional'),
        ('admin_demo', 'admin@demo.com', 'demo123', 'admin'),
        ('ngo_demo', 'ngo@demo.com', 'demo123', 'ngo')
    ]
    
    for username, email, password, role in demo_users:
        password_hash = hash_password(password)
        
        # Check if user already exists
        existing = c.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if not existing:
            c.execute(
                'INSERT INTO users (username, email, password_hash, role, is_verified) VALUES (?, ?, ?, ?, 1)',
                (username, email, password_hash, role)
            )
            print(f"Created demo user: {username} ({role})")
        else:
            print(f"Demo user already exists: {username}")
    
    conn.commit()
    conn.close()
    print("Demo users created successfully!")

if __name__ == '__main__':
    create_demo_users()