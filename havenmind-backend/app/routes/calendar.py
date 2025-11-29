from flask import Blueprint, request, jsonify
from ..models import CalendarEvent, get_db_session
from ..utils.ai_helper import ai_helper
from datetime import datetime

bp = Blueprint('calendar', __name__, url_prefix='/api/calendar')

@bp.route('/events', methods=['POST'])
def create_event():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')
    event_date = datetime.fromisoformat(data.get('event_date'))
    user_id = data.get('user_id', 1)
    
    # Analyze stress level from title/description
    analysis = ai_helper.analyze_sentiment(f"{title} {description}")
    stress_level = analysis['stress_level']
    
    session = get_db_session()
    event = CalendarEvent(
        user_id=user_id,
        title=title,
        description=description,
        event_date=event_date,
        stress_level=stress_level,
        cognitive_load_impact=0.7 if stress_level == 'high' else 0.4 if stress_level == 'medium' else 0.2
    )
    session.add(event)
    session.commit()
    
    return jsonify({
        'id': event.id,
        'title': event.title,
        'stress_level': event.stress_level,
        'event_date': event.event_date.isoformat()
    })

@bp.route('/events', methods=['GET'])
def get_events():
    user_id = request.args.get('user_id', 1)
    session = get_db_session()
    events = session.query(CalendarEvent).filter_by(user_id=user_id).order_by(CalendarEvent.event_date).all()
    
    return jsonify([{
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'event_date': event.event_date.isoformat(),
        'stress_level': event.stress_level,
        'cognitive_load_impact': event.cognitive_load_impact
    } for event in events])