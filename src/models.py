
from src import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

voter_period_association = db.Table('voter_period_association',
    db.Column('voter_id', db.Integer, db.ForeignKey('voter.id')),
    db.Column('election_period_id', db.Integer, db.ForeignKey('election_period.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    is_admin = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(256))
    voter_id = db.Column(db.Integer, db.ForeignKey('voter.id'))

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
    votes = db.relationship('Vote', backref='voter', lazy='dynamic', cascade="all, delete-orphan")
    candidate_info = db.relationship('Candidate', backref='voter_info', uselist=False)

class ElectionPeriod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    voters = db.relationship('Voter', secondary=voter_period_association, backref='election_periods')
    lists = db.relationship('CandidateList', backref='election_period', lazy='dynamic', cascade="all, delete-orphan")
    votes = db.relationship('Vote', backref='election_period', lazy='dynamic', cascade="all, delete-orphan")

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
    dignity = db.Column(db.String(128))
    image = db.Column(db.String(256), nullable=True)
    candidate_list_id = db.Column(db.Integer, db.ForeignKey('candidate_list.id'), nullable=False)
    voter_id = db.Column(db.Integer, db.ForeignKey('voter.id'), nullable=False)

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voter_id = db.Column(db.Integer, db.ForeignKey('voter.id'), nullable=False)
    election_period_id = db.Column(db.Integer, db.ForeignKey('election_period.id'), nullable=False)
    candidate_list_id = db.Column(db.Integer, db.ForeignKey('candidate_list.id'), nullable=False)
