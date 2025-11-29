import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel, pipeline
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import json
import re
from typing import Dict, List, Tuple, Optional

class MLContextAnalyzer:
    def __init__(self):
        """Initialize ML-based context analyzer with pre-trained models"""
        
        # Load pre-trained models
        try:
            # Emotion classification model
            self.emotion_classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Sentence transformer for semantic similarity
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Mental health specific model
            self.mental_health_classifier = pipeline(
                "text-classification",
                model="mental/mental-roberta-base",
                device=0 if torch.cuda.is_available() else -1
            )
            
            print("✅ ML models loaded successfully")
            
        except Exception as e:
            print(f"⚠️ Error loading ML models: {e}")
            # Fallback to basic models
            self.emotion_classifier = None
            self.sentence_model = None
            self.mental_health_classifier = None
        
        # Training data for context understanding
        self.context_examples = {
            'academic_achievement': [
                "I completed all my assignments successfully",
                "Finished my project and feeling accomplished",
                "Got good grades on my exams",
                "Submitted all homework on time",
                "Proud of my academic progress"
            ],
            'academic_stress': [
                "Too many assignments to complete",
                "Overwhelmed with coursework and deadlines",
                "Struggling to keep up with studies",
                "Stressed about upcoming exams",
                "Can't manage my academic workload"
            ],
            'family_separation': [
                "My brother is leaving for another city",
                "Sister going away for work",
                "Family member traveling out of station",
                "Missing my loved ones who are far away",
                "Sad because family is going away"
            ],
            'employment_issues': [
                "Lost my job and feeling devastated",
                "Got laid off from work",
                "Struggling to find employment",
                "Company terminated my position",
                "Unemployed and worried about future"
            ],
            'social_isolation': [
                "Feeling lonely and disconnected",
                "Don't have many friends to talk to",
                "Isolated from social activities",
                "Missing social connections",
                "Feel alone and misunderstood"
            ],
            'financial_stress': [
                "Worried about money and expenses",
                "Can't afford basic necessities",
                "Financial problems causing anxiety",
                "Struggling with budget constraints",
                "Economic pressure affecting wellbeing"
            ]
        }
        
        # Encode context examples for similarity matching
        self._encode_context_examples()
        
        # Therapeutic response templates (learned patterns)
        self.response_patterns = {
            'validation': [
                "Your feelings are completely valid and understandable",
                "It's natural to feel this way given your situation",
                "What you're experiencing is a normal human response"
            ],
            'normalization': [
                "Many people face similar challenges",
                "You're not alone in feeling this way",
                "This is a common experience for students/people"
            ],
            'empowerment': [
                "You have the strength to get through this",
                "This situation is temporary and manageable",
                "You've overcome challenges before"
            ],
            'guidance': [
                "What small step could you take today?",
                "How might you approach this differently?",
                "What support do you need right now?"
            ]
        }
    
    def _encode_context_examples(self):
        """Encode context examples using sentence transformers"""
        if not self.sentence_model:
            return
            
        self.context_embeddings = {}
        for context, examples in self.context_examples.items():
            embeddings = self.sentence_model.encode(examples)
            self.context_embeddings[context] = embeddings
    
    def analyze_context_ml(self, text: str) -> Dict:
        """Analyze context using machine learning models"""
        
        results = {
            'primary_context': 'general',
            'confidence': 0.0,
            'emotions': {},
            'mental_health_indicators': {},
            'semantic_similarity': {},
            'ml_confidence': 0.0
        }
        
        try:
            # 1. Emotion Analysis using transformer model
            if self.emotion_classifier:
                emotions = self.emotion_classifier(text)
                results['emotions'] = {
                    'primary_emotion': emotions[0]['label'],
                    'confidence': emotions[0]['score'],
                    'all_emotions': emotions
                }
            
            # 2. Mental Health Classification
            if self.mental_health_classifier:
                mental_health = self.mental_health_classifier(text)
                results['mental_health_indicators'] = {
                    'classification': mental_health[0]['label'],
                    'confidence': mental_health[0]['score']
                }
            
            # 3. Semantic Similarity Analysis
            if self.sentence_model and hasattr(self, 'context_embeddings'):
                text_embedding = self.sentence_model.encode([text])
                
                similarities = {}
                for context, embeddings in self.context_embeddings.items():
                    # Calculate similarity with all examples in this context
                    sims = cosine_similarity(text_embedding, embeddings)[0]
                    similarities[context] = np.max(sims)  # Take best match
                
                # Find best matching context
                best_context = max(similarities, key=similarities.get)
                best_score = similarities[best_context]
                
                results['semantic_similarity'] = similarities
                results['primary_context'] = best_context
                results['confidence'] = best_score
                results['ml_confidence'] = best_score
            
            # 4. Combine multiple signals for final decision
            final_context, final_confidence = self._combine_ml_signals(results, text)
            results['primary_context'] = final_context
            results['confidence'] = final_confidence
            
        except Exception as e:
            print(f"ML analysis error: {e}")
            results['error'] = str(e)
        
        return results
    
    def _combine_ml_signals(self, results: Dict, text: str) -> Tuple[str, float]:
        """Combine multiple ML signals for final context decision"""
        
        # Weight different signals
        semantic_weight = 0.5
        emotion_weight = 0.3
        mental_health_weight = 0.2
        
        final_score = 0.0
        final_context = results.get('primary_context', 'general')
        
        # Semantic similarity score
        if 'semantic_similarity' in results:
            semantic_score = results['confidence']
            final_score += semantic_score * semantic_weight
        
        # Emotion-based context adjustment
        if 'emotions' in results and results['emotions']:
            emotion = results['emotions'].get('primary_emotion', '').lower()
            emotion_conf = results['emotions'].get('confidence', 0.0)
            
            # Map emotions to contexts
            emotion_context_map = {
                'joy': 'academic_achievement',
                'sadness': 'family_separation',
                'fear': 'academic_stress',
                'anger': 'employment_issues',
                'surprise': 'general'
            }
            
            if emotion in emotion_context_map:
                emotion_context = emotion_context_map[emotion]
                # Boost score if emotion aligns with semantic context
                if emotion_context == final_context:
                    final_score += emotion_conf * emotion_weight
        
        # Mental health indicator boost
        if 'mental_health_indicators' in results:
            mh_conf = results['mental_health_indicators'].get('confidence', 0.0)
            final_score += mh_conf * mental_health_weight
        
        return final_context, min(final_score, 1.0)
    
    def generate_ml_response(self, text: str, context_analysis: Dict) -> str:
        """Generate response using ML-learned patterns"""
        
        context = context_analysis.get('primary_context', 'general')
        confidence = context_analysis.get('confidence', 0.0)
        emotions = context_analysis.get('emotions', {})
        
        # Only use ML response if confidence is high enough
        if confidence < 0.3:
            return self._generate_general_response(text, emotions)
        
        # Generate context-specific response using learned patterns
        response_parts = []
        
        # 1. Validation based on detected emotion
        primary_emotion = emotions.get('primary_emotion', '').lower()
        if primary_emotion in ['sadness', 'fear', 'anger']:
            response_parts.append(np.random.choice(self.response_patterns['validation']))
        
        # 2. Context-specific acknowledgment
        context_responses = {
            'academic_achievement': [
                "It's wonderful that you've completed your assignments! That sense of accomplishment is well-deserved.",
                "Congratulations on finishing your work! Your dedication and effort are really paying off."
            ],
            'academic_stress': [
                "I can sense you're feeling overwhelmed with your academic workload right now.",
                "Academic pressure can be really intense, and your feelings are completely understandable."
            ],
            'family_separation': [
                "It sounds like you're missing someone important to you who's going away.",
                "Family separations can be really difficult, even when they're temporary."
            ],
            'employment_issues': [
                "Losing employment is one of life's most stressful experiences.",
                "Job-related stress can affect every aspect of your wellbeing."
            ],
            'social_isolation': [
                "Feeling disconnected from others can be really painful.",
                "Loneliness is a difficult emotion that many people struggle with."
            ],
            'financial_stress': [
                "Financial worries can create significant anxiety and stress.",
                "Money concerns affect so many aspects of daily life."
            ]
        }
        
        if context in context_responses:
            response_parts.append(np.random.choice(context_responses[context]))
        
        # 3. Normalization
        response_parts.append(np.random.choice(self.response_patterns['normalization']))
        
        # 4. Guidance question
        response_parts.append(np.random.choice(self.response_patterns['guidance']))
        
        return ' '.join(response_parts)
    
    def _generate_general_response(self, text: str, emotions: Dict) -> str:
        """Generate general response when context is unclear"""
        
        primary_emotion = emotions.get('primary_emotion', '').lower() if emotions else ''
        
        if primary_emotion in ['sadness', 'fear', 'anger']:
            return "I can sense you're going through something difficult right now. Your feelings are valid, and it's important to acknowledge them. What kind of support would be most helpful for you today?"
        elif primary_emotion in ['joy', 'surprise']:
            return "I can hear positive energy in your words! It's great that you're taking time to reflect on your experiences. How are you feeling about everything right now?"
        else:
            return "Thank you for sharing your thoughts with me. Regular reflection is valuable for understanding yourself better. What's on your mind today?"
    
    def learn_from_interaction(self, text: str, context: str, user_feedback: Optional[str] = None):
        """Learn from user interactions to improve context detection"""
        
        # This would implement online learning to improve the model
        # For now, we can store interactions for future training
        
        interaction_data = {
            'text': text,
            'predicted_context': context,
            'user_feedback': user_feedback,
            'timestamp': str(np.datetime64('now'))
        }
        
        # In a real implementation, this would update model weights
        # or add to training data for periodic retraining
        
        return interaction_data

# Global instance
ml_analyzer = MLContextAnalyzer()