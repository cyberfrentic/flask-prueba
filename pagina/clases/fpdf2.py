from fpdf import FPDF
import os
from datetime import datetime
from flask import make_response



class PDF(FPDF):
    
    def header(self):
        #Ruta del la carpeta imagenes del servidor
        imagenes=os.path.abspath("static/img/")
        # Logo  con esta ruta se dirige al server y no a la maquina cliente
        self.image(os.path.join(imagenes, "sintitulo.png"), 10, 8, 200)
        # Arial bold 15
        self.set_font('Arial', 'B', 8)
        self.ln(35)
        # Move to the right
        self.cell(100)
        # Title
        fe = str(datetime.today())[0:10]
        dia = fe[8:10]
        mes = fe[5:7]
        anio = fe[:4]
        meses = {
            '01': 'Enero',
            '02': 'Febrero',
            '03': 'Marzo',
            '04': 'Abril',
            '05': 'Mayo',
            '06': 'Junio',
            '07': 'Julio',
            '08': 'Agosto',
            '09': 'Septiembre',
            '10': 'Octubre',
            '11': 'Noviembre',
            '12': 'Diciembre',
        }
        fecha = str(dia + ' ' + meses[mes] + ' ' + anio)
        self.cell(80, 20, 'Asunto: Constancia de No Adeudo', 1, 0, 'R')
        self.ln(3)
        self.cell(100)
        self.cell(80, 20, 'Felipe Carrillo Puerto, a ' + fecha, 0, 0, 'R')
        self.ln(3)
        self.cell(100)
        self.cell(80, 20, '\"2018, año por una Educacion inclusiva \"', 0, 0, 'R')
        # Line break
        self.ln(20)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-35)
        # Arial italic 8
        self.set_font('Arial', 'B', 12)
        # Texto de pie de pagina
        self.cell(0, 10, 'Comision de Agua Potable y Alcantarillado', 0, 0, 'C')
        self.ln(5)
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, 'Calle 65 % 66 y 68 Col. Centro. C. P. 77200. Felipe Carrillo Puerto, Quintana Roo, Mexico.',
                  0, 0, 'C')
        self.ln(5)
        self.cell(0, 10, 'Tel.: (983) 83-02-46 Ext', 0, 0, 'C')
        self.ln(5)
        self.cell(0, 10, 'www.capa.gob.mx', 0, 0, 'C')
        self.ln(5)
        # Page number
        self.cell(0, 10, 'Página ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')


def letras():
    meses = {
        '01': 'Enero',
        '02': 'Febrero',
        '03': 'Marzo',
        '04': 'Abril',
        '05': 'Mayo',
        '06': 'Junio',
        '07': 'Julio',
        '08': 'Agosto',
        '09': 'Septiembre',
        '10': 'Octubre',
        '11': 'Noviembre',
        '12': 'Diciembre',
    }
    dias = {
        '01': 'Primero',
        '02': 'Dos',
        '03': 'Tres',
        '04': 'Cuatro',
        '05': 'Cinco',
        '06': 'Seis',
        '07': 'Siete',
        '08': 'Ocho',
        '09': 'Nueve',
        '10': 'Diez',
        '11': 'Once',
        '12': 'Doce',
        '13': 'Trece',
        '14': 'Catorce',
        '15': 'Quince',
        '16': 'Dieciseis',
        '17': 'Diecisiete',
        '18': 'Dieciocho',
        '19': 'Diecinueve',
        '20': 'Veinte',
        '21': 'VeintiUno',
        '22': 'VeintiDos',
        '23': 'VeintiTres',
        '24': 'VeintiCuatro',
        '25': 'VeintiCinco',
        '26': 'VeintiSeis',
        '27': 'VeintiSiete',
        '28': 'VeintiOcho',
        '29': 'VeintiNueve',
        '30': 'Treinta',
        '31': 'Treinta y uno',
    }
    anios = {
        '2018': 'Dos mil dieciocho',
        '2019': 'Dos mil diecinueve',
        '2020': 'Dos mil veinte',
        '2021': 'Dos mil veintiuno',
    }
    dia = str(datetime.today())[8:10]
    mes = str(datetime.today())[5:7]
    anio = str(datetime.today())[:4]

    return (dias[dia] + ' dias del mes de ' + meses[mes] + ' de ' + anios[anio]).upper()


def imprimir(**datos):
    # Instantiation of inherited class
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    #fe = str(datetime.today())[0:10]
    # Long meaningless piece of text
    loremipsum = """EL QUE SUSCRIBE, GERENTE DEL ORGANISMO OPERADOR FELIPE CARRILLO \
    PUERTO, HACE CONSTAR QUE EN LOS ARCHIVOS DE ESTE ORGANISMO A LA FECHA NO EXISTE\
    ADEUDO POR EL SERVICIO DE AGUA POTABLE Y ALCANTARILLADO DEL CONTRATO NUMERO %s A\
    NOMBRE DE %s CON LA DIRECCION EN LA %s, CON LA CEDULA CATASTRAL %s.\n
    POR LO ANTERIOR Y NO EXISTIENDO NINGUN INCONVENIENTE SE EXTIENDE LA PRESENTE A SOLICITUD\
    DEL USUARIO, PARA LOS USOS Y FINES LEGALES QUE CONVENGAN, FELIPE CARRILLO PUERTO\
    QUINTANA ROO A LOS %s.""" % (
    datos['contrato'], datos['nombre'].upper(), datos['direccion'].upper(), datos['cedula'], letras())
    pdf.ln(15)
    pdf.set_font('Arial', size=12)
    pdf.cell(0, 10, 'A QUIEN CORRESPONDA:', 0, 0, 'L')
    pdf.ln(25)
    pdf.set_font('Arial', size=10)
    pdf.multi_cell(180, 5.25, loremipsum, 'J')
    pdf.ln(25)
    pdf.cell(0, 10, 'A T E N T A M E N T E', 0, 0, 'C')
    pdf.ln(25)
    pdf.cell(0, 10, 'LIC. HENRY DAVID AMAYA BRICEÑO', 0, 0, 'C')
    pdf.ln(5)
    pdf.cell(0, 10, 'EN SUPLENCIA DEL C. JESUS MANUEL AGUILAR BE', 0, 0, 'C')
    pdf.ln(5)
    pdf.cell(0, 10, 'DESIGNADO MEDIANTE OFICIO CAPA/DG/CJ/0220/2019', 0, 0, 'C')
    pdf.ln(5)
    pdf.cell(0, 10, 'CON FECHA 28-02-2019', 0, 0, 'C')
    pdf.ln(10)
    pdf.set_font('Arial', size=8)
    pdf.cell(0, 10, 'C. C. P. ARCHIVO', 0, 0, 'L')
    pdf.ln(10)
    pdf.cell(0, 10, 'EMIS>Landeros', 0, 0, 'L')
    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=%s.pdf' % 'constancia'
    return response


def imprimir2(**datos):
    # Instantiation of inherited class
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    #fe = str(datetime.today())[0:10]
    # Long meaningless piece of text
    loremipsum = """EL QUE SUSCRIBE, GERENTE DEL ORGANISMO OPERADOR FELIPE CARRILLO \
    PUERTO, HACE CONSTAR QUE EN LOS ARCHIVOS DE ESTE ORGANISMO A LA FECHA NO EXISTE\
    CONTRATO POR EL SERVICIO DE AGUA POTABLE Y ALCANTARILLADO  A\
    NOMBRE DE %s CON LA DIRECCION EN LA %s, CON LA CEDULA CATASTRAL %s.\n
    POR LO ANTERIOR Y NO EXISTIENDO NINGUN INCONVENIENTE SE EXTIENDE LA PRESENTE A SOLICITUD\
    DEL USUARIO, PARA LOS USOS Y FINES LEGALES QUE CONVENGAN, FELIPE CARRILLO PUERTO\
    QUINTANA ROO A LOS %s.""" % (
    datos['nombre'].upper(), datos['direccion'].upper(), datos['cedula'], letras())
    pdf.ln(15)
    pdf.set_font('Arial', size=12)
    pdf.cell(0, 10, 'A QUIEN CORRESPONDA:', 0, 0, 'L')
    pdf.ln(25)
    pdf.set_font('Arial', size=10)
    pdf.multi_cell(180, 5.25, loremipsum, 'J')
    pdf.ln(25)
    pdf.cell(0, 10, 'A T E N T A M E N T E', 0, 0, 'C')
    pdf.ln(25)
    pdf.cell(0, 10, 'LIC. HENRY DAVID AMAYA BRICEÑO', 0, 0, 'C')
    pdf.ln(5)
    pdf.cell(0, 10, 'EN SUPLENCIA DEL C. JESUS MANUEL AGUILAR BE', 0, 0, 'C')
    pdf.ln(5)
    pdf.cell(0, 10, 'DESIGNADO MEDIANTE OFICIO CAPA/DG/CJ/0220/2019', 0, 0, 'C')
    pdf.ln(5)
    pdf.cell(0, 10, 'CON FECHA 28-02-2019', 0, 0, 'C')
    pdf.ln(10)
    pdf.set_font('Arial', size=8)
    pdf.cell(0, 10, 'C. C. P. ARCHIVO', 0, 0, 'L')
    pdf.ln(10)
    pdf.cell(0, 10, 'EMIS>Landeros', 0, 0, 'R')
    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=%s.pdf' % 'constancia'
    return response