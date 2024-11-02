# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/your_database'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable track modifications to save resources
    SESSION_TYPE = 'filesystem'
    TEMPLATES_AUTO_RELOAD = True
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_TRANSLATION_DIRECTORIES = './translations'