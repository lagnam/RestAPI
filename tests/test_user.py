from flask_testing import TestCase

from app import app
from db import db
from init_db import initialize_db


def setup_function():
    print("setup")
    db.create_all()
    initialize_db()
    print("done")


def teardown_function() -> None:
    db.drop_all()
    
    
def test_create(client):
    resp = client.post("/user/user1", json={'type': 'user'})
    resp_json = resp.json

    assert resp.status_code == 201
    assert resp_json["name"] == "user1"
    assert resp_json["type"] == "user"


def test_get(client):
    resp = client.get("/user/admin")
    resp_json = resp.json

    assert resp.status_code == 200
    assert resp_json["name"] == "admin"
    assert resp_json["type"] == "admin"


def test_update_all(client):
    resp = client.put("/user/user", json={'name': 'test_update', 'type': 'admin'})

    assert resp.status_code == 204

    resp = client.get("/user/test_update")
    resp_json = resp.json

    assert resp.status_code == 200
    assert resp_json["name"] == "test_update"
    assert resp_json["type"] == "admin"


def test_update_name(client):
    resp = client.put("/user/user", json={'name': 'test_update'})

    assert resp.status_code == 204

    resp = client.get("/user/test_update")
    resp_json = resp.json

    assert resp.status_code == 200
    assert resp_json["name"] == "test_update"
    assert resp_json["type"] == "user"


def test_update_type(client):
    resp = client.put("/user/user", json={'type': 'owner'})

    assert resp.status_code == 204

    resp = client.get("/user/user")
    resp_json = resp.json

    assert resp.status_code == 200
    assert resp_json["name"] == "user"
    assert resp_json["type"] == "owner"


def test_create_with_missing_params(client):
    resp = client.post("/user/user1")
    assert resp.status_code == 400


def test_create_duplicate_error(client):
    resp = client.post("/user/user", json={'type': 'owner'})
    assert resp.status_code == 400


def test_get_unkown_name(client):
    resp = client.get("/user/user1")
    assert resp.status_code == 404


def test_update_unkown_name(client):
    resp = client.put("/user/user1", json={'type': 'owner'})
    assert resp.status_code == 404


def test_update_missing_params(client):
    resp = client.put("/user/user")
    assert resp.status_code == 400