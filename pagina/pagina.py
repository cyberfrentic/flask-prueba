from flask import Flask
from flask import render_template
from flask import request
from forms import Create_Form, LoginForm, Factura
from flask_wtf import CsrfProtect
from flask import redirect, url_for
from flask import session
from flask import flash
from config import DevelopmentConfig
from models import db
from models import User, Compras, Padron, Combustible, Ticket
from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from xml.dom import minidom
import collections as co
import os
from models import Compras, Articulos
from clases.fpdf2 import imprimir, imprimir2
from clases.fpdf3 import tabla
from flask import send_file
from sqlalchemy import distinct
import xlrd
import datetime
###########################################
import pymysql
pymysql.install_as_MySQLdb()
###########################################
ALLOWED_EXTENSIONS = set(["xml","xls"])
def allowed_file(filename):
	return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
###########################################
def exceldate(serial):
    seconds = (serial - 25569) * 86400.0
    d = datetime.datetime.utcfromtimestamp(seconds)
    return d.strftime('%Y-%m-%d')
###########################################
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
crsf = CsrfProtect()


@app.before_request
def before_request():
	if 'username' not in session and request.endpoint in ['constancias','upload_file','contacto','get_file','create', 'folio', 'fondoContable', 'ticket']:
		return redirect(url_for('home'))
	elif 'username' in session and request.endpoint in ['login']:
		return redirect(url_for('home'))
	elif 'username' in session and (session['username']) != 'hugo' and request.endpoint in ['create']:
		return redirect(url_for('home'))
	elif 'username' in session and (session['username']) == 'lorena' and request.endpoint in ['upload_file','get_file','create', 'folio','fondoContable', 'ticket']:
		return redirect(url_for('home'))
	elif 'username' in session and (session['username']) == 'pascual' and request.endpoint in ['constancias']:
		return redirect(url_for('home'))


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
    nombre = (session['username']).upper()
    return render_template('index.html', form=create_form, nombre=nombre)


@app.route('/')
@app.route('/home')
def home():
	if 'username' in session:
		nombre = (session['username']).upper()
		return render_template("home.html",nombre=nombre)
	else:
		return render_template("home.html")


@app.route('/constancias',  methods=["GET", "POST"])
def constancias():
	if request.method == 'POST':
		global btn
		if 'search' in request.form['boton']:
			contrato = request.form['contrato']
			try:
				query1 = Padron.query.filter_by(cuenta=contrato).first()
				nombre = (session['username']).upper()
				return render_template("constancias.html", nombre=nombre, name=query1.nombre, direccion= query1.direccion, contrato=contrato)
			except AttributeError:
				flash('El contrato no existe')
		elif 'generar' in request.form['boton']:
			if request.form.get('validar')=='activo':
				nombre = request.form['nombre']
				direccion = request.form['direccion']
				cedula = request.form['cedula']
				if cedula=="":
					flash("La cedula catastral es necesaria")
				else:
					x=imprimir2(nombre=nombre, direccion=direccion, cedula=cedula)
					return (x)
			else:
				contrato = request.form['contrato']
				nombre = request.form['nombre']
				direccion = request.form['direccion']
				cedula = request.form['cedula']
				if cedula=="":
					flash("La cedula catastral es necesaria")
				else:
					x=imprimir(contrato=contrato, nombre=nombre, direccion=direccion, cedula=cedula)
					return (x)
	nombre = (session['username']).upper()
	return render_template("constancias.html", nombre=nombre)
	
	

@app.route('/fondoContable',  methods=["GET", "POST"])
def fondoContable():
	nombre = (session['username']).upper()
	lista=()
	lista2=[]
	query1 = db.session.query(Compras.nombre).distinct(Compras.nombre).order_by(Compras.nombre)
	row = query1.all()
	if query1 != None:
		for item in row:
			lista+=item
	global query2
	if request.method=="POST":
		if 'form1' in request.form['btn1']:
			if request.form.getlist('mismo'):
				valores = request.form.getlist('mismo')
				if len(valores)!= 0:
					cuantos = len(valores)
					s=''
					for i in range(len(valores)):
						s+=valores[i]
				if '1' == s:
					folio_text = request.form['folio_text']
					query2 = Compras.query.filter_by(folio=folio_text).all()
					return render_template("fondoContable.html",lista=lista, lista2=query2, nombre=nombre)
				elif '2' == s:
					fecha_ini = request.form['fecha_Inicial']
					fecha_fin = request.form['fecha_Final']
					if str(fecha_ini)> str(fecha_fin):
						flash('La consulta no se puede realizar, la fecha final debe ser mayo o igual a la fecha inicial')
					query2 = db.session.query(Compras.id, Compras.fecha, Compras.total, Compras.subtotal, Compras.folio, Compras.iva, Compras.rfc, Compras.nombre, Compras.UUiD).filter(Compras.fecha.between(fecha_ini, fecha_fin))
					return render_template("fondoContable.html", lista=lista, lista2=query2, nombre=nombre)
				elif '3' == s:
					proveedor = request.form['TextProv']
					query2 = Compras.query.filter_by(nombre=proveedor).all()
					return render_template("fondoContable.html", lista=lista, lista2=query2, nombre=nombre)
				elif '12' == s:
					folio_text = request.form['folio_text']
					fecha_ini = request.form['fecha_Inicial']
					fecha_fin = request.form['fecha_Final']
					query2 = db.session.query(Compras.id, Compras.fecha, Compras.total, Compras.subtotal, Compras.folio, Compras.iva, Compras.rfc, Compras.nombre, Compras.UUiD).filter(Compras.fecha.between(fecha_ini, fecha_fin)).filter(Compras.folio==folio_text)
					return render_template("fondoContable.html", lista=lista, lista2=query2, nombre=nombre)
				elif '23' == s:
					fecha_ini = request.form['fecha_Inicial']
					fecha_fin = request.form['fecha_Final']
					proveedor = request.form['TextProv']
					query2 = db.session.query(Compras.id, Compras.fecha, Compras.total, Compras.subtotal, Compras.folio, Compras.iva, Compras.rfc, Compras.nombre, Compras.UUiD).filter(Compras.fecha.between(fecha_ini, fecha_fin)).filter(Compras.nombre==proveedor)
					return render_template("fondoContable.html", lista=lista, lista2=query2, nombre=nombre)
				elif '13' == s:
					folio_text = request.form['folio_text']
					proveedor = request.form['TextProv']
					query2 = db.session.query(Compras.id, Compras.fecha, Compras.total, Compras.subtotal, Compras.folio, Compras.iva, Compras.rfc, Compras.nombre, Compras.UUiD).filter(Compras.folio==folio_text).filter(Compras.nombre==proveedor)
					return render_template("fondoContable.html", lista=lista, lista2=query2, nombre=nombre)
				elif '123' == s:
					folio_text = request.form['folio_text']
					fecha_ini = request.form['fecha_Inicial']
					fecha_fin = request.form['fecha_Final']
					proveedor = request.form['TextProv']
					query2 = db.session.query(Compras.id, Compras.fecha, Compras.total, Compras.subtotal, Compras.folio, Compras.iva, Compras.rfc, Compras.nombre, Compras.UUiD).filter(Compras.folio==folio_text).filter(Compras.fecha.between(fecha_ini, fecha_fin)).filter(Compras.nombre==proveedor)
					return render_template("fondoContable.html", lista=lista, lista2=query2, nombre=nombre)
			else:
				flash('Debe elegir una opción')
		elif 'form2' in request.form['btn1']:
			totales=0
			for item in query2:
				j=[
				str(item.fecha)[:10],
				item.total,
				item.subtotal,
				item.iva,
				item.rfc,
				item.nombre,
				item.UUiD
				]
				totales+=item.total
				lista2.append(j)
			x=tabla(lista2, totales)
			return (x)
	return render_template("fondoContable.html", lista=lista, nombre=nombre)

@app.route('/contanto')
def contacto():
	nombre = (session['username']).upper()
	return render_template("contacto.html", nombre=nombre)

@app.route('/logout')
def logout():
	if 'username' in session:
		session.pop('username')
	return redirect(url_for('home'))

@app.errorhandler(400)
def regreso(e):
	nombre = (session['username']).upper()
	x=request.endpoint
	return render_template(x +'.html', nombre=nombre), 400

@app.errorhandler(404)
def page_not_found(e):
	if 'username' in session:
		nombre = (session['username']).upper()
		return render_template('404.html', nombre=nombre), 404
	else:
		return render_template('404.html'), 404
	
@app.route('/ticket', methods=["GET", "POST"])
def ticket():
	if request.method == 'POST':
		fecha = request.form["fecha"]
		hora = request.form["appt-time"]
		cant = request.form["cantidad"]
		comb = request.form["optionsRadios"]
		precio = request.form["precio"]
		subtotal = request.form["subtotal"]
		iva = request.form["iva"]
		total = request.form["total"]
		donde = request.form["placa"]
		placa = request.form["tipo"]
		obser = request.form["comentarios"]
		if (len(request.form.getlist('validar'))) < 1:
			tra = request.form["transaccion"]
			query1 = Ticket.query.filter_by(transaccion=tra).first()
			if query1 != None:
				flash("El ticket ya fue capturado")
				nombre = (session['username']).upper()
				return render_template("ticket.html", nombre=nombre)
		elif (len(request.form.getlist('validar'))) == 1:
			tra = 0
			flash('El ticket es un planchado y no cuenta con numero de folio')
		ticket = Ticket(
					nuFolio = tra,
					fecha = str(fecha)+' '+ str(hora),
					litros = cant,
					combustible = comb,
					precio = precio,
					subtotal = subtotal,
					iva = iva,
					total = total,
					medio = donde,
					placa = placa,
					observaciones = obser,
					)
		db.session.add(ticket)
		db.session.commit()
		flash('Ticket Fue Agregado correctamente con numero de folio: {}'.format(str(tra)))
	if 'username' in session:
		nombre = (session['username']).upper()
		return render_template("ticket.html", nombre=nombre)
	else:
		return render_template("ticket.html")

@app.route('/folio',  methods=["GET", "POST"])
def folio():
	nombre = (session['username']).upper()
	if request.method == 'POST':
		global folio
		if 'form1' in request.form['btn1']:
			folio = request.form['folio']
			query1=Compras.query.filter_by(id=folio).first()
			if query1 != None:
				lista=(query1.fecha, str(query1.total), str(query1.subtotal), str(query1.iva), query1.rfc, query1.nombre, query1.UUiD)
				return render_template('folio.html', lista=lista, nombre=nombre)
			else:
				flash("El Folio no existe")
		elif 'form2' in request.form['btn1']:
			numero_folio = request.form['numero']
			compras = Compras.query.filter_by(id = folio).first()
			if compras.folio == None:
				compras.folio=numero_folio
				db.session.commit()
				flash('Número de Folio Agregado')
			else:
				flash('El Registro Cuenta con un número de Fondo {}'.format(compras.folio))
	return render_template('folio.html',nombre=nombre)


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
            nombre, extension = filename.split('.')
            if extension=='xml':
            	f.save(os.path.join(app.config["UPLOAD_FOLDER"]+'\\xml', filename))
            	return redirect(url_for("get_fileXml", filename=filename))
            elif extension=='xls':
            	f.save(os.path.join(app.config["UPLOAD_FOLDER"]+'\\xls', filename))
            	return redirect(url_for("get_fileXls", filename=filename))
        return "File not allowed."
    nombre = (session['username']).upper()
    return render_template("leer.html", nombre=nombre)

@app.route("/uploads/xls/<filename>", methods=['GET', 'POST'])
def get_fileXls(filename):
	book = xlrd.open_workbook(app.config["UPLOAD_FOLDER"]+'\\xls\\'+filename)
	sheet = book.sheet_by_index(0)
	data = dict()
	lista1=[]
	lista2=[]
	fact= sheet.cell(2,0).value
	try:
		uuid = Combustible.query.filter_by(factura=fact).first()
		flash('El registro no existe')
		for i in range(sheet.nrows-2):	
			data={
				'placa' : str(sheet.cell(i+2,2).value),
				'nutarjeta' : sheet.cell(i+2,3).value,
				'centroCosto' : sheet.cell(i+2,4).value,
				'fechaCarga' : exceldate(sheet.cell(i+2,5).value) +' '+ str(sheet.cell(i+2,6).value),
				'nuFolio' : sheet.cell(i+2,7).value,
				'esCarga' : sheet.cell(i+2,8).value,
				'nombreEs' : sheet.cell(i+2,9).value,
				'descripcion' : sheet.cell(i+2,10).value,
				'litros' : sheet.cell(i+2,11).value,
				'precio' : sheet.cell(i+2,12).value,
				'importe' : sheet.cell(i+2,14).value,
				'odom' : sheet.cell(i+2,15).value,
				'odoAnt' : sheet.cell(i+2,16).value,
			}
			lista1.append(data)
			for i in range(sheet.nrows-2):
				combustible=Combustible(
					factura = sheet.cell(i+2,0).value,
					leyenda = sheet.cell(i+2,1).value,
					placa = str(sheet.cell(i+2,2).value),
					nutarjeta = sheet.cell(i+2,3).value,
					centroCosto = sheet.cell(i+2,4).value,
					fechaCarga = exceldate(sheet.cell(i+2,5).value) +' '+ str(sheet.cell(i+2,6).value),
					nuFolio = sheet.cell(i+2,7).value,
					esCarga = sheet.cell(i+2,8).value,
					nombreEs = sheet.cell(i+2,9).value,
					descripcion = sheet.cell(i+2,10).value,
					litros = sheet.cell(i+2,11).value,
					precio = sheet.cell(i+2,12).value,
					importe =sheet.cell(i+2,14).value,
					odom = sheet.cell(i+2,15).value,
					odoAnt = sheet.cell(i+2,16).value,
					kmRec = sheet.cell(i+2,17).value,
					kmLts = str(sheet.cell(i+2,18).value),
					pKm = sheet.cell(i+2,19).value,
					conductor = sheet.cell(i+2,20).value,
				)
			db.session.add(combustible)
			db.session.commit()
		flash('El registro fue agragado con exito, Factura No. {}'.format(str(int(fact))))
	except ValueError:
		flash('El registro existe en la base de datos, Factura No. {}'.format(str(int(fact))))
		nombre = (session['username']).upper()
		return render_template("leer.html", nombre=nombre)
	nombre = (session['username']).upper()
	return render_template("combustible.html", data=lista1, fact=(str(int(fact))), nombre=nombre)

@app.route("/uploads/xml/<filename>", methods=['GET', 'POST'])
def get_fileXml(filename):
	lista1=[]
	lista2=[]
	articulo=[]
	xmlDoc = minidom.parse(app.config["UPLOAD_FOLDER"]+'\\xml\\'+filename)
	nodes = xmlDoc.childNodes
	comprobante = nodes[0]
	compAtrib = dict(comprobante.attributes.items())
	atributos = dict()
	articulos = dict()
	atributos['fecha'] = compAtrib['Fecha']
	atributos['total'] = compAtrib['Total']
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
	else:
		flash('El registro Existe en la base de datos')
		return render_template("leer.html")	
	factura = Factura(request.form)
	compras=Compras(
			UUiD = atributos['UUiD'],
			rfc = atributos['rfc'],
			nombre = atributos['nombre'],
			subtotal = atributos['subTotal'],
			iva = atributos['IVA'],
			total = atributos['total'],
			fecha = atributos['fecha'],
			placas = factura.placas.data,
			observaciones = factura.observaciones.data
			)
	if (request.method == 'POST') and (factura.validate()):
		db.session.add(compras)
		db.session.commit()
		id_compra = Compras.query.filter_by(UUiD = atributos['UUiD']).first()
		for dc in range(Cant_Diccio):
			arti = Articulos(
				compras_id = id_compra.id,
				cantidad = articulos['cantidad'+str(dc+1)],
				descripcion = articulos['descripcion'+str(dc+1)],
				p_u = articulos['valorUnitario'+str(dc+1)],
				importe = articulos['importe'+str(dc+1)]
				)
			db.session.add(arti)
			db.session.commit()
		flash('Registro agregado y tiene el Folio: {}'.format(id_compra.id))
	lista1.append(atributos)
	nombre = (session['username']).upper()
	return render_template("ListaXML.HTML", lista=lista1, lista2=sample, form=factura, nombre=nombre)


if __name__ == '__main__':
	crsf.init_app(app)
	db.init_app(app)
	with app.app_context():
		db.create_all()
	app.run(port=8000, host='0.0.0.0')