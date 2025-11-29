from flask import Blueprint, request, jsonify
from ..models import JournalEntry, get_db_session
from ..utils.ai_helper import ai_helper
from ..utils.gemini_ai_helper import gemini_ai
from datetime import datetime, timedelta
from sqlalchemy import func

bp = Blueprint('journal', __name__, url_prefix='/api/journal')

@bp.route('/entries', methods=['POST'])
def create_entry():
    data = request.get_json()
    content = data.get('content')
    user_id = data.get('user_id', 1)  # Default user for demo
    
    # Get user context for personalized responses
    user_context = _get_user_context(user_id)
    
    # Advanced sentiment analysis using Gemini
    sentiment_analysis = gemini_ai.analyze_sentiment_advanced(content)
    
    # Crisis assessment
    crisis_assessment = gemini_ai.assess_crisis_risk(content, sentiment_analysis)
    
    # Generate therapeutic AI response
    ai_response = gemini_ai.generate_therapeutic_response(content, sentiment_analysis, user_context)
    
    # Save to database
    session = get_db_session()
    entry = JournalEntry(
        user_id=user_id,
        content=content,
        sentiment_score=sentiment_analysis['score'],
        emotion_tags=sentiment_analysis['sentiment'],
        ai_response=ai_response
    )
    session.add(entry)
    session.commit()
    
    response_data = {
        'id': entry.id,
        'sentiment': sentiment_analysis,
        'ai_response': ai_response,
        'created_at': entry.created_at.isoformat()
    }
    
    # Add crisis support information if needed
    if crisis_assessment['crisis_level'] in ['high', 'immediate']:
        response_data['crisis_support'] = {
            'show_resources': True,
            'message': 'I notice you might be going through a particularly difficult time. Please consider reaching out for additional support.',
            'resources': [
                {'name': 'Crisis Text Line', 'contact': 'Text HOME to 741741'},
                {'name': 'National Suicide Prevention Lifeline', 'contact': '988'},
                {'name': 'Campus Counseling Center', 'contact': 'Contact your student services'}
            ]
        }
    
    return jsonify(response_data)

@bp.route('/entries', methods=['GET'])
def get_entries():
    user_id = request.args.get('user_id', 1)
    session = get_db_session()
    entries = session.query(JournalEntry).filter_by(user_id=user_id).order_by(JournalEntry.created_at.desc()).limit(10).all()
    
    return jsonify([{
        'id': entry.id,
        'content': entry.content,
        'sentiment_score': entry.sentiment_score,
        'emotion_tags': entry.emotion_tags,
        'ai_response': entry.ai_response,
        'created_at': entry.created_at.isoformat()
    } for entry in entries])

@bp.route('/prompts', methods=['GET'])
def get_personalized_prompts():
    user_id = request.args.get('user_id', 1)
    user_context = _get_user_context(user_id)
    
    # Generate personalized prompts using Gemini
    prompts = gemini_ai.generate_personalized_prompts(user_context)
    
    return jsonify({'prompts': prompts})

def _get_user_context(user_id: int) -> dict:
    """Get user context for personalized AI responses"""
    session = get_db_session()
    
    # Get recent entries (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_entries = session.query(JournalEntry).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.created_at >= thirty_days_ago
    ).all()
    
    if not recent_entries:
        return {
            'mood_trend': 'neutral',
            'recent_stress': 'unknown',
            'writing_frequency': 'new_user',
            'common_emotions': [],
            'concerns': []
        }
    
    # Calculate mood trend
    avg_sentiment = sum(entry.sentiment_score or 0.5 for entry in recent_entries) / len(recent_entries)
    mood_trend = 'positive' if avg_sentiment > 0.6 else 'negative' if avg_sentiment < 0.4 else 'neutral'
    
    # Get common emotions
    emotions = [entry.emotion_tags for entry in recent_entries if entry.emotion_tags]
    common_emotions = list(set(emotions))
    
    # Assess recent stress level
    recent_negative = sum(1 for entry in recent_entries[-5:] if (entry.sentiment_score or 0.5) < 0.4)
    recent_stress = 'high' if recent_negative >= 3 else 'medium' if recent_negative >= 1 else 'low'
    
    return {
        'mood_trend': mood_trend,
        'recent_stress': recent_stress,
        'writing_frequency': 'regular' if len(recent_entries) > 10 else 'occasional',
        'common_emotions': common_emotions,
        'concerns': [],  # Could be extracted from content analysis
        'stress_level': recent_stress
    }