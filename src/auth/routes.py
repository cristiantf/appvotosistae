from flask import render_template, flash, redirect, url_for, request, session
from flask_login import login_user, logout_user, current_user

from src.auth import bp
from src.auth.forms import LoginForm, RegistrationForm
from src.models import User, Voter
from src import db

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.admin_dashboard'))
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Usuario o contraseña inválidos', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            if user.is_admin:
                # Corrected redirect for admin users
                next_page = url_for('admin.admin_dashboard')
            else:
                next_page = url_for('main.index')
        return redirect(next_page)
        
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    session.pop('impersonator_id', None)
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    from src.models import SystemSettings
    settings = SystemSettings.query.first()
    if settings and not settings.is_registration_open:
        flash('El registro de nuevos usuarios está deshabilitado temporalmente.', 'warning')
        return redirect(url_for('auth.login'))

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if voter exists and is not already linked
        voter = Voter.query.filter_by(cedula=form.cedula.data).first()
        if not voter:
            flash('Cédula no encontrada en el padrón electoral.', 'danger')
            return render_template('auth/register.html', title='Register', form=form)

        existing_user = User.query.filter_by(voter_id=voter.id).first()
        if existing_user:
            flash('Este votante ya tiene una cuenta de usuario asociada.', 'warning')
            return redirect(url_for('auth.login'))

        user = User(username=form.username.data, voter_id=voter.id)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('¡Felicidades, ahora eres un usuario registrado!', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', title='Register', form=form)
