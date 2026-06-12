
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField, FileField, PasswordField
from wtforms.validators import DataRequired, ValidationError, Optional
from src.models import Voter, ElectionPeriod, User
from flask_wtf.file import FileAllowed

class FileUploadForm(FlaskForm):
    file = FileField('CSV File', validators=[DataRequired(), FileAllowed(['csv', 'xlsx'], 'CSV or Excel files only!')])
    submit = SubmitField('Upload')

from wtforms import StringField, SubmitField, BooleanField, SelectField, FileField, PasswordField, DateTimeLocalField
from wtforms.validators import DataRequired, ValidationError, Optional

class ElectionPeriodForm(FlaskForm):
    name = StringField('Nombre del Periodo', validators=[DataRequired()])
    start_date = DateTimeLocalField('Fecha y Hora de Inicio', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    end_date = DateTimeLocalField('Fecha y Hora de Cierre', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    submit = SubmitField('Guardar Periodo')

class CandidateListForm(FlaskForm):
    name = StringField('List Name', validators=[DataRequired()])
    image = FileField('List Image', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Create List')

class DignityForm(FlaskForm):
    name = StringField('Dignity Name', validators=[DataRequired()])
    submit = SubmitField('Save Dignity')

class AddCandidateForm(FlaskForm):
    dignity = SelectField('Dignity', coerce=int, validators=[DataRequired()])
    voter = SelectField('Voter', coerce=int, validators=[DataRequired()])
    image = FileField('Candidate Image', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Add Candidate')

    def __init__(self, *args, **kwargs):
        super(AddCandidateForm, self).__init__(*args, **kwargs)
        self.voter.choices = []
        self.dignity.choices = []

class EditCandidateForm(FlaskForm):
    dignity = SelectField('Dignity', coerce=int, validators=[DataRequired()])
    image = FileField('New Candidate Image', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Update Candidate')
    
    def __init__(self, *args, **kwargs):
        super(EditCandidateForm, self).__init__(*args, **kwargs)
        self.dignity.choices = []

class VoterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])
    cedula = StringField('Cédula', validators=[DataRequired()])
    submit = SubmitField('Update Voter')

    def __init__(self, original_cedula=None, *args, **kwargs):
        super(VoterForm, self).__init__(*args, **kwargs)
        self.original_cedula = original_cedula

    def validate_cedula(self, cedula):
        if cedula.data != self.original_cedula:
            voter = Voter.query.filter_by(cedula=cedula.data).first()
            if voter:
                raise ValidationError('This cédula is already in use. Please choose a different one.')

class EditUserForm(FlaskForm):
    username = StringField('Username (Cédula)', validators=[DataRequired()])
    password = PasswordField('Nueva Contraseña (dejar en blanco para mantener la actual)')
    submit = SubmitField('Actualizar Usuario')

    def __init__(self, original_username=None, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Este nombre de usuario ya está en uso.')

class CreateUserForm(FlaskForm):
    username = StringField('Username (Ej: Cédula o Alias)', validators=[DataRequired()])
    name = StringField('Nombres', validators=[DataRequired()])
    lastname = StringField('Apellidos', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    is_admin = BooleanField('Hacer Administrador')
    submit = SubmitField('Crear Usuario')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nombre de usuario ya está en uso.')

class SystemSettingsForm(FlaskForm):
    registration_enabled = BooleanField('Habilitar Registro de Usuarios')
    registration_start_date = DateTimeLocalField('Fecha de Inicio (Opcional)', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    registration_end_date = DateTimeLocalField('Fecha de Fin (Opcional)', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    submit = SubmitField('Guardar Configuración')
