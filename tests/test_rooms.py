def test_rooms_ui(client):
    r = client.get("/api/rooms-ui")
    assert r.status_code == 200
    rooms = r.json()
    assert len(rooms) > 0
    assert "name" in rooms[0]
    assert "slots" in rooms[0]

def test_add_room_admin(client, admin_token):
    r = client.post("/api/add-room", json={"name": "Test Room", "description": "Test"}, headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    assert r.json()["ok"] == True

def test_add_room_user(client, user_token):
    r = client.post("/api/add-room", json={"name": "Test Room", "description": "Test"}, headers={"Authorization": f"Bearer {user_token}"})
    assert r.json()["error"] == "только админ"

def test_delete_room_admin(client, admin_token):
    r = client.delete("/api/room/1?token=" + admin_token)
    assert r.json()["ok"] == True

def test_delete_room_user(client, user_token):
    r = client.delete("/api/room/1?token=" + user_token)
    assert r.json()["error"] == "только админ"