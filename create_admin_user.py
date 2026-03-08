
from src import create_app, db
from src.models import User

app = create_app()

with app.app_context():
    if not User.query.filter_by(username='admin2').first():
        admin_user = User(username='admin2', is_admin=True)
        admin_user.set_password('12345678')
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user 'admin2' created successfully.")
    else:
        print("Admin user 'admin2' already exists.")
