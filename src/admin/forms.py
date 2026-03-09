
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField, FileField
from wtforms.validators import DataRequired, ValidationError, Optional
from src.models import Voter, ElectionPeriod
from flask_wtf.file import FileAllowed

class FileUploadForm(FlaskForm):
    file = FileField('CSV File', validators=[DataRequired(), FileAllowed(['csv', 'xlsx'], 'CSV or Excel files only!')])
    submit = SubmitField('Upload')

class ElectionPeriodForm(FlaskForm):
    name = StringField('Election Period Name', validators=[DataRequired()])
    submit = SubmitField('Create Period')

class CandidateListForm(FlaskForm):
    name = StringField('List Name', validators=[DataRequired()])
    image = FileField('List Image', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Create List')

class AddCandidateForm(FlaskForm):
    dignity = StringField('Dignity', validators=[DataRequired()])
    voter = SelectField('Voter', coerce=int, validators=[DataRequired()])
    image = FileField('Candidate Image', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Add Candidate')

    def __init__(self, *args, **kwargs):
        super(AddCandidateForm, self).__init__(*args, **kwargs)
        self.voter.choices = []

class EditCandidateForm(FlaskForm):
    dignity = StringField('Dignity', validators=[DataRequired()])
    image = FileField('New Candidate Image', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Update Candidate')

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
