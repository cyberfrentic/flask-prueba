import os
class Config(object):
	SECRET_KEY = 'altavista2018'

class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = 'mysql://pascual:lh260182lh@127.0.0.1/flask'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	UPLOAD_FOLDER = os.path.abspath("static/uploads/")