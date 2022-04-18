
def test_signup(client):
    resp = client.post('/signup', json={'email': 'some@thing.com', 'password': 'abcd.1234'})
    assert resp.status_code == 200
    assert b'"success": true' in resp.data


def test_email_missing(client):
    resp = client.post('/signup', json={'password': 'abcxyz'})
    assert b'"success": false' in resp.data
    assert b'"error": "Email not provided!"' in resp.data