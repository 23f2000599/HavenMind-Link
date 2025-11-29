import re
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import Dict, List, Tuple

class NLPContextAnalyzer:
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
        
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize
        
        self.stop_words = set(stopwords.words('english'))
        self.tokenize = word_tokenize
        
        # Context templates for semantic matching
        self.context_templates = {
            'job_loss': [
                "lost my job and feeling worried about future",
                "got laid off from work and stressed about money",
                "unemployed and anxious about finding new employment",
                "fired from company and concerned about career",
                "job termination causing financial stress"
            ],
            'company_placement_loss': [
                "lost company placement for internship program",
                "company withdrew internship offer before semester",
                "placement cancelled and worried about graduation requirements",
                "internship company closed and need alternative",
                "lost corporate training opportunity"
            ],
            'academic_stress': [
                "semester started with heavy course workload",
                "too many assignments and feeling overwhelmed",
                "academic pressure from multiple classes",
                "struggling with coursework and deadlines",
                "university studies causing stress"
            ],
            'financial_stress': [
                "worried about money and paying expenses",
                "financial difficulties affecting daily life",
                "struggling to afford basic necessities",
                "economic pressure and budget concerns",
                "money problems causing anxiety"
            ],
            'career_anxiety': [
                "uncertain about future career prospects",
                "worried about professional development",
                "anxious about job market and opportunities",
                "concerned about career path decisions",
                "future employment prospects causing stress"
            ]
        }
        
        # Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 3),
            max_features=1000
        )
        
        # Prepare training data
        all_templates = []
        self.template_labels = []
        
        for context, templates in self.context_templates.items():
            all_templates.extend(templates)
            self.template_labels.extend([context] * len(templates))
        
        # Fit vectorizer on templates
        self.template_vectors = self.vectorizer.fit_transform(all_templates)
    
    def analyze_context(self, text: str) -> Dict:
        """Analyze text context using NLP and semantic similarity"""
        
        # Preprocess text
        cleaned_text = self._preprocess_text(text)
        
        # Extract key entities and emotions
        entities = self._extract_entities(cleaned_text)
        emotions = self._extract_emotions(cleaned_text)
        
        # Find semantic context using similarity
        context_scores = self._calculate_context_similarity(cleaned_text)
        
        # Determine primary context
        primary_context = max(context_scores.items(), key=lambda x: x[1])
        
        # Extract specific concerns
        concerns = self._extract_concerns(cleaned_text, entities)
        
        return {
            'primary_context': primary_context[0],
            'confidence': primary_context[1],
            'context_scores': context_scores,
            'entities': entities,
            'emotions': emotions,
            'concerns': concerns,
            'severity': self._assess_severity(emotions, concerns)
        }
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Handle contractions
        contractions = {
            "i'm": "i am", "don't": "do not", "can't": "cannot",
            "won't": "will not", "shouldn't": "should not"
        }
        
        for contraction, expansion in contractions.items():
            text = text.replace(contraction, expansion)
        
        return text
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract relevant entities from text"""
        entities = {
            'work_related': [],
            'academic_related': [],
            'emotional_states': [],
            'time_references': []
        }
        
        # Work-related entities
        work_patterns = [
            r'\b(job|work|employment|company|office|boss|colleague|salary|income)\b',
            r'\b(laid off|fired|terminated|unemployed|jobless)\b',
            r'\b(internship|placement|training|corporate|business)\b'
        ]
        
        for pattern in work_patterns:
            matches = re.findall(pattern, text)
            entities['work_related'].extend(matches)
        
        # Academic entities
        academic_patterns = [
            r'\b(semester|course|class|assignment|exam|study|university|college)\b',
            r'\b(professor|teacher|grade|deadline|project|homework)\b'
        ]
        
        for pattern in academic_patterns:
            matches = re.findall(pattern, text)
            entities['academic_related'].extend(matches)
        
        # Emotional states
        emotion_patterns = [
            r'\b(sad|worried|anxious|stressed|overwhelmed|scared|depressed)\b',
            r'\b(happy|excited|confident|grateful|proud|motivated)\b'
        ]
        
        for pattern in emotion_patterns:
            matches = re.findall(pattern, text)
            entities['emotional_states'].extend(matches)
        
        # Time references
        time_patterns = [
            r'\b(today|tomorrow|yesterday|week|month|semester|year)\b',
            r'\b(before|after|during|until|since)\b'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, text)
            entities['time_references'].extend(matches)
        
        return entities
    
    def _extract_emotions(self, text: str) -> Dict[str, float]:
        """Extract and score emotional content"""
        emotion_lexicon = {
            'sadness': ['sad', 'depressed', 'down', 'miserable', 'heartbroken', 'devastated'],
            'anxiety': ['anxious', 'worried', 'nervous', 'scared', 'afraid', 'panicked'],
            'stress': ['stressed', 'overwhelmed', 'pressure', 'burden', 'exhausted'],
            'anger': ['angry', 'frustrated', 'annoyed', 'furious', 'irritated'],
            'fear': ['scared', 'afraid', 'terrified', 'frightened', 'worried'],
            'hope': ['hopeful', 'optimistic', 'confident', 'positive', 'encouraged'],
            'joy': ['happy', 'excited', 'joyful', 'pleased', 'delighted']
        }
        
        emotion_scores = {}
        words = text.split()
        
        for emotion, keywords in emotion_lexicon.items():
            score = sum(1 for word in words if word in keywords)
            emotion_scores[emotion] = score / len(words) if words else 0
        
        return emotion_scores
    
    def _calculate_context_similarity(self, text: str) -> Dict[str, float]:
        """Calculate semantic similarity with context templates"""
        
        # Transform input text
        text_vector = self.vectorizer.transform([text])
        
        # Calculate similarities
        similarities = cosine_similarity(text_vector, self.template_vectors)[0]
        
        # Aggregate scores by context
        context_scores = {}
        for i, label in enumerate(self.template_labels):
            if label not in context_scores:
                context_scores[label] = []
            context_scores[label].append(similarities[i])
        
        # Take maximum similarity for each context
        for context in context_scores:
            context_scores[context] = max(context_scores[context])
        
        return context_scores
    
    def _extract_concerns(self, text: str, entities: Dict) -> List[str]:
        """Extract specific concerns from text"""
        concerns = []
        
        # Financial concerns
        if any(word in text for word in ['money', 'financial', 'afford', 'pay', 'cost', 'expensive']):
            concerns.append('financial_security')
        
        # Career concerns
        if any(word in text for word in ['future', 'career', 'job', 'employment', 'work']):
            concerns.append('career_prospects')
        
        # Academic concerns
        if any(word in text for word in ['semester', 'grade', 'exam', 'assignment', 'study']):
            concerns.append('academic_performance')
        
        # Time pressure
        if any(word in text for word in ['deadline', 'time', 'months', 'weeks', 'before']):
            concerns.append('time_pressure')
        
        # Social concerns
        if any(word in text for word in ['alone', 'lonely', 'isolated', 'friends', 'family']):
            concerns.append('social_support')
        
        return concerns
    
    def _assess_severity(self, emotions: Dict, concerns: List) -> str:
        """Assess severity level based on emotions and concerns"""
        
        # High severity indicators
        high_severity_emotions = ['sadness', 'anxiety', 'stress']
        high_severity_score = sum(emotions.get(emotion, 0) for emotion in high_severity_emotions)
        
        # Crisis indicators
        crisis_concerns = ['financial_security', 'career_prospects']
        crisis_score = len([c for c in concerns if c in crisis_concerns])
        
        if high_severity_score > 0.3 or crisis_score >= 2:
            return 'high'
        elif high_severity_score > 0.1 or crisis_score >= 1:
            return 'medium'
        else:
            return 'low'
    
    def generate_therapeutic_response(self, analysis: Dict, text: str) -> str:
        """Generate contextual therapeutic response based on NLP analysis"""
        
        context = analysis['primary_context']
        confidence = analysis['confidence']
        emotions = analysis['emotions']
        concerns = analysis['concerns']
        severity = analysis['severity']
        
        # Base response templates
        response_templates = {
            'job_loss': {
                'validation': "I'm so sorry to hear about your job loss. Losing employment is one of life's most stressful experiences.",
                'normalization': "It's completely understandable that you're feeling {emotions}.",
                'guidance': "Remember that this setback doesn't define your worth or future potential.",
                'question': "What support systems do you have available right now?"
            },
            'company_placement_loss': {
                'validation': "Losing your company placement is incredibly stressful, especially with academic pressures.",
                'normalization': "Your feelings are completely valid - this kind of uncertainty is genuinely difficult.",
                'guidance': "Many students face similar challenges, and there are often alternative paths forward.",
                'question': "Have you been able to speak with your academic advisor about options?"
            },
            'academic_stress': {
                'validation': "Academic pressure can feel overwhelming, especially at the start of a semester.",
                'normalization': "It's completely normal to feel this way when facing a heavy workload.",
                'guidance': "Remember, you don't have to tackle everything at once.",
                'question': "What's one task you could focus on first to feel more in control?"
            },
            'financial_stress': {
                'validation': "Financial concerns can be incredibly overwhelming and stressful.",
                'normalization': "Worrying about money is one of the most common sources of anxiety.",
                'guidance': "There are often resources and support systems available to help.",
                'question': "Have you looked into financial aid or support services?"
            },
            'career_anxiety': {
                'validation': "Uncertainty about your future career can feel really overwhelming.",
                'normalization': "Many people experience anxiety about their professional path.",
                'guidance': "Career paths are rarely linear, and there are many opportunities ahead.",
                'question': "What aspects of your future feel most concerning right now?"
            }
        }
        
        # Get template or use default
        template = response_templates.get(context, {
            'validation': "I hear that you're going through a challenging time.",
            'normalization': "Your feelings are completely valid.",
            'guidance': "Remember that difficult emotions are temporary.",
            'question': "What would help you feel a little better today?"
        })
        
        # Extract dominant emotions for personalization
        dominant_emotions = [emotion for emotion, score in emotions.items() if score > 0.1]
        emotion_text = ', '.join(dominant_emotions) if dominant_emotions else 'this way'
        
        # Build response
        response_parts = [
            template['validation'],
            template['normalization'].format(emotions=emotion_text),
            template['guidance'],
            template['question']
        ]
        
        return ' '.join(response_parts)

# Global instance
nlp_analyzer = NLPContextAnalyzer()