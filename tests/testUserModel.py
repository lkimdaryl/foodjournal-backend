import asyncio
from conftest import client, SessionLocal
from auth.service import get_user_by_id


class TestUserModel:

    @classmethod
    def setup_class(cls):
        cls.valid_user1 = {
            "first_name": "Thomas",
            "last_name": "Powell",
            "username": "tpowell",
            "password": "pass123",
            "email": "tpowell@foodjournal.com"
        }
        cls.valid_user3 = {
            "first_name": "Joe",
            "last_name": "Bob",
            "username": "joebob",
            "password": "joebobpass",
            "email": "joebob@gmail.com"
        }
        client.post("/api/v1/auth/create_user", json=cls.valid_user1)
        client.post("/api/v1/auth/create_user", json=cls.valid_user3)

        # store user1 id from login for use in test_get_user_by_id
        resp = client.post("/api/v1/auth/login", data={
            "username": cls.valid_user1["username"],
            "password": cls.valid_user1["password"]
        })
        cls.user1_id = resp.json()["user_id"]

    @staticmethod
    def _get_token(user: dict) -> str:
        response = client.post("/api/v1/auth/login", data={
            "username": user["username"],
            "password": user["password"]
        })
        return response.json()["access_token"]

    # test creating a valid user
    def test_create_user(self):
        user_data = {
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser",
            "password": "testuserpass",
            "email": "testuser@gmail.com"
        }
        response = client.post("/api/v1/auth/create_user", json=user_data)
        assert response.status_code == 200

    # test duplicate email is rejected
    def test_create_user_duplicate_email(self):
        user_data = {
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser_dup",
            "password": "testuserpass",
            "email": self.valid_user1["email"]
        }
        response = client.post("/api/v1/auth/create_user", json=user_data)
        assert response.status_code == 400
        assert response.json() == {"detail": f"Email {user_data['email']} already exists"}

    # test invalid email is rejected
    def test_create_user_invalid_email(self):
        user_data = {
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser_invalid",
            "password": "testuserpass",
            "email": "invalid_email"
        }
        response = client.post("/api/v1/auth/create_user", json=user_data)
        assert response.status_code == 400

    # test duplicate username is rejected
    def test_create_user_duplicate_username(self):
        user_data = {
            "first_name": "Test",
            "last_name": "User",
            "username": self.valid_user1["username"],
            "password": "testuserpass",
            "email": "unique_email@gmail.com"
        }
        response = client.post("/api/v1/auth/create_user", json=user_data)
        assert response.status_code == 400
        assert response.json() == {"detail": f"User {user_data['username']} already exists"}

    # test valid login succeeds
    def test_login(self):
        response = client.post("/api/v1/auth/login", data={
            "username": self.valid_user1["username"],
            "password": self.valid_user1["password"]
        })
        json_response = response.json()
        assert "access_token" in json_response
        assert json_response["token_type"] == "bearer"
        assert json_response["email"] == self.valid_user1["email"]

    # test login with email address instead of username
    def test_login_with_email(self):
        response = client.post("/api/v1/auth/login", data={
            "username": self.valid_user1["email"],
            "password": self.valid_user1["password"]
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

    # test invalid username is rejected
    def test_invalid_username_login(self):
        response = client.post("/api/v1/auth/login", data={
            "username": "fakeUser",
            "password": "fakePass"
        })
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid email or username, try again."}

    # test invalid password is rejected
    def test_invalid_password_login(self):
        response = client.post("/api/v1/auth/login", data={
            "username": self.valid_user1["username"],
            "password": "wrongpass"
        })
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid password, try again."}

    # test unauthenticated request to update_user is rejected
    def test_update_user_no_auth(self):
        response = client.patch("/api/v1/auth/update_user", json={"first_name": "Hacker"})
        assert response.status_code == 403

    # test unauthenticated request to get_user is rejected
    def test_get_user_no_auth(self):
        response = client.get("/api/v1/auth/get_user")
        assert response.status_code == 403

    # test update with no data returns 400
    def test_no_update_data(self):
        token = self._get_token(self.valid_user3)
        response = client.patch(
            "/api/v1/auth/update_user",
            json={},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400
        assert response.json() == {"detail": "No fields to update"}

    # test update with a duplicate email is rejected
    def test_duplicate_update_email(self):
        token = self._get_token(self.valid_user3)
        response = client.patch(
            "/api/v1/auth/update_user",
            json={"email": self.valid_user1["email"]},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400
        assert response.json() == {"detail": f'Email {self.valid_user1["email"]} already exists'}

    # test update with an invalid email is rejected
    def test_invalid_update_email(self):
        token = self._get_token(self.valid_user3)
        response = client.patch(
            "/api/v1/auth/update_user",
            json={"email": "invalidEmail"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400

    # test update with a duplicate username is rejected
    def test_duplicate_update_username(self):
        token = self._get_token(self.valid_user3)
        response = client.patch(
            "/api/v1/auth/update_user",
            json={"username": self.valid_user1["username"]},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400
        assert response.json() == {"detail": f'User {self.valid_user1["username"]} already exists'}

    # test valid update succeeds
    def test_update_user(self):
        token = self._get_token(self.valid_user3)
        update_data = {"first_name": "JoeBob", "last_name": "Joe", "username": "joebobjoe"}
        response = client.patch(
            "/api/v1/auth/update_user",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.json() == {"message": "User was updated"}

    # test updating password invalidates old one and enables new one
    # note: valid_user3's username is now "joebobjoe" after test_update_user
    def test_update_password(self):
        resp = client.post("/api/v1/auth/login", data={
            "username": "joebobjoe",
            "password": "joebobpass"
        })
        token = resp.json()["access_token"]

        client.patch(
            "/api/v1/auth/update_user",
            json={"password": "newpassword123"},
            headers={"Authorization": f"Bearer {token}"}
        )

        # old password should no longer work
        resp = client.post("/api/v1/auth/login", data={
            "username": "joebobjoe", "password": "joebobpass"
        })
        assert resp.status_code == 401

        # new password should work
        resp = client.post("/api/v1/auth/login", data={
            "username": "joebobjoe", "password": "newpassword123"
        })
        assert resp.status_code == 200

    # test get_user endpoint returns authenticated user's profile without password
    def test_get_user(self):
        token = self._get_token(self.valid_user1)
        response = client.get(
            "/api/v1/auth/get_user",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        user = response.json()
        assert user["username"] == self.valid_user1["username"]
        assert user["email"] == self.valid_user1["email"]
        assert "password" not in user

    # test get_user returns exactly the expected set of fields
    def test_get_user_response_shape(self):
        token = self._get_token(self.valid_user1)
        response = client.get(
            "/api/v1/auth/get_user",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        expected_keys = {"id", "first_name", "last_name", "username", "email", "profile_picture"}
        assert set(response.json().keys()) == expected_keys

    # test get_user_by_id service returns the correct username
    def test_get_user_by_id(self):
        db = SessionLocal()
        try:
            result = asyncio.run(get_user_by_id(self.user1_id, db))
            assert result == self.valid_user1["username"]
        finally:
            db.close()

    # test that a blacklisted token is rejected on other protected endpoints
    def test_blacklisted_token_on_update(self):
        token = self._get_token(self.valid_user1)
        client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        response = client.patch(
            "/api/v1/auth/update_user",
            json={"first_name": "Ghost"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401

    # test logout invalidates the token
    def test_logout(self):
        token = self._get_token(self.valid_user1)
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        follow_up = client.get(
            "/api/v1/auth/get_user",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert follow_up.status_code == 401
