from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import datetime

db = SQLAlchemy()

class User(db.Model):
	__tablename__= 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), unique=True)
	email = db.Column(db.String(40))
	password = db.Column(db.String(93))
	created_date = db.Column(db.DateTime, default=datetime.datetime.now)

	def __init__(self, username, password, email):
		self.username = username
		self.password = self.__crate_password(password)
		self.email = email

	def __crate_password(self, password):
		return generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password, password)

class Compras(db.Model):
	__tablename__='compras'
	id = db.Column(db.Integer, primary_key=True)
	UUiD = db.Column(db.String(36), unique=True)
	rfc = db.Column(db.String(13), index=True)
	nombre = db.Column(db.String(150))
	subtotal = db.Column(db.Float)
	iva = db.Column(db.Float)
	total = db.Column(db.Float)
	fecha = db.Column(db.DateTime)
	placas = db.Column(db.String(8))
	observaciones = db.Column(db.Text)
	folio = db.Column(db.Integer)


class Articulos(db.Model):
	__tablename__ = 'articulos'
	id = db.Column(db.Integer, primary_key=True)
	compras_id = db.Column(db.Integer, db.ForeignKey("compras.id"), nullable=False)
	compras = relationship(Compras, backref = backref('comprass', uselist=True))
	cantidad = db.Column(db.Float)
	descripcion = db.Column(db.String(150))
	p_u = db.Column(db.Float)
	importe = db.Column(db.Float)

class Padron(db.Model):
	__tablename__='padron'
	cuenta = db.Column(db.Integer, primary_key=True, unique=True, index=True)
	nombre = db.Column(db.String(120))
	direccion = db.Column(db.String(150))

class Combustible(db.Model):
	__tablename__='combustible'
	id = 			db.Column(db.Integer, primary_key=True)
	factura = 		db.Column(db.Integer)
	leyenda = 		db.Column(db.String(25))
	placa = 		db.Column(db.String(20))
	nutarjeta = 	db.Column(db.String(15))
	centroCosto = 	db.Column(db.String(20))
	fechaCarga = 	db.Column(db.DateTime)
	nuFolio = 		db.Column(db.Integer)
	esCarga = 		db.Column(db.String(10))
	nombreEs = 		db.Column(db.String(15))
	descripcion = 	db.Column(db.String(15))
	litros = 		db.Column(db.Float)
	precio = 		db.Column(db.Float)
	importe = 		db.Column(db.Float)
	odom = 			db.Column(db.Integer)
	odoAnt = 		db.Column(db.Integer)
	kmRec = 		db.Column(db.Float)
	kmLts = 		db.Column(db.String(10))
	pKm = 			db.Column(db.Float)
	conductor = 	db.Column(db.String(10))

class Ticket(db.Model):
	__tablename__='ticket'
	id = db.Column(db.Integer, primary_key=True)
	nuFolio = db.Column(db.Integer)
	fecha = db.Column(db.DateTime)
	litros = db.Column(db.Float)
	combustible = db.Column(db.String(7))
	precio = db.Column(db.Float)
	subtotal = db.Column(db.Float)
	iva = db.Column(db.Float)
	total = db.Column(db.Float)
	medio = db.Column(db.String(8))
	placa = db.Column(db.String(9))
	observaciones = db.Column(db.Text)

class InformativoImss(db.Model):
	__tablename__='informativoimss'
	id = db.Column(db.Integer, primary_key=True)
	clave = db.Column(db.String(9))
	nombre = db.Column(db.String(34))
	mes = db.Column(db.Integer)
	anio = db.Column(db.Integer)
	imssEyME = db.Column(db.Float)
	imssIyVE = db.Column(db.Float)
	imssEyMP = db.Column(db.Float)
	imssIyVP =  db.Column(db.Float)
	imssCyVP = db.Column(db.Float)
	imssRTP  = db.Column(db.Float)
	imssGuaP = db.Column(db.Float)
	imssRetP = db.Column(db.Float)

class InfomativoIssste(db.Model):
	__tablename__='informativoissste'
	id = db.Column(db.Integer, primary_key=True)
	clave = db.Column(db.String(9))
	nombre = db.Column(db.String(34))
	mes = db.Column(db.Integer)
	anio = db.Column(db.Integer)
	retirIssste = db.Column(db.Float)
	fovissste = db.Column(db.Float)
	salBaseIsteEm = db.Column(db.Float)
	salBaseIstPa = db.Column(db.Float)
	isteSegSaludP = db.Column(db.Float)
	isteRtPat = db.Column(db.Float)
	isteIyVPat = db.Column(db.Float)
	isteServSocP = db.Column(db.Float)
	isteCyVPat = db.Column(db.Float)
	ajusteIstePat = db.Column(db.Float)
	exePrevSoc = db.Column(db.Float)