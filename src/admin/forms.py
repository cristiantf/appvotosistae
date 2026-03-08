from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, SelectField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from src.models import Voter

class FileUploadForm(FlaskForm):
    file = FileField('Archivo Excel', validators=[DataRequired()])
    submit = SubmitField('Subir')

class ElectionPeriodForm(FlaskForm):
    name = StringField('Nombre del Período Electoral', validators=[DataRequired()])
    submit = SubmitField('Crear Período')

class CandidateListForm(FlaskForm):
    name = StringField('Nombre de la Lista', validators=[DataRequired()])
    submit = SubmitField('Crear Lista')

class CandidateForm(FlaskForm):
    voter = SelectField('Votante', coerce=int, validators=[DataRequired()])
    dignity = StringField('Dignidad', validators=[DataRequired()])
    submit = SubmitField('Añadir Candidato')

class VoterForm(FlaskForm):
    name = StringField('Nombres', validators=[DataRequired()])
    lastname = StringField('Apellidos', validators=[DataRequired()])
    cedula = StringField('Cédula', validators=[DataRequired()])
    submit = SubmitField('Guardar Cambios')

    def __init__(self, original_cedula, *args, **kwargs):
        super(VoterForm, self).__init__(*args, **kwargs)
        self.original_cedula = original_cedula

    def validate_cedula(self, cedula):
        if cedula.data != self.original_cedula:
            voter = Voter.query.filter_by(cedula=cedula.data).first()
            if voter:
                raise ValidationError('Esta cédula ya está registrada. Por favor, use una diferente.')
