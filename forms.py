from wtforms import Form
from wtforms import StringField, TextField
from wtforms.fields.html5 import EmailField
from wtforms import PasswordField
from wtforms import HiddenField
from wtforms import validators
from models import User

def length_honeypot(form, field):
	if len(field.data) > 0:
		raise validators.ValidationError('El Campo debe estar vacio.')

class Create_Form(Form):
    username = StringField('Username',
    	[validators.Required(message = 'El user es requerido!.'),
    	validators.length(min=4, max=50, message='ingrese un username valido!.')
    	])
    password = PasswordField('Password', [validators.Required(message='El password es Indispensable!.')])
    email = EmailField('Correo electronico',
        [validators.Required(message = 'El Email es requerido!.'),
        validators.Email(message='Ingrese un email valido!.'),
        validators.length(min=4, max=50, message='Ingrese un email valido!.')
        ])
    #honeypot= HiddenField('',[length_honeypot])
    
    def validate_username(form, field):
        username = field.data
        user = User.query.filter_by(username = username).first()
        if user is not None:
            raise validators.ValidationError('El usuario ya existe en la base de datos.')


class LoginForm(Form):
	username = StringField('username',
		[validators.Required(message = 'El userename es Requerido!.'),
		validators.length(min= 4, max=25, message= 'ingrese un username valido!.')
		])
	password = PasswordField('Password', [validators.Required(message='El password es Requerido!.')])