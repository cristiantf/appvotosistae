
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
# The login view is now in the 'auth' blueprint
login_manager.login_view = 'auth.login'
migrate = Migrate()
scheduler = APScheduler(scheduler=BackgroundScheduler(timezone="UTC"))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    app.config['SCHEDULER_API_ENABLED'] = False
    scheduler.init_app(app)

    with app.app_context():
        # Register blueprints
        from src.main import bp as main_bp
        app.register_blueprint(main_bp)

        from src.auth import bp as auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')

        from src.admin import bp as admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')

        from src.voting import bp as voting_bp
        app.register_blueprint(voting_bp, url_prefix='/voting')

        # Iniciar Scheduler si no está corriendo
        if not scheduler.running:
            scheduler.start()
            
            # Registrar Job para respaldos
            @scheduler.task('interval', id='auto_backup_job', minutes=1, misfire_grace_time=900)
            def auto_backup_job():
                from src.models import ElectionPeriod
                from src.backup import generate_election_backup
                from datetime import datetime
                
                with scheduler.app.app_context():
                    now = datetime.now()
                    # Buscar elecciones que terminaron y no han sido respaldadas
                    finished_periods = ElectionPeriod.query.filter(
                        ElectionPeriod.end_date < now,
                        ElectionPeriod.backup_generated == False,
                        ElectionPeriod.is_active == True
                    ).all()
                    
                    for period in finished_periods:
                        try:
                            generate_election_backup(period.id)
                            print(f"[Backup Auto] Respaldo generado para la elección: {period.name}")
                        except Exception as e:
                            print(f"[Backup Auto Error] {e}")

    # Import and register CLI commands
    from src import commands
    app.cli.add_command(commands.clean_orphans)

    @app.context_processor
    def inject_settings():
        from src.models import SystemSettings
        try:
            settings = SystemSettings.query.first()
            if not settings:
                settings = SystemSettings()
                db.session.add(settings)
                db.session.commit()
            return dict(settings=settings)
        except Exception:
            return dict(settings=None)

    return app

from src import models
