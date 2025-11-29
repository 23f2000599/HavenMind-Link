# HavenMind - Gemini AI Integration

## 🤖 Enhanced Therapeutic AI Responses

This update integrates Google's Gemini AI to provide more personalized, therapeutic responses in the journal section, replacing generic responses with context-aware, empathetic interactions.

## ✨ New Features

### 🧠 Advanced Sentiment Analysis
- **Multi-dimensional emotion detection** - Identifies specific emotions beyond just positive/negative
- **Stress level assessment** - Evaluates low/medium/high/crisis stress levels
- **Context awareness** - Considers user's journaling history and patterns

### 💬 Therapeutic Responses
- **Personalized responses** - Tailored to individual student experiences
- **Validation and empathy** - Acknowledges specific emotions and situations
- **Practical guidance** - Offers actionable coping strategies
- **Crisis detection** - Identifies concerning content and provides resources

### 📝 Smart Prompts
- **Adaptive prompts** - Generated based on recent mood patterns
- **Student-focused** - Addresses college-specific challenges
- **Growth-oriented** - Encourages reflection and personal development

## 🚀 Quick Setup

### 1. Run the Setup Script
```bash
python setup_gemini.py
```

### 2. Get Your Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key

### 3. Configure Environment
Edit `havenmind-basic/.env`:
```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 4. Start the Application
```bash
cd havenmind-basic
python app.py
```

## 📋 Manual Setup (Alternative)

### Install Dependencies
```bash
# For basic app
cd havenmind-basic
pip install -r requirements.txt

# For backend (if using)
cd ../havenmind-backend
pip install -r requirements.txt
```

### Environment Configuration
Create/edit `havenmind-basic/.env`:
```env
# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=havenmind-secret-2024

# Database Configuration
DATABASE_URL=sqlite:///havenmind.db
```

## 🔄 Before vs After Comparison

### ❌ Before (Generic Response)
**Student Input:** "Its my first day of college and i already came slightly late which is making me scared cause my id card could get taken away"

**Old AI Response:** "Thank you for taking time to journal today. Regular reflection, even about ordinary moments, is a valuable practice for mental wellness."

### ✅ After (Therapeutic Response)
**Student Input:** "Its my first day of college and i already came slightly late which is making me scared cause my id card could get taken away"

**New AI Response:** "Starting college can feel overwhelming, and being late on your first day is understandably stressful. Remember that many students face similar anxieties - you're not alone in this experience. These initial worries often feel bigger than they actually are. How can you prepare yourself to feel more confident tomorrow?"

## 🛠️ Technical Implementation

### Architecture
```
havenmind-basic/
├── app.py                 # Main Flask app with Gemini integration
├── .env                   # Environment variables
├── requirements.txt       # Dependencies
└── templates/
    └── journal.html       # Enhanced journal interface

havenmind-backend/
├── app/
│   └── utils/
│       └── gemini_ai_helper.py  # Gemini AI integration
└── requirements.txt       # Backend dependencies
```

### Key Components

#### 1. GeminiTherapeuticAI Class
- **Sentiment Analysis**: Advanced emotion detection using Gemini Pro
- **Therapeutic Responses**: Context-aware, empathetic responses
- **Crisis Assessment**: Identifies concerning content
- **Personalized Prompts**: Adaptive writing suggestions

#### 2. Fallback System
- Graceful degradation when Gemini API is unavailable
- Enhanced basic responses for common scenarios
- Maintains functionality without API key

#### 3. User Context Integration
- Analyzes recent journaling patterns
- Considers mood trends and stress levels
- Personalizes responses based on history

## 🔒 Privacy & Security

- **No data storage**: Journal entries are not sent to external servers for training
- **API-only usage**: Gemini processes content in real-time without retention
- **Local database**: All user data remains in local SQLite database
- **Secure configuration**: API keys stored in environment variables

## 🎯 Therapeutic Approach

### Evidence-Based Techniques
- **Cognitive Behavioral Therapy (CBT)** principles
- **Validation therapy** for emotional acknowledgment
- **Mindfulness** and grounding techniques
- **Solution-focused** brief therapy approaches

### Student-Specific Focus
- College transition challenges
- Academic stress management
- Social anxiety and isolation
- Time management and overwhelm
- Identity and independence issues

## 🚨 Crisis Support Integration

### Automatic Detection
- Identifies concerning language patterns
- Assesses risk levels (none/low/medium/high/immediate)
- Provides appropriate resource recommendations

### Resource Integration
- Crisis Text Line: Text HOME to 741741
- National Suicide Prevention Lifeline: 988
- Campus counseling center referrals
- Emergency contact suggestions

## 📊 Analytics & Insights

### Enhanced Tracking
- Emotion pattern analysis
- Stress level trends
- Writing frequency correlation
- Therapeutic response effectiveness

### Personalized Insights
- Mood trend identification
- Coping strategy suggestions
- Wellness activity recommendations
- Progress tracking over time

## 🔧 Customization Options

### Response Styles
- Adjust therapeutic approach intensity
- Customize cultural sensitivity settings
- Modify crisis detection thresholds
- Personalize prompt generation

### Integration Points
- Calendar stress correlation
- Peer support system integration
- Professional referral pathways
- Wellness activity suggestions

## 🐛 Troubleshooting

### Common Issues

#### API Key Not Working
```bash
# Check if key is properly set
echo $GEMINI_API_KEY

# Verify .env file format
cat havenmind-basic/.env
```

#### Fallback Mode Active
- Check internet connection
- Verify API key validity
- Review error logs in console
- Ensure proper environment loading

#### Dependencies Missing
```bash
# Reinstall requirements
pip install -r havenmind-basic/requirements.txt
pip install -r havenmind-backend/requirements.txt
```

## 📈 Performance Considerations

### Response Times
- Gemini API calls: ~1-3 seconds
- Fallback responses: Instant
- Caching for repeated patterns
- Async processing for better UX

### Rate Limits
- Gemini API: 60 requests per minute (free tier)
- Automatic fallback on rate limit
- Request queuing for high usage
- Usage monitoring and alerts

## 🔮 Future Enhancements

### Planned Features
- **Multi-language support** for diverse student populations
- **Voice journal integration** with speech-to-text
- **Peer response suggestions** for support network building
- **Professional therapist integration** for escalated cases
- **Wellness plan generation** based on journal patterns

### Advanced AI Features
- **Emotion trajectory prediction** for proactive support
- **Personalized coping strategy recommendations**
- **Group therapy session suggestions**
- **Academic stress correlation analysis**

## 📞 Support & Resources

### Documentation
- [Gemini AI Documentation](https://ai.google.dev/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Mental Health Resources](https://www.mentalhealth.gov/)

### Crisis Resources
- **Immediate danger**: Call 911
- **Crisis Text Line**: Text HOME to 741741
- **National Suicide Prevention Lifeline**: 988
- **Campus Resources**: Contact your student counseling center

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Install development dependencies
4. Run tests
5. Submit pull request

### Guidelines
- Follow therapeutic best practices
- Maintain privacy and security standards
- Test with diverse student scenarios
- Document all changes thoroughly

---

**Note**: This integration prioritizes student mental health and safety. If you're experiencing a mental health crisis, please reach out to professional resources immediately.