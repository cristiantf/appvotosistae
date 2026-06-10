from dotenv import load_dotenv
load_dotenv()

from main import app
from src import db
from src.models import User, Voter

with app.app_context():
    # Ensure they don't already exist
    for c in ['0000000001', '0000000002', '0000000003']:
        v = Voter.query.filter_by(cedula=c).first()
        if v:
            db.session.delete(v)
            
    for u in ['superadmin', 'admin', 'usuario']:
        user = User.query.filter_by(username=u).first()
        if user:
            db.session.delete(user)
    db.session.commit()

    # Create Voters
    v1 = Voter(cedula='0000000001', name='Super', lastname='Admin')
    v2 = Voter(cedula='0000000002', name='Admin', lastname='Normal')
    v3 = Voter(cedula='0000000003', name='Usuario', lastname='Estudiante')
    
    db.session.add_all([v1, v2, v3])
    db.session.commit()
    
    # Create Users
    u1 = User(username='superadmin', is_admin=True, voter_id=v1.id)
    u1.set_password('superadmin')
    
    u2 = User(username='admin', is_admin=True, voter_id=v2.id)
    u2.set_password('admin')
    
    u3 = User(username='usuario', is_admin=False, voter_id=v3.id)
    u3.set_password('usuario')
    
    db.session.add_all([u1, u2, u3])
    db.session.commit()
    print("Users created successfully!")
