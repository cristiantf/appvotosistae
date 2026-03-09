
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
# The login view is now in the 'auth' blueprint
login_manager.login_view = 'auth.login'
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from src.main import bp as main_bp
    app.register_blueprint(main_bp)

    from src.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from src.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from src.voting import bp as voting_bp
    app.register_blueprint(voting_bp, url_prefix='/voting')

    # Import and register CLI commands
    from src import commands
    app.cli.add_command(commands.clean_orphans)

    return app

from src import models
