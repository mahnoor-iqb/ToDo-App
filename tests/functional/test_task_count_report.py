
import re
import json


def test_task_count_report(client):
    resp = client.post(
        '/login', json={'email': 'testuser@gmail.com', 'password': 'password'})

    assert resp.status_code == 200

    access_token = re.findall(r'access_token=(.*);',
                              resp.headers.get("Set-cookie"))

    client.set_cookie('access_token', access_token[0])
    resp = client.get('/reports/task-count')
    assert resp.status_code == 200
    
    report = json.loads(resp.data.decode('utf-8')).get("payload")
    assert report["completed_tasks"] == 1
    assert report["remaining_tasks"] == 1
    assert report["total_tasks"] == 2

    resp = client.get('/logout/')
    assert resp.status_code == 200


def test_bad_http_method(client):
    resp = client.post('/reports/task-count')
    assert b'"success": false' in resp.data
    assert b'"error": "The method is not allowed for the requested URL."' in resp.data
