from flask import Blueprint, request, jsonify
from ..models import JournalEntry, CalendarEvent, User, get_db_session
from ..utils.ai_helper import ai_helper
from datetime import datetime, timedelta

bp = Blueprint('ai_analysis', __name__, url_prefix='/api/ai')

@bp.route('/cognitive-load/<int:user_id>', methods=['GET'])
def get_cognitive_load(user_id):
    session = get_db_session()
    
    # Get recent events and journal entries
    week_ago = datetime.utcnow() - timedelta(days=7)
    events = session.query(CalendarEvent).filter(
        CalendarEvent.user_id == user_id,
        CalendarEvent.event_date >= week_ago
    ).all()
    
    journal_entries = session.query(JournalEntry).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.created_at >= week_ago
    ).all()
    
    # Calculate cognitive load
    cognitive_load = ai_helper.calculate_cognitive_load(events, journal_entries)
    
    # Update user's cognitive load score
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        user.cognitive_load_score = cognitive_load
        session.commit()
    
    return jsonify({
        'cognitive_load_index': cognitive_load,
        'status': 'high' if cognitive_load > 0.7 else 'medium' if cognitive_load > 0.4 else 'low',
        'recommendation': ai_helper.suggest_wellness_break(cognitive_load)
    })

@bp.route('/wellness-suggestion', methods=['POST'])
def get_wellness_suggestion():
    data = request.get_json()
    cognitive_load = data.get('cognitive_load', 0.5)
    
    suggestion = ai_helper.suggest_wellness_break(cognitive_load)
    
    return jsonify(suggestion)

@bp.route('/emotion-analysis', methods=['POST'])
def analyze_emotion():
    data = request.get_json()
    text = data.get('text', '')
    
    analysis = ai_helper.analyze_sentiment(text)
    
    return jsonify(analysis)