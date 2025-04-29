import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'\xe1\x86\xa1\x83\x84r\xde\x0bu\x84\xb5\xfc\xd7\xf0y\xa8L!\xc7\xcd\x1f\xd4-\x9a'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+mysqlconnector://root:@localhost/calora_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False