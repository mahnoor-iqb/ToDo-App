import re
import json


def test_get_all_tasks(client):
    resp = client.post(
        '/login', json={'email': 'testuser@gmail.com', 'password': 'password'})

    assert resp.status_code == 200

    access_token = re.findall(r'access_token=(.*);',
                              resp.headers.get("Set-cookie"))

    client.set_cookie('access_token', access_token[0])
    resp = client.get('/tasks/')
    tasks = json.loads(resp.data.decode('utf-8')).get("payload")
    assert resp.status_code == 200
    assert len(tasks) == 2

    resp = client.get('/logout/')
    assert resp.status_code == 200


def test_missing_access_token(client):
    resp = client.get('/tasks/')
    assert b'"success": false' in resp.data
    assert b'"error": "Access token not provided!"' in resp.data