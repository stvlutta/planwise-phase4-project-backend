import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('postgresql://planwise:VEql6cmK1BeLb91d9EWE7AjcxKIJY1UQ@dpg-d1dsug15pdvs73augq50-a/planwise') or 'sqlite:///task_manager.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    JWT_SECRET_KEY = os.environ.get('DUwwbfDWL0ObSLkP54zkbQVvSUOBe9XR03wFPRL7fgo=') or 'jwt-secret-string'
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('FRONTEND_URL', 'https://planwise-phase4-project-frontend.vercel.app').split(',')
    
    # Flask Configuration
    ENV = os.environ.get('FLASK_ENV', 'production')
    DEBUG = ENV == 'development'
