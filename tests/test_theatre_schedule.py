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
    resp = client.post("/schedule/theatre/theatre1", json={'time': "2:55", 'screen': '1', 'movie': 'test'})
    resp_json = resp.json

    assert resp.status_code == 201
    assert resp_json["movie"] == "test"
    assert resp_json["theatre"] == "theatre1"
    assert resp_json["time"] == "02:55"

    resp = client.get("/schedule/theatre/theatre1")
    resp_json = resp.json
    assert resp.status_code == 200
    assert "test" in resp_json
    assert "02:55" in resp_json["test"]


def test_get_all_schedules(client):
    resp = client.get("/schedule/theatre/theatre1")
    resp_json = resp.json

    assert resp.status_code == 200
    assert resp_json == {"avengers1": ["11:30", "23:30"], "avengers2": ["11:50", "16:15", "20:30"],
                         "avengers3": ["14:30"], "avengers4": ["19:00", "21:05"]}


def test_get_movie_schedules(client):
    resp = client.get("/schedule/theatre/theatre1", json={"movie": "avengers2"})
    resp_json = resp.json

    assert resp.status_code == 200
    assert resp_json == {"avengers2": ["11:50", "16:15", "20:30"]}


def test_update(client):
    resp = client.put("/schedule/theatre/theatre1",
                      json={'updated_time': "0:55", "time": "11:30", 'screen': '1', 'movie': 'avengers1'}
                      )
    assert resp.status_code == 204

    resp = client.get("/schedule/theatre/theatre1")
    resp_json = resp.json

    assert resp.status_code == 200
    assert resp_json["avengers1"] == ["00:55", "23:30"]


def test_delete_movie_schedules(client):
    resp = client.delete("/schedule/theatre/theatre1", json={"movie": "avengers1"})
    assert resp.status_code == 204

    resp = client.get("/schedule/theatre/theatre1", json={"movie": "avengers1"})
    resp_json = resp.json
    assert resp_json == {}


def test_delete_movie_screen_schedules(client):
    resp = client.delete("/schedule/theatre/theatre1", json={"movie": "avengers2", "screen": 2})
    assert resp.status_code == 204

    resp = client.get("/schedule/theatre/theatre1",  json={"movie": "avengers2"})
    resp_json = resp.json
    assert resp_json["avengers2"] == ["16:15", "20:30"]


def test_delete_screen_schedules(client):
    resp = client.delete("/schedule/theatre/theatre1", json={"screen": 2})
    assert resp.status_code == 204

    resp = client.get("/schedule/theatre/theatre1")
    resp_json = resp.json
    assert resp_json == {"avengers2": ["16:15", "20:30"], "avengers1": ["11:30"], "avengers3": ["14:30"]}


def test_delete_theatre_schedules(client):
    resp = client.delete("/schedule/theatre/theatre1")
    assert resp.status_code == 204

    resp = client.get("/schedule/theatre/theatre1")
    resp_json = resp.json
    assert resp_json == {}


create_missing_params = [
    {},
    {'movie': 'avengers1', 'screen': 1},
    {'time': '10:30', 'screen': 1},
    {'movie': 'avengers1', 'screen': 1},
    {'screen': 1},
    {'movie': 'avengers1'},
    {'time': '10:30'}
]


@pytest.mark.parametrize('json_param', create_missing_params)
def test_create_with_missing_params(client, json_param):
    resp = client.post("/schedule/theatre/theatre1", json=json_param)
    assert resp.status_code == 400


create_time_error_params = [
    {"time": "1abc:30", 'screen': 1, 'movie': 'avengers1'},
    {"time": "abc", 'screen': 1, 'movie': 'avengers1'},
    {"time": "123:30", 'screen': 1, 'movie': 'avengers1'},
    {"time": "34:00", 'screen': 1, 'movie': 'avengers1'},
    {"time": "12:72", 'screen': 1, 'movie': 'avengers1'},
]


@pytest.mark.parametrize('json_params', create_time_error_params)
def test_create_time_error(client, json_params):
    resp = client.post("/schedule/theatre/theatre1", json=json_params)
    assert resp.status_code == 400


def test_create_duplicate_error(client):
    resp = client.post("/schedule/theatre/theatre1", json={'screen': 1, 'time': '11:30', 'movie': 'avengers1'})
    assert resp.status_code == 400


create_invalid_screens_params = [
    {'screen': 0, 'time': '3:30', 'movie': 'avengers1'},
    {'screen': -1, 'time': '3:30', 'movie': 'avengers1'},
    {'screen': 10, 'time': '3:30', 'movie': 'avengers1'}
]


@pytest.mark.parametrize('json_param', create_invalid_screens_params)
def test_create_with_invalid_screen(client, json_param):
    resp = client.post("/schedule/theatre/theatre1", json=json_param)
    assert resp.status_code == 400


def test_create_with_unkown_theatre(client):
    resp = client.post("/schedule/theatre/theatre0", json={'screen': 1, 'time': '3:30', 'movie': 'avengers1'})
    assert resp.status_code == 404


def test_create_with_unkown_movie(client):
    resp = client.post("/schedule/theatre/theatre1", json={'screen': 1, 'time': '3:30', 'movie': 'avengers0'})
    assert resp.status_code == 404


get_error_params = [
    {'screen': 1, 'time': '11:30', 'movie': 'avengers1'},
    {'time': '11:30', 'movie': 'avengers1'},
    {'screen': 1, 'movie': 'avengers1'},
    {'time': '11:30'},
    {"screen": 1},
    {"updated_time": "11:30"},
    {"updated_time": "11:30", 'movie': 'avengers1'}
]


@pytest.mark.parametrize('json_param', get_error_params)
def test_get_error(client, json_param):
    resp = client.get("/schedule/theatre/theatre1", json=json_param)
    assert resp.status_code == 400


def test_get_unkown_movie(client):
    resp = client.get("/schedule/theatre/theatre1", json={'movie': 'avengers0'})
    assert resp.status_code == 404


def test_get_unkown_theatre(client):
    resp = client.get("/schedule/theatre/theatre0", json={'movie': 'avengers1'})
    assert resp.status_code == 404


def test_update_unkown_movie(client):
    resp = client.put(
        "/schedule/theatre/theatre1",
        json={'updated_time': "0:55", "time": "11:30", 'screen': '1', 'movie': 'avengers0'}
    )
    assert resp.status_code == 404


def test_update_unkown_theatre(client):
    resp = client.put(
        "/schedule/theatre/theatre0",
        json={'updated_time': "0:55", "time": "11:30", 'screen': '1', 'movie': 'avengers1'}
    )
    assert resp.status_code == 404


update_missing_params = [
    {'updated_time': "0:55", "time": "11:30", 'screen': '1'},
    {'updated_time': "0:55", "time": "11:30", 'movie': 'avengers1'},
    {'updated_time': "0:55", 'screen': '1', 'movie': 'avengers1'},
    {"time": "11:30", 'screen': '1', 'movie': 'avengers1'},
    {'screen': '1', 'movie': 'avengers1'},
    {'updated_time': "0:55", 'movie': 'avengers1'},
    {"time": "11:30", 'movie': 'avengers1'},
    {'updated_time': "0:55", "time": "11:30"},
    {'updated_time': "0:55", 'screen': '1'},
    {"time": "11:30", 'screen': '1'},
    {'movie': 'avengers1'},
    {'screen': '1'},
    {"time": "11:30"},
    {'updated_time': "0:55"},
    {}
]


@pytest.mark.parametrize('json_param', update_missing_params)
def test_update_missing_params(client, json_param):
    resp = client.put("/schedule/theatre/theatre1", json=json_param)
    assert resp.status_code == 400


update_invalid_screen_params = [
    {"updated_time": "0:55", "time": "11:30", "screen": 0, 'movie': 'avengers1'},
    {'updated_time': "0:55", "time": "11:30", 'screen': -1, 'movie': 'avengers1'},
    {'updated_time': "0:55", "time": "11:30", 'screen': 10, 'movie': 'avengers1'}
]


@pytest.mark.parametrize('json_param', update_invalid_screen_params)
def test_update_with_invalid_screen(client, json_param):
    resp = client.put("/schedule/theatre/theatre1", json=json_param)
    assert resp.status_code == 400


update_time_error_params = [
    {"updated_time": "1abc:30", 'screen': 1, 'movie': 'avengers1', 'time': '11:30'},
    {"updated_time": "abc", 'screen': 1, 'movie': 'avengers1', 'time': '11:30'},
    {"updated_time": "123:30", 'screen': 1, 'movie': 'avengers1', 'time': '11:30'},
    {"updated_time": "34:00", 'screen': 1, 'movie': 'avengers1', 'time': '11:30'},
    {"updated_time": "12:72", 'screen': 1, 'movie': 'avengers1', 'time': '11:30'},
    {"time": "1abc:30", 'screen': 1, 'movie': 'avengers1', 'updated_time': '11:30'},
    {"time": "abc", 'screen': 1, 'movie': 'avengers1', 'updated_time': '11:30'},
    {"time": "123:30", 'screen': 1, 'movie': 'avengers1', 'updated_time': '11:30'},
    {"time": "34:00", 'screen': 1, 'movie': 'avengers1', 'updated_time': '11:30'},
    {"time": "12:72", 'screen': 1, 'movie': 'avengers1', 'updated_time': '11:30'},
]


@pytest.mark.parametrize('json_params', update_time_error_params)
def test_update_time_error(client, json_params):
    resp = client.put("/schedule/theatre/theatre1", json=json_params)
    assert resp.status_code == 400


update_unkown_schedule=[
    {'updated_time': "1:55", "time": "00:30", 'screen': '1', 'movie': 'avengers1'},
    {'updated_time': "1:55", "time": "11:30", 'screen': '2', 'movie': 'avengers1'}
]


@pytest.mark.parametrize('json_params', update_unkown_schedule)
def test_update_unkown_schedule(client, json_params):
    resp = client.put("/schedule/theatre/theatre1", json=json_params)
    assert resp.status_code == 404


delete_error_with_params = [
    {"time": "11:30"},
    {"updated_time": "00:30", "time": "11:30"},
{"updated_time": "00:30"}
]


@pytest.mark.parametrize('json_param', delete_error_with_params)
def test_delete_error_with_params(client, json_param):
    resp = client.delete("/schedule/theatre/theatre1", json=json_param)
    assert resp.status_code == 400


def test_delete_unkown_movie(client):
    resp = client.delete("/schedule/theatre/theatre1", json={"time": "11:30", 'screen': 1, 'movie': 'avengers0'})
    assert resp.status_code == 404


def test_delete_unkown_theatre(client):
    resp = client.delete("/schedule/theatre/theatre0", json={"time": "11:30", 'screen': 1, 'movie': 'avengers1'})
    assert resp.status_code == 404


delete_time_error_params = [
    {"time": "1abc:30", 'screen': 1, 'movie': 'avengers1'},
    {"time": "abc", 'screen': 1, 'movie': 'avengers1'},
    {"time": "123:30", 'screen': 1, 'movie': 'avengers1'},
    {"time": "34:00", 'screen': 1, 'movie': 'avengers1'},
    {"time": "12:72", 'screen': 1, 'movie': 'avengers1'},
]


@pytest.mark.parametrize('json_params', delete_time_error_params)
def test_delete_time_error(client, json_params):
    resp = client.delete("/schedule/theatre/theatre1", json=json_params)
    assert resp.status_code == 400


delete_invalid_screen_params = [
    ({"screen": 0, "theatre": "theatre1"}, 400),
    ({"time": "11:30", 'screen': -1, 'movie': 'avengers1'}, 400),
    ({"time": "11:30", 'screen': 10, 'movie': 'avengers1'}, 404),
]


@pytest.mark.parametrize('json_param, resp_code', delete_invalid_screen_params)
def test_delete_invalid_screen(client, json_param, resp_code):
    resp = client.delete("/schedule/theatre/theatre1", json=json_param)
    assert resp.status_code == resp_code


delete_unkown_schedule = [
    {"time": "00:30", 'screen': '1', 'movie': 'avengers1'},
    {"time": "11:30", 'screen': '2', 'movie': 'avengers1'}
]


@pytest.mark.parametrize('json_params', delete_unkown_schedule)
def test_delete_unkown_schedule(client, json_params):
    resp = client.delete("/schedule/theatre/theatre1", json=json_params)
    assert resp.status_code == 404