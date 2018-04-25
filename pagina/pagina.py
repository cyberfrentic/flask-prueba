from flask import Flask
from flask import render_template
from flask import request
from forms import Create_Form, LoginForm
from flask_wtf import CsrfProtect
from flask import redirect, url_for
from flask import session
from flask import flash
from config import DevelopmentConfig
from models import db
from models import User

import pymysql
pymysql.install_as_MySQLdb()
###########################################
from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from xml.dom import minidom
import collections as co
import os, sys
from models import Compras

ALLOWED_EXTENSIONS = set(["xml"])

def allowed_file(filename):
	return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


###########################################



app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
crsf = CsrfProtect()


@app.before_request
def before_request():
	if 'username' not in session and request.endpoint in ['home','abount','upload_file','contacto','get_file','create']:
		return redirect(url_for('login'))
	elif 'username' in session and request.endpoint in ['login']:
		return redirect(url_for('home'))
	elif 'username' in session:
		x = (session['username'])
		if x != 'hugo' and request.endpoint in ['create']:
			return redirect(url_for('home'))


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
	login_form = LoginForm(request.form)
	if request.method == 'POST' and login_form.validate() :
		username = login_form.username.data
		password = login_form.password.data
		user = User.query.filter_by(username = username).first()
		if user is not None and user.verify_password(password):
			succes_message='Bienvenido {}'.format(username)
			session['username']= username
			return redirect(url_for('home'))
		else:
			error_message = '{} No es un usuario del sistema'.format(username)
			flash(error_message)
	return render_template('login.html', form = login_form)


@app.route('/create', methods=['GET', 'POST'])
def create():
    create_form = Create_Form(request.form)
    if request.method == 'POST' and create_form.validate() :

    	user = User(create_form.username.data,
    				create_form.password.data,
    				create_form.email.data)
    	db.session.add(user)
    	db.session.commit()

    	succes_message = 'Usuario registrado en la base de datos'
    	flash(succes_message)
    return render_template('index.html', form=create_form)


@app.route('/home')
def home():
	return render_template("home.html")		


@app.route('/abount')
def abount():
	return render_template("abount.html")


@app.route('/contanto')
def contacto():
    return render_template("contacto.html")

@app.route('/logout')
def logout():
	if 'username' in session:
		session.pop('username')
	return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

#############################################

@app.route("/servicios", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if not "file" in request.files:
            return "No file part in the form."
        f = request.files["file"]
        if f.filename == "":
            return "No file selected."
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            return redirect(url_for("get_file", filename=filename))
        return "File not allowed."

    return render_template("leer.html")

@app.route("/uploads/<filename>")
def get_file(filename):
	lista1=[]
	lista2=[]
	articulo=[]
	xmlDoc = minidom.parse(app.config["UPLOAD_FOLDER"]+'\\'+filename)
	nodes = xmlDoc.childNodes
	comprobante = nodes[0]
	compAtrib = dict(comprobante.attributes.items())
	atributos = dict()
	articulos = dict()
	atributos['fecha'] = compAtrib['Fecha']#[0:10]
	atributos['total'] = compAtrib['Total']#.rjust(10, '0')
	atributos['subTotal'] = compAtrib['SubTotal']
	for nodo in comprobante.getElementsByTagName("cfdi:Impuestos"):
            atributos['IVA'] = nodo.getAttribute('TotalImpuestosTrasladados')

            emisor = comprobante.getElementsByTagName('cfdi:Emisor')
            atributos['rfc'] = emisor[0].getAttribute('Rfc')
            atributos['nombre'] = emisor[0].getAttribute('Nombre')
            timbre = comprobante.getElementsByTagName('tfd:TimbreFiscalDigital')
            try:
                atributos['UUiD'] = timbre[0].getAttribute('UUID')
            except KeyError:
                atributos['UUiD'] = ' '
            conceptos = comprobante.getElementsByTagName('cfdi:Conceptos')
            concept = conceptos[0].getElementsByTagName('cfdi:Concepto')
            x = 0
            for nodo in comprobante.getElementsByTagName("cfdi:Conceptos"):
                x=0
                for nodo2 in nodo.getElementsByTagName("cfdi:Concepto"):
                    x += 1
                    articulos['cantidad'+str(x)] = nodo2.getAttribute('Cantidad')
                    articulos['descripcion'+str(x)] = nodo2.getAttribute('Descripcion')
                    articulos['valorUnitario'+str(x)] = nodo2.getAttribute('ValorUnitario')
                    articulos['importe'+str(x)] = nodo2.getAttribute('Importe')

                    
	Cant_Diccio = int(len(articulos)/4)
	sample = [co.defaultdict(int) for _ in range(Cant_Diccio)]
	for dc in range(Cant_Diccio):
		sample[dc] = {
			'cantidad' : articulos['cantidad'+str(dc+1)],
			'descripcion' : articulos['descripcion'+str(dc+1)],
			'valor' : articulos['valorUnitario'+str(dc+1)],
			'importe' : articulos['importe'+str(dc+1)]
			}

	uuid = Compras.query.filter_by(UUiD = atributos['UUiD']).first()
	if (uuid==None):
		flash('El registro no existe')
		factura = Factura(request.form)
		if request.method == 'POST' and Factura.validate() :
			compras=Compras(
				UUiD = atributos['UUiD'],
				rfc = atributos['rfc'],
				nombre = atributos['nombre'],
				subtotal = atributos['subTotal'],
				iva = atributos['IVA'],
				total = atributos['total'],
				fecha = atributos['fecha']
				)
			db.session.add(compras)

			db.session.commit()
			flash('Registro agregado')
	else:
		flash('El registro Existe en la base de datos')
	lista1.append(atributos)
	return render_template("ListaXML.HTML", lista=lista1, lista2=sample, form=factura)#send_from_directory(app.config["UPLOAD_FOLDER"], filename)

#############################################


if __name__ == '__main__':
	crsf.init_app(app)
	db.init_app(app)
	with app.app_context():
		db.create_all()
	app.run(port=8000, host='0.0.0.0')