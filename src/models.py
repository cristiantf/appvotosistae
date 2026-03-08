
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
    has_voted = db.Column(db.Boolean, default=False)
    votes = db.relationship('Vote', backref='voter', lazy=True)

class ElectionPeriod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    voters = db.relationship('Voter', secondary=voter_period_association, backref='election_periods')

class CandidateList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    election_period_id = db.Column(db.Integer, db.ForeignKey('election_period.id'))
    candidates = db.relationship('Candidate', backref='candidate_list', lazy=True)

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    dignity = db.Column(db.String(128))
    candidate_list_id = db.Column(db.Integer, db.ForeignKey('candidate_list.id'))
    voter_id = db.Column(db.Integer, db.ForeignKey('voter.id'))
    votes = db.Column(db.Integer, default=0)
    voter = db.relationship('Voter', backref='candidates')

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voter_id = db.Column(db.Integer, db.ForeignKey('voter.id'))
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'))
    election_period_id = db.Column(db.Integer, db.ForeignKey('election_period.id'))
    location = db.Column(db.String(256))
    photo = db.Column(db.String(256))
