import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-wonliy-pos'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///wonliy.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
