from flask import url_for
from src.models import User
from src import db

def test_profile_access(client, regular_user):
    # Sin sesión: debería redirigir a login
    response = client.get(url_for('main.profile'), follow_redirects=True)
    html = response.data.decode('utf-8')
    assert 'Please log in to access this page.' in html

    # Con sesión: debería cargar perfil
    client.post(url_for('auth.login'), data={
        'username': 'user',
        'password': 'user_password'
    }, follow_redirects=True)
    
    response = client.get(url_for('main.profile'))
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'Configuración de Cuenta' in html

def test_password_change_success(client, app, regular_user):
    with client:
        client.post(url_for('auth.login'), data={
            'username': 'user',
            'password': 'user_password'
        }, follow_redirects=True)
        
        # Cambiar contraseña correctamente
        response = client.post(url_for('main.profile'), data={
            'current_password': 'user_password',
            'new_password': 'new_secure_password',
            'confirm_new_password': 'new_secure_password'
        }, follow_redirects=True)
        
        # Validar UI
        html = response.data.decode('utf-8')
        assert 'Tu perfil ha sido actualizado con éxito.' in html
        
        # Validar BD puramente Backend
        with app.app_context():
            user = User.query.filter_by(username='user').first()
            assert user.check_password('new_secure_password') == True
            assert user.check_password('user_password') == False

def test_password_change_failure(client, app, regular_user):
    with client:
        client.post(url_for('auth.login'), data={
            'username': 'user',
            'password': 'user_password'
        }, follow_redirects=True)
        
        # Cambiar contraseña con clave actual errónea
        response = client.post(url_for('main.profile'), data={
            'current_password': 'wrong_current_password',
            'new_password': 'new_secure_password',
            'confirm_new_password': 'new_secure_password'
        }, follow_redirects=True)
        
        # Validar UI
        html = response.data.decode('utf-8')
        assert 'La contraseña actual es incorrecta.' in html
        
        # Validar BD puramente Backend
        with app.app_context():
            user = User.query.filter_by(username='user').first()
            assert user.check_password('new_secure_password') == False
            assert user.check_password('user_password') == True
