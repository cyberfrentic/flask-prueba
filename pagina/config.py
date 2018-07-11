import os
class Config(object):
	SECRET_KEY = 'altavista2018'

class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = 'mysql://pascual:lh260182lh@192.168.1.211/flask'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	UPLOAD_FOLDER = os.path.abspath("static/uploads/")