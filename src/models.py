
from src import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

voter_period_association = db.Table('voter_period_association',
    db.Column('voter_id', db.Integer, db.ForeignKey('voter.id')),
    db.Column('election_period_id', db.Integer, db.ForeignKey('election_period.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    name = db.Column(db.String(128), nullable=True)
    lastname = db.Column(db.String(128), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_superadmin = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(256))
    profile_picture = db.Column(db.String(256), nullable=True, default='uploads/profile_pics/default_avatar.png')
    voter_id = db.Column(db.Integer, db.ForeignKey('voter.id'))
    voter = db.relationship('Voter', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class Voter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(128))
    lastname = db.Column(db.String(128))
    face_descriptor = db.Column(db.Text, nullable=True) # Almacena el Array[128] en JSON
    participations = db.relationship('VoterParticipation', backref='voter', lazy='dynamic', cascade="all, delete-orphan")
    candidate_info = db.relationship('Candidate', backref='voter_info', uselist=False)

class ElectionPeriod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    backup_generated = db.Column(db.Boolean, default=False)
    voters = db.relationship('Voter', secondary=voter_period_association, backref='election_periods')
    lists = db.relationship('CandidateList', backref='election_period', lazy='dynamic', cascade="all, delete-orphan")
    votes = db.relationship('Vote', backref='election_period', lazy='dynamic', cascade="all, delete-orphan")
    participations = db.relationship('VoterParticipation', backref='election_period', lazy='dynamic', cascade="all, delete-orphan")
    dignities = db.relationship('Dignity', backref='election_period', lazy='dynamic', cascade="all, delete-orphan")

    @property
    def current_status(self):
        from datetime import datetime
        if not self.is_active:
            return 'manual_inactive'
        
        now = datetime.now()
        
        if self.start_date and now < self.start_date:
            return 'pending'
            
        if self.end_date and now > self.end_date:
            return 'finished'
            
        return 'active'

    @property
    def is_voting_open(self):
        return self.current_status == 'active'

class Dignity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    election_period_id = db.Column(db.Integer, db.ForeignKey('election_period.id'), nullable=False)

class CandidateList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    image = db.Column(db.String(256), nullable=True)
    election_period_id = db.Column(db.Integer, db.ForeignKey('election_period.id'), nullable=False)
    candidates = db.relationship('Candidate', backref='candidate_list', lazy='dynamic', cascade="all, delete-orphan")
    votes = db.relationship('Vote', backref='candidate_list', lazy='dynamic', cascade="all, delete-orphan")

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    dignity_id = db.Column(db.Integer, db.ForeignKey('dignity.id'), nullable=True)
    dignity = db.relationship('Dignity')
    image = db.Column(db.String(256), nullable=True)
    candidate_list_id = db.Column(db.Integer, db.ForeignKey('candidate_list.id'), nullable=False)
    voter_id = db.Column(db.Integer, db.ForeignKey('voter.id'), nullable=False)

class VoterParticipation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voter_id = db.Column(db.Integer, db.ForeignKey('voter.id'), nullable=False)
    election_period_id = db.Column(db.Integer, db.ForeignKey('election_period.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    election_period_id = db.Column(db.Integer, db.ForeignKey('election_period.id'), nullable=False)
    candidate_list_id = db.Column(db.Integer, db.ForeignKey('candidate_list.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(256), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text, nullable=True)
    user = db.relationship('User', backref=db.backref('audit_logs', lazy=True, cascade="all, delete-orphan"))

class SystemSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    registration_enabled = db.Column(db.Boolean, default=True)
    registration_start_date = db.Column(db.DateTime, nullable=True)
    registration_end_date = db.Column(db.DateTime, nullable=True)

    @property
    def is_registration_open(self):
        if not self.registration_enabled:
            return False
            
        now = datetime.now()
        
        if self.registration_start_date and now < self.registration_start_date:
            return False
            
        if self.registration_end_date and now > self.registration_end_date:
            return False
            
        return True
