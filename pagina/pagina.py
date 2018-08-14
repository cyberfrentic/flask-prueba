from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, send_file
from forms import Create_Form, LoginForm, Factura
from flask_wtf import CsrfProtect
from config import DevelopmentConfig
from models import db, User, Compras, Padron, Combustible, Ticket, Articulos, InfomativoIssste, InformativoImss
from werkzeug.utils import secure_filename
from xml.dom import minidom
import collections as co
import os
from clases.fpdf2 import imprimir, imprimir2
from clases.fpdf3 import tabla
from clases.gasolina1 import tabla as gasolina
from sqlalchemy import distinct
from sqlalchemy.sql import text
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
	if 'username' not in session and request.endpoint in ['constancias','upload_file','contacto','get_file','create', 'folio', 'fondoContable', 'ticket', 'ticketvsfactura', 'consultaTicket']:
		return redirect(url_for('home'))
	elif 'username' in session and request.endpoint in ['login']:
		return redirect(url_for('home'))
	elif 'username' in session and (session['username']) != 'hugo' and request.endpoint in ['create']:
		return redirect(url_for('home'))
	elif 'username' in session and (session['username']) == 'lorena' and request.endpoint in ['upload_file','get_file','create', 'folio','fondoContable', 'ticket', 'ticketvsfactura', 'consultaTicket']:
		return redirect(url_for('home'))
	elif 'username' in session and (session['username']) == 'pascual' and (session['username']) == 'matty' and (session['username']) == 'merle' and (session['username']) == 'wilma' and request.endpoint in ['constancias']:
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
						return render_template("fondoContable.html", nombre=nombre)
					else:
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
				flash('Debe elegir una opcion')
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

@app.route('/ticketvsfactura',  methods=["GET", "POST"])
def ticketvsfactura():
	if 'username' in session:
		nombre = (session['username']).upper()
	else:
		nombre='Login'
	if request.method=='POST':
		num = request.form['numero']
		strq = "select t1.nuFolio, t1.placa,t1.litros, t1.importe from combustible t1 where t1.nufolio not in\
		 (select t2.nuFolio from ticket t2 where t1.nuFolio = t2.nuFolio) and t1.factura = '%s' and t1.descripcion != 'COMISION'" % num
		stmt = text(strq)
		result = db.session.execute(stmt)
		strq = "select count(*) from combustible t1 where t1.nufolio not in\
		 (select t2.nuFolio from ticket t2 where t1.nuFolio = t2.nuFolio) and t1.factura = '%s' and t1.descripcion != 'COMISION'" % num
		stmt = text(strq)
		cant = db.session.execute(stmt)
		return render_template("ticketvsfactura.html", lista=result, nombre=nombre, factura=num, cantidad=cant)
	return render_template("ticketvsfactura.html", nombre=nombre)

@app.route('/consultaTicket', methods=["GET", "POST"])
def consultaTicket():
	nombre = (session['username']).upper()
	global p, p2, p3, p4, p5, fecha_ini, fecha_fin, total1, total2, total3, total4, total5, lit1, lit2, lit3, lit4, lit5
	if request.method=="POST":
		if 'form1' in request.form['btn1']:
			fecha_ini = request.form['fecha_Inicial']
			fecha_fin = request.form['fecha_Final']
			if str(fecha_ini)> str(fecha_fin):
				flash("La consulta no se puede realizar, la fecha inicial debe ser igual o menor a la fecha final")
				return render_template("consultaTicket.html", nombre=nombre)
			else:
				p=[]
				p2=[]
				p3=[]
				p4=[]
				p5=[]
				x=[]
				j=0
				lit1=0
				lit2=0
				lit3=0
				lit4=0
				lit5=0
				total1=0
				total2=0
				total3=0
				total4=0
				total5=0
				gerencia = ["TA-9629-G"]
				tecnica = ["TA-9625-G", "TA-9642-G", "TA-5720-G", "TA-9639-G", "SZ-1007-H", "SZ-1009-H", "SZ-9449-H"]
				comercial = ["SZ-1008-H", "TA-9638-G"]
				tarjeta1=["BIDON", "SZ-9439-H","TB-5720-G"]
				tarjeta2=["BIDON DIESEL", "BIDON GASOLINA", "VERSA SEDAN", "RLT3S", "RLT1S", "VCN9A"]
				for item in gerencia:
					strq = "select placa as placa, sum(litros) as litros, sum(total) as total  from ticket  where placa = '%s' and fecha between '%s' and '%s' " % (item, fecha_ini, fecha_fin)
					stmt = text(strq)
					cant = db.session.execute(stmt)
					for i in cant:
						if (i[0]!= None):
							j+=1
							x=(j, i[0],("{0:.2f}".format(i[1])), ("{0:.2f}".format(i[2])))
							lit1 += float(x[2])
							total1 += float(x[3])
							p.append(x)
				for item in tecnica:
					strq = "select placa as placa, sum(litros) as litros, sum(total) as total  from ticket  where placa = '%s' and fecha between '%s' and '%s' " % (item, fecha_ini, fecha_fin)
					stmt = text(strq)
					cant = db.session.execute(stmt)
					for i in cant:
						if (i[0]!= None):
							j+=1
							x=(j, i[0],("{0:.2f}".format(i[1])), ("{0:.2f}".format(i[2])))
							lit2 += float(x[2])
							total2 += float(x[3])
							p2.append(x)
				for item in comercial:
					strq = "select placa as placa, sum(litros) as litros, sum(total) as total  from ticket  where placa = '%s' and fecha between '%s' and '%s' " % (item, fecha_ini, fecha_fin)
					stmt = text(strq)
					cant = db.session.execute(stmt)
					for i in cant:
						if (i[0]!= None):
							j+=1
							x=(j, i[0],("{0:.2f}".format(i[1])), ("{0:.2f}".format(i[2])))
							print (x[2])
							lit3 += float(x[2])
							total3 += float(x[3])
							p3.append(x)
				for item in tarjeta1:
					strq = "select placa as placa, sum(litros) as litros, sum(total) as total  from ticket  where placa = '%s' and fecha between '%s' and '%s' " % (item, fecha_ini, fecha_fin)
					stmt = text(strq)
					cant = db.session.execute(stmt)
					for i in cant:
						if (i[0]!= None):
							j+=1
							x=(j, i[0],("{0:.2f}".format(i[1])), ("{0:.2f}".format(i[2])))
							print (x[2])
							lit4 += float(x[2])
							total4 += float(x[3])
							p4.append(x)
				for item in tarjeta2:
					strq = "select placa as placa, sum(litros) as litros, sum(total) as total  from ticket  where placa = '%s' and fecha between '%s' and '%s' " % (item, fecha_ini, fecha_fin)
					stmt = text(strq)
					cant = db.session.execute(stmt)
					for i in cant:
						if (i[0]!= None):
							j+=1
							x=(j, i[0],("{0:.2f}".format(i[1])), ("{0:.2f}".format(i[2])))
							print (x[2])
							lit5 += float(x[2])
							total5 += float(x[3])
							p5.append(x)
				print(p, p2, p3, p4, p5, lit1, lit2, lit3, lit4, lit5, total1, total2, total3, total4, total5)					
				return render_template("consultaTicket.html", lista=p, lista2=p2, lista3=p3, lista4=p4, lista5=p5, litros1= lit1, litros2=lit2, litros3=lit3, litros4=lit4, litros5=lit5, total1=total1, total2=total2, total3=total3, total4=total4, total5=total5, nombre=nombre)
		if 'form2' in request.form['btn1']:
			x = gasolina(fecha_ini, fecha_fin, p, p2, p3, p4, p5, lit1, lit2, lit3, lit4, lit5, total1, total2, total3, total4, total5)
			return (x)
	if 'username' in session:
		nombre = (session['username']).upper()
		return render_template("consultaTicket.html", nombre=nombre)
	else:
		return render_template("consultaTicket.html")

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
			query1 = Ticket.query.filter_by(nuFolio=tra).first()
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
            flash("No file part in the form.")
        f = request.files["file"]
        if f.filename == "":
            flash("No file selected.")
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
	if fact:
		try:
			uuid = Combustible.query.filter_by(factura=fact).first()
			if uuid == None:
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
			else:
				flash('El registro existe en la base de datos, Factura No. {}'.format(str(int(fact))))
				nombre = (session['username']).upper()
				return render_template("leer.html", nombre=nombre)
		except ValueError:
			flash('El registro existe en la base de datos, Factura No. {}'.format(str(int(fact))))
			nombre = (session['username']).upper()
			return render_template("leer.html", nombre=nombre)
		nombre = (session['username']).upper()
		return render_template("combustible.html", data=lista1, fact=(str(int(fact))), nombre=nombre)
	else:
		fecha = exceldate(int(sheet.cell(2,1).value))
		dImss=dict()
		dIssste=dict()
		lista1=[]
		lista2=[]
		if type(fecha) is str :
			if int(fecha[5:7])>0 and int(fecha[5:7])<13 :
				mes=(fecha[5:7])
				anio = (fecha[0:4])
				consul = InformativoImss.query.filter_by(mes=mes).filter_by(anio=anio).first()
				if consul == None:
					for i in range(sheet.nrows-5):
						if (sheet.cell(i+5,43).value==0 and sheet.cell(i+5,68).value==0):
							pass
						else:
							if sheet.cell(i+5,43).value != 0:
								dImss = {
									'clave': str(sheet.cell(i+5,0).value),
									'nombre': sheet.cell(i+5,1).value,
									'imssCyVE': "{0:.2f}".format(sheet.cell(i+5,45).value), 
									'imssEyMP' : "{0:.2f}".format(sheet.cell(i+5,47).value), 
									'imssIyVP' : "{0:.2f}".format(sheet.cell(i+5,48).value),
									'imssCyVp' : "{0:.2f}".format(sheet.cell(i+5,49).value),
									'imssRTP' : "{0:.2f}".format(sheet.cell(i+5,50).value),
									'imssGuaP' : "{0:.2f}".format(sheet.cell(i+5,51).value),
									'imssRetP' : "{0:.2f}".format(sheet.cell(i+5,52).value),
									'INFONAVITP':"{0:.2f}".format(sheet.cell(i+5,53).value),
									'DESC. INFONAVIT':"{0:.2f}".format(sheet.cell(i+5,112).value + sheet.cell(i+5,113).value),
									'total' :"{0:.2f}".format(sheet.cell(i+5,45).value+sheet.cell(i+5,47).value+sheet.cell(i+5,48).value+sheet.cell(i+5,49).value+sheet.cell(i+5,50).value+sheet.cell(i+5,51).value+sheet.cell(i+5,52).value+sheet.cell(i+5,53).value+sheet.cell(i+5,112).value+sheet.cell(i+5,113).value)
								}
								lista1.append(dImss)
					nombre = (session['username']).upper()
					return render_template("comparativoHumnos.html", data=lista1, fecha= mes+'-'+anio, nombre=nombre)
	return ("no hay datos")

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