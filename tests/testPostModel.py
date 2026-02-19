from conftest import client


class TestPostModel:

    @classmethod
    def setup_class(cls):
        cls.test_user = {
            "first_name": "Post",
            "last_name": "Tester",
            "username": "posttester",
            "password": "postpass",
            "email": "posttester@gmail.com"
        }
        cls.other_user = {
            "first_name": "Other",
            "last_name": "User",
            "username": "otheruser",
            "password": "otherpass",
            "email": "otheruser@gmail.com"
        }
        client.post("/api/v1/auth/create_user", json=cls.test_user)
        client.post("/api/v1/auth/create_user", json=cls.other_user)

        # get token and user_id from login
        resp = client.post("/api/v1/auth/login", data={
            "username": cls.test_user["username"],
            "password": cls.test_user["password"]
        })
        login = resp.json()
        cls.token = login["access_token"]
        cls.user_id = login["user_id"]

        resp = client.post("/api/v1/auth/login", data={
            "username": cls.other_user["username"],
            "password": cls.other_user["password"]
        })
        cls.other_token = resp.json()["access_token"]

        cls.valid_post = {
            "food_name": "burrito",
            "restaurant_name": "Taco Stand",
            "rating": 4.5,
            "review": "Super good tortilla",
            "tags": "mexican"
        }

        # create an initial post and capture its id for update/delete tests
        resp = client.post(
            "/api/v1/post_review/create_post_review",
            json=cls.valid_post,
            headers={"Authorization": f"Bearer {cls.token}"}
        )
        msg = resp.json().get("message", "Post 0 created")
        cls.post_id = int(msg.split()[1])

    @staticmethod
    def _auth_headers(token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}

    # test creating a valid post succeeds
    def test_create_post(self):
        response = client.post(
            "/api/v1/post_review/create_post_review",
            json=self.valid_post,
            headers=self._auth_headers(self.token)
        )
        assert response.status_code == 200
        assert "message" in response.json()

    # test rating below 1.0 is rejected
    def test_create_post_invalid_rating_low(self):
        post = {**self.valid_post, "rating": 0.5}
        response = client.post(
            "/api/v1/post_review/create_post_review",
            json=post,
            headers=self._auth_headers(self.token)
        )
        assert response.status_code == 422

    # test rating above 5.0 is rejected
    def test_create_post_invalid_rating_high(self):
        post = {**self.valid_post, "rating": 5.5}
        response = client.post(
            "/api/v1/post_review/create_post_review",
            json=post,
            headers=self._auth_headers(self.token)
        )
        assert response.status_code == 422

    # test missing required fields (food_name, rating, review) returns 422
    def test_create_post_missing_required_fields(self):
        response = client.post(
            "/api/v1/post_review/create_post_review",
            json={"restaurant_name": "Somewhere"},
            headers=self._auth_headers(self.token)
        )
        assert response.status_code == 422

    # test unauthenticated create is rejected
    def test_create_post_no_auth(self):
        response = client.post(
            "/api/v1/post_review/create_post_review",
            json=self.valid_post
        )
        assert response.status_code == 403

    # test get all posts returns a list
    def test_get_posts(self):
        response = client.get("/api/v1/post_review/get_post_review")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    # test get_post_review response includes joined fields from UserModel
    def test_get_posts_response_shape(self):
        response = client.get("/api/v1/post_review/get_post_review")
        assert response.status_code == 200
        post = response.json()[0]
        assert "username" in post
        assert "profile_pic" in post
        assert "food_name" in post
        assert "rating" in post

    # test get posts by user_id
    def test_get_posts_by_id(self):
        response = client.get(f"/api/v1/post_review/get_posts_by_id?user_id={self.user_id}")
        assert response.status_code == 200
        posts = response.json()
        assert isinstance(posts, list)
        assert all(p["user_id"] == self.user_id for p in posts)

    # test get posts by user with no posts returns an empty list
    def test_get_posts_by_id_no_posts(self):
        response = client.get("/api/v1/post_review/get_posts_by_id?user_id=99999")
        assert response.status_code == 200
        assert response.json() == []

    # test owner can update their post
    def test_update_post(self):
        updated = {**self.valid_post, "food_name": "updated burrito", "rating": 3.0}
        response = client.patch(
            f"/api/v1/post_review/update_post_review?post_id={self.post_id}",
            json=updated,
            headers=self._auth_headers(self.token)
        )
        assert response.status_code == 200
        assert response.json() == {"message": f"Post {self.post_id} updated"}

    # test update actually persists the new field values
    def test_update_post_persists_changes(self):
        resp = client.post(
            "/api/v1/post_review/create_post_review",
            json=self.valid_post,
            headers=self._auth_headers(self.token)
        )
        pid = int(resp.json()["message"].split()[1])

        updated = {**self.valid_post, "food_name": "tacos", "rating": 2.0}
        client.patch(
            f"/api/v1/post_review/update_post_review?post_id={pid}",
            json=updated,
            headers=self._auth_headers(self.token)
        )

        resp = client.get(f"/api/v1/post_review/get_posts_by_id?user_id={self.user_id}")
        posts = resp.json()
        match = next((p for p in posts if p["id"] == pid), None)
        assert match is not None
        assert match["food_name"] == "tacos"
        assert match["rating"] == 2.0

    # test non-owner cannot update another user's post
    def test_update_post_unauthorized(self):
        updated = {**self.valid_post, "food_name": "hacked", "rating": 1.0}
        response = client.patch(
            f"/api/v1/post_review/update_post_review?post_id={self.post_id}",
            json=updated,
            headers=self._auth_headers(self.other_token)
        )
        assert response.status_code == 403

    # test update on a non-existent post returns 404
    def test_update_post_not_found(self):
        response = client.patch(
            "/api/v1/post_review/update_post_review?post_id=99999",
            json=self.valid_post,
            headers=self._auth_headers(self.token)
        )
        assert response.status_code == 404

    # test non-owner cannot delete another user's post
    def test_delete_post_unauthorized(self):
        response = client.delete(
            f"/api/v1/post_review/delete_post_review?post_id={self.post_id}",
            headers=self._auth_headers(self.other_token)
        )
        assert response.status_code == 403

    # test owner can delete their post
    def test_delete_post(self):
        response = client.delete(
            f"/api/v1/post_review/delete_post_review?post_id={self.post_id}",
            headers=self._auth_headers(self.token)
        )
        assert response.status_code == 200
        assert response.json() == {"message": f"Post {self.post_id} deleted"}

    # test deleted post is no longer returned in the user's feed
    def test_deleted_post_not_in_feed(self):
        resp = client.post(
            "/api/v1/post_review/create_post_review",
            json=self.valid_post,
            headers=self._auth_headers(self.token)
        )
        temp_id = int(resp.json()["message"].split()[1])

        client.delete(
            f"/api/v1/post_review/delete_post_review?post_id={temp_id}",
            headers=self._auth_headers(self.token)
        )

        resp = client.get(f"/api/v1/post_review/get_posts_by_id?user_id={self.user_id}")
        assert resp.status_code == 200
        ids = [p["id"] for p in resp.json()]
        assert temp_id not in ids

    # test delete on a non-existent post returns 404
    def test_delete_post_not_found(self):
        response = client.delete(
            "/api/v1/post_review/delete_post_review?post_id=99999",
            headers=self._auth_headers(self.token)
        )
        assert response.status_code == 404
