def test_index(client):
    """Test the index page."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to the Voting App' in response.data
