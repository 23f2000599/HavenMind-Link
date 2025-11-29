import os
import random

class AIHelper:
    def __init__(self):
        pass
    
    def analyze_sentiment(self, text):
        # Simple keyword-based sentiment analysis
        negative_words = ['stressed', 'anxious', 'overwhelmed', 'tired', 'sad', 'difficult', 'hard', 'worried']
        positive_words = ['happy', 'good', 'great', 'excited', 'confident', 'relaxed', 'calm', 'peaceful']
        
        text_lower = text.lower()
        negative_count = sum(1 for word in negative_words if word in text_lower)
        positive_count = sum(1 for word in positive_words if word in text_lower)
        
        if negative_count > positive_count:
            return {'sentiment': 'negative', 'score': 0.3, 'stress_level': 'high'}
        elif positive_count > negative_count:
            return {'sentiment': 'positive', 'score': 0.8, 'stress_level': 'low'}
        else:
            return {'sentiment': 'neutral', 'score': 0.5, 'stress_level': 'medium'}
    
    def calculate_cognitive_load(self, events, journal_entries):
        base_load = 0.3
        
        for event in events:
            if event.stress_level == 'high':
                base_load += 0.2
            elif event.stress_level == 'medium':
                base_load += 0.1
        
        negative_entries = sum(1 for entry in journal_entries if entry.sentiment_score and entry.sentiment_score < 0.4)
        base_load += (negative_entries * 0.1)
        
        return min(base_load, 1.0)
    
    def generate_journal_response(self, user_input, sentiment_analysis):
        responses = {
            'negative': [
                "I hear that you're going through a tough time. Remember that difficult feelings are temporary. What's one small thing you could do today to take care of yourself?",
                "It sounds like you're facing some challenges right now. Your feelings are valid, and it's okay to not be okay sometimes. Consider reaching out to someone you trust.",
                "Thank you for sharing these difficult thoughts with me. You're being brave by acknowledging how you feel. What support do you need right now?"
            ],
            'positive': [
                "Thank you for sharing your thoughts. It's wonderful that you're taking time to reflect. Keep nurturing this positive mindset!",
                "I'm glad to hear you're feeling good! It's great that you're journaling and staying connected with your emotions.",
                "Your positive energy comes through in your writing. Remember to celebrate these good moments!"
            ],
            'neutral': [
                "Thank you for taking time to journal today. Regular reflection is a powerful tool for mental wellness.",
                "I appreciate you sharing your thoughts. How are you feeling about your day overall?",
                "Journaling is a great way to process your experiences. What would you like to focus on moving forward?"
            ]
        }
        
        sentiment = sentiment_analysis['sentiment']
        return random.choice(responses.get(sentiment, responses['neutral']))

def suggest_wellness_break(self, cognitive_load_score):
        if cognitive_load_score > 0.8:
            return {
                'activity': 'Deep Breathing Exercise',
                'duration': '5 minutes',
                'description': 'Take 5 deep breaths, focusing on exhaling longer than inhaling.'
            }
        elif cognitive_load_score > 0.6:
            return {
                'activity': 'Short Walk',
                'duration': '10 minutes',
                'description': 'Step outside or walk around your space to reset your mind.'
            }
        else:
            return {
                'activity': 'Gratitude Moment',
                'duration': '2 minutes',
                'description': 'Think of three things you\'re grateful for today.'
            }

ai_helper = AIHelper()