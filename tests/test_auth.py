def test_login_user(client):
    r = client.post("/api/login", json={"username": "user", "password": "user123"})
    assert r.status_code == 200
    assert "token" in r.json()

def test_login_wrong_password(client):
    r = client.post("/api/login", json={"username": "user", "password": "wrong"})
    assert r.json()["error"] == "Неверный пароль"

def test_me(client, user_token):
    r = client.get(f"/api/me?token={user_token}")
    assert r.status_code == 200
    assert r.json()["username"] == "user"

def test_me_bad_token(client):
    r = client.get("/api/me?token=bad")
    assert "error" in r.json()