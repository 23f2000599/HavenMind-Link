from flask import Flask
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'havenmind-secret-key-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///havenmind.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    CORS(app)
    
    from .models import init_db
    init_db(app)
    
    from .routes import auth, journal, calendar, support, ai_analysis
    app.register_blueprint(auth.bp)
    app.register_blueprint(journal.bp)
    app.register_blueprint(calendar.bp)
    app.register_blueprint(support.bp)
    app.register_blueprint(ai_analysis.bp)
    
    @app.route('/')
    def home():
        return {'message': 'HavenMind Link API is running', 'status': 'active'}
    
    return app