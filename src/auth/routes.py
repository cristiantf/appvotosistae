from flask import render_template, flash, redirect, url_for
from flask_login import login_user, logout_user, current_user
from src import db
from src.auth import bp
from src.auth.forms import LoginForm, CreateAdminForm
from src.models import User

@bp.route('/create_admin', methods=['GET', 'POST'])
def create_admin():
    if User.query.filter_by(is_admin=True).first():
        flash('An admin user already exists.')
        return redirect(url_for('main.index'))

    form = CreateAdminForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, is_admin=True)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Admin user created successfully.')
        return redirect(url_for('admin.index'))
    return render_template('create_admin.html', title='Create Admin', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.index'))
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return render_template('login.html', title='Sign In', form=form)
        login_user(user)
        if user.is_admin:
            return redirect(url_for('admin.index'))
        return redirect(url_for('main.index'))
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
