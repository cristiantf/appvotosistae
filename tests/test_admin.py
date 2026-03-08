
from flask import url_for

def test_admin_dashboard_access(client, admin_user):
    with client:
        client.post(url_for('auth.login'), data={
            'username': 'admin',
            'password': 'admin'
        }, follow_redirects=True)

        response = client.get(url_for('admin.index'))
        assert response.status_code == 200

def test_create_election_period(client, admin_user):
    with client:
        client.post(url_for('auth.login'), data={
            'username': 'admin',
            'password': 'admin'
        }, follow_redirects=True)

        response = client.post(url_for('admin.manage_elections'), data={
            'name': 'Test Election 2024'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'New election period has been created.' in response.data

def test_admin_dashboard_unauthorized_access(client, regular_user):
    with client:
        client.post(url_for('auth.login'), data={
            'username': 'user',
            'password': 'user'
        }, follow_redirects=True)

        response = client.get(url_for('admin.index'))
        assert response.status_code == 302
        assert response.location == url_for('main.index', _external=False)

        # Follow the redirect and check for the flash message
        response = client.get(url_for('admin.index'), follow_redirects=True)
        assert b'You do not have permission to access this page.' in response.data
