from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_view = 'auth.login'

    with app.app_context():
        from src import models # Import models here

        from src.auth import bp as auth_blueprint
        app.register_blueprint(auth_blueprint, url_prefix='/auth')

        from src.main import bp as main_blueprint
        app.register_blueprint(main_blueprint)

        from src.admin import bp as admin_blueprint
        app.register_blueprint(admin_blueprint, url_prefix='/admin')

        from src.voto import bp as voto_blueprint
        app.register_blueprint(voto_blueprint, url_prefix='/vote')

    return app
