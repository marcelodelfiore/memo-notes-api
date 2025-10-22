from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

BASE = "/v1/notes"


def test_create_and_get_note():
    payload = {"title": "Hello", "content": "World", "tags": ["a", "b"]}
    r = client.post(BASE, json=payload)
    assert r.status_code == 201, r.text
    note = r.json()
    assert note["id"] >= 1
    assert note["title"] == "Hello"

    # GET by id (should return JSON + ETag)
    r2 = client.get(f"{BASE}/{note['id']}")
    assert r2.status_code == 200
    fetched = r2.json()
    assert fetched["id"] == note["id"]
    assert fetched["title"] == "Hello"
    assert "etag" in {k.lower(): v for k, v in r2.headers.items()}

    # Conditional GET (If-None-Match -> 304)
    etag = r2.headers.get("ETag")
    r3 = client.get(f"{BASE}/{note['id']}", headers={"If-None-Match": etag})
    assert r3.status_code == 304


def test_list_and_filters_with_pagination_envelope():
    # Create a few notes (don't assume empty store)
    ids = []
    for i in range(3):
        r = client.post(BASE, json={"title": f"T{i}", "content": "zzz", "tags": ["x"]})
        assert r.status_code == 201
        ids.append(r.json()["id"])

    # List (envelope with items/total/limit/offset)
    r = client.get(BASE)
    assert r.status_code == 200
    payload = r.json()
    assert {"items", "total", "limit", "offset"} <= payload.keys()
    assert isinstance(payload["items"], list)
    assert payload["total"] >= 3

    # Search filter
    r = client.get(BASE, params={"q": "T1"})
    assert r.status_code == 200
    payload = r.json()
    assert all(
        ("T1" in item["title"]) or ("T1" in item["content"])
        for item in payload["items"]
    )

    # Tag filter
    r = client.get(BASE, params={"tag": "x"})
    assert r.status_code == 200
    payload = r.json()
    assert len(payload["items"]) >= 3

    # Pagination window (limit/offset)
    r = client.get(BASE, params={"limit": 1, "offset": 0})
    assert r.status_code == 200
    page1 = r.json()
    assert len(page1["items"]) == 1

    r = client.get(BASE, params={"limit": 1, "offset": 1})
    assert r.status_code == 200
    page2 = r.json()
    assert len(page2["items"]) == 1

    # Pages should be different notes when enough items are present
    if page1["items"] and page2["items"]:
        assert page1["items"][0]["id"] != page2["items"][0]["id"]


def test_update_and_delete():
    # create
    r = client.post(BASE, json={"title": "Old", "content": "C", "tags": []})
    assert r.status_code == 201
    note_id = r.json()["id"]

    # update (PUT)
    r = client.put(f"{BASE}/{note_id}", json={"title": "New", "content": "D", "tags": ["t"]})
    assert r.status_code == 200
    updated = r.json()
    assert updated["title"] == "New"
    assert updated["tags"] == ["t"]

    # delete (204 no content)
    r = client.delete(f"{BASE}/{note_id}")
    assert r.status_code == 204
    assert not r.content  # must be empty

    # confirm 404
    r = client.get(f"{BASE}/{note_id}")
    assert r.status_code == 404
