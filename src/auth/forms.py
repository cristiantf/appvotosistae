from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from src.models import User, Voter

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recuérdame')
    submit = SubmitField('Acceder')

class RegistrationForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    cedula = StringField('Cédula', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    password2 = PasswordField(
        'Repetir Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrarse')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Por favor, utiliza un nombre de usuario diferente.')

    def validate_cedula(self, cedula):
        voter = Voter.query.filter_by(cedula=cedula.data).first()
        if voter is None:
            raise ValidationError('Esta cédula no se encuentra en el padrón electoral.')
        user = User.query.filter_by(voter_id=voter.id).first()
        if user is not None:
            raise ValidationError('Esta cédula ya tiene un usuario asociado.')

class CreateAdminForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Crear Administrador')

from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import Optional

class UserProfileForm(FlaskForm):
    current_password = PasswordField('Contraseña Actual', validators=[DataRequired()])
    new_password = PasswordField('Nueva Contraseña', validators=[Optional()])
    confirm_new_password = PasswordField(
        'Confirmar Nueva Contraseña', validators=[EqualTo('new_password', message='Las contraseñas deben coincidir.')]
    )
    profile_picture = FileField('Foto de Perfil', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Solo se permiten imágenes (JPG, PNG).')
    ])
    submit = SubmitField('Actualizar Perfil')
