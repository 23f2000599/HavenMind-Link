def analyze_sentiment_simple(content):
    """Simple sentiment analysis without external APIs"""
    content_lower = content.lower()
    
    # Crisis detection - highest priority
    crisis_words = ['die', 'diee', 'dieee', 'kill myself', 'end it', 'suicide', 'hurt myself', 'no point', 'give up', 'cant go on', 'want to die', 'wanna die', 'end my life']
    crisis_patterns = ['go die', 'imma die', 'gonna die', 'wanna die', 'so imma go die']
    
    has_crisis = any(word in content_lower for word in crisis_words)
    if not has_crisis:
        has_crisis = any(pattern in content_lower for pattern in crisis_patterns)
    
    if has_crisis:
        return 0.05, 'crisis'
    
    # Negative words
    negative_words = ['stressed', 'anxious', 'overwhelmed', 'tired', 'sad', 'depressed', 'worried', 'frustrated', 'angry', 'lonely', 'hopeless', 'exhausted', 'scared', 'afraid', 'upset', 'miss', 'dont care', "don't care", 'whatever', 'ded', 'dead', 'drained', 'burnt out', 'burnout', 'struggling', 'rough', 'tough', 'hard', 'due', 'deadline', 'not started', 'have to learn', 'so much work', "don't know", 'stuck', 'suffocating', 'piling up', 'screaming', 'blowing up', 'magically', 'zero progress']
    
    # Positive words
    positive_words = ['happy', 'good', 'great', 'excited', 'confident', 'grateful', 'peaceful', 'motivated', 'accomplished', 'loved', 'optimistic', 'energized', 'yay', 'groove', 'getting into', 'finally', 'progress', 'better', 'improving', 'finished', 'completed', 'done']
    
    negative_count = sum(1 for word in negative_words if word in content_lower)
    positive_count = sum(1 for word in positive_words if word in content_lower)
    
    # Check for specific academic stress patterns
    academic_stress_patterns = ['project due', 'due on', 'haven\'t even touched', 'know nothing about', 'learn from scratch', 'dad issues', 'deadlines', 'can\'t think straight']
    academic_stress = sum(1 for pattern in academic_stress_patterns if pattern in content_lower)
    
    if academic_stress >= 2 or negative_count > positive_count + 2:
        return 0.2, 'negative'
    elif negative_count > positive_count:
        return 0.3, 'negative'
    elif positive_count > negative_count:
        return 0.8, 'positive'
    else:
        return 0.5, 'neutral'

def generate_contextual_response(content, emotion_tags, sentiment_score):
    """Generate contextual response based on content analysis"""
    content_lower = content.lower()
    
    # Crisis response
    if emotion_tags == 'crisis':
        return """I'm very concerned about what you've shared. Your life has value and meaning, even when things feel overwhelming. Please reach out for immediate support:

CRISIS RESOURCES (INDIA):
- AASRA Suicide Prevention: 91-9820466726
- Vandrevala Foundation: 1860-2662-345
- iCall Helpline: 022-25521111
- Sneha India: 044-24640050
- Emergency: 112 or 100

You don't have to face this alone. There are people who want to help you through this difficult time. Please consider reaching out to a counselor, trusted friend, or family member right now."""
    
    # Academic overwhelm with multiple deadlines
    if any(phrase in content_lower for phrase in ['project due', 'due on', 'deadlines', 'haven\'t even touched', 'know nothing about', 'learn from scratch']):
        return """I can hear the overwhelming stress in your words about these multiple project deadlines. Having projects due so close together, especially when you need to learn new technologies like Flask and Vue from scratch, feels incredibly daunting. It's completely understandable to feel lost and stuck when facing unfamiliar tech with tight deadlines.

Let's break this down into manageable steps:
1. Focus on the Nov 27th project first - what's the minimum viable version you can create?
2. For Flask and Vue, start with basic tutorials - you don't need to master everything, just enough to build your project
3. Consider reaching out to classmates, professors, or online communities for help

Remember: You don't have to be perfect. A working basic project is better than a perfect unfinished one. What's one small step you could take right now to get started?"""
    
    # Exhaustion with some progress
    elif any(word in content_lower for word in ['ded', 'dead', 'exhausted', 'drained']) and any(word in content_lower for word in ['groove', 'getting into', 'finally', 'progress']):
        return """I can hear that you're feeling really drained and exhausted right now, but it sounds like you're also starting to find your rhythm and make some progress. That's actually a really positive sign - even when we feel physically and emotionally depleted, recognizing that we're getting into a groove shows resilience. It's okay to feel tired while still moving forward. How can you take care of yourself while maintaining this momentum?"""
    
    # Pure exhaustion
    elif any(word in content_lower for word in ['ded', 'dead', 'exhausted', 'drained', 'burnt out']):
        return """It sounds like you're feeling really exhausted and drained right now. When we say we feel 'dead' or completely worn out, it usually means we've been pushing ourselves pretty hard. Your body and mind are telling you they need some care and rest. What's been taking so much out of you lately? And what's one small thing you could do today to recharge, even just a little?"""
    
    # Family issues combined with academic stress
    elif 'dad issues' in content_lower or ('family' in content_lower and any(word in content_lower for word in ['issues', 'problems', 'stress'])):
        return """It sounds like you're dealing with family stress on top of your academic pressures. Having personal and academic challenges happening at the same time can feel incredibly overwhelming. It's important to acknowledge that you're handling multiple difficult situations right now. Have you been able to talk to anyone about what you're going through? Sometimes just having someone listen can help lighten the load."""
    
    # General academic stress
    elif any(word in content_lower for word in ['project', 'deadline', 'assignment', 'study', 'exam']):
        return """Academic pressure can be intense, and it sounds like you're feeling the weight of your coursework right now. It's important to remember that feeling overwhelmed doesn't mean you can't handle it - it just means you're human. Breaking things down into smaller, manageable pieces can help. What's the most pressing thing you need to address first?"""
    
    # Positive responses
    elif emotion_tags == 'positive':
        return """I love seeing your positive energy come through in your reflection! These good moments are precious and worth celebrating. How might you carry this positive energy forward?"""
    
    # General negative support
    elif emotion_tags == 'negative':
        return """I can sense you're going through something challenging right now. Your feelings are important and valid. It takes courage to express what you're experiencing. What kind of support would be most helpful for you today?"""
    
    # Neutral/default
    else:
        return """Thank you for sharing your thoughts with me. Taking time to reflect like this shows real self-awareness. What's been on your mind lately that you'd like to explore further?"""