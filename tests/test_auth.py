from flask import url_for
from src.models import User

def test_login_success(client, regular_user):
    with client:
        # Act: Enviar credenciales correctas
        response = client.post(url_for('auth.login'), data={
            'username': 'user',
            'password': 'user_password'
        }, follow_redirects=True)
        
        # Assert: Código 200 y comprobación visual HTML
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert '¡Hola, user!' in html
        assert 'Cerrar Sesión' in html

def test_login_failure(client, regular_user):
    with client:
        # Act: Enviar credenciales incorrectas
        response = client.post(url_for('auth.login'), data={
            'username': 'user',
            'password': 'wrong_password'
        }, follow_redirects=True)
        
        # Assert: Código 200 (se carga el formulario de nuevo con error)
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert 'Usuario o contraseña inválidos' in html

def test_logout(client, regular_user):
    with client:
        # Primero hace login
        client.post(url_for('auth.login'), data={
            'username': 'user',
            'password': 'user_password'
        }, follow_redirects=True)
        
        # Luego hace logout
        response = client.get(url_for('auth.logout'), follow_redirects=True)
        
        # Assert: Se redirige al index/login y no está el menú de usuario
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert 'Iniciar Sesión' in html
