import os
import google.generativeai as genai
from datetime import datetime
import json
import re
from typing import Dict, List, Optional

class GeminiTherapeuticAI:
    def __init__(self):
        # Configure Gemini AI
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            # For demo purposes, you'll need to set this environment variable
            print("Warning: GEMINI_API_KEY not found. Please set your API key.")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        
        # Therapeutic response framework
        self.therapeutic_context = """
        You are a compassionate AI mental health companion for college students. Your role is to:
        
        1. Provide empathetic, non-judgmental responses
        2. Validate emotions and experiences
        3. Offer gentle guidance and coping strategies
        4. Recognize signs of distress and suggest appropriate support
        5. Use therapeutic techniques like cognitive reframing, mindfulness, and emotional regulation
        6. Be culturally sensitive and age-appropriate for college students
        7. Never diagnose or replace professional therapy
        
        Response Guidelines:
        - Keep responses between 2-4 sentences
        - Use warm, supportive language
        - Acknowledge specific emotions mentioned
        - Offer practical, actionable suggestions when appropriate
        - Include gentle questions to encourage reflection
        - Reference student-specific challenges (academics, social life, independence)
        """
    
    def analyze_sentiment_advanced(self, text: str) -> Dict:
        """Advanced sentiment analysis using Gemini AI"""
        if not self.model:
            return self._fallback_sentiment_analysis(text)
        
        prompt = f"""
        Analyze the emotional content of this journal entry from a college student. 
        Provide a JSON response with:
        - sentiment: "positive", "negative", "neutral", "mixed"
        - emotions: list of specific emotions detected (max 3)
        - stress_level: "low", "medium", "high", "crisis"
        - concerns: list of specific concerns or challenges mentioned
        - strengths: positive aspects or coping mechanisms mentioned
        
        Journal entry: "{text}"
        
        Respond only with valid JSON.
        """
        
        try:
            response = self.model.generate_content(prompt)
            analysis = json.loads(response.text)
            
            # Add numerical score for compatibility
            score_map = {"positive": 0.8, "mixed": 0.5, "neutral": 0.5, "negative": 0.2}
            analysis['score'] = score_map.get(analysis.get('sentiment', 'neutral'), 0.5)
            
            return analysis
        except Exception as e:
            print(f"Gemini analysis error: {e}")
            return self._fallback_sentiment_analysis(text)
    
    def generate_therapeutic_response(self, user_input: str, sentiment_analysis: Dict, user_context: Optional[Dict] = None) -> str:
        """Generate personalized therapeutic response using Gemini AI"""
        if not self.model:
            return self._fallback_therapeutic_response(user_input, sentiment_analysis)
        
        # Build context-aware prompt
        context_info = ""
        if user_context:
            context_info = f"""
            Additional context about the student:
            - Previous entries mood trend: {user_context.get('mood_trend', 'unknown')}
            - Recent stress level: {user_context.get('recent_stress', 'unknown')}
            - Writing frequency: {user_context.get('writing_frequency', 'unknown')}
            """
        
        prompt = f"""
        {self.therapeutic_context}
        
        {context_info}
        
        Current journal entry analysis:
        - Sentiment: {sentiment_analysis.get('sentiment', 'neutral')}
        - Emotions detected: {', '.join(sentiment_analysis.get('emotions', []))}
        - Stress level: {sentiment_analysis.get('stress_level', 'medium')}
        - Concerns: {', '.join(sentiment_analysis.get('concerns', []))}
        - Strengths: {', '.join(sentiment_analysis.get('strengths', []))}
        
        Student's journal entry: "{user_input}"
        
        Provide a therapeutic response that:
        1. Acknowledges their specific experience and emotions
        2. Validates their feelings
        3. Offers gentle support or coping strategy if appropriate
        4. Includes a thoughtful question or reflection prompt
        
        Keep the response warm, personal, and between 2-4 sentences.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini response error: {e}")
            return self._fallback_therapeutic_response(user_input, sentiment_analysis)
    
    def generate_personalized_prompts(self, user_context: Dict) -> List[str]:
        """Generate personalized journal prompts based on user's history"""
        if not self.model:
            return self._fallback_prompts()
        
        prompt = f"""
        Generate 5 personalized journal prompts for a college student based on their recent patterns:
        
        Context:
        - Recent mood trend: {user_context.get('mood_trend', 'neutral')}
        - Common emotions: {', '.join(user_context.get('common_emotions', []))}
        - Stress level: {user_context.get('stress_level', 'medium')}
        - Areas of concern: {', '.join(user_context.get('concerns', []))}
        
        Create prompts that:
        1. Encourage self-reflection
        2. Address their specific emotional patterns
        3. Promote growth and coping
        4. Are relevant to college life
        5. Vary in depth and focus
        
        Return as a JSON array of strings.
        """
        
        try:
            response = self.model.generate_content(prompt)
            prompts = json.loads(response.text)
            return prompts if isinstance(prompts, list) else self._fallback_prompts()
        except Exception as e:
            print(f"Gemini prompts error: {e}")
            return self._fallback_prompts()
    
    def assess_crisis_risk(self, text: str, sentiment_analysis: Dict) -> Dict:
        """Assess if the journal entry indicates crisis-level concerns"""
        if not self.model:
            return self._fallback_crisis_assessment(text, sentiment_analysis)
        
        prompt = f"""
        Assess this journal entry for mental health crisis indicators. Look for:
        - Suicidal ideation or self-harm mentions
        - Severe hopelessness or despair
        - Substance abuse concerns
        - Extreme isolation or withdrawal
        - Academic/life crisis situations
        
        Journal entry: "{text}"
        Detected stress level: {sentiment_analysis.get('stress_level', 'medium')}
        
        Respond with JSON:
        {
            "crisis_level": "none|low|medium|high|immediate",
            "risk_factors": ["list of specific concerns"],
            "recommended_action": "description of suggested response",
            "urgent": true/false
        }
        """
        
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            print(f"Crisis assessment error: {e}")
            return self._fallback_crisis_assessment(text, sentiment_analysis)
    
    def _fallback_sentiment_analysis(self, text: str) -> Dict:
        """Fallback sentiment analysis when Gemini is unavailable"""
        negative_words = ['stressed', 'anxious', 'overwhelmed', 'tired', 'sad', 'difficult', 'hard', 'worried', 'scared', 'late', 'afraid']
        positive_words = ['happy', 'good', 'great', 'excited', 'confident', 'relaxed', 'calm', 'peaceful', 'grateful', 'proud']
        
        text_lower = text.lower()
        negative_count = sum(1 for word in negative_words if word in text_lower)
        positive_count = sum(1 for word in positive_words if word in text_lower)
        
        if negative_count > positive_count:
            sentiment = 'negative'
            score = 0.3
            stress_level = 'high' if negative_count > 2 else 'medium'
        elif positive_count > negative_count:
            sentiment = 'positive'
            score = 0.8
            stress_level = 'low'
        else:
            sentiment = 'neutral'
            score = 0.5
            stress_level = 'medium'
        
        return {
            'sentiment': sentiment,
            'score': score,
            'stress_level': stress_level,
            'emotions': [sentiment],
            'concerns': [],
            'strengths': []
        }
    
    def _fallback_therapeutic_response(self, user_input: str, sentiment_analysis: Dict) -> str:
        """Fallback therapeutic responses when Gemini is unavailable"""
        sentiment = sentiment_analysis.get('sentiment', 'neutral')
        stress_level = sentiment_analysis.get('stress_level', 'medium')
        
        # More therapeutic responses based on the example
        if sentiment == 'negative' and 'late' in user_input.lower() and 'college' in user_input.lower():
            return "Starting college can feel overwhelming, and being late on your first day is understandably stressful. Remember that many students face similar anxieties - you're not alone in this experience. These initial worries often feel bigger than they actually are. How can you prepare yourself to feel more confident tomorrow?"
        
        responses = {
            'negative': {
                'high': [
                    "I can sense you're going through a really challenging time right now. Your feelings are completely valid, and it takes courage to express them. What's one small thing that might bring you a moment of comfort today?",
                    "It sounds like you're carrying a heavy emotional load. Please know that difficult periods don't last forever, even when they feel overwhelming. Have you been able to reach out to anyone for support?",
                    "I hear the pain in your words, and I want you to know that your struggles matter. Sometimes when we're in distress, it helps to focus on just getting through today. What's one thing you can do to take care of yourself right now?"
                ],
                'medium': [
                    "I notice you're dealing with some difficult feelings. It's important to acknowledge these emotions rather than push them away. What do you think might help you process what you're experiencing?",
                    "Thank you for sharing these challenging thoughts with me. Even in difficult moments, there's strength in your willingness to reflect and write. How are you taking care of yourself during this time?"
                ]
            },
            'positive': [
                "It's wonderful to hear the positivity in your reflection! These moments of joy and contentment are so important to acknowledge and celebrate. What do you think contributed most to feeling this way today?",
                "Your positive energy really comes through in your writing. It's beautiful when we can recognize and appreciate the good moments in our lives. How might you carry this feeling forward?"
            ],
            'neutral': [
                "Thank you for taking time to reflect today. Sometimes the most ordinary moments hold important insights about our inner world. What stood out to you most as you wrote this?",
                "I appreciate you sharing your thoughts, even when they feel routine or unclear. Regular reflection like this is a powerful tool for understanding yourself better. What would you like to explore more deeply?"
            ]
        }
        
        if sentiment == 'negative':
            return responses['negative'][stress_level][0] if responses['negative'].get(stress_level) else responses['negative']['medium'][0]
        else:
            return responses.get(sentiment, responses['neutral'])[0]
    
    def _fallback_prompts(self) -> List[str]:
        """Fallback journal prompts"""
        return [
            "What's one thing that challenged you today, and how did you handle it?",
            "Describe a moment today when you felt most like yourself.",
            "What are you grateful for right now, and why does it matter to you?",
            "If you could give advice to yourself from a week ago, what would you say?",
            "What's something you're looking forward to, and how does that make you feel?"
        ]
    
    def _fallback_crisis_assessment(self, text: str, sentiment_analysis: Dict) -> Dict:
        """Fallback crisis assessment"""
        crisis_keywords = ['suicide', 'kill myself', 'end it all', 'no point', 'give up', 'can\'t go on']
        text_lower = text.lower()
        
        has_crisis_indicators = any(keyword in text_lower for keyword in crisis_keywords)
        stress_level = sentiment_analysis.get('stress_level', 'medium')
        
        if has_crisis_indicators or stress_level == 'high':
            return {
                'crisis_level': 'high' if has_crisis_indicators else 'medium',
                'risk_factors': ['Concerning language detected'] if has_crisis_indicators else ['High stress level'],
                'recommended_action': 'Suggest professional support resources',
                'urgent': has_crisis_indicators
            }
        
        return {
            'crisis_level': 'none',
            'risk_factors': [],
            'recommended_action': 'Continue monitoring',
            'urgent': False
        }

# Global instance
gemini_ai = GeminiTherapeuticAI()