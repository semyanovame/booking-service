def test_book_slot(client, user_token):
    r = client.post("/api/book", json={"slot_id": 1, "date": "2027-01-01", "token": user_token})
    assert r.status_code == 200
    assert r.json()["ok"] == True

def test_book_occupied(client, user_token, admin_token):
    client.post("/api/book", json={"slot_id": 1, "date": "2027-01-02", "token": admin_token})
    r = client.post("/api/book", json={"slot_id": 1, "date": "2027-01-02", "token": user_token})
    assert r.json()["error"] == "слот уже занят"

def test_book_past(client, user_token):
    r = client.post("/api/book", json={"slot_id": 1, "date": "2020-01-01", "token": user_token})
    assert r.json()["error"] == "нельзя бронировать прошлое"

def test_cancel_own(client, user_token):
    r = client.post("/api/book", json={"slot_id": 1, "date": "2027-01-03", "token": user_token})
    r = client.delete(f"/api/book/1?token={user_token}")
    assert r.json()["ok"] == True

def test_cancel_other_as_admin(client, user_token, admin_token):
    r = client.post("/api/book", json={"slot_id": 1, "date": "2027-01-04", "token": user_token})
    r = client.delete(f"/api/book/1?token={admin_token}")
    assert r.json()["ok"] == True

def test_stats(client, admin_token):
    r = client.get(f"/api/stats?token={admin_token}")
    assert r.status_code == 200
    assert "total_slots" in r.json()

def test_stats_user(client, user_token):
    r = client.get(f"/api/stats?token={user_token}")
    assert r.json()["error"] == "только админ"