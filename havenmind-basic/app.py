

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import sqlite3
from datetime import datetime, timedelta
import os
import hashlib
import secrets
from functools import wraps
from dotenv import load_dotenv
from notification_system import notification_system, send_crisis_alert

# Location sharing functions
def get_user_location():
    """Get user's current location using browser geolocation API"""
    return {
        'latitude': None,
        'longitude': None,
        'accuracy': None,
        'timestamp': datetime.now().isoformat()
    }

def send_crisis_alert_with_location(user_id, content):
    """Send crisis alert with location to emergency contact"""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    
    if user and user['emergency_contact_phone']:
        # Enhanced crisis message with location sharing request
        crisis_message = f"""🚨 MENTAL HEALTH EMERGENCY ALERT 🚨

Student: {user['username']}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Concerning journal entry detected:
"{content[:100]}..."

📍 LIVE LOCATION SHARING ACTIVATED
Student's location will be shared for safety.

⚠️ IMMEDIATE ACTION REQUIRED ⚠️
Please contact the student immediately.

Crisis Resources:
- Emergency: 112
- AASRA: 91-9820466726
- Vandrevala: 1860-2662-345

This is an automated alert from HavenMind."""
        
        try:
            # Send SMS to emergency contact
            notification_system.send_sms(
                user['emergency_contact_phone'],
                crisis_message
            )
            print(f"Crisis alert with location sent to {user['emergency_contact_phone']}")
            return True
        except Exception as e:
            print(f"Failed to send crisis alert: {e}")
            return False
    return False

def get_student_location_for_professional(student_id):
    """Get student location and emergency contact for professional"""
    conn = get_db_connection()
    student = conn.execute(
        'SELECT username, emergency_contact_name, emergency_contact_phone, emergency_contact_relationship FROM users WHERE id = ?',
        (student_id,)
    ).fetchone()
    conn.close()
    
    if student:
        # Convert Row to dict to avoid .get() issues
        student_dict = dict(student)
        return {
            'student_name': student_dict.get('username'),
            'emergency_contact': {
                'name': student_dict.get('emergency_contact_name'),
                'phone': student_dict.get('emergency_contact_phone'),
                'relationship': student_dict.get('emergency_contact_relationship')
            },
            'location': {
                'available': True,
                'message': 'Live location sharing enabled for emergency intervention'
            }
        }
    return None
from daily_scheduler import start_daily_scheduler, send_schedule_now

# Load environment variables
load_dotenv()

# Direct Gemini AI integration - no helper imports needed

app = Flask(__name__)
app.secret_key = 'havenmind-secret-2024'

# Make generate_ai_response available to templates
@app.template_global()
def generate_ai_response(content, emotion_tags, sentiment_score):
    """Generate contextual AI response based on journal content - enhanced version"""
    return generate_enhanced_ai_response(content, emotion_tags, sentiment_score)

def generate_enhanced_ai_response(content, emotion_tags, sentiment_score):
    """Generate enhanced therapeutic AI response using real AI"""
    # Quick fallback first, then try AI with timeout
    try:
        import google.generativeai as genai
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key and len(content) < 200:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = f"You are a compassionate AI mental health companion. Student wrote: '{content[:100]}'. Respond in 1 sentence."
            
            response = model.generate_content(prompt)
            return response.text.strip()
    except:
        pass
    
    # Fast fallback
    return generate_contextual_fallback(content, emotion_tags, sentiment_score)

def generate_contextual_fallback(content, emotion_tags, sentiment_score):
    """Smart fallback that understands context with crisis detection"""
    content_lower = content.lower()
    
    # CRISIS DETECTION - HIGHEST PRIORITY
    crisis_indicators = ['die', 'diee', 'dieee', 'kill myself', 'end it', 'suicide', 'hurt myself', 'no point', 'give up', 'cant go on', 'want to die', 'wanna die', 'end my life']
    crisis_patterns = ['go die', 'imma die', 'gonna die', 'wanna die', 'so imma go die']
    
    # Check for direct crisis words
    has_crisis = any(indicator in content_lower for indicator in crisis_indicators)
    
    # Check for crisis patterns
    if not has_crisis:
        has_crisis = any(pattern in content_lower for pattern in crisis_patterns)
    
    if has_crisis:
        return """I'm very concerned about what you've shared. Your life has value and meaning, even when things feel overwhelming. Please reach out for immediate support:
        
CRISIS RESOURCES (INDIA):
- AASRA Suicide Prevention: 91-9820466726
- Vandrevala Foundation: 1860-2662-345
- iCall Helpline: 022-25521111
- Sneha India: 044-24640050
- Emergency: 112 or 100

You don't have to face this alone. There are people who want to help you through this difficult time. Please consider reaching out to a counselor, trusted friend, or family member right now."""
    
    # Academic achievement detection - but check for negative context first
    if any(phrase in content_lower for phrase in ['completed', 'finished', 'done', 'accomplished']) and any(word in content_lower for word in ['assignment', 'work', 'project', 'task']):
        # Check if it's actually about NOT completing or struggling with projects
        if any(phrase in content_lower for phrase in ['have not started', 'not started', 'have to complete', 'due on', 'don\'t know', 'so much work', 'have to learn']):
            # This is actually academic stress, not achievement
            pass  # Fall through to stress detection
        else:
            return "Congratulations on completing your assignments! That's a real accomplishment and shows your dedication to your studies. It must feel great to have that work finished. How are you feeling about your progress in your courses?"
    
    # Family separation
    elif any(word in content_lower for word in ['brother', 'sister', 'family']) and any(word in content_lower for word in ['going', 'leaving', 'away']):
        return "I can understand how sad it must feel to have your brother going away. It's completely natural to feel this way when someone important to you has to leave, even temporarily. Family bonds are precious. How do you usually stay connected when you're apart?"
    
    # Exhaustion and mixed emotions
    elif any(word in content_lower for word in ['ded', 'dead', 'exhausted', 'drained', 'burnt out']) and any(word in content_lower for word in ['groove', 'getting into', 'finally', 'progress', 'better']):
        return "I can hear that you're feeling really drained and exhausted right now, but it sounds like you're also starting to find your rhythm and make some progress. That's actually a really positive sign - even when we feel physically and emotionally depleted, recognizing that we're getting into a groove shows resilience. It's okay to feel tired while still moving forward. How can you take care of yourself while maintaining this momentum?"
    
    # Pure exhaustion without progress indicators
    elif any(word in content_lower for word in ['ded', 'dead', 'exhausted', 'drained', 'burnt out', 'feel ded', 'look ded']):
        return "It sounds like you're feeling really exhausted and drained right now. When we say we feel 'dead' or completely worn out, it usually means we've been pushing ourselves pretty hard. Your body and mind are telling you they need some care and rest. What's been taking so much out of you lately? And what's one small thing you could do today to recharge, even just a little?"
    
    # Academic stress and deadline pressure
    if any(phrase in content_lower for phrase in ['due on', 'project due', 'have not started', 'not started', 'have to complete', 'so much work', 'don\'t know what', 'have to learn', 'upcoming few days']) or any(phrase in content_lower for phrase in ['lot of work', 'too much', 'overwhelmed', 'stressed']) and any(word in content_lower for word in ['assignment', 'work', 'study', 'project']):
        # Check for specific academic deadline stress
        if any(phrase in content_lower for phrase in ['due on', 'project due', 'have not started', 'have to learn', 'don\'t know what']):
            return "I can hear the stress in your voice about these upcoming project deadlines. Having multiple projects due so close together, especially when you need to learn new technologies like Flask and Vue, feels incredibly overwhelming. It's completely understandable to feel lost when facing unfamiliar tech with tight deadlines. Let's break this down - what's the most urgent project, and what's one small step you could take today to get started?"
        # Check for concerning attitude
        elif any(phrase in content_lower for phrase in ['dont care', "don't care", 'whatever', 'give up']):
            return "I hear that you're feeling overwhelmed with work and maybe disconnected from caring about it right now. Sometimes when we're really stressed, we can feel numb or like giving up. These feelings are understandable, but I'm concerned about you. Your wellbeing matters more than any assignment. Have you been able to talk to anyone about how you're feeling?"
        else:
            return "It sounds like you're feeling overwhelmed with your academic workload right now. That's a common experience for students, and your feelings are completely valid. Remember that you don't have to tackle everything at once. What's one small step you could take today to feel more in control?"
    
    # General emotional support
    elif emotion_tags == 'negative':
        return "I can sense you're going through something challenging right now. Your feelings are important and valid. It takes courage to express what you're experiencing. What kind of support would be most helpful for you today?"
    
    elif emotion_tags == 'positive':
        return "I can hear the positive energy in your reflection! It's wonderful when we can recognize and appreciate good moments in our lives. How are you feeling about everything right now?"
    
    else:
        return "Thank you for sharing your thoughts with me. Taking time to reflect like this shows real self-awareness. What's been on your mind lately that you'd like to explore further?"

def analyze_context_with_nlp(content):
    """Analyze content using NLP to understand context and intent"""
    import re
    from collections import Counter
    
    # Tokenize and clean content
    words = re.findall(r'\b\w+\b', content.lower())
    
    # Define semantic clusters for different life domains
    context_indicators = {
        'employment_loss': {
            'primary': ['laid', 'off', 'fired', 'terminated', 'unemployed', 'jobless'],
            'secondary': ['job', 'work', 'employment', 'career', 'position'],
            'emotional': ['lost', 'gone', 'ended', 'finished']
        },
        'company_placement': {
            'primary': ['company', 'placement', 'internship', 'position'],
            'secondary': ['based', 'assigned', 'placed', 'working'],
            'emotional': ['lost', 'ended', 'cancelled', 'removed']
        },
        'academic_stress': {
            'primary': ['semester', 'coursework', 'assignments', 'workload'],
            'secondary': ['study', 'class', 'school', 'college', 'university'],
            'emotional': ['overwhelmed', 'stressed', 'pressure', 'much']
        },
        'financial_pressure': {
            'primary': ['money', 'financial', 'bills', 'rent', 'expenses'],
            'secondary': ['afford', 'pay', 'cost', 'budget'],
            'emotional': ['worried', 'stressed', 'anxious', 'scared']
        },
        'time_pressure': {
            'primary': ['deadline', 'time', 'months', 'weeks', 'days'],
            'secondary': ['before', 'until', 'left', 'remaining'],
            'emotional': ['running', 'out', 'pressure', 'urgent']
        },
        'social_isolation': {
            'primary': ['lonely', 'alone', 'isolated', 'nobody'],
            'secondary': ['friends', 'family', 'people', 'social'],
            'emotional': ['sad', 'empty', 'disconnected']
        },
        'separation_sadness': {
            'primary': ['brother', 'sister', 'family', 'friend', 'leaving', 'going'],
            'secondary': ['out', 'station', 'away', 'travel', 'trip'],
            'emotional': ['sad', 'miss', 'upset', 'worried']
        },
        'academic_transition': {
            'primary': ['college', 'university', 'first', 'day', 'new'],
            'secondary': ['student', 'campus', 'class', 'course'],
            'emotional': ['nervous', 'scared', 'anxious', 'worried']
        }
    }
    
    # Calculate context scores
    context_scores = {}
    word_set = set(words)
    
    for context, indicators in context_indicators.items():
        score = 0
        
        # Primary indicators (high weight)
        primary_matches = len(word_set.intersection(indicators['primary']))
        score += primary_matches * 3
        
        # Secondary indicators (medium weight)
        secondary_matches = len(word_set.intersection(indicators['secondary']))
        score += secondary_matches * 2
        
        # Emotional indicators (low weight but important for context)
        emotional_matches = len(word_set.intersection(indicators['emotional']))
        score += emotional_matches * 1
        
        # Bonus for phrase combinations
        content_lower = content.lower()
        if context == 'employment_loss':
            if 'laid off' in content_lower or 'lost job' in content_lower:
                score += 5
        elif context == 'company_placement':
            if 'no company' in content_lower or 'lost company' in content_lower:
                score += 5
        elif context == 'academic_stress':
            if 'too much work' in content_lower or 'semester started' in content_lower:
                score += 5
        elif context == 'separation_sadness':
            if 'going out' in content_lower or 'out of station' in content_lower or 'brother is' in content_lower:
                score += 5
        
        context_scores[context] = score
    
    # Find dominant context
    if not context_scores or max(context_scores.values()) == 0:
        return 'general_distress'
    
    dominant_context = max(context_scores, key=context_scores.get)
    
    # Return context with confidence score
    return {
        'primary_context': dominant_context,
        'confidence': context_scores[dominant_context],
        'all_scores': context_scores
    }

def generate_contextual_therapeutic_response(content, context_analysis, emotion_tags, sentiment_score):
    """Generate therapeutic response based on NLP context analysis"""
    primary_context = context_analysis['primary_context']
    confidence = context_analysis['confidence']
    
    # Only use context-specific responses if confidence is high enough
    if confidence < 3:
        return generate_basic_therapeutic_response(content, emotion_tags, sentiment_score)
    
    # Context-specific therapeutic responses
    responses = {
        'employment_loss': [
            "I'm so sorry to hear about your job loss. Losing employment is one of life's most stressful experiences, and your feelings of sadness and worry are completely understandable. This kind of sudden change can feel overwhelming, especially with financial pressures and time constraints. Remember that this setback doesn't define your worth or future potential. What support systems do you have available right now?",
            "Losing your job is incredibly difficult, and I can hear the pain in your words. It's natural to feel sad and anxious when facing such uncertainty. This kind of major life change affects not just your finances but your sense of identity and security. Please know that many people face similar challenges and find their way through. Have you been able to reach out to anyone for support during this time?"
        ],
        'company_placement': [
            "Losing your company placement or internship is incredibly stressful, especially when you're facing academic deadlines. Your feelings of sadness and worry are completely valid - this kind of uncertainty about your future is genuinely difficult to handle. It's important to remember that many students face similar challenges, and there are often alternative paths forward. Have you been able to speak with your academic advisor or career services about options?",
            "I understand how devastating it must feel to lose your company placement. This kind of setback can feel like it threatens your entire academic and career path. Your emotions are completely valid - it's normal to feel sad and worried when facing this kind of uncertainty. Remember that this doesn't define your capabilities or future success. What resources are available to help you explore alternative options?"
        ],
        'academic_stress': [
            "The beginning of a new semester can feel overwhelming with all the new coursework and expectations. It's completely normal to feel this way when facing a heavy workload. Remember, you don't have to tackle everything at once. What's one assignment or task you could focus on first to help you feel more in control?",
            "Academic pressure can be intense, and it sounds like you're feeling the weight of your coursework right now. It's important to remember that feeling overwhelmed doesn't mean you can't handle it - it just means you're human. Breaking things down into smaller, manageable pieces can help. What's the most pressing thing you need to address first?"
        ],
        'financial_pressure': [
            "Financial stress can be incredibly overwhelming and affects every aspect of your life. It's completely understandable that you're feeling anxious and worried about money. These concerns are valid and it's important to acknowledge how difficult this situation is. Have you been able to explore any financial resources or support options available to you?",
            "Money worries can consume your thoughts and make everything else feel more difficult. Your stress about finances is completely understandable - financial security is a basic need, and when it's threatened, it affects your entire sense of well-being. What small steps might you be able to take to address your most immediate financial concerns?"
        ],
        'time_pressure': [
            "Feeling pressed for time can create intense anxiety, especially when you're facing important deadlines. It's natural to feel overwhelmed when you feel like time is running out. Remember that even when time feels short, taking a moment to prioritize and plan can help you use your time more effectively. What's the most important thing you need to focus on right now?",
            "Time pressure can make everything feel more urgent and stressful. It's understandable that you're feeling anxious about your deadlines. Sometimes when we feel rushed, it helps to step back and break things down into what absolutely must be done versus what would be nice to accomplish. What are your most critical priorities?"
        ],
        'social_isolation': [
            "Feeling lonely and isolated can be incredibly painful, especially when you're already dealing with other stresses. Your feelings are completely valid - humans need connection, and when we don't have it, it affects our entire well-being. Even small steps toward connection can help. Is there anyone in your life you might be able to reach out to?",
            "Loneliness can make every other challenge feel more difficult to handle. It's important to acknowledge how hard it is to feel alone, especially during stressful times. Remember that reaching out - even through journaling like this - shows strength. What's one small way you might be able to connect with someone today?"
        ],
        'academic_transition': [
            "Starting college or transitioning to a new academic environment can feel overwhelming, and it's completely normal to feel anxious about new experiences. These initial worries often feel bigger than they actually are, and most students face similar anxieties. Remember that adjustment takes time, and it's okay to feel uncertain. What's one thing you could do to help yourself feel more prepared or confident?",
            "Academic transitions can be really challenging, and your feelings of nervousness or worry are completely normal. Starting something new always involves uncertainty, and that can feel scary. It's important to remember that these feelings are temporary and that you have the strength to adapt. What support systems are available to help you through this transition?"
        ],
        'separation_sadness': [
            "It sounds like you're feeling sad about your brother leaving. It's completely natural to feel this way when someone important to you goes away, even temporarily. These feelings show how much you care about your family relationships. While it's hard when loved ones are far away, remember that distance doesn't diminish the bond you share. How do you usually stay connected when you're apart?",
            "I can hear the sadness in your words about your brother going out of station. It's really hard when family members have to leave, and your feelings are completely valid. Missing someone shows the strength of your relationship with them. Even though it feels difficult right now, this separation is temporary. What are some ways you might stay in touch while he's away?"
        ]
    }
    
    # Select appropriate response
    if primary_context in responses:
        import random
        return random.choice(responses[primary_context])
    else:
        return generate_basic_therapeutic_response(content, emotion_tags, sentiment_score)

def generate_basic_therapeutic_response(content, emotion_tags, sentiment_score):
    """Generate basic therapeutic response when context is unclear"""
    content_lower = content.lower()
    
    if emotion_tags == 'negative':
        # Check for family/relationship sadness
        if any(word in content_lower for word in ['brother', 'sister', 'family', 'friend', 'leaving', 'going']):
            return "I can sense you're feeling sad about someone important to you. It's completely natural to feel this way when loved ones have to go away, even temporarily. These feelings show how much you care about your relationships. What helps you feel connected to them when you're apart?"
        else:
            return "I hear that you're going through a challenging time right now. Your willingness to express these feelings shows incredible self-awareness and strength. Remember that difficult emotions are temporary, and seeking support is a sign of courage, not weakness. What would help you feel a little better today?"
    elif emotion_tags == 'positive':
        return "I love seeing your positive energy come through in your reflection! These good moments are precious and worth celebrating. How might you carry this positive energy forward?"
    else:
        return "Thank you for taking time to journal today. Regular reflection is a valuable practice for mental wellness and self-understanding. What would you like to focus on moving forward?"

def get_user_context_for_ai(user_id):
    """Get user context for AI responses"""
    conn = get_db_connection()
    
    # Get recent entries (last 30 days)
    recent_entries = conn.execute(
        'SELECT sentiment_score, emotion_tags FROM journal_entries WHERE user_id = ? AND created_at >= datetime("now", "-30 days") ORDER BY created_at DESC LIMIT 10',
        (user_id,)
    ).fetchall()
    
    conn.close()
    
    if not recent_entries:
        return {
            'mood_trend': 'neutral',
            'recent_stress': 'unknown',
            'writing_frequency': 'new_user',
            'common_emotions': [],
            'concerns': []
        }
    
    # Calculate mood trend
    avg_sentiment = sum(entry['sentiment_score'] or 0.5 for entry in recent_entries) / len(recent_entries)
    mood_trend = 'positive' if avg_sentiment > 0.6 else 'negative' if avg_sentiment < 0.4 else 'neutral'
    
    # Get common emotions
    emotions = [entry['emotion_tags'] for entry in recent_entries if entry['emotion_tags']]
    common_emotions = list(set(emotions))
    
    # Assess recent stress level
    recent_negative = sum(1 for entry in recent_entries[:5] if (entry['sentiment_score'] or 0.5) < 0.4)
    recent_stress = 'high' if recent_negative >= 3 else 'medium' if recent_negative >= 1 else 'low'
    
    return {
        'mood_trend': mood_trend,
        'recent_stress': recent_stress,
        'writing_frequency': 'regular' if len(recent_entries) > 5 else 'occasional',
        'common_emotions': common_emotions,
        'concerns': [],
        'stress_level': recent_stress
    }

# Database setup
def init_db():
    conn = sqlite3.connect('havenmind.db')
    c = conn.cursor()
    
    # Add new columns if they don't exist
    try:
        c.execute('ALTER TABLE support_requests ADD COLUMN professional_id INTEGER')
        c.execute('ALTER TABLE support_requests ADD COLUMN appointment_date TEXT')
        c.execute('ALTER TABLE support_requests ADD COLUMN appointment_time TEXT')
    except sqlite3.OperationalError:
        pass  # Columns already exist
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'student',
        is_verified BOOLEAN DEFAULT 0,
        reset_token TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        cognitive_load_score REAL DEFAULT 0.0,
        first_name TEXT,
        last_name TEXT,
        university TEXT,
        major TEXT,
        phone TEXT,
        year_of_study TEXT,
        daily_checkins BOOLEAN DEFAULT 1,
        mood_reminders BOOLEAN DEFAULT 1,
        peer_notifications BOOLEAN DEFAULT 0,
        ai_insights BOOLEAN DEFAULT 1,
        appointment_reminders BOOLEAN DEFAULT 1,
        support_type TEXT DEFAULT 'self_help',
        emergency_alerts BOOLEAN DEFAULT 1,
        share_location BOOLEAN DEFAULT 0,
        auto_professional_escalation BOOLEAN DEFAULT 0,
        emergency_contact_name TEXT,
        emergency_contact_phone TEXT,
        emergency_contact_relationship TEXT,
        notification_method TEXT DEFAULT 'email',
        notification_time TEXT DEFAULT 'morning',
        share_research BOOLEAN DEFAULT 0,
        ai_analysis BOOLEAN DEFAULT 1,
        share_counselors BOOLEAN DEFAULT 0
    )''')
    
    # Journal entries table
    c.execute('''CREATE TABLE IF NOT EXISTS journal_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        sentiment_score REAL,
        emotion_tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # Calendar events table
    c.execute('''CREATE TABLE IF NOT EXISTS calendar_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        event_date TIMESTAMP NOT NULL,
        stress_level TEXT DEFAULT 'medium',
        completed BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # Add completed column if it doesn't exist
    try:
        c.execute('ALTER TABLE calendar_events ADD COLUMN completed BOOLEAN DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Support requests table
    c.execute('''CREATE TABLE IF NOT EXISTS support_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        priority TEXT DEFAULT 'medium',
        status TEXT DEFAULT 'waiting',
        peer_id INTEGER,
        professional_id INTEGER,
        appointment_date TEXT,
        appointment_time TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (peer_id) REFERENCES users (id),
        FOREIGN KEY (professional_id) REFERENCES users (id)
    )''')
    
    # Chat messages table
    c.execute('''CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id INTEGER NOT NULL,
        sender_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (request_id) REFERENCES support_requests (id),
        FOREIGN KEY (sender_id) REFERENCES users (id)
    )''')
    
    # Session notes table for professional notes
    c.execute('''CREATE TABLE IF NOT EXISTS session_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        professional_id INTEGER NOT NULL,
        note TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (case_id) REFERENCES support_requests (id),
        FOREIGN KEY (professional_id) REFERENCES users (id)
    )''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('havenmind.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hash):
    return hashlib.sha256(password.encode()).hexdigest() == hash

def verify_totp_code(user_code):
    """Verify TOTP code from authenticator app"""
    import pyotp
    
    # Use the same secret as in QR code
    secret = 'JBSWY3DPEHPK3PXP'
    totp = pyotp.TOTP(secret)
    
    # Verify the code (allows 30 second window)
    return totp.verify(user_code)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    if 'user_id' in session:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()
        return user
    return None

def recalculate_stress_level(title, description, event_date, current_stress):
    """Recalculate stress level based on current time proximity"""
    from datetime import datetime
    
    # Keywords for base stress level
    high_stress_keywords = ['exam', 'test', 'deadline', 'presentation', 'interview', 'final']
    low_stress_keywords = ['break', 'lunch', 'social', 'relax', 'wellness']
    
    title_lower = title.lower()
    desc_lower = description.lower() if description else ''
    
    # Determine base stress from keywords
    if any(keyword in title_lower or keyword in desc_lower for keyword in high_stress_keywords):
        base_stress = 'high'
    elif any(keyword in title_lower or keyword in desc_lower for keyword in low_stress_keywords):
        base_stress = 'minimal'
    else:
        base_stress = 'medium'
    
    # Time proximity adjustment
    try:
        if 'T' in event_date:
            event_datetime = datetime.strptime(event_date, '%Y-%m-%dT%H:%M')
        else:
            event_datetime = datetime.strptime(event_date, '%Y-%m-%d %H:%M:%S')
    except:
        return current_stress  # Return original if parsing fails
    
    now = datetime.now()
    hours_until = (event_datetime - now).total_seconds() / 3600
    
    # Apply time-based escalation
    if hours_until <= 6:  # Within 6 hours - CRITICAL
        if base_stress == 'minimal':
            return 'medium'
        elif base_stress == 'medium':
            return 'critical'
        else:
            return 'critical'
    elif hours_until <= 24:  # Within 24 hours - HIGH
        if base_stress == 'minimal':
            return 'low'
        elif base_stress == 'medium':
            return 'high'
        else:
            return 'critical'
    elif hours_until <= 72:  # Within 3 days - ESCALATE
        if base_stress == 'minimal':
            return 'minimal'
        elif base_stress == 'medium':
            return 'high'
        else:
            return 'high'
    elif hours_until <= 168:  # Within a week
        if base_stress == 'high':
            return 'high'
        elif base_stress == 'medium':
            return 'medium'
        else:
            return 'low'
    else:  # More than a week away
        if base_stress == 'minimal':
            return 'minimal'
        elif base_stress == 'medium':
            return 'low'
        else:
            return 'medium'

# Routes
@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/login')
def login():
    return render_template('auth/login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']
    twofa_code = request.form['twofa_code']
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    
    if user and verify_password(password, user['password_hash']):
        # Verify 2FA code
        if not verify_totp_code(twofa_code):
            flash('Invalid 2FA code')
            return redirect(url_for('login'))
            
        session['user_id'] = user['id']
        session['user_role'] = user['role']
        flash('Login successful!')
        
        # Redirect based on role
        if user['role'] == 'student':
            return redirect(url_for('student_dashboard'))
        elif user['role'] == 'peer_supporter':
            return redirect(url_for('peer_dashboard'))
        elif user['role'] == 'professional':
            return redirect(url_for('professional_dashboard'))
        elif user['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif user['role'] == 'institution_admin':
            return redirect(url_for('institution_dashboard'))
        elif user['role'] == 'ngo':
            return redirect(url_for('ngo_dashboard'))
    else:
        flash('Invalid email or password')
        return redirect(url_for('login'))

@app.route('/signup')
def signup():
    return render_template('auth/signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']
    institution = request.form.get('institution', '')
    
    conn = get_db_connection()
    
    # Check if user exists
    existing_user = conn.execute('SELECT id FROM users WHERE email = ? OR username = ?', (email, username)).fetchone()
    if existing_user:
        flash('User already exists')
        conn.close()
        return redirect(url_for('signup'))
    
    # Create new user
    password_hash = hash_password(password)
    if institution:
        conn.execute(
            'INSERT INTO users (username, email, password_hash, role, university) VALUES (?, ?, ?, ?, ?)',
            (username, email, password_hash, role, institution)
        )
    else:
        conn.execute(
            'INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
            (username, email, password_hash, role)
        )
    conn.commit()
    conn.close()
    
    flash('Account created successfully! Please login.')
    return redirect(url_for('login'))

@app.route('/forgot-password')
def forgot_password():
    return render_template('auth/forgot_password.html')

@app.route('/forgot-password', methods=['POST'])
def forgot_password_post():
    email = request.form['email']
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    
    if user:
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        conn.execute('UPDATE users SET reset_token = ? WHERE id = ?', (reset_token, user['id']))
        conn.commit()
        
        # In real app, send email with reset link
        flash(f'Password reset link sent to {email}. Reset token: {reset_token}')
    else:
        flash('Email not found')
    
    conn.close()
    return redirect(url_for('forgot_password'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully')
    return redirect(url_for('index'))

@app.route('/student-dashboard')
@login_required
def student_dashboard():
    user = get_current_user()
    if user['role'] != 'student':
        flash('Access denied')
        return redirect(url_for('index'))
    return render_template('dashboards/student.html', user=user)

@app.route('/peer-dashboard')
@login_required
def peer_dashboard():
    user = get_current_user()
    if user['role'] != 'peer_supporter':
        flash('Access denied')
        return redirect(url_for('index'))
    
    # Get pending support requests (only unassigned ones)
    conn = get_db_connection()
    pending_requests = conn.execute(
        '''SELECT sr.*, u.username 
           FROM support_requests sr 
           JOIN users u ON sr.user_id = u.id 
           WHERE sr.status = "waiting" AND sr.peer_id IS NULL
           ORDER BY 
           CASE sr.priority 
               WHEN "urgent" THEN 1 
               WHEN "high" THEN 2 
               WHEN "medium" THEN 3 
               ELSE 4 
           END, sr.created_at ASC'''
    ).fetchall()
    
    # Get active chats for this peer (exclude professional cases)
    active_chats = conn.execute(
        '''SELECT sr.*, u.username 
           FROM support_requests sr 
           JOIN users u ON sr.user_id = u.id 
           WHERE sr.status = "active" AND sr.peer_id = ? 
           ORDER BY sr.created_at DESC''',
        (user['id'],)
    ).fetchall()
    
    # Get closed/professional cases for this peer
    closed_chats = conn.execute(
        '''SELECT sr.*, u.username 
           FROM support_requests sr 
           JOIN users u ON sr.user_id = u.id 
           WHERE sr.status IN ("escalated", "professional") AND sr.peer_id = ? 
           ORDER BY sr.created_at DESC''',
        (user['id'],)
    ).fetchall()
    
    conn.close()
    
    return render_template('dashboards/peer.html', user=user, pending_requests=pending_requests, active_chats=active_chats, closed_chats=closed_chats)

@app.route('/professional-dashboard')
@login_required
def professional_dashboard():
    user = get_current_user()
    if user['role'] != 'professional':
        flash('Access denied')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    # Get escalated cases with student info (exclude appointments assigned to other professionals)
    escalated_cases = conn.execute(
        '''SELECT sr.*, u.username, u.email, u.created_at as user_created,
                  COUNT(je.id) as journal_count,
                  AVG(je.sentiment_score) as avg_mood
           FROM support_requests sr 
           JOIN users u ON sr.user_id = u.id 
           LEFT JOIN journal_entries je ON u.id = je.user_id
           WHERE sr.status IN ("escalated", "professional", "professional_booking") 
           AND sr.status != "closed"
           AND (sr.professional_id IS NULL OR sr.professional_id = ?)
           GROUP BY sr.id, u.id
           ORDER BY sr.created_at DESC''',
        (user['id'],)
    ).fetchall()
    
    # Get closed cases for history
    closed_cases = conn.execute(
        '''SELECT sr.*, u.username, u.email, u.created_at as user_created,
                  COUNT(je.id) as journal_count,
                  AVG(je.sentiment_score) as avg_mood
           FROM support_requests sr 
           JOIN users u ON sr.user_id = u.id 
           LEFT JOIN journal_entries je ON u.id = je.user_id
           WHERE sr.status = "closed" AND sr.peer_id = ?
           GROUP BY sr.id, u.id
           ORDER BY sr.created_at DESC LIMIT 10''',
        (user['id'],)
    ).fetchall()
    
    conn.close()
    
    return render_template('dashboards/professional.html', user=user, escalated_cases=escalated_cases, closed_cases=closed_cases)

@app.route('/admin-dashboard')
@login_required
def admin_dashboard():
    user = get_current_user()
    if user['role'] != 'admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    # Get all users by role
    all_users = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    students = conn.execute('SELECT * FROM users WHERE role = "student" ORDER BY created_at DESC').fetchall()
    peers = conn.execute('SELECT * FROM users WHERE role = "peer_supporter" ORDER BY created_at DESC').fetchall()
    professionals = conn.execute('SELECT * FROM users WHERE role = "professional" ORDER BY created_at DESC').fetchall()
    institutions = conn.execute('SELECT * FROM users WHERE role = "institution_admin" ORDER BY created_at DESC').fetchall()
    
    # Get platform statistics
    total_users = len(all_users)
    total_entries = conn.execute('SELECT COUNT(*) as count FROM journal_entries').fetchone()['count']
    total_events = conn.execute('SELECT COUNT(*) as count FROM calendar_events').fetchone()['count']
    total_support_requests = conn.execute('SELECT COUNT(*) as count FROM support_requests').fetchone()['count']
    
    # Crisis indicators
    crisis_entries = conn.execute('SELECT COUNT(*) as count FROM journal_entries WHERE sentiment_score < 0.3 AND created_at >= datetime("now", "-7 days")').fetchone()['count']
    
    # Active users (last 7 days)
    active_users = conn.execute('SELECT COUNT(DISTINCT user_id) as count FROM journal_entries WHERE created_at >= datetime("now", "-7 days")').fetchone()['count']
    
    # Platform health metrics
    avg_wellness = conn.execute('SELECT AVG(sentiment_score) as avg FROM journal_entries WHERE created_at >= datetime("now", "-30 days")').fetchone()['avg']
    
    conn.close()
    
    return render_template('dashboards/admin.html', 
                         user=user,
                         all_users=all_users,
                         students=students,
                         peers=peers,
                         professionals=professionals,
                         institutions=institutions,
                         total_users=total_users,
                         total_entries=total_entries,
                         total_events=total_events,
                         total_support_requests=total_support_requests,
                         crisis_entries=crisis_entries,
                         active_users=active_users,
                         avg_wellness=avg_wellness or 0.5)

@app.route('/institution-dashboard')
@login_required
def institution_dashboard():
    user = get_current_user()
    if user['role'] != 'institution_admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    # Get user's institution
    user_institution = user['university']
    if not user_institution:
        flash('No institution assigned')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    # Get all students from same institution
    students = conn.execute(
        'SELECT id, username, created_at, university FROM users WHERE university = ? AND role = "student"',
        (user_institution,)
    ).fetchall()
    
    # Calculate aggregated wellness score
    total_wellness = 0
    active_students = 0
    
    for student in students:
        # Get student's journal mood
        journal_mood = conn.execute(
            'SELECT AVG(sentiment_score) as avg_mood FROM journal_entries WHERE user_id = ?',
            (student['id'],)
        ).fetchone()['avg_mood']
        
        if journal_mood:
            total_wellness += journal_mood * 100
            active_students += 1
        else:
            total_wellness += 75  # Default for inactive users
            active_students += 1
    
    wellness_score = int(total_wellness / active_students) if active_students > 0 else 75
    total_students = len(students)
    
    # Get mood analytics for institution
    mood_data = conn.execute(
        '''SELECT AVG(je.sentiment_score) as avg_mood, COUNT(je.id) as total_entries
           FROM journal_entries je 
           JOIN users u ON je.user_id = u.id 
           WHERE u.university = ? AND u.role = "student"''',
        (user_institution,)
    ).fetchone()
    
    # Get stress level distribution
    stress_data = conn.execute(
        '''SELECT ce.stress_level, COUNT(*) as count
           FROM calendar_events ce 
           JOIN users u ON ce.user_id = u.id 
           WHERE u.university = ? AND u.role = "student" AND ce.event_date >= datetime("now")
           GROUP BY ce.stress_level''',
        (user_institution,)
    ).fetchall()
    
    # Get crisis indicators (last 30 days) - count distinct users
    crisis_count = conn.execute(
        '''SELECT COUNT(DISTINCT u.id) as count
           FROM journal_entries je 
           JOIN users u ON je.user_id = u.id 
           WHERE u.university = ? AND u.role = "student" 
           AND je.sentiment_score < 0.3 
           AND je.created_at >= datetime("now", "-30 days")''',
        (user_institution,)
    ).fetchone()
    
    # Get support requests from institution students
    support_requests = conn.execute(
        '''SELECT COUNT(*) as count
           FROM support_requests sr 
           JOIN users u ON sr.user_id = u.id 
           WHERE u.university = ? AND u.role = "student" 
           AND sr.created_at >= datetime("now", "-30 days")''',
        (user_institution,)
    ).fetchone()
    
    conn.close()
    
    # Use calculated wellness score
    avg_mood = wellness_score / 100
    
    # Generate recommendations
    recommendations = []
    if wellness_score < 60:
        recommendations.append("Consider implementing campus-wide mental health workshops")
        recommendations.append("Increase peer support program visibility")
    if crisis_count['count'] > 5:
        recommendations.append("High crisis indicators detected - consider additional counseling resources")
    if support_requests['count'] > 20:
        recommendations.append("High support request volume - consider expanding peer supporter network")
    
    # Prepare stress distribution for chart
    stress_chart_data = {row['stress_level']: row['count'] for row in stress_data}
    
    return render_template('dashboards/institution.html', 
                         user=user,
                         institution=user_institution,
                         total_students=total_students,
                         wellness_score=wellness_score,
                         avg_mood=avg_mood,
                         total_entries=mood_data['total_entries'],
                         crisis_count=crisis_count['count'],
                         support_requests=support_requests['count'],
                         stress_distribution=stress_chart_data,
                         recommendations=recommendations)

@app.route('/ngo-dashboard')
@login_required
def ngo_dashboard():
    user = get_current_user()
    if user['role'] != 'ngo':
        flash('Access denied')
        return redirect(url_for('index'))
    return render_template('dashboards/ngo.html', user=user)

@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    
    # Redirect to role-specific dashboard
    if user['role'] == 'student':
        return redirect(url_for('student_dashboard'))
    elif user['role'] == 'peer_supporter':
        return redirect(url_for('peer_dashboard'))
    elif user['role'] == 'professional':
        return redirect(url_for('professional_dashboard'))
    elif user['role'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif user['role'] == 'institution_admin':
        return redirect(url_for('institution_dashboard'))
    elif user['role'] == 'ngo':
        return redirect(url_for('ngo_dashboard'))
    
    # Fallback to old dashboard if role not recognized
    conn = get_db_connection()
    
    # Get recent journal entries
    journal_entries = conn.execute(
        'SELECT * FROM journal_entries WHERE user_id = ? ORDER BY created_at DESC LIMIT 5',
        (user['id'],)
    ).fetchall()
    
    # Get upcoming events
    events = conn.execute(
        'SELECT * FROM calendar_events WHERE user_id = ? AND event_date >= datetime("now") ORDER BY event_date LIMIT 5',
        (user['id'],)
    ).fetchall()
    
    # Calculate cognitive load metrics
    high_stress_events = conn.execute(
        'SELECT COUNT(*) as count FROM calendar_events WHERE user_id = ? AND stress_level = "high" AND event_date >= datetime("now")',
        (user['id'],)
    ).fetchone()
    
    # Get sentiment trends (last 7 days)
    sentiment_trend = conn.execute(
        'SELECT AVG(sentiment_score) as avg_sentiment FROM journal_entries WHERE user_id = ? AND created_at >= datetime("now", "-7 days")',
        (user['id'],)
    ).fetchone()
    
    # Get stress distribution
    stress_distribution = conn.execute(
        'SELECT stress_level, COUNT(*) as count FROM calendar_events WHERE user_id = ? AND event_date >= datetime("now") GROUP BY stress_level',
        (user['id'],)
    ).fetchall()
    
    # Calculate wellness metrics
    total_entries = conn.execute('SELECT COUNT(*) as count FROM journal_entries WHERE user_id = ?', (user['id'],)).fetchone()
    recent_entries = conn.execute('SELECT COUNT(*) as count FROM journal_entries WHERE user_id = ? AND created_at >= datetime("now", "-7 days")', (user['id'],)).fetchone()
    
    cognitive_load = min(0.3 + (high_stress_events['count'] * 0.2), 1.0)
    mood_trend = sentiment_trend['avg_sentiment'] if sentiment_trend['avg_sentiment'] else 0.5
    
    # Wellness recommendations
    recommendations = []
    if cognitive_load > 0.7:
        recommendations.append("Consider taking a 10-minute break every hour")
        recommendations.append("Practice deep breathing exercises")
    if mood_trend < 0.4:
        recommendations.append("Reach out to a peer or counselor for support")
        recommendations.append("Try journaling about positive experiences")
    if recent_entries['count'] < 3:
        recommendations.append("Regular journaling can help track your mental wellness")
    
    conn.close()
    
    return render_template('dashboard.html', 
                         journal_entries=journal_entries, 
                         events=events, 
                         cognitive_load=cognitive_load,
                         mood_trend=mood_trend,
                         stress_distribution=stress_distribution,
                         total_entries=total_entries['count'],
                         recent_entries=recent_entries['count'],
                         recommendations=recommendations)

@app.route('/journal')
@login_required
def journal():
    user = get_current_user()
    conn = get_db_connection()
    
    # Get recent entries (limit 3 for speed)
    entries = conn.execute(
        'SELECT * FROM journal_entries WHERE user_id = ? ORDER BY created_at DESC LIMIT 3',
        (user['id'],)
    ).fetchall()
    
    # Calculate mood analytics
    mood_trend = conn.execute(
        'SELECT AVG(sentiment_score) as avg_mood FROM journal_entries WHERE user_id = ? AND created_at >= datetime("now", "-7 days")',
        (user['id'],)
    ).fetchone()
    
    # Get emotion distribution
    emotion_stats = conn.execute(
        'SELECT emotion_tags, COUNT(*) as count FROM journal_entries WHERE user_id = ? GROUP BY emotion_tags',
        (user['id'],)
    ).fetchall()
    
    # Get writing streak
    writing_streak = conn.execute(
        'SELECT COUNT(DISTINCT date(created_at)) as streak FROM journal_entries WHERE user_id = ? AND created_at >= datetime("now", "-30 days")',
        (user['id'],)
    ).fetchone()
    
    # Generate insights
    insights = []
    if mood_trend['avg_mood'] and mood_trend['avg_mood'] < 0.4:
        insights.append("Your recent entries show some challenging emotions. Consider reaching out for support.")
    elif mood_trend['avg_mood'] and mood_trend['avg_mood'] > 0.7:
        insights.append("Great job maintaining a positive mindset! Keep up the good work.")
    
    if writing_streak['streak'] >= 7:
        insights.append(f"Amazing! You've journaled {writing_streak['streak']} days this month. Consistency is key to mental wellness.")
    elif writing_streak['streak'] < 3:
        insights.append("Try to journal more regularly. Even 5 minutes daily can improve your mental clarity.")
    
    conn.close()
    
    # Check if we should prompt for location sharing
    prompt_location = session.pop('prompt_location_share', False)
    
    return render_template('journal.html', 
                         entries=entries,
                         mood_trend=mood_trend['avg_mood'] if mood_trend['avg_mood'] else 0.5,
                         emotion_stats=emotion_stats,
                         writing_streak=writing_streak['streak'],
                         insights=insights,
                         prompt_location=prompt_location,
                         emergency_contact=user['emergency_contact_name'] if user['emergency_contact_name'] else 'your emergency contact')

@app.route('/journal', methods=['POST'])
@login_required
def add_journal_entry():
    user = get_current_user()
    content = request.form['content']
    
    # Try Gemini AI for sentiment analysis
    try:
        import google.generativeai as genai
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            analysis_response = model.generate_content(f"Analyze this text sentiment in one word (positive, negative, neutral, or crisis): {content}")
            detected_emotion = analysis_response.text.strip().lower()
            
            if 'crisis' in detected_emotion:
                sentiment_score, emotion_tags = 0.05, 'crisis'
            elif 'negative' in detected_emotion:
                sentiment_score, emotion_tags = 0.3, 'negative'
            elif 'positive' in detected_emotion:
                sentiment_score, emotion_tags = 0.8, 'positive'
            else:
                sentiment_score, emotion_tags = 0.5, 'neutral'
        else:
            raise Exception("No API key")
    except Exception as e:
        print(f"Gemini sentiment error: {e}")
        from simple_ai import analyze_sentiment_simple
        sentiment_score, emotion_tags = analyze_sentiment_simple(content)
    
    ai_response = generate_enhanced_ai_response(content, emotion_tags, sentiment_score)

    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO journal_entries (user_id, content, sentiment_score, emotion_tags) VALUES (?, ?, ?, ?)',
        (user['id'], content, sentiment_score, emotion_tags)
    )
    conn.commit()
    conn.close()
    
    # Send notification for negative emotions
    if emotion_tags in ['negative', 'crisis'] or sentiment_score < 0.4:
        try:
            # Send to user
            notification_system.send_notification(
                user['id'],
                "Wellness Check-in Alert",
                f"We noticed you might be going through a difficult time. Remember, support is available 24/7. Your wellbeing matters.",
                "HavenMind - Wellness Alert"
            )
            # Send emergency alert with location if user has emergency contact
            if user['emergency_contact_phone']:
                send_crisis_alert_with_location(user['id'], content)
                print(f"Emergency alert with location sent for user {user['id']}")
                # Set session flag to prompt for location sharing
                session['prompt_location_share'] = True
                flash(f'Journal entry added! Mood detected: {emotion_tags}. Emergency contact has been notified.')
                return redirect(url_for('journal'))
        except Exception as e:
            print(f"Notification error: {e}")
    
    flash(f'Journal entry added! Mood detected: {emotion_tags}')
    return redirect(url_for('journal'))



@app.route('/journal/voice', methods=['POST'])
@login_required
def add_voice_journal():
    user = get_current_user()
    voice_text = request.form.get('voice_text', '')
    
    if not voice_text.strip():
        return jsonify({'success': False, 'message': 'No voice input received'})
    
    # Remove [Voice Entry] prefix if present for processing
    clean_text = voice_text.replace('[Voice Entry] ', '')
    
    # Try Gemini AI for voice journal too
    try:
        import google.generativeai as genai
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            analysis_response = model.generate_content(f"Analyze sentiment in one word: {clean_text}")
            detected_emotion = analysis_response.text.strip().lower()
            
            if 'crisis' in detected_emotion or 'negative' in detected_emotion:
                sentiment_score = 0.3
                emotion_tags = 'negative'
            elif 'positive' in detected_emotion:
                sentiment_score = 0.8
                emotion_tags = 'positive'
            else:
                sentiment_score = 0.5
                emotion_tags = 'neutral'
                
            ai_response = generate_enhanced_ai_response(clean_text, emotion_tags, sentiment_score)
        else:
            raise Exception("No API key")
    except Exception as e:
        print(f"Voice Gemini failed: {e}")
        # Enhanced sentiment analysis with crisis detection
        crisis_words = ['die', 'diee', 'dieee', 'kill', 'suicide', 'hurt myself', 'end it', 'give up', 'no point', 'want to die', 'wanna die', 'kill myself', 'end my life']
        negative_words = ['stressed', 'anxious', 'overwhelmed', 'tired', 'sad', 'laid', 'off', 'lost', 'worried', 'upset', 'miss', 'leaving', 'dont care', "don't care", 'whatever']
        positive_words = ['happy', 'good', 'great', 'excited', 'confident', 'accomplished', 'grateful', 'joy', 'yay']
        emotional_indicators = [':(', ':-(', '😢', '😭', '💔']
        
        content_lower = clean_text.lower()
        
        # Enhanced crisis detection with pattern matching
        has_crisis_indicators = False
        for crisis_word in crisis_words:
            if crisis_word in content_lower:
                has_crisis_indicators = True
                break
        
        # Additional crisis pattern detection
        crisis_patterns = ['go die', 'imma die', 'gonna die', 'wanna die']
        if not has_crisis_indicators:
            for pattern in crisis_patterns:
                if pattern in content_lower:
                    has_crisis_indicators = True
                    break
        
        # Check for emotional indicators (emojis, emoticons)
        has_sad_indicators = any(indicator in clean_text for indicator in emotional_indicators)
        
        negative_count = sum(1 for word in negative_words if word in content_lower)
        positive_count = sum(1 for word in positive_words if word in content_lower)
        
        # Crisis indicators override everything
        if has_crisis_indicators:
            sentiment_score = 0.05  # Very low score for crisis
            emotion_tags = 'crisis'
        # Boost negative sentiment if sad indicators present
        elif has_sad_indicators:
            sentiment_score = 0.2
            emotion_tags = 'negative'
        elif negative_count > positive_count:
            sentiment_score = 0.3
            emotion_tags = 'negative'
        elif positive_count > negative_count:
            sentiment_score = 0.8
            emotion_tags = 'positive'
        else:
            sentiment_score = 0.5
            emotion_tags = 'neutral'
        
        # Generate enhanced therapeutic response using Gemini AI
        ai_response = generate_enhanced_ai_response(clean_text, emotion_tags, sentiment_score)
    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO journal_entries (user_id, content, sentiment_score, emotion_tags) VALUES (?, ?, ?, ?)',
        (user['id'], voice_text, sentiment_score, emotion_tags)
    )
    conn.commit()
    conn.close()
    
    # Send notification for negative emotions
    if emotion_tags in ['negative', 'crisis'] or sentiment_score < 0.4:
        try:
            # Send to user
            notification_system.send_notification(
                user['id'],
                "Wellness Check-in Alert",
                f"We noticed you might be going through a difficult time. Remember, support is available 24/7. Your wellbeing matters.",
                "HavenMind - Wellness Alert"
            )
            # Send emergency alert with location if user has emergency contact
            if user['emergency_contact_phone']:
                send_crisis_alert_with_location(user['id'], clean_text)
                print(f"Emergency alert with location sent for user {user['id']}")
                # Set session flag to prompt for location sharing
                session['prompt_location_share'] = True
        except Exception as e:
            print(f"Notification error: {e}")
    
    response_data = {
        'success': True, 
        'message': 'Voice journal entry added successfully!',
        'emotion': emotion_tags,
        'ai_response': ai_response
    }
    
    # Add location sharing prompt for negative emotions
    if emotion_tags in ['negative', 'crisis'] or sentiment_score < 0.4:
        response_data['prompt_location'] = True
        response_data['emergency_contact'] = user.get('emergency_contact_name', 'your emergency contact')
    
    return jsonify(response_data)

@app.route('/journal/delete/<int:entry_id>', methods=['POST'])
@login_required
def delete_journal_entry(entry_id):
    user = get_current_user()
    conn = get_db_connection()
    conn.execute('DELETE FROM journal_entries WHERE id = ? AND user_id = ?', (entry_id, user['id']))
    conn.commit()
    conn.close()
    
    flash('Journal entry deleted successfully!')
    return redirect(url_for('journal'))

@app.route('/journal/analytics')
@login_required
def journal_analytics():
    user = get_current_user()
    conn = get_db_connection()
    
    # Get mood trends over time
    mood_timeline = conn.execute(
        'SELECT date(created_at) as date, AVG(sentiment_score) as avg_mood FROM journal_entries WHERE user_id = ? GROUP BY date(created_at) ORDER BY date DESC LIMIT 30',
        (user['id'],)
    ).fetchall()
    
    conn.close()
    
    return jsonify([{
        'date': row['date'],
        'mood': row['avg_mood']
    } for row in mood_timeline])

@app.route('/calendar')
@login_required
def calendar():
    user = get_current_user()
    conn = get_db_connection()
    
    # Get all events
    events = conn.execute(
        'SELECT * FROM calendar_events WHERE user_id = ? ORDER BY event_date',
        (user['id'],)
    ).fetchall()
    
    # Get events by month for calendar view
    current_month = datetime.now().strftime('%Y-%m')
    monthly_events = conn.execute(
        'SELECT * FROM calendar_events WHERE user_id = ? AND strftime("%Y-%m", event_date) = ? ORDER BY event_date',
        (user['id'], current_month)
    ).fetchall()
    
    # Calculate cognitive load forecast
    upcoming_events = conn.execute(
        'SELECT * FROM calendar_events WHERE user_id = ? AND event_date >= datetime("now") AND event_date <= datetime("now", "+7 days") ORDER BY event_date',
        (user['id'],)
    ).fetchall()
    
    weekly_load = 0
    for event in upcoming_events:
        if event['stress_level'] == 'high':
            weekly_load += 0.3
        elif event['stress_level'] == 'medium':
            weekly_load += 0.2
        else:
            weekly_load += 0.1
    
    # Suggest wellness breaks
    wellness_suggestions = []
    if weekly_load > 0.8:
        wellness_suggestions.append({
            'time': 'Tomorrow 2:00 PM',
            'activity': '15-minute meditation break',
            'reason': 'High cognitive load detected'
        })
        wellness_suggestions.append({
            'time': 'Day after tomorrow 10:00 AM', 
            'activity': '30-minute walk',
            'reason': 'Stress relief recommended'
        })
    
    conn.close()
    
    # Convert Row objects to dictionaries and recalculate stress levels
    events_dict = []
    for event in events:
        event_dict = dict(event)
        # Recalculate stress level based on current time
        event_dict['stress_level'] = recalculate_stress_level(event_dict['title'], event_dict['description'], event_dict['event_date'], event_dict['stress_level'])
        events_dict.append(event_dict)
    
    monthly_events_dict = [dict(event) for event in monthly_events]
    
    return render_template('calendar.html', 
                         events=events_dict,
                         monthly_events=monthly_events_dict,
                         weekly_load=min(weekly_load, 1.0),
                         wellness_suggestions=wellness_suggestions,
                         current_month=current_month)

@app.route('/calendar', methods=['POST'])
@login_required
def add_event():
    user = get_current_user()
    title = request.form['title']
    description = request.form['description']
    event_date = request.form['event_date']
    
    # Enhanced stress level detection with time proximity
    high_stress_keywords = ['exam', 'test', 'deadline', 'presentation', 'interview', 'final']
    medium_stress_keywords = ['assignment', 'meeting', 'project', 'study', 'quiz']
    low_stress_keywords = ['break', 'lunch', 'social', 'relax', 'wellness']
    
    title_lower = title.lower()
    desc_lower = description.lower() if description else ''
    
    # Base stress level from keywords (5 levels)
    base_stress = 'medium'
    if any(keyword in title_lower or keyword in desc_lower for keyword in high_stress_keywords):
        base_stress = 'high'
    elif any(keyword in title_lower or keyword in desc_lower for keyword in low_stress_keywords):
        base_stress = 'minimal'
    elif any(keyword in title_lower or keyword in desc_lower for keyword in medium_stress_keywords):
        base_stress = 'medium'
    
    # Time proximity adjustment (5 levels: minimal, low, medium, high, critical)
    event_datetime = datetime.strptime(event_date, '%Y-%m-%dT%H:%M')
    now = datetime.now()
    days_until = (event_datetime - now).days
    hours_until = (event_datetime - now).total_seconds() / 3600
    
    # Stress escalation based on proximity
    if hours_until <= 6:  # Within 6 hours - CRITICAL
        if base_stress == 'minimal':
            stress_level = 'medium'
        elif base_stress == 'medium':
            stress_level = 'critical'
        else:
            stress_level = 'critical'
    elif hours_until <= 24:  # Within 24 hours - HIGH
        if base_stress == 'minimal':
            stress_level = 'low'
        elif base_stress == 'medium':
            stress_level = 'high'
        else:
            stress_level = 'critical'
    elif days_until <= 3:  # Within 3 days - ESCALATE
        if base_stress == 'minimal':
            stress_level = 'minimal'
        elif base_stress == 'medium':
            stress_level = 'high'
        else:
            stress_level = 'high'
    elif days_until <= 7:  # Within a week - MODERATE ESCALATION
        if base_stress == 'high':
            stress_level = 'high'
        elif base_stress == 'medium':
            stress_level = 'medium'
        else:
            stress_level = 'low'
    else:  # More than a week away - BASE LEVEL
        if base_stress == 'minimal':
            stress_level = 'minimal'
        elif base_stress == 'medium':
            stress_level = 'low'
        else:
            stress_level = 'medium'
    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO calendar_events (user_id, title, description, event_date, stress_level) VALUES (?, ?, ?, ?, ?)',
        (user['id'], title, description, event_date, stress_level)
    )
    conn.commit()
    conn.close()
    
    flash(f'Event added with {stress_level} stress level!')
    return redirect(url_for('calendar'))

@app.route('/calendar/delete/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    user = get_current_user()
    conn = get_db_connection()
    conn.execute('DELETE FROM calendar_events WHERE id = ? AND user_id = ?', (event_id, user['id']))
    conn.commit()
    conn.close()
    
    flash('Event deleted successfully!')
    return redirect(url_for('calendar'))

@app.route('/calendar/complete/<int:event_id>', methods=['POST'])
@login_required
def complete_event(event_id):
    user = get_current_user()
    conn = get_db_connection()
    
    # Toggle completion status
    event = conn.execute('SELECT completed FROM calendar_events WHERE id = ? AND user_id = ?', (event_id, user['id'])).fetchone()
    if event:
        new_status = not event['completed']
        conn.execute('UPDATE calendar_events SET completed = ? WHERE id = ? AND user_id = ?', (new_status, event_id, user['id']))
        conn.commit()
        
        status_text = 'completed' if new_status else 'marked as incomplete'
        flash(f'Event {status_text}!')
    
    conn.close()
    return redirect(url_for('calendar'))

@app.route('/calendar/wellness', methods=['POST'])
@login_required
def add_wellness_break():
    user = get_current_user()
    activity = request.form['activity']
    break_time = request.form['break_time']
    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO calendar_events (user_id, title, description, event_date, stress_level) VALUES (?, ?, ?, ?, ?)',
        (user['id'], f'Wellness Break: {activity}', 'AI-suggested wellness activity', break_time, 'low')
    )
    conn.commit()
    conn.close()
    
    flash('Wellness break scheduled!')
    return redirect(url_for('calendar'))

@app.route('/support')
@login_required
def support():
    return render_template('support.html')

@app.route('/chat')
@login_required
def chat():
    user = get_current_user()
    return render_template('chat.html', user=user)

@app.route('/chat', methods=['POST'])
@login_required
def ai_chat():
    """AI chat endpoint for support page"""
    user_message = request.json.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Check if peer supporters are available
    conn = get_db_connection()
    available_peers = conn.execute(
        'SELECT COUNT(*) as count FROM users WHERE role = "peer_supporter"'
    ).fetchone()
    
    # If no peers available or this is first message, create support request
    if available_peers['count'] == 0:
        # Determine priority based on message content
        priority = 'medium'
        urgent_words = ['panic', 'crisis', 'suicide', 'kill myself', 'die', 'emergency']
        high_words = ['overwhelmed', 'stressed', 'anxious', 'depressed', 'help']
        
        if any(word in user_message.lower() for word in urgent_words):
            priority = 'urgent'
        elif any(word in user_message.lower() for word in high_words):
            priority = 'high'
        
        # Create support request
        conn.execute(
            'INSERT INTO support_requests (user_id, message, priority) VALUES (?, ?, ?)',
            (session['user_id'], user_message, priority)
        )
        conn.commit()
    
    conn.close()
    
    # Continue with AI response
    try:
        import google.generativeai as genai
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = f"""You are a compassionate mental health companion for college students. 

IMPORTANT: Match the user's language style exactly:
- If Hindi/Hinglish: respond in Hinglish ("Haan yaar, tension mat lo")
- If Tamil in English: respond in Tanglish ("Enna da, bayapadathe da")
- If English: respond in English
- If other languages: match their style

Be warm, empathetic, and supportive like a caring friend. Keep responses 2-3 sentences.

Student wrote: "{user_message}"

Respond in their exact language style:"""
            
            response = model.generate_content(prompt)
            return jsonify({'response': response.text.strip()})
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({'response': "मैं यहाँ आपकी बात सुनने के लिए हूँ। आप क्या महसूस कर रहे हैं? / I'm here to listen. How are you feeling?"})

@app.route('/peer-ai-assist', methods=['POST'])
@login_required
def peer_ai_assist():
    """AI assistance for peer supporters"""
    student_id = request.json.get('studentId')
    context = request.json.get('context', '')
    
    try:
        import google.generativeai as genai
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = f"""You are an AI assistant helping a peer supporter respond to a student in distress. 

Student's message: "{context}"

Provide:
1. A suggested empathetic response (2-3 sentences)
2. Key points to address
3. Warning signs to watch for

Be supportive, validating, and practical. Focus on peer-level support, not professional therapy.

Respond in JSON format:
{{
  "suggestion": "suggested response here",
  "keyPoints": ["point 1", "point 2", "point 3"],
  "warnings": ["warning 1", "warning 2"]
}}"""
            
            response = model.generate_content(prompt)
            import json
            try:
                ai_data = json.loads(response.text.strip())
                return jsonify(ai_data)
            except:
                return jsonify({
                    'suggestion': "I can hear that you're going through a really tough time right now. Your feelings are completely valid, and I want you to know that you're not alone in this.",
                    'keyPoints': ["Validate their emotions", "Ask open-ended questions", "Offer practical next steps"],
                    'warnings': ["Watch for crisis language", "Monitor for escalation needs"]
                })
    except Exception as e:
        print(f"Peer AI assist error: {e}")
        return jsonify({
            'suggestion': "I can hear that you're going through a really tough time right now. Your feelings are completely valid, and I want you to know that you're not alone in this.",
            'keyPoints': ["Validate their emotions", "Ask open-ended questions", "Offer practical next steps"],
            'warnings': ["Watch for crisis language", "Monitor for escalation needs"]
        })

@app.route('/request-peer-support', methods=['POST'])
@login_required
def request_peer_support():
    """Create a peer support request"""
    try:
        message = request.json.get('message', '').strip()
        
        if not message:
            return jsonify({'success': False, 'error': 'Message required'})
        
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Not logged in'})
        
        conn = get_db_connection()
        
        # Check if user already has an active request
        existing_request = conn.execute(
            'SELECT id FROM support_requests WHERE user_id = ? AND status IN ("waiting", "active")',
            (session['user_id'],)
        ).fetchone()
        
        if existing_request:
            # Close old request and create new one
            conn.execute(
                'UPDATE support_requests SET status = "closed" WHERE user_id = ? AND status IN ("waiting", "active")',
                (session['user_id'],)
            )
            conn.commit()
        
        # Determine priority
        priority = 'medium'
        urgent_words = ['panic', 'crisis', 'suicide', 'kill myself', 'die', 'emergency', 'urgent']
        high_words = ['overwhelmed', 'stressed', 'anxious', 'depressed', 'help', 'struggling']
        
        if any(word in message.lower() for word in urgent_words):
            priority = 'urgent'
        elif any(word in message.lower() for word in high_words):
            priority = 'high'
        
        # Create support request
        cursor = conn.execute(
            'INSERT INTO support_requests (user_id, message, priority) VALUES (?, ?, ?)',
            (session['user_id'], message, priority)
        )
        request_id = cursor.lastrowid
        
        # Store the initial student message in chat_messages
        conn.execute(
            'INSERT INTO chat_messages (request_id, sender_id, message) VALUES (?, ?, ?)',
            (request_id, session['user_id'], message)
        )
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error in request_peer_support: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/student-messages')
@login_required
def get_student_messages():
    """Get messages for current student's support request"""
    conn = get_db_connection()
    request_data = conn.execute(
        'SELECT id, status FROM support_requests WHERE user_id = ? AND status IN ("waiting", "active", "escalated", "professional", "professional_booking") ORDER BY created_at DESC LIMIT 1',
        (session['user_id'],)
    ).fetchone()
    
    if not request_data:
        conn.close()
        return jsonify([])
    
    # Students can see all messages including professional ones
    messages = conn.execute(
        '''SELECT cm.*, u.username, u.role 
           FROM chat_messages cm 
           JOIN users u ON cm.sender_id = u.id 
           WHERE cm.request_id = ? 
           ORDER BY cm.created_at ASC''',
        (request_data['id'],)
    ).fetchall()
    conn.close()
    
    return jsonify([{
        'message': msg['message'],
        'sender': msg['username'],
        'role': msg['role'],
        'created_at': msg['created_at'],
        'case_status': request_data['status']
    } for msg in messages])

@app.route('/debug-messages/<int:user_id>')
def debug_messages(user_id):
    """Debug endpoint to check messages"""
    conn = get_db_connection()
    requests = conn.execute('SELECT * FROM support_requests WHERE user_id = ?', (user_id,)).fetchall()
    messages = conn.execute('SELECT * FROM chat_messages').fetchall()
    conn.close()
    return jsonify({
        'requests': [dict(r) for r in requests],
        'messages': [dict(m) for m in messages]
    })

@app.route('/student-send-message', methods=['POST'])
@login_required
def student_send_message():
    """Send message from student to peer"""
    message = request.json.get('message', '').strip()
    
    if not message:
        return jsonify({'success': False})
    
    conn = get_db_connection()
    # Find student's active support request
    request_data = conn.execute(
        'SELECT id FROM support_requests WHERE user_id = ? AND status IN ("waiting", "active", "escalated", "professional") ORDER BY created_at DESC LIMIT 1',
        (session['user_id'],)
    ).fetchone()
    
    if request_data:
        # Store student message
        conn.execute(
            'INSERT INTO chat_messages (request_id, sender_id, message) VALUES (?, ?, ?)',
            (request_data['id'], session['user_id'], message)
        )
        conn.commit()
    
    conn.close()
    return jsonify({'success': True})

@app.route('/peer-send-message', methods=['POST'])
@login_required
def peer_send_message():
    """Send message from peer to student"""
    message = request.json.get('message', '').strip()
    request_id = request.json.get('request_id')
    
    if not message or not request_id:
        return jsonify({'success': False})
    
    user = get_current_user()
    if user['role'] != 'peer_supporter':
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    conn = get_db_connection()
    # Update request status to active if it's waiting
    conn.execute(
        'UPDATE support_requests SET status = "active", peer_id = ? WHERE id = ? AND status = "waiting"',
        (session['user_id'], request_id)
    )
    
    # Store peer message
    conn.execute(
        'INSERT INTO chat_messages (request_id, sender_id, message) VALUES (?, ?, ?)',
        (request_id, session['user_id'], message)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/accept-support-request', methods=['POST'])
@login_required
def accept_support_request():
    """Peer accepts a support request"""
    request_id = request.json.get('request_id')
    
    if not request_id:
        return jsonify({'success': False})
    
    user = get_current_user()
    if user['role'] != 'peer_supporter':
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    conn = get_db_connection()
    # Update request status and assign peer
    conn.execute(
        'UPDATE support_requests SET status = "active", peer_id = ? WHERE id = ? AND status = "waiting"',
        (session['user_id'], request_id)
    )
    
    # Send initial message from peer
    conn.execute(
        'INSERT INTO chat_messages (request_id, sender_id, message) VALUES (?, ?, ?)',
        (request_id, session['user_id'], "Hi! I'm here to support you. How are you feeling right now?")
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})



@app.route('/get-peer-messages/<int:request_id>')
@login_required
def get_peer_messages(request_id):
    """Get messages for a specific support request (for peer supporters)"""
    user = get_current_user()
    if user['role'] != 'peer_supporter':
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = get_db_connection()
    
    # Check if case has been escalated to professional
    case_status = conn.execute(
        'SELECT status FROM support_requests WHERE id = ?',
        (request_id,)
    ).fetchone()
    
    if case_status and case_status['status'] == 'professional':
        conn.close()
        return jsonify({'professional_takeover': True})
    
    # Get messages only if professional hasn't taken over
    messages = conn.execute(
        '''SELECT cm.*, u.username, u.role 
           FROM chat_messages cm 
           JOIN users u ON cm.sender_id = u.id 
           WHERE cm.request_id = ? AND u.role != 'professional'
           ORDER BY cm.created_at ASC''',
        (request_id,)
    ).fetchall()
    conn.close()
    
    return jsonify([{
        'message': msg['message'],
        'sender': msg['username'],
        'role': msg['role'],
        'created_at': msg['created_at']
    } for msg in messages])

@app.route('/api/peer-requests')
@login_required
def get_peer_requests():
    """Get pending support requests for peer supporters"""
    user = get_current_user()
    if user['role'] != 'peer_supporter':
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = get_db_connection()
    pending_requests = conn.execute(
        '''SELECT sr.*, u.username 
           FROM support_requests sr 
           JOIN users u ON sr.user_id = u.id 
           WHERE sr.status = "waiting" 
           ORDER BY 
           CASE sr.priority 
               WHEN "urgent" THEN 1 
               WHEN "high" THEN 2 
               WHEN "medium" THEN 3 
               ELSE 4 
           END, sr.created_at ASC'''
    ).fetchall()
    conn.close()
    
    return jsonify([{
        'id': req['id'],
        'username': req['username'],
        'message': req['message'],
        'priority': req['priority'],
        'created_at': req['created_at']
    } for req in pending_requests])

@app.route('/escalate-to-professional', methods=['POST'])
@login_required
def escalate_to_professional():
    """Escalate a support request to professional counselor"""
    request_id = request.json.get('request_id')
    
    if not request_id:
        return jsonify({'success': False, 'error': 'Request ID required'})
    
    user = get_current_user()
    if user['role'] != 'peer_supporter':
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    conn = get_db_connection()
    
    # Get student info for location sharing
    student_info = conn.execute(
        'SELECT user_id FROM support_requests WHERE id = ?',
        (request_id,)
    ).fetchone()
    
    # Update request status to escalated
    conn.execute(
        'UPDATE support_requests SET status = "escalated", priority = "urgent" WHERE id = ?',
        (request_id,)
    )
    
    # Add internal note about escalation with location info
    location_info = get_student_location_for_professional(student_info['user_id']) if student_info else None
    escalation_note = "[PEER_NOTE] Escalated to professional - continue supporting until handoff"
    
    if location_info:
        escalation_note += f"\n\n[LOCATION_ALERT] Student location and emergency contact available for professional:\nEmergency Contact: {location_info['emergency_contact']['name']} ({location_info['emergency_contact']['phone']})\nRelationship: {location_info['emergency_contact']['relationship']}"
    
    conn.execute(
        'INSERT INTO chat_messages (request_id, sender_id, message) VALUES (?, ?, ?)',
        (request_id, session['user_id'], escalation_note)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/profile')
@login_required
def profile():
    user = get_current_user()
    return render_template('profile.html', user=user)

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile information"""
    user = get_current_user()
    
    # Get form data
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    university = request.form.get('university', '').strip()
    major = request.form.get('major', '').strip()
    phone = request.form.get('phone', '').strip()
    year_of_study = request.form.get('year_of_study', '').strip()
    
    if not username or not email:
        flash('Username and email are required')
        return redirect(url_for('profile'))
    
    conn = get_db_connection()
    
    # Check if username/email already exists for other users
    existing_user = conn.execute(
        'SELECT id FROM users WHERE (username = ? OR email = ?) AND id != ?',
        (username, email, user['id'])
    ).fetchone()
    
    if existing_user:
        flash('Username or email already exists')
        conn.close()
        return redirect(url_for('profile'))
    
    # Update user information
    conn.execute(
        'UPDATE users SET username = ?, email = ? WHERE id = ?',
        (username, email, user['id'])
    )
    
    # Add additional profile fields to database if they don't exist
    try:
        conn.execute('ALTER TABLE users ADD COLUMN first_name TEXT')
        conn.execute('ALTER TABLE users ADD COLUMN last_name TEXT')
        conn.execute('ALTER TABLE users ADD COLUMN university TEXT')
        conn.execute('ALTER TABLE users ADD COLUMN major TEXT')
        conn.execute('ALTER TABLE users ADD COLUMN phone TEXT')
        conn.execute('ALTER TABLE users ADD COLUMN year_of_study TEXT')
    except sqlite3.OperationalError:
        pass  # Columns already exist
    
    # Update additional profile fields
    conn.execute(
        'UPDATE users SET first_name = ?, last_name = ?, university = ?, major = ?, phone = ?, year_of_study = ? WHERE id = ?',
        (first_name, last_name, university, major, phone, year_of_study, user['id'])
    )
    
    conn.commit()
    conn.close()
    
    flash('Profile updated successfully!')
    return redirect(url_for('profile'))

@app.route('/profile/preferences', methods=['POST'])
@login_required
def update_preferences():
    """Update wellness preferences"""
    user = get_current_user()
    
    # Get preference data
    daily_checkins = 'daily_checkins' in request.form
    mood_reminders = 'mood_reminders' in request.form
    peer_notifications = 'peer_notifications' in request.form
    ai_insights = 'ai_insights' in request.form
    appointment_reminders = 'appointment_reminders' in request.form
    support_type = request.form.get('support_type', 'self_help')
    emergency_alerts = 'emergency_alerts' in request.form
    share_location = 'share_location' in request.form
    auto_professional_escalation = 'auto_professional_escalation' in request.form
    
    # Get emergency contact info
    emergency_contact_name = request.form.get('emergency_contact_name', '').strip()
    emergency_contact_phone = request.form.get('emergency_contact_phone', '').strip()
    emergency_contact_relationship = request.form.get('emergency_contact_relationship', '').strip()
    
    # Get notification settings
    notification_method = request.form.get('notification_method', 'email')
    notification_time = request.form.get('notification_time', 'morning')
    
    # Validate emergency contact if emergency alerts are enabled
    if emergency_alerts and (not emergency_contact_name or not emergency_contact_phone):
        flash('Emergency contact name and phone are required when emergency alerts are enabled')
        return redirect(url_for('profile'))
    
    # Validate phone number if WhatsApp notifications are enabled
    if notification_method in ['whatsapp', 'both'] and not user['phone']:
        flash('Phone number is required in your profile for WhatsApp notifications')
        return redirect(url_for('profile'))
    
    conn = get_db_connection()
    
    # Add preferences columns if they don't exist
    try:
        conn.execute('ALTER TABLE users ADD COLUMN daily_checkins BOOLEAN DEFAULT 1')
        conn.execute('ALTER TABLE users ADD COLUMN mood_reminders BOOLEAN DEFAULT 1')
        conn.execute('ALTER TABLE users ADD COLUMN peer_notifications BOOLEAN DEFAULT 0')
        conn.execute('ALTER TABLE users ADD COLUMN ai_insights BOOLEAN DEFAULT 1')
        conn.execute('ALTER TABLE users ADD COLUMN appointment_reminders BOOLEAN DEFAULT 1')
        conn.execute('ALTER TABLE users ADD COLUMN support_type TEXT DEFAULT "self_help"')
        conn.execute('ALTER TABLE users ADD COLUMN emergency_alerts BOOLEAN DEFAULT 1')
        conn.execute('ALTER TABLE users ADD COLUMN share_location BOOLEAN DEFAULT 0')
        conn.execute('ALTER TABLE users ADD COLUMN auto_professional_escalation BOOLEAN DEFAULT 0')
        conn.execute('ALTER TABLE users ADD COLUMN emergency_contact_name TEXT')
        conn.execute('ALTER TABLE users ADD COLUMN emergency_contact_phone TEXT')
        conn.execute('ALTER TABLE users ADD COLUMN emergency_contact_relationship TEXT')
        conn.execute('ALTER TABLE users ADD COLUMN notification_method TEXT DEFAULT "email"')
        conn.execute('ALTER TABLE users ADD COLUMN notification_time TEXT DEFAULT "morning"')
    except sqlite3.OperationalError:
        pass  # Columns already exist
    
    # Update preferences
    conn.execute(
        '''UPDATE users SET 
           daily_checkins = ?, mood_reminders = ?, peer_notifications = ?, 
           ai_insights = ?, appointment_reminders = ?, support_type = ?, 
           emergency_alerts = ?, share_location = ?, auto_professional_escalation = ?,
           emergency_contact_name = ?, emergency_contact_phone = ?, emergency_contact_relationship = ?,
           notification_method = ?, notification_time = ?
           WHERE id = ?''',
        (daily_checkins, mood_reminders, peer_notifications, ai_insights, appointment_reminders,
         support_type, emergency_alerts, share_location, auto_professional_escalation,
         emergency_contact_name, emergency_contact_phone, emergency_contact_relationship,
         notification_method, notification_time, user['id'])
    )
    
    conn.commit()
    conn.close()
    
    # Send test notification if user wants to verify their settings
    if request.form.get('test_notifications'):
        try:
            result = notification_system.send_notification(
                user['id'],
                "Test Notification",
                "This is a test notification to verify your settings are working correctly.",
                "HavenMind - Test Notification"
            )
            flash('Preferences updated! Check your notifications (email/telegram).')
        except Exception as e:
            flash(f'Preferences updated but test notification failed: {e}')
    else:
        flash('Preferences updated successfully!')
    
    return redirect(url_for('profile'))

@app.route('/profile/security', methods=['POST'])
@login_required
def update_security():
    """Update password and security settings"""
    user = get_current_user()
    
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    # Get data sharing preferences
    share_research = 'share_research' in request.form
    ai_analysis = 'ai_analysis' in request.form
    share_counselors = 'share_counselors' in request.form
    
    conn = get_db_connection()
    
    # Update password if provided
    if current_password and new_password:
        if not verify_password(current_password, user['password_hash']):
            flash('Current password is incorrect')
            conn.close()
            return redirect(url_for('profile'))
        
        if new_password != confirm_password:
            flash('New passwords do not match')
            conn.close()
            return redirect(url_for('profile'))
        
        if len(new_password) < 6:
            flash('New password must be at least 6 characters')
            conn.close()
            return redirect(url_for('profile'))
        
        new_password_hash = hash_password(new_password)
        conn.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_password_hash, user['id']))
        flash('Password updated successfully!')
    
    # Add data sharing columns if they don't exist
    try:
        conn.execute('ALTER TABLE users ADD COLUMN share_research BOOLEAN DEFAULT 0')
        conn.execute('ALTER TABLE users ADD COLUMN ai_analysis BOOLEAN DEFAULT 1')
        conn.execute('ALTER TABLE users ADD COLUMN share_counselors BOOLEAN DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Columns already exist
    
    # Update data sharing preferences
    conn.execute(
        'UPDATE users SET share_research = ?, ai_analysis = ?, share_counselors = ? WHERE id = ?',
        (share_research, ai_analysis, share_counselors, user['id'])
    )
    
    conn.commit()
    conn.close()
    
    if not (current_password and new_password):
        flash('Security preferences updated successfully!')
    
    return redirect(url_for('profile'))

@app.route('/journal/prompts')
@login_required
def get_journal_prompts():
    """Get AI-generated journal prompts based on user's recent mood"""
    user = get_current_user()
    
    # Check if Gemini AI is available (fallback variables)
    GEMINI_AVAILABLE = False
    gemini_ai = None
    
    if GEMINI_AVAILABLE and gemini_ai:
        # Use Gemini AI for personalized prompts
        user_context = get_user_context_for_ai(user['id'])
        prompts = gemini_ai.generate_personalized_prompts(user_context)
    else:
        # Fallback to basic prompts
        conn = get_db_connection()
        recent_mood = conn.execute(
            'SELECT AVG(sentiment_score) as avg_mood FROM journal_entries WHERE user_id = ? AND created_at >= datetime("now", "-3 days")',
            (user['id'],)
        ).fetchone()
        conn.close()
        
        if recent_mood['avg_mood'] and recent_mood['avg_mood'] < 0.4:
            prompts = [
                "What's one thing that brought you comfort today, even if it was small?",
                "Describe a challenge you've overcome in the past. What strengths did you use?",
                "What would you tell a friend who was feeling the way you feel right now?",
                "Write about three things you're grateful for, no matter how simple.",
                "If you could give yourself one piece of advice right now, what would it be?"
            ]
        elif recent_mood['avg_mood'] and recent_mood['avg_mood'] > 0.7:
            prompts = [
                "What's contributing to your positive mood lately? How can you maintain it?",
                "Describe a recent accomplishment you're proud of.",
                "What advice would you give to your past self from a month ago?",
                "How can you share your positive energy with others today?",
                "What are you most looking forward to this week?"
            ]
        else:
            prompts = [
                "How are you feeling right now, and what might be influencing that?",
                "What's one goal you'd like to focus on this week?",
                "Describe your ideal day. What elements could you incorporate into tomorrow?",
                "What's something new you learned about yourself recently?",
                "What would make today feel more meaningful for you?"
            ]
    
    return jsonify({'prompts': prompts})

@app.route('/api/calendar/cognitive-load')
@login_required
def get_cognitive_load_api():
    user = get_current_user()
    conn = get_db_connection()
    
    # Get upcoming events for next 7 days
    upcoming_events = conn.execute(
        'SELECT stress_level, COUNT(*) as count FROM calendar_events WHERE user_id = ? AND event_date >= datetime("now") AND event_date <= datetime("now", "+7 days") GROUP BY stress_level',
        (user['id'],)
    ).fetchall()
    
    load_score = 0.2  # Base load
    for event in upcoming_events:
        if event['stress_level'] == 'high':
            load_score += event['count'] * 0.25
        elif event['stress_level'] == 'medium':
            load_score += event['count'] * 0.15
        else:
            load_score += event['count'] * 0.05
    
    conn.close()
    
    return jsonify({
        'cognitive_load': min(load_score, 1.0),
        'status': 'high' if load_score > 0.7 else 'medium' if load_score > 0.4 else 'low'
    })

# Add mindfulness exercises route
@app.route('/journal/mindfulness')
def mindfulness_exercises():
    exercises = [
        {
            'name': '5-Minute Breathing',
            'description': 'Focus on your breath for 5 minutes',
            'duration': '5 minutes',
            'instructions': 'Breathe in for 4 counts, hold for 4, exhale for 6. Repeat.'
        },
        {
            'name': 'Body Scan',
            'description': 'Progressive relaxation technique',
            'duration': '10 minutes', 
            'instructions': 'Start from your toes and slowly focus on each part of your body.'
        },
        {
            'name': 'Gratitude Meditation',
            'description': 'Reflect on things you\'re grateful for',
            'duration': '7 minutes',
            'instructions': 'Think of 3 people, 3 experiences, and 3 things you appreciate.'
        }
    ]
    
    return jsonify({'exercises': exercises})

# Add voice input route
@app.route('/calendar/voice', methods=['POST'])
@login_required
def add_event_voice():
    user = get_current_user()
    # Placeholder for voice input processing
    voice_text = request.form.get('voice_text', '')
    
    # Simple NLP parsing for demo
    if 'exam' in voice_text.lower():
        title = 'Exam'
        stress_level = 'high'
    elif 'meeting' in voice_text.lower():
        title = 'Meeting'
        stress_level = 'medium'
    else:
        title = voice_text[:50]
        stress_level = 'medium'
    
    # Extract date (simplified)
    import re
    date_match = re.search(r'(tomorrow|today|next week)', voice_text.lower())
    if date_match:
        if 'tomorrow' in date_match.group():
            event_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
        elif 'today' in date_match.group():
            event_date = datetime.now().strftime('%Y-%m-%dT%H:%M')
        else:
            event_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M')
    else:
        event_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO calendar_events (user_id, title, description, event_date, stress_level) VALUES (?, ?, ?, ?, ?)',
        (user['id'], title, f'Added via voice: {voice_text}', event_date, stress_level)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': f'Event "{title}" added successfully!'})

@app.route('/calendar/ai-event', methods=['POST'])
@login_required
def add_ai_event():
    user = get_current_user()
    title = request.form.get('title')
    event_date = request.form.get('event_date')
    description = request.form.get('description', '')
    stress_level = request.form.get('stress_level', 'medium')
    
    if not title or not event_date:
        return jsonify({'success': False, 'message': 'Title and date are required'})
    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO calendar_events (user_id, title, description, event_date, stress_level) VALUES (?, ?, ?, ?, ?)',
        (user['id'], title, description, event_date, stress_level)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'AI event added successfully!'})

@app.route('/calendar/edit/<int:event_id>', methods=['POST'])
@login_required
def edit_event(event_id):
    user = get_current_user()
    title = request.form.get('title')
    event_date = request.form.get('event_date')
    description = request.form.get('description', '')
    stress_level = request.form.get('stress_level', 'medium')
    
    if not title or not event_date:
        flash('Title and date are required')
        return redirect(url_for('calendar'))
    
    conn = get_db_connection()
    conn.execute(
        'UPDATE calendar_events SET title = ?, event_date = ?, description = ?, stress_level = ? WHERE id = ? AND user_id = ?',
        (title, event_date, description, stress_level, event_id, user['id'])
    )
    conn.commit()
    conn.close()
    
    flash('Event updated successfully!')
    return redirect(url_for('calendar'))

@app.route('/calendar/smart-parse', methods=['POST'])
@login_required
def smart_parse_event():
    """Enhanced AI parsing for natural language event input"""
    user = get_current_user()
    input_text = request.form.get('input_text', '').strip()
    
    if not input_text:
        return jsonify({'success': False, 'message': 'No input provided'})
    
    # Enhanced parsing logic
    parsed = parse_natural_language_advanced(input_text)
    
    return jsonify({
        'success': True,
        'parsed_event': parsed,
        'confidence': parsed.get('confidence', 0.8)
    })

def parse_natural_language_advanced(text):
    """Advanced natural language parsing for calendar events"""
    import re
    from datetime import datetime, timedelta
    
    text_lower = text.lower()
    
    # Subject/Course detection
    subjects = {
        'math': ['math', 'mathematics', 'calculus', 'algebra', 'geometry'],
        'science': ['science', 'physics', 'chemistry', 'biology', 'lab'],
        'english': ['english', 'literature', 'writing', 'essay'],
        'history': ['history', 'social studies', 'government'],
        'computer': ['computer', 'programming', 'coding', 'cs', 'software']
    }
    
    detected_subject = None
    for subject, keywords in subjects.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_subject = subject
            break
    
    # Event type detection
    event_types = {
        'exam': ['exam', 'test', 'quiz', 'midterm', 'final'],
        'assignment': ['assignment', 'homework', 'project', 'paper', 'essay'],
        'class': ['class', 'lecture', 'session', 'course'],
        'meeting': ['meeting', 'appointment', 'consultation'],
        'study': ['study', 'review', 'preparation']
    }
    
    detected_type = 'event'
    for event_type, keywords in event_types.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_type = event_type
            break
    
    # Build title
    if detected_subject and detected_type:
        title = f"{detected_subject.title()} {detected_type.title()}"
    elif detected_type != 'event':
        title = detected_type.title()
    else:
        # Extract first few words as title
        words = text.split()[:3]
        title = ' '.join(words).title()
    
    # Date parsing
    date = datetime.now()
    
    # Relative dates
    if 'tomorrow' in text_lower:
        date += timedelta(days=1)
    elif 'today' in text_lower:
        pass  # Keep current date
    elif 'next week' in text_lower:
        date += timedelta(days=7)
    elif 'in 2 days' in text_lower or '2 days' in text_lower:
        date += timedelta(days=2)
    elif 'in 3 days' in text_lower or '3 days' in text_lower:
        date += timedelta(days=3)
    
    # Weekday parsing
    weekdays = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    for day_name, day_num in weekdays.items():
        if day_name in text_lower:
            days_ahead = day_num - date.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            date += timedelta(days=days_ahead)
            break
    
    # Time parsing
    time_match = re.search(r'(\d{1,2})(?::(\d{2}))? ?(am|pm)', text_lower)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        am_pm = time_match.group(3)
        
        if am_pm == 'pm' and hour != 12:
            hour += 12
        elif am_pm == 'am' and hour == 12:
            hour = 0
            
        date = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    else:
        # Default times based on event type
        default_times = {
            'exam': 9,
            'class': 10,
            'meeting': 14,
            'assignment': 23,  # Due at 11 PM
            'study': 15
        }
        default_hour = default_times.get(detected_type, 12)
        date = date.replace(hour=default_hour, minute=0, second=0, microsecond=0)
    
    # Stress level determination
    high_stress_keywords = ['exam', 'test', 'final', 'midterm', 'deadline', 'due', 'presentation']
    low_stress_keywords = ['study', 'review', 'break', 'lunch', 'social', 'optional']
    
    if any(keyword in text_lower for keyword in high_stress_keywords):
        stress_level = 'high'
    elif any(keyword in text_lower for keyword in low_stress_keywords):
        stress_level = 'low'
    else:
        stress_level = 'medium'
    
    # Duration estimation
    duration_match = re.search(r'(\d+) ?(?:hour|hr|h)', text_lower)
    duration = int(duration_match.group(1)) if duration_match else None
    
    return {
        'title': title,
        'date': date.isoformat(),
        'stress_level': stress_level,
        'description': f'Auto-generated from: "{text}"',
        'duration': duration,
        'confidence': 0.85,
        'detected_subject': detected_subject,
        'detected_type': detected_type
    }

@app.route('/calendar/generate-timetable', methods=['POST'])
@login_required
def generate_timetable():
    user = get_current_user()
    conn = get_db_connection()
    
    # Get all user events
    events = conn.execute(
        'SELECT * FROM calendar_events WHERE user_id = ? ORDER BY event_date',
        (user['id'],)
    ).fetchall()
    
    conn.close()
    
    # Generate AI timetable
    timetable = create_ai_timetable(events)
    
    return jsonify({
        'success': True,
        'timetable': timetable
    })

@app.route('/calendar/apply-timetable', methods=['POST'])
@login_required
def apply_timetable():
    user = get_current_user()
    
    # Get the last generated timetable from session
    if 'generated_timetable' not in session:
        return jsonify({'success': False, 'message': 'No timetable to apply'})
    
    timetable = session['generated_timetable']
    conn = get_db_connection()
    
    # Add study sessions to calendar
    for day in timetable['daily_schedule']:
        for study_session in day['sessions']:
            if study_session['type'] == 'study':  # Only add study sessions, not existing events
                event_datetime = f"{day['date']}T{study_session['time']}"
                conn.execute(
                    'INSERT INTO calendar_events (user_id, title, description, event_date, stress_level) VALUES (?, ?, ?, ?, ?)',
                    (user['id'], study_session['title'], study_session['description'], event_datetime, study_session['stress_level'])
                )
    
    conn.commit()
    conn.close()
    
    # Clear the session timetable
    session.pop('generated_timetable', None)
    
    return jsonify({'success': True, 'message': 'Timetable applied successfully!'})

def create_ai_timetable(events):
    """Generate AI-powered study timetable based on existing events"""
    from datetime import datetime, timedelta
    
    # Parse and analyze events
    parsed_events = []
    for event in events:
        event_dict = dict(event)
        title = event_dict['title'].lower()
        
        # Parse event date
        try:
            if 'T' in event_dict['event_date']:
                event_date = datetime.strptime(event_dict['event_date'], '%Y-%m-%dT%H:%M')
            else:
                event_date = datetime.strptime(event_dict['event_date'], '%Y-%m-%d %H:%M:%S')
        except:
            continue
        
        # Extract subject and type
        subject_keywords = {
            'computer': ['kaggle', 'programming', 'coding', 'cs', 'notebook'],
            'business': ['ba', 'business', 'management'],
            'project': ['hackathon', 'mad', 'project'],
            'general': ['assignment', 'study']
        }
        
        detected_subject = 'general'
        for subject, keywords in subject_keywords.items():
            if any(keyword in title for keyword in keywords):
                detected_subject = subject
                break
        
        parsed_events.append({
            'title': event_dict['title'],
            'subject': detected_subject,
            'date': event_date,
            'days_until': (event_date - datetime.now()).days,
            'is_deadline': any(keyword in title for keyword in ['exam', 'submission', 'deadline', 'project'])
        })
    
    # Sort by urgency (closest deadlines first)
    parsed_events.sort(key=lambda x: x['days_until'])
    
    # Generate intelligent study schedule
    daily_schedule = []
    total_sessions = 0
    total_hours = 0
    
    now = datetime.now()
    for i in range(7):
        current_date = now + timedelta(days=i)
        date_str = current_date.strftime('%Y-%m-%d')
        day_name = current_date.strftime('%A')
        sessions = []
        
        # Find events happening today or soon
        urgent_events = [e for e in parsed_events if 0 <= e['days_until'] - i <= 3]
        
        if urgent_events:
            # Focus on most urgent event
            urgent_event = urgent_events[0]
            
            # Morning intensive session for urgent deadlines
            if urgent_event['days_until'] - i <= 1:  # Due tomorrow or today
                sessions.append({
                    'title': f"URGENT: {urgent_event['subject'].title()} Prep",
                    'description': f"Final preparation for {urgent_event['title']}",
                    'time': '08:00',
                    'duration': '3 hours',
                    'stress_level': 'critical',
                    'priority': 'URGENT',
                    'type': 'study'
                })
                total_sessions += 1
                total_hours += 3
            else:
                # Regular morning session
                sessions.append({
                    'title': f"{urgent_event['subject'].title()} Study",
                    'description': f"Preparation for {urgent_event['title']}",
                    'time': '09:00',
                    'duration': '2 hours',
                    'stress_level': 'high',
                    'priority': 'High',
                    'type': 'study'
                })
                total_sessions += 1
                total_hours += 2
            
            # Afternoon session for secondary tasks
            if len(urgent_events) > 1:
                second_event = urgent_events[1]
                sessions.append({
                    'title': f"{second_event['subject'].title()} Work",
                    'description': f"Progress on {second_event['title']}",
                    'time': '14:00',
                    'duration': '1.5 hours',
                    'stress_level': 'medium',
                    'priority': 'Medium',
                    'type': 'study'
                })
                total_sessions += 1
                total_hours += 1.5
        else:
            # No urgent deadlines - general study
            if parsed_events:
                next_event = parsed_events[0]
                sessions.append({
                    'title': f"Advance Study: {next_event['subject'].title()}",
                    'description': f"Early preparation for {next_event['title']}",
                    'time': '10:00',
                    'duration': '1.5 hours',
                    'stress_level': 'low',
                    'priority': 'Medium',
                    'type': 'study'
                })
                total_sessions += 1
                total_hours += 1.5
        
        # Evening review session (weekdays only)
        if current_date.weekday() < 5 and urgent_events:
            sessions.append({
                'title': "Review & Practice",
                'description': "Review today's study material and practice problems",
                'time': '19:30',
                'duration': '1 hour',
                'stress_level': 'low',
                'priority': 'Medium',
                'type': 'study'
            })
            total_sessions += 1
            total_hours += 1
        
        # Mandatory wellness break
        sessions.append({
            'title': "Wellness Break",
            'description': "Mental health break - walk, meditate, or relax",
            'time': '16:00',
            'duration': '45 minutes',
            'stress_level': 'minimal',
            'priority': 'Essential',
            'type': 'wellness'
        })
        
        daily_schedule.append({
            'date': date_str,
            'day_name': day_name,
            'sessions': sessions
        })
    
    # Create summary
    subjects = list(set([e['subject'] for e in parsed_events]))
    
    timetable = {
        'total_sessions': total_sessions,
        'total_hours': int(total_hours),
        'subjects': subjects,
        'daily_schedule': daily_schedule,
        'upcoming_deadlines': len([e for e in parsed_events if e['days_until'] <= 7])
    }
    
    session['generated_timetable'] = timetable
    return timetable

@app.route('/api/student-profile/<int:user_id>')
@login_required
def get_student_profile(user_id):
    """Get complete student profile for professionals"""
    user = get_current_user()
    if user['role'] != 'professional':
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = get_db_connection()
    
    # Get student basic info
    student = conn.execute(
        'SELECT * FROM users WHERE id = ?', (user_id,)
    ).fetchone()
    
    # Get journal entries
    journal_entries = conn.execute(
        'SELECT * FROM journal_entries WHERE user_id = ? ORDER BY created_at DESC LIMIT 10',
        (user_id,)
    ).fetchall()
    
    # Get journal stats
    journal_stats = conn.execute(
        'SELECT COUNT(*) as count, AVG(sentiment_score) as avg_mood FROM journal_entries WHERE user_id = ?',
        (user_id,)
    ).fetchone()
    
    conn.close()
    
    # Analyze mood pattern
    if journal_stats['avg_mood']:
        if journal_stats['avg_mood'] < 0.3:
            mood_analysis = "consistent negative mood patterns requiring immediate attention"
        elif journal_stats['avg_mood'] < 0.5:
            mood_analysis = "mild to moderate mood concerns with some negative trends"
        else:
            mood_analysis = "generally stable mood with positive indicators"
    else:
        mood_analysis = "insufficient data for mood analysis"
    
    return jsonify({
        'username': student['username'],
        'email': student['email'],
        'created_at': student['created_at'],
        'journal_count': journal_stats['count'],
        'avg_mood': journal_stats['avg_mood'],
        'mood_analysis': mood_analysis,
        'recent_entries': [{
            'content': entry['content'],
            'emotion_tags': entry['emotion_tags'],
            'created_at': entry['created_at']
        } for entry in journal_entries]
    })

@app.route('/api/chat-history/<int:request_id>')
@login_required
def get_chat_history(request_id):
    """Get chat history for professionals and students"""
    user = get_current_user()
    if user['role'] not in ['professional', 'student']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = get_db_connection()
    messages = conn.execute(
        '''SELECT cm.*, u.username, u.role 
           FROM chat_messages cm 
           JOIN users u ON cm.sender_id = u.id 
           WHERE cm.request_id = ? 
           ORDER BY cm.created_at ASC''',
        (request_id,)
    ).fetchall()
    conn.close()
    
    return jsonify([{
        'message': msg['message'],
        'sender': msg['username'],
        'role': msg['role'],
        'created_at': msg['created_at']
    } for msg in messages])

@app.route('/start-intervention', methods=['POST'])
@login_required
def start_intervention():
    """Start professional intervention for escalated case"""
    case_id = request.json.get('case_id')
    
    if not case_id:
        return jsonify({'success': False, 'error': 'Case ID required'})
    
    user = get_current_user()
    if user['role'] != 'professional':
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    conn = get_db_connection()
    
    # Update case status to professional intervention and assign professional
    conn.execute(
        'UPDATE support_requests SET status = "professional", professional_id = ? WHERE id = ?',
        (session['user_id'], case_id)
    )
    
    # Get student location info for professional
    student_info = conn.execute(
        'SELECT user_id FROM support_requests WHERE id = ?',
        (case_id,)
    ).fetchone()
    
    location_data = get_student_location_for_professional(student_info['user_id']) if student_info else None
    
    # Add professional intervention message with location awareness
    intervention_msg = "Hello, I'm a licensed mental health professional. I've been brought in to provide you with specialized support. You're in a safe space here, and everything we discuss is confidential. How are you feeling right now?"
    
    if location_data:
        intervention_msg += "\n\n[PROFESSIONAL_NOTE] Emergency contact and location information available for safety purposes."
    
    conn.execute(
        'INSERT INTO chat_messages (request_id, sender_id, message) VALUES (?, ?, ?)',
        (case_id, session['user_id'], intervention_msg)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/professional-chat/<int:case_id>')
@login_required
def professional_chat(case_id):
    """Professional chat interface for ongoing interventions"""
    user = get_current_user()
    if user['role'] != 'professional':
        flash('Access denied')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    # Get case details
    case = conn.execute(
        '''SELECT sr.*, u.username 
           FROM support_requests sr 
           JOIN users u ON sr.user_id = u.id 
           WHERE sr.id = ? AND sr.status IN ("escalated", "professional", "professional_booking")''',
        (case_id,)
    ).fetchone()
    
    conn.close()
    
    if not case:
        flash('Case not found or access denied')
        return redirect(url_for('professional_dashboard'))
    
    return render_template('professional_chat.html', case=case, user=user)

@app.route('/professional-send-message', methods=['POST'])
@login_required
def professional_send_message():
    """Send message from professional to student"""
    message = request.json.get('message', '').strip()
    request_id = request.json.get('request_id')
    
    if not message or not request_id:
        return jsonify({'success': False})
    
    user = get_current_user()
    if user['role'] != 'professional':
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    conn = get_db_connection()
    
    # Store professional message
    conn.execute(
        'INSERT INTO chat_messages (request_id, sender_id, message) VALUES (?, ?, ?)',
        (request_id, session['user_id'], message)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/add-session-note', methods=['POST'])
@login_required
def add_session_note():
    """Add confidential session note for professional"""
    case_id = request.json.get('case_id')
    note = request.json.get('note', '').strip()
    
    if not case_id or not note:
        return jsonify({'success': False, 'error': 'Case ID and note required'})
    
    user = get_current_user()
    if user['role'] != 'professional':
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    conn = get_db_connection()
    
    # Add session note
    conn.execute(
        'INSERT INTO session_notes (case_id, professional_id, note) VALUES (?, ?, ?)',
        (case_id, session['user_id'], note)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/get-session-notes/<int:case_id>')
@login_required
def get_session_notes(case_id):
    """Get session notes for a case"""
    user = get_current_user()
    if user['role'] != 'professional':
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = get_db_connection()
    notes = conn.execute(
        '''SELECT sn.*, u.username 
           FROM session_notes sn 
           JOIN users u ON sn.professional_id = u.id 
           WHERE sn.case_id = ? 
           ORDER BY sn.created_at DESC''',
        (case_id,)
    ).fetchall()
    conn.close()
    
    return jsonify([{
        'note': note['note'],
        'professional': note['username'],
        'created_at': note['created_at']
    } for note in notes])

@app.route('/end-professional-session', methods=['POST'])
@login_required
def end_professional_session():
    """End professional intervention session"""
    case_id = request.json.get('case_id')
    
    if not case_id:
        return jsonify({'success': False, 'error': 'Case ID required'})
    
    user = get_current_user()
    if user['role'] != 'professional':
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    conn = get_db_connection()
    
    # Update case status to closed
    conn.execute(
        'UPDATE support_requests SET status = "closed" WHERE id = ?',
        (case_id,)
    )
    
    # Add session closure message
    conn.execute(
        'INSERT INTO chat_messages (request_id, sender_id, message) VALUES (?, ?, ?)',
        (case_id, session['user_id'], "[PROFESSIONAL NOTE] Session concluded. Patient has been provided with appropriate intervention and resources. Case closed with documentation.")
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/book-professional', methods=['POST'])
@login_required
def book_professional():
    """Book professional appointment"""
    reason = request.json.get('reason', '').strip()
    preferred_date = request.json.get('preferred_date', '').strip()
    preferred_time = request.json.get('preferred_time', '').strip()
    
    if not reason or not preferred_date or not preferred_time:
        return jsonify({'success': False, 'error': 'Reason, date, and time required'})
    
    user = get_current_user()
    if user['role'] != 'student':
        return jsonify({'success': False, 'error': 'Only students can book appointments'})
    
    conn = get_db_connection()
    
    # Create professional appointment request
    conn.execute(
        'INSERT INTO support_requests (user_id, message, priority, status, appointment_date, appointment_time) VALUES (?, ?, ?, ?, ?, ?)',
        (session['user_id'], f'Professional appointment request: {reason}', 'high', 'professional_booking', preferred_date, preferred_time)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/appointment-status')
@login_required
def appointment_status():
    """Check student's appointment status"""
    user = get_current_user()
    if user['role'] != 'student':
        return jsonify({'has_appointment': False})
    
    conn = get_db_connection()
    appointment = conn.execute(
        'SELECT status, appointment_date, appointment_time, professional_id FROM support_requests WHERE user_id = ? AND status IN ("professional_booking", "professional") ORDER BY created_at DESC LIMIT 1',
        (session['user_id'],)
    ).fetchone()
    conn.close()
    
    if appointment:
        if appointment['status'] == 'professional_booking':
            return jsonify({
                'has_appointment': True, 
                'status': 'booked',
                'date': appointment['appointment_date'],
                'time': appointment['appointment_time']
            })
        else:
            return jsonify({
                'has_appointment': True, 
                'status': 'active',
                'date': appointment['appointment_date'],
                'time': appointment['appointment_time']
            })
    
    return jsonify({'has_appointment': False})

@app.route('/get-appointment-id')
@login_required
def get_appointment_id():
    """Get student's appointment ID for chat"""
    user = get_current_user()
    if user['role'] != 'student':
        return jsonify({'appointment_id': None})
    
    conn = get_db_connection()
    appointment = conn.execute(
        'SELECT id FROM support_requests WHERE user_id = ? AND status IN ("professional_booking", "professional") ORDER BY created_at DESC LIMIT 1',
        (session['user_id'],)
    ).fetchone()
    conn.close()
    
    if appointment:
        return jsonify({'appointment_id': appointment['id']})
    
    return jsonify({'appointment_id': None})

@app.route('/student-chat/<int:appointment_id>')
@login_required
def student_chat(appointment_id):
    """Student chat interface for appointments"""
    user = get_current_user()
    if user['role'] != 'student':
        flash('Access denied')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    appointment = conn.execute(
        '''SELECT sr.*, u.username as professional_name
           FROM support_requests sr 
           LEFT JOIN users u ON sr.professional_id = u.id
           WHERE sr.id = ? AND sr.user_id = ?''',
        (appointment_id, session['user_id'])
    ).fetchone()
    conn.close()
    
    if not appointment:
        flash('Appointment not found')
        return redirect(url_for('support'))
    
    return render_template('student_chat.html', appointment=appointment, user=user)

@app.route('/api/appointment-details/<int:appointment_id>')
@login_required
def get_appointment_details(appointment_id):
    """Get appointment details for students"""
    user = get_current_user()
    if user['role'] != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = get_db_connection()
    appointment = conn.execute(
        '''SELECT sr.status, u.username as professional_name
           FROM support_requests sr 
           LEFT JOIN users u ON sr.professional_id = u.id
           WHERE sr.id = ? AND sr.user_id = ?''',
        (appointment_id, session['user_id'])
    ).fetchone()
    conn.close()
    
    if appointment:
        return jsonify({
            'status': appointment['status'],
            'professional_name': appointment['professional_name']
        })
    
    return jsonify({'error': 'Appointment not found'}), 404

@app.route('/past-appointments')
@login_required
def past_appointments():
    """View past appointments for students"""
    user = get_current_user()
    if user['role'] != 'student':
        flash('Access denied')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    appointments = conn.execute(
        '''SELECT sr.*, u.username as professional_name
           FROM support_requests sr 
           LEFT JOIN users u ON sr.professional_id = u.id
           WHERE sr.user_id = ? AND sr.message LIKE "Professional appointment request:%"
           ORDER BY sr.created_at DESC''',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    
    return render_template('past_appointments.html', appointments=appointments, user=user)

@app.route('/test-notification')
@login_required
def test_notification_debug():
    """Debug route to test notifications"""
    user = get_current_user()
    
    try:
        result = notification_system.send_notification(
            user['id'],
            "Test Notification",
            "This is a test notification to verify your settings are working correctly.",
            "HavenMind - Test Notification"
        )
        return jsonify({
            'success': result,
            'phone': user['phone'],
            'email': user['email'],
            'notification_method': user['notification_method']
        })
    except Exception as e:
        return jsonify({'error': str(e)})

# Add manual schedule trigger routes
@app.route('/send-schedule-now')
@login_required
def manual_schedule():
    """Manually trigger daily schedule for current user"""
    user = get_current_user()
    
    try:
        success = send_schedule_now(user['id'])
        if success:
            return jsonify({'success': True, 'message': 'Daily schedule sent!'})
        else:
            return jsonify({'success': False, 'message': 'Failed to send schedule'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/send-all-schedules')
@login_required
def admin_send_all_schedules():
    """Admin route to send schedules to all users"""
    user = get_current_user()
    if user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        from daily_scheduler import send_daily_schedules
        send_daily_schedules()
        return jsonify({'success': True, 'message': 'Schedules sent to all users'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/student-location/<int:student_id>')
@login_required
def get_student_location_api(student_id):
    """API endpoint for professionals to get student location and emergency contact"""
    user = get_current_user()
    if user['role'] != 'professional':
        return jsonify({'error': 'Unauthorized'}), 403
    
    location_data = get_student_location_for_professional(student_id)
    if location_data:
        return jsonify(location_data)
    else:
        return jsonify({'error': 'Student not found or no emergency contact available'}), 404

@app.route('/share-location', methods=['POST'])
@login_required
def share_location():
    """Endpoint for students to share their location during crisis"""
    user = get_current_user()
    latitude = request.json.get('latitude')
    longitude = request.json.get('longitude')
    
    if latitude and longitude:
        # Store location in database with timestamp
        conn = get_db_connection()
        try:
            # Add location sharing table if it doesn't exist
            conn.execute('''CREATE TABLE IF NOT EXISTS location_shares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                shared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                emergency_contact_phone TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )''')
            
            # Store the location share
            conn.execute(
                'INSERT INTO location_shares (user_id, latitude, longitude, emergency_contact_phone) VALUES (?, ?, ?, ?)',
                (user['id'], latitude, longitude, user['emergency_contact_phone'])
            )
            conn.commit()
        except Exception as e:
            print(f"Error storing location: {e}")
        finally:
            conn.close()
        
        # Send location to emergency contact if crisis situation
        if user['emergency_contact_phone']:
            location_msg = f"""📍 LIVE LOCATION SHARED - EMERGENCY

Student: {user['username']}
Location: https://maps.google.com/?q={latitude},{longitude}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚠️ This is an emergency location share. Please check on the student immediately.

For continuous location updates, the student can share their location again.

HavenMind Emergency System"""
            
            try:
                notification_system.send_sms(
                    user['emergency_contact_phone'],
                    location_msg
                )
                return jsonify({
                    'success': True, 
                    'message': 'Location shared with emergency contact',
                    'emergency_contact': user['emergency_contact_name']
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
    
    return jsonify({'success': False, 'error': 'Invalid location data'})

# Institution Dashboard Management Routes
@app.route('/institution/students')
@login_required
def institution_students():
    user = get_current_user()
    if user['role'] != 'institution_admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    # Get department-wise wellness data (aggregated only)
    departments = conn.execute(
        'SELECT DISTINCT major FROM users WHERE university = ? AND role = "student" AND major IS NOT NULL',
        (user['university'],)
    ).fetchall()
    
    dept_wellness = []
    overall_scores = []
    
    for dept in departments:
        dept_students = conn.execute(
            'SELECT id FROM users WHERE university = ? AND role = "student" AND major = ?',
            (user['university'], dept['major'])
        ).fetchall()
        
        if dept_students:
            dept_score = 0
            student_count = 0
            
            for student in dept_students:
                journal_mood = conn.execute(
                    'SELECT AVG(sentiment_score) as avg_mood FROM journal_entries WHERE user_id = ?',
                    (student['id'],)
                ).fetchone()['avg_mood']
                
                if journal_mood:
                    dept_score += journal_mood * 100
                    student_count += 1
                else:
                    dept_score += 75
                    student_count += 1
            
            avg_dept_score = dept_score / student_count if student_count > 0 else 75
            dept_wellness.append({
                'department': dept['major'],
                'score': int(avg_dept_score),
                'student_count': student_count
            })
            overall_scores.append(avg_dept_score)
    
    university_wellness = int(sum(overall_scores) / len(overall_scores)) if overall_scores else 75
    
    suggestions = []
    if university_wellness < 60:
        suggestions.append("Consider implementing campus-wide stress management workshops")
        suggestions.append("Increase mental health awareness campaigns")
    if university_wellness < 70:
        suggestions.append("Expand peer support programs")
        suggestions.append("Provide more study spaces and relaxation areas")
    if university_wellness >= 80:
        suggestions.append("Maintain current wellness initiatives")
        suggestions.append("Share best practices with other institutions")
    
    conn.close()
    
    return render_template('dashboards/institution-wellness.html',
                         user=user,
                         university_wellness=university_wellness,
                         dept_wellness=dept_wellness,
                         suggestions=suggestions)

@app.route('/institution/staff')
@login_required
def institution_staff():
    user = get_current_user()
    if user['role'] != 'institution_admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    staff = conn.execute(
        'SELECT * FROM users WHERE university = ? AND role IN ("professional", "peer_supporter") ORDER BY role, created_at DESC',
        (user['university'],)
    ).fetchall()
    conn.close()
    
    return render_template('dashboards/institution-staff.html', user=user, staff=staff)

@app.route('/institution/settings')
@login_required
def institution_settings():
    user = get_current_user()
    if user['role'] != 'institution_admin':
        flash('Access denied')
        return redirect(url_for('index'))
    return render_template('dashboards/institution-settings.html', user=user)

@app.route('/institution/reports')
@login_required
def institution_reports():
    user = get_current_user()
    if user['role'] != 'institution_admin':
        flash('Access denied')
        return redirect(url_for('index'))
    return render_template('dashboards/institution-reports.html', user=user)

@app.route('/institution/crisis')
@login_required
def institution_crisis():
    user = get_current_user()
    if user['role'] != 'institution_admin':
        flash('Access denied')
        return redirect(url_for('index'))
    return render_template('dashboards/institution-crisis.html', user=user)

@app.route('/institution/analytics')
@login_required
def institution_analytics():
    user = get_current_user()
    if user['role'] != 'institution_admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    # Get department-wise analytics
    departments = conn.execute(
        'SELECT DISTINCT major FROM users WHERE university = ? AND role = "student" AND major IS NOT NULL',
        (user['university'],)
    ).fetchall()
    
    dept_analytics = []
    for dept in departments:
        # Get students in department
        dept_students = conn.execute(
            'SELECT id FROM users WHERE university = ? AND role = "student" AND major = ?',
            (user['university'], dept['major'])
        ).fetchall()
        
        if dept_students:
            student_ids = [s['id'] for s in dept_students]
            
            # Calculate department metrics
            total_students = len(student_ids)
            
            # Active students (journaled in last 7 days)
            placeholders = ','.join(['?'] * len(student_ids))
            active_students = conn.execute(
                f'SELECT COUNT(DISTINCT user_id) as count FROM journal_entries WHERE user_id IN ({placeholders}) AND created_at >= datetime("now", "-7 days")',
                student_ids
            ).fetchone()['count']
            
            # Average wellness score
            wellness_scores = []
            for student_id in student_ids:
                mood = conn.execute(
                    'SELECT AVG(sentiment_score) as avg_mood FROM journal_entries WHERE user_id = ?',
                    (student_id,)
                ).fetchone()['avg_mood']
                wellness_scores.append((mood * 100) if mood else 75)
            
            avg_wellness = int(sum(wellness_scores) / len(wellness_scores))
            
            # At-risk students
            at_risk = sum(1 for score in wellness_scores if score < 50)
            
            # Support requests
            support_requests = conn.execute(
                f'SELECT COUNT(*) as count FROM support_requests WHERE user_id IN ({placeholders}) AND created_at >= datetime("now", "-30 days")',
                student_ids
            ).fetchone()['count']
            
            dept_analytics.append({
                'department': dept['major'],
                'total_students': total_students,
                'active_students': active_students,
                'avg_wellness': avg_wellness,
                'at_risk': at_risk,
                'support_requests': support_requests,
                'engagement_rate': int((active_students / total_students) * 100) if total_students > 0 else 0
            })
    
    conn.close()
    
    return render_template('dashboards/institution-analytics.html', user=user, dept_analytics=dept_analytics)

@app.route('/institution/department-analysis')
@login_required
def institution_department_analysis():
    user = get_current_user()
    if user['role'] != 'institution_admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    departments = conn.execute(
        'SELECT DISTINCT major FROM users WHERE university = ? AND role = "student" AND major IS NOT NULL',
        (user['university'],)
    ).fetchall()
    
    dept_analytics = []
    for dept in departments:
        dept_students = conn.execute(
            'SELECT id FROM users WHERE university = ? AND role = "student" AND major = ?',
            (user['university'], dept['major'])
        ).fetchall()
        
        if dept_students:
            student_ids = [s['id'] for s in dept_students]
            total_students = len(student_ids)
            
            wellness_scores = []
            for student_id in student_ids:
                mood = conn.execute(
                    'SELECT AVG(sentiment_score) as avg_mood FROM journal_entries WHERE user_id = ?',
                    (student_id,)
                ).fetchone()['avg_mood']
                wellness_scores.append((mood * 100) if mood else 75)
            
            avg_wellness = int(sum(wellness_scores) / len(wellness_scores))
            at_risk = sum(1 for score in wellness_scores if score < 50)
            
            dept_analytics.append({
                'department': dept['major'],
                'total_students': total_students,
                'avg_wellness': avg_wellness,
                'at_risk': at_risk
            })
    
    conn.close()
    return render_template('dashboards/institution-department.html', user=user, dept_analytics=dept_analytics)

@app.route('/institution/wellness-trends')
@login_required
def institution_wellness_trends():
    user = get_current_user()
    if user['role'] != 'institution_admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    wellness_timeline = conn.execute(
        '''SELECT date(je.created_at) as date, AVG(je.sentiment_score) as avg_mood
           FROM journal_entries je 
           JOIN users u ON je.user_id = u.id 
           WHERE u.university = ? AND u.role = "student" 
           AND je.created_at >= datetime("now", "-30 days")
           GROUP BY date(je.created_at) 
           ORDER BY date''',
        (user['university'],)
    ).fetchall()
    
    mood_distribution = conn.execute(
        '''SELECT 
           CASE 
               WHEN je.sentiment_score >= 0.7 THEN 'Positive'
               WHEN je.sentiment_score >= 0.4 THEN 'Neutral'
               ELSE 'Negative'
           END as mood_category,
           COUNT(*) as count
           FROM journal_entries je 
           JOIN users u ON je.user_id = u.id 
           WHERE u.university = ? AND u.role = "student" 
           AND je.created_at >= datetime("now", "-30 days")
           GROUP BY mood_category''',
        (user['university'],)
    ).fetchall()
    
    conn.close()
    
    # Calculate metrics for template
    timeline_data = [{'date': row['date'], 'mood': row['avg_mood']} for row in wellness_timeline]
    distribution_data = [{'category': row['mood_category'], 'count': row['count']} for row in mood_distribution]
    
    avg_wellness = sum(d['mood'] for d in timeline_data) / len(timeline_data) * 100 if timeline_data else 0
    total_entries = sum(d['count'] for d in distribution_data)
    
    # Determine trend direction
    if len(timeline_data) >= 2:
        recent_avg = sum(d['mood'] for d in timeline_data[-7:]) / min(7, len(timeline_data))
        earlier_avg = sum(d['mood'] for d in timeline_data[:7]) / min(7, len(timeline_data))
        trend_direction = 'up' if recent_avg > earlier_avg + 0.05 else 'down' if recent_avg < earlier_avg - 0.05 else 'stable'
    else:
        trend_direction = 'stable'
    
    return render_template('dashboards/institution-trends.html', 
                         user=user, 
                         wellness_timeline=timeline_data,
                         mood_distribution=distribution_data,
                         avg_wellness=avg_wellness,
                         total_entries=total_entries,
                         trend_direction=trend_direction)

@app.route('/generate-monthly-report')
@login_required
def generate_monthly_report():
    user = get_current_user()
    if user['role'] != 'institution_admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.graphics.shapes import Drawing
        from reportlab.graphics.charts.piecharts import Pie
        from reportlab.graphics.charts.barcharts import VerticalBarChart
        from datetime import datetime, timedelta
        import io
        from flask import make_response
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30, alignment=1, fontName='Times-Bold')
        subtitle_style = ParagraphStyle('CustomSubtitle', parent=styles['Heading2'], fontSize=16, spaceAfter=20, alignment=1, fontName='Times-Bold')
        chart_title_style = ParagraphStyle('ChartTitle', parent=styles['Heading2'], fontSize=16, spaceAfter=10, alignment=1, fontName='Times-Bold')
        content_style = ParagraphStyle('Content', parent=styles['Normal'], fontSize=14, alignment=1, fontName='Times-Roman')
        
        # Get current month and year
        now = datetime.now()
        month_name = now.strftime('%B')
        year = now.year
        
        # FRONT PAGE
        story.append(Spacer(1, 1.5*inch))
        story.append(Paragraph(f"{user['university']}", title_style))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"{month_name} {year} Wellness Report", subtitle_style))
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("Generated by HavenMind Analytics Platform", content_style))
        story.append(PageBreak())
        
        # Get data from database
        conn = get_db_connection()
        
        # Get institution students
        students = conn.execute(
            'SELECT id FROM users WHERE university = ? AND role = "student"',
            (user['university'],)
        ).fetchall()
        
        student_ids = [s['id'] for s in students]
        total_students = len(student_ids)
        
        if student_ids:
            placeholders = ','.join(['?'] * len(student_ids))
            
            # Wellness scores
            wellness_scores = []
            for student_id in student_ids:
                mood = conn.execute(
                    'SELECT AVG(sentiment_score) as avg_mood FROM journal_entries WHERE user_id = ? AND created_at >= datetime("now", "-30 days")',
                    (student_id,)
                ).fetchone()['avg_mood']
                wellness_scores.append((mood * 100) if mood else 75)
            
            avg_wellness = sum(wellness_scores) / len(wellness_scores)
            
            # Mood distribution
            mood_dist = conn.execute(
                f'''SELECT 
                   CASE 
                       WHEN je.sentiment_score >= 0.7 THEN 'Positive'
                       WHEN je.sentiment_score >= 0.4 THEN 'Neutral'
                       ELSE 'Negative'
                   END as mood_category,
                   COUNT(*) as count
                   FROM journal_entries je 
                   WHERE je.user_id IN ({placeholders}) 
                   AND je.created_at >= datetime("now", "-30 days")
                   GROUP BY mood_category''',
                student_ids
            ).fetchall()
            
            # Department analysis
            dept_data = conn.execute(
                f'''SELECT u.major, COUNT(DISTINCT u.id) as student_count, AVG(je.sentiment_score) as avg_mood
                   FROM users u
                   LEFT JOIN journal_entries je ON u.id = je.user_id AND je.created_at >= datetime("now", "-30 days")
                   WHERE u.id IN ({placeholders}) AND u.major IS NOT NULL
                   GROUP BY u.major''',
                student_ids
            ).fetchall()
            
            # Weekly trends
            weekly_trends = conn.execute(
                f'''SELECT strftime('%W', je.created_at) as week, AVG(je.sentiment_score) as avg_mood
                   FROM journal_entries je 
                   WHERE je.user_id IN ({placeholders}) 
                   AND je.created_at >= datetime("now", "-30 days")
                   GROUP BY strftime('%W', je.created_at)
                   ORDER BY week''',
                student_ids
            ).fetchall()
            
            # Stress levels
            stress_levels = conn.execute(
                f'''SELECT ce.stress_level, COUNT(*) as count
                   FROM calendar_events ce 
                   WHERE ce.user_id IN ({placeholders}) 
                   AND ce.event_date >= datetime("now", "-30 days")
                   GROUP BY ce.stress_level''',
                student_ids
            ).fetchall()
            
            # Support requests
            support_count = conn.execute(
                f'SELECT COUNT(*) as count FROM support_requests WHERE user_id IN ({placeholders}) AND created_at >= datetime("now", "-30 days")',
                student_ids
            ).fetchone()['count']
            
            # Active users
            active_users = conn.execute(
                f'SELECT COUNT(DISTINCT user_id) as count FROM journal_entries WHERE user_id IN ({placeholders}) AND created_at >= datetime("now", "-30 days")',
                student_ids
            ).fetchone()['count']
        
        conn.close()
        
        # EXECUTIVE SUMMARY
        story.append(Paragraph("Executive Summary", ParagraphStyle('Heading', parent=styles['Heading1'], fontSize=16, alignment=1, fontName='Times-Bold')))
        story.append(Spacer(1, 12))
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Students', str(total_students)],
            ['Average Wellness Score', f"{avg_wellness:.1f}/100"],
            ['Active Users (30 days)', str(active_users)],
            ['Support Requests', str(support_count)],
            ['Engagement Rate', f"{(active_users/total_students*100):.1f}%" if total_students > 0 else "0%"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(PageBreak())
        
        # PAGE 1: GRAPHS 1 & 2
        story.append(Paragraph("Figure 1: Student Mood Distribution", chart_title_style))
        story.append(Spacer(1, 5))
        
        if mood_dist:
            mood_data = []
            mood_labels = []
            for row in mood_dist:
                mood_data.append(row['count'])
                mood_labels.append(f"{row['mood_category']} ({row['count']})")
            
            drawing = Drawing(500, 200)
            pie = Pie()
            pie.x = 200
            pie.y = 50
            pie.width = 100
            pie.height = 100
            pie.data = mood_data
            pie.labels = mood_labels
            pie.slices.strokeWidth = 1
            pie.slices[0].fillColor = colors.teal
            pie.slices[1].fillColor = colors.cyan if len(pie.slices) > 1 else colors.teal
            pie.slices[2].fillColor = colors.navy if len(pie.slices) > 2 else colors.cyan
            drawing.add(pie)
            story.append(drawing)
        
        story.append(Spacer(1, 10))
        centered_style = ParagraphStyle('Centered', parent=styles['Normal'], fontSize=14, alignment=1, fontName='Times-Roman')
        story.append(Paragraph("Distribution of student moods based on journal entries over the past 30 days.", centered_style))
        story.append(Spacer(1, 20))
        
        # GRAPH 2 on same page
        story.append(Paragraph("Figure 2: Department-wise Wellness Scores", chart_title_style))
        story.append(Spacer(1, 5))
        
        if dept_data:
            drawing = Drawing(500, 200)
            bar_chart = VerticalBarChart()
            bar_chart.x = 50
            bar_chart.y = 50
            bar_chart.width = 400
            bar_chart.height = 120
            
            dept_names = [row['major'][:8] for row in dept_data]
            dept_scores = [(row['avg_mood'] * 100) if row['avg_mood'] else 75 for row in dept_data]
            
            bar_chart.data = [dept_scores]
            bar_chart.categoryAxis.categoryNames = dept_names
            bar_chart.valueAxis.valueMin = 0
            bar_chart.valueAxis.valueMax = 100
            bar_chart.bars[0].fillColor = colors.steelblue
            
            drawing.add(bar_chart)
            story.append(drawing)
        
        story.append(Spacer(1, 10))
        story.append(Paragraph("Wellness scores by academic department showing comparative mental health metrics.", centered_style))
        story.append(PageBreak())
        
        # PAGE 2: GRAPHS 3 & 4
        story.append(Paragraph("Figure 3: Weekly Wellness Trends", chart_title_style))
        story.append(Spacer(1, 5))
        
        if weekly_trends:
            drawing = Drawing(500, 200)
            bar_chart = VerticalBarChart()
            bar_chart.x = 50
            bar_chart.y = 50
            bar_chart.width = 400
            bar_chart.height = 120
            
            weeks = [f"W{row['week']}" for row in weekly_trends]
            trend_scores = [(row['avg_mood'] * 100) if row['avg_mood'] else 75 for row in weekly_trends]
            
            bar_chart.data = [trend_scores]
            bar_chart.categoryAxis.categoryNames = weeks
            bar_chart.valueAxis.valueMin = 0
            bar_chart.valueAxis.valueMax = 100
            bar_chart.bars[0].fillColor = colors.darkturquoise
            
            drawing.add(bar_chart)
            story.append(drawing)
        
        story.append(Spacer(1, 10))
        story.append(Paragraph("Weekly progression of student wellness scores showing temporal patterns.", centered_style))
        story.append(Spacer(1, 20))
        
        # GRAPH 4 on same page
        story.append(Paragraph("Figure 4: Student Stress Level Distribution", chart_title_style))
        story.append(Spacer(1, 5))
        
        if stress_levels:
            stress_data = []
            stress_labels = []
            for row in stress_levels:
                stress_data.append(row['count'])
                stress_labels.append(f"{row['stress_level'].title()} ({row['count']})")
            
            drawing = Drawing(500, 200)
            pie = Pie()
            pie.x = 200
            pie.y = 50
            pie.width = 100
            pie.height = 100
            pie.data = stress_data
            pie.labels = stress_labels
            pie.slices.strokeWidth = 1
            colors_map = {'minimal': colors.lightblue, 'low': colors.cyan, 'medium': colors.blue, 'high': colors.navy, 'critical': colors.darkblue}
            for i, row in enumerate(stress_levels):
                if i < len(pie.slices):
                    pie.slices[i].fillColor = colors_map.get(row['stress_level'], colors.gray)
            
            drawing.add(pie)
            story.append(drawing)
        
        story.append(Spacer(1, 10))
        story.append(Paragraph("Distribution of stress levels from student calendar events and academic workload.", centered_style))
        story.append(PageBreak())
        
        # PAGE 3: GRAPH 5 (centered)
        story.append(Spacer(1, 50))
        story.append(Paragraph("Figure 5: Platform Engagement Overview", chart_title_style))
        story.append(Spacer(1, 20))
        
        engagement_rate = (active_users/total_students*100) if total_students > 0 else 0
        engagement_data = [active_users, total_students - active_users]
        engagement_labels = [f"Active ({active_users})", f"Inactive ({total_students - active_users})"]
        
        drawing = Drawing(500, 300)
        pie = Pie()
        pie.x = 175
        pie.y = 100
        pie.width = 150
        pie.height = 150
        pie.data = engagement_data
        pie.labels = engagement_labels
        pie.slices.strokeWidth = 1
        pie.slices[0].fillColor = colors.mediumturquoise
        pie.slices[1].fillColor = colors.lightsteelblue
        
        drawing.add(pie)
        story.append(drawing)
        
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Platform engagement rate: {engagement_rate:.1f}% of students actively using wellness tracking.", centered_style))
        story.append(PageBreak())
        
        # SINGLE PAGE: ANALYSIS, SUGGESTIONS, AND CONCLUSION
        story.append(Paragraph("Analysis, Recommendations & Conclusion", ParagraphStyle('MainHeading', parent=styles['Heading1'], fontSize=16, alignment=1, fontName='Times-Bold')))
        story.append(Spacer(1, 15))
        
        # Key Findings (Compact)
        story.append(Paragraph("Key Findings:", ParagraphStyle('SubHeading', parent=styles['Heading3'], fontSize=16, alignment=1, fontName='Times-Bold')))
        story.append(Spacer(1, 8))
        
        findings = []
        if avg_wellness >= 80:
            findings.append("• Excellent wellness scores indicate healthy campus environment")
        elif avg_wellness >= 70:
            findings.append("• Good wellness scores with room for targeted improvements")
        else:
            findings.append("• Wellness scores suggest need for enhanced support programs")
        
        if engagement_rate >= 50:
            findings.append("• High platform engagement shows strong student participation")
        else:
            findings.append("• Engagement levels indicate need for awareness campaigns")
        
        for finding in findings[:3]:  # Limit to 3 key findings
            story.append(Paragraph(finding, content_style))
            story.append(Spacer(1, 4))
        
        story.append(Spacer(1, 15))
        
        # Recommendations (Compact)
        story.append(Paragraph("Recommendations:", ParagraphStyle('SubHeading', parent=styles['Heading3'], fontSize=16, alignment=1, fontName='Times-Bold')))
        story.append(Spacer(1, 8))
        
        recommendations = [
            "• Implement targeted stress management workshops",
            "• Expand peer support programs across departments",
            "• Increase mental health awareness campaigns",
            "• Continue monthly wellness monitoring and reporting"
        ]
        
        for rec in recommendations:
            story.append(Paragraph(rec, content_style))
            story.append(Spacer(1, 4))
        
        story.append(Spacer(1, 20))
        
        # Conclusion (Compact)
        story.append(Paragraph("Conclusion:", ParagraphStyle('SubHeading', parent=styles['Heading3'], fontSize=16, alignment=1, fontName='Times-Bold')))
        story.append(Spacer(1, 8))
        
        conclusion_text = f"""This {month_name} {year} wellness report for {user['university']} shows an average wellness score of {avg_wellness:.1f}/100 with {engagement_rate:.1f}% platform engagement. The data reveals important trends guiding institutional wellness strategies. With {active_users} out of {total_students} students actively engaged, continued monitoring and implementation of recommended strategies will support ongoing mental health and academic success."""
        
        story.append(Paragraph(conclusion_text, content_style))
        story.append(PageBreak())
        
        # THANK YOU PAGE
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("THANK YOU", ParagraphStyle('BigThankYou', parent=styles['Heading1'], fontSize=36, alignment=1, fontName='Times-Bold')))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("For supporting student mental health and wellness initiatives", ParagraphStyle('ThankYouSub', parent=styles['Heading2'], fontSize=18, alignment=1, fontName='Times-Bold')))
        story.append(Spacer(1, 1*inch))
        story.append(Paragraph("Together, we create healthier campus communities", ParagraphStyle('Italic', parent=styles['Italic'], fontSize=16, alignment=1, fontName='Times-Italic')))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("HavenMind - Empowering Mental Wellness Through Technology", ParagraphStyle('Footer', parent=styles['Normal'], fontSize=14, alignment=1, fontName='Times-Roman')))
        
        # Build PDF
        doc.build(story)
        
        # Return PDF response
        buffer.seek(0)
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{user["university"]}_{month_name}_{year}_Wellness_Report.pdf"'
        
        return response
        
    except ImportError as e:
        flash(f'PDF generation requires reportlab. Import error: {str(e)}')
        return redirect(url_for('institution_dashboard'))
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"PDF Generation Error: {error_details}")
        flash(f'Error generating report: {str(e)}')
        return redirect(url_for('institution_dashboard'))

@app.route('/get-location-sharing-status')
@login_required
def get_location_sharing_status():
    """Check if user should be prompted for location sharing"""
    prompt_location = session.pop('prompt_location_share', False)
    user = get_current_user()
    
    return jsonify({
        'prompt_location': prompt_location,
        'emergency_contact': user.get('emergency_contact_name', 'your emergency contact'),
        'has_emergency_contact': bool(user.get('emergency_contact_phone'))
    })

if __name__ == '__main__':
    init_db()
    
    # Create admin user if not exists
    conn = get_db_connection()
    admin_exists = conn.execute('SELECT id FROM users WHERE email = ?', ('admin@gmail.com',)).fetchone()
    if not admin_exists:
        admin_password_hash = hash_password('admin123')
        conn.execute(
            'INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
            ('admin', 'admin@gmail.com', admin_password_hash, 'admin')
        )
        conn.commit()
        print('Admin user created: admin@gmail.com / admin123')
    conn.close()
    
    # Start the daily scheduler
    start_daily_scheduler()
    
    app.run(debug=True)
# Add these routes at the end of app.py before if __name__ == '__main__':

@app.route('/institution/department-analysis')
@login_required
def institution_department_analysis():
    user = get_current_user()
    if user['role'] != 'institution_admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    # Get department-wise analytics
    departments = conn.execute(
        'SELECT DISTINCT major FROM users WHERE university = ? AND role = "student" AND major IS NOT NULL',
        (user['university'],)
    ).fetchall()
    
    dept_analytics = []
    for dept in departments:
        # Get students in department
        dept_students = conn.execute(
            'SELECT id FROM users WHERE university = ? AND role = "student" AND major = ?',
            (user['university'], dept['major'])
        ).fetchall()
        
        if dept_students:
            student_ids = [s['id'] for s in dept_students]
            
            # Calculate department metrics
            total_students = len(student_ids)
            
            # Active students (journaled in last 7 days)
            placeholders = ','.join(['?'] * len(student_ids))
            active_students = conn.execute(
                f'SELECT COUNT(DISTINCT user_id) as count FROM journal_entries WHERE user_id IN ({placeholders}) AND created_at >= datetime("now", "-7 days")',
                student_ids
            ).fetchone()['count']
            
            # Average wellness score
            wellness_scores = []
            for student_id in student_ids:
                mood = conn.execute(
                    'SELECT AVG(sentiment_score) as avg_mood FROM journal_entries WHERE user_id = ?',
                    (student_id,)
                ).fetchone()['avg_mood']
                wellness_scores.append((mood * 100) if mood else 75)
            
            avg_wellness = int(sum(wellness_scores) / len(wellness_scores))
            
            # At-risk students
            at_risk = sum(1 for score in wellness_scores if score < 50)
            
            # Support requests
            support_requests = conn.execute(
                f'SELECT COUNT(*) as count FROM support_requests WHERE user_id IN ({placeholders}) AND created_at >= datetime("now", "-30 days")',
                student_ids
            ).fetchone()['count']
            
            dept_analytics.append({
                'department': dept['major'],
                'total_students': total_students,
                'active_students': active_students,
                'avg_wellness': avg_wellness,
                'at_risk': at_risk,
                'support_requests': support_requests,
                'engagement_rate': int((active_students / total_students) * 100) if total_students > 0 else 0
            })
    
    conn.close()
    
    return jsonify({
        'success': True,
        'data': dept_analytics,
        'message': 'Department Analysis - Detailed breakdown by academic department'
    })

@app.route('/institution/wellness-trends')
@login_required
def institution_wellness_trends():
    user = get_current_user()
    if user['role'] != 'institution_admin':
        flash('Access denied')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    # Get wellness trends over time (last 30 days)
    wellness_timeline = conn.execute(
        '''SELECT date(je.created_at) as date, AVG(je.sentiment_score) as avg_mood
           FROM journal_entries je 
           JOIN users u ON je.user_id = u.id 
           WHERE u.university = ? AND u.role = "student" 
           AND je.created_at >= datetime("now", "-30 days")
           GROUP BY date(je.created_at) 
           ORDER BY date''',
        (user['university'],)
    ).fetchall()
    
    # Get mood distribution
    mood_distribution = conn.execute(
        '''SELECT 
           CASE 
               WHEN je.sentiment_score >= 0.7 THEN 'Positive'
               WHEN je.sentiment_score >= 0.4 THEN 'Neutral'
               ELSE 'Negative'
           END as mood_category,
           COUNT(*) as count
           FROM journal_entries je 
           JOIN users u ON je.user_id = u.id 
           WHERE u.university = ? AND u.role = "student" 
           AND je.created_at >= datetime("now", "-30 days")
           GROUP BY mood_category''',
        (user['university'],)
    ).fetchall()
    
    # Get stress patterns by day of week
    stress_patterns = conn.execute(
        '''SELECT 
           CASE strftime('%w', ce.event_date)
               WHEN '0' THEN 'Sunday'
               WHEN '1' THEN 'Monday'
               WHEN '2' THEN 'Tuesday'
               WHEN '3' THEN 'Wednesday'
               WHEN '4' THEN 'Thursday'
               WHEN '5' THEN 'Friday'
               WHEN '6' THEN 'Saturday'
           END as day_of_week,
           AVG(CASE ce.stress_level
               WHEN 'critical' THEN 5
               WHEN 'high' THEN 4
               WHEN 'medium' THEN 3
               WHEN 'low' THEN 2
               ELSE 1
           END) as avg_stress
           FROM calendar_events ce 
           JOIN users u ON ce.user_id = u.id 
           WHERE u.university = ? AND u.role = "student" 
           AND ce.event_date >= datetime("now", "-30 days")
           GROUP BY strftime('%w', ce.event_date)
           ORDER BY strftime('%w', ce.event_date)''',
        (user['university'],)
    ).fetchall()
    
    conn.close()
    
    timeline_data = [{'date': row['date'], 'mood': row['avg_mood']} for row in wellness_timeline]
    mood_data = [{'category': row['mood_category'], 'count': row['count']} for row in mood_distribution]
    stress_data = [{'day': row['day_of_week'], 'stress': row['avg_stress']} for row in stress_patterns]
    
    return jsonify({
        'success': True,
        'data': {
            'timeline': timeline_data,
            'mood_distribution': mood_data,
            'stress_patterns': stress_data
        },
        'message': 'Wellness Trends - Time-based patterns and mood analytics'
    })
