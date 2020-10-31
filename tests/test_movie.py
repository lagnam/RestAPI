from db import db
from init_db import initialize_db


def setup_function():
    print("setup")
    db.create_all()
    initialize_db()
    print("done")


def teardown_function() -> None:
    db.drop_all()


def test_create( client):
    resp = client.post("/movie/test_movie", json={'genre': 'test'})
    resp_json = resp.json

    assert resp.status_code == 201
    assert resp_json["name"] == "test_movie"


def test_get( client):
    resp = client.get("/movie/avengers1")
    resp_json = resp.json

    assert resp.status_code == 200
    assert resp_json["name"] == "avengers1"
    assert resp_json["genre"] == "gnr1"


def test_update( client):
    resp = client.put("/movie/avengers1", json={'name': 'test_update', 'genre': 'test_update'})

    assert resp.status_code == 204

    resp = client.get("/movie/test_update")
    resp_json = resp.json

    assert resp.status_code == 200
    assert resp_json["name"] == "test_update"
    assert resp_json["genre"] == "test_update"


def test_update_name( client):
    resp = client.put("/movie/avengers1", json={'name': 'test_update'})

    assert resp.status_code == 204

    resp = client.get("/movie/test_update")
    resp_json = resp.json

    assert resp.status_code == 200
    assert resp_json["name"] == "test_update"
    assert resp_json["genre"] == "gnr1"


def test_update_genre( client):
    resp = client.put("/movie/avengers1", json={'genre': 'test_update'})

    assert resp.status_code == 204

    resp = client.get("/movie/avengers1")
    resp_json = resp.json

    assert resp.status_code == 200
    assert resp_json["name"] == "avengers1"
    assert resp_json["genre"] == "test_update"


def test_delete( client):
    resp = client.delete("/movie/test")
    assert resp.status_code == 204


def test_create_error( client):
    resp = client.post("/movie/avengers4")
    assert resp.status_code == 400


def test_create_with_missing_params( client):
    resp = client.post("/movie/avengers5")
    assert resp.status_code == 400


def test_create_duplicate_error( client):
    resp = client.post("/movie/avengers4", json={'genre': 'gnr1'})
    assert resp.status_code == 400


def test_get_error( client):
    resp = client.get("/movie/avengers")
    assert resp.status_code == 404


def test_update_unkown_name( client):
    resp = client.put("/movie/avengers", json={'name': 'test_update', 'genre': 'test_update'})
    assert resp.status_code == 404


def test_update_missing_params( client):
    resp = client.put("/movie/avengers1")
    assert resp.status_code == 400


def test_delete_with_existing_schedules( client):
    resp = client.delete("/movie/avengers1")
    assert resp.status_code == 400


def test_delete_unkown_movie( client):
    resp = client.delete("/movie/avengers")
    assert resp.status_code == 404