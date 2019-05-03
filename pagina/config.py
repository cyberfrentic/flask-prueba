import os
class Config(object):
	SECRET_KEY = 'altavista2018'

class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = 'mysql://administrador:ha260182ha@192.168.15.45/flask'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	UPLOAD_FOLDER = os.path.abspath("static/uploads/")