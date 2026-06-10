def test_index(client):
    """Test the index page."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Voting System' in response.data
