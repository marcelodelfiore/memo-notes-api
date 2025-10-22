from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_and_get_note():
    payload = {"title": "Hello", "content": "World", "tags": ["a", "b"]}
    r = client.post("/notes", json=payload)
    assert r.status_code == 201, r.text
    note = r.json()
    assert note["id"] >= 1
    assert note["title"] == "Hello"

    r2 = client.get(f"/notes/{note['id']}")
    assert r2.status_code == 200
    fetched = r2.json()
    assert fetched["id"] == note["id"]
    assert fetched["title"] == "Hello"


def test_list_and_filters():
    # create a few notes
    for i in range(3):
        client.post("/notes", json={"title": f"T{i}", "content": "zzz", "tags": ["x"]})

    r = client.get("/notes")
    assert r.status_code == 200
    arr = r.json()
    assert isinstance(arr, list)
    assert len(arr) >= 3

    r = client.get("/notes", params={"q": "T1"})
    assert r.status_code == 200
    arr = r.json()
    assert all("T1" in item["title"] or "T1" in item["content"] for item in arr)

    r = client.get("/notes", params={"tag": "x"})
    assert r.status_code == 200
    arr = r.json()
    assert len(arr) >= 3


def test_update_and_delete():
    # create
    r = client.post("/notes", json={"title": "Old", "content": "C", "tags": []})
    assert r.status_code == 201
    note_id = r.json()["id"]

    # update
    r = client.put(f"/notes/{note_id}", json={"title": "New", "content": "D", "tags": ["t"]})
    assert r.status_code == 200
    updated = r.json()
    assert updated["title"] == "New"
    assert updated["tags"] == ["t"]

    # delete
    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204

    # confirm 404
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404
