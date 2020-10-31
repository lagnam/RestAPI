import pytest

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
    resp = client.post("/theatre/test_theatre", json={'screens': 10, 'location': 'test'})
    resp_json = resp.json

    assert resp.status_code == 201
    assert resp_json["name"] == "test_theatre"


def test_get(client):
    resp = client.get("/theatre/theatre1")
    resp_json = resp.json

    assert resp.status_code == 200
    assert resp_json["name"] == "theatre1"
    assert resp_json["screens"] == 2
    assert resp_json["location"] == "hyd"


def test_update_all(client):
    resp = client.put("/theatre/theatre1", json={'name': 'test_update', 'screens': 10, 'location': 'test'})

    assert resp.status_code == 204

    resp = client.get("/theatre/test_update")
    resp_json = resp.json

    assert resp.status_code == 200
    assert resp_json["name"] == "test_update"
    assert resp_json["screens"] == 10
    assert resp_json["location"] == "test"


def test_update_name(client):
    resp = client.put("/theatre/theatre1", json={'name': 'test_update'})

    assert resp.status_code == 204

    resp = client.get("/theatre/test_update")
    resp_json = resp.json

    assert resp.status_code == 200
    assert resp_json["name"] == "test_update"
    assert resp_json["screens"] == 2
    assert resp_json["location"] == "hyd"


def test_update_screen(client):
    resp = client.put("/theatre/theatre1", json={'screens': 10})

    assert resp.status_code == 204

    resp = client.get("/theatre/theatre1")
    resp_json = resp.json

    assert resp.status_code == 200
    assert resp_json["name"] == "theatre1"
    assert resp_json["screens"] == 10
    assert resp_json["location"] == "hyd"


update_multiple_params = [
    ({'screens': 5, 'location': 'test1'}, {"name": "theatre1", "screens": 5, "location": "test1"}),
    ({'name': 'test_update1', 'screens': 10}, {"name": "test_update1", "screens": 10, "location": "hyd"}),
    ({'name': 'test_update2', 'location': 'test2'}, {"name": "test_update2", "screens": 2, "location": "test2"})
]


@pytest.mark.parametrize("json_params, expected_resp", update_multiple_params)
def test_update_multiple_params(client, json_params, expected_resp):
    resp = client.put("/theatre/theatre1", json=json_params)

    assert resp.status_code == 204

    resp = client.get(f"/theatre/{expected_resp['name']}")
    resp_json = resp.json

    assert resp.status_code == 200
    assert resp_json["name"] == expected_resp["name"]
    assert resp_json["screens"] == expected_resp["screens"]
    assert resp_json["location"] == expected_resp["location"]


def test_delete(client):
    resp = client.delete("/theatre/test")
    assert resp.status_code == 204


def test_create_with_missing_params(client):
    resp = client.post("/theatre/theatre1")
    assert resp.status_code == 400

    resp = client.post("/theatre/theatre1", json={'location': 'test2'})
    assert resp.status_code == 400

    resp = client.post("/theatre/theatre1", json={'screens': 10})
    assert resp.status_code == 400


def test_create_duplicate_error(client):
    resp = client.post("/theatre/theatre1", json={'screens': 0, 'location': 'test'})
    assert resp.status_code == 400


def test_create_with_invalid_screens(client):
    resp = client.post("/theatre/theatre", json={'screens': 0, 'location': 'test'})
    assert resp.status_code == 400

    resp = client.post("/theatre/theatre", json={'screens': -1, 'location': 'test'})
    assert resp.status_code == 400


def test_get_error(client):
    resp = client.get("/theatre/theatre")
    assert resp.status_code == 404


def test_update_unkown_name(client):
    resp = client.put("/theatre/theatre", json={'name': 'test_update', 'screens': 10, 'location': 'test'})
    assert resp.status_code == 404


def test_update_missing_params(client):
    resp = client.put("/theatre/theatre1")
    assert resp.status_code == 400


def test_update_screens_error(client):
    resp = client.put("/theatre/theatre1", json={'name': 'test_update', 'screens': 1, 'location': 'test'})
    assert resp.status_code == 400

    resp = client.put("/theatre/theatre1", json={'name': 'test_update', 'screens': 0, 'location': 'test'})
    assert resp.status_code == 400

    resp = client.put("/theatre/theatre1", json={'name': 'test_update', 'screens': -1, 'location': 'test'})
    assert resp.status_code == 400


def test_delete_with_existing_schedules(client):
    resp = client.delete("/theatre/theatre1")

    assert resp.status_code == 400


def test_delete_unkown_movie(client):
    resp = client.delete("/theatre/theatre")

    assert resp.status_code == 404