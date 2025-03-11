import json
import jwt

from django.test import TestCase

from zone3000.settings import JWT_SECRET, JWT_ALGORITHM
from custom_users.models import CustomUser
from links.models import RedirectRule


class UrlViewsTestBase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            username="testuser",
            password="testpassword123",
        )

        self.redirect_rule1 = RedirectRule.objects.create(
            user=self.user,
            redirect_url="https://example.com",
            is_private=False
        )
        self.redirect_rule2 = RedirectRule.objects.create(
            user=self.user,
            redirect_url="https://example.org",
            is_private=True
        )

        payload = {
            "user_id": self.user.id,
            "username": self.user.username,
            "type": "access"
        }
        self.token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        self.auth_header = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}


class UrlViewTests(UrlViewsTestBase):
    def setUp(self):
        super().setUp()
        self.url = "/url/"

    def test_create_url_success(self):
        data = {
            "redirect_url": "https://test.com",
            "is_private": False
        }

        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type="application/json",
            **self.auth_header
        )

        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["redirect_url"], "https://test.com")
        self.assertEqual(response_data["is_private"], False)

    def test_create_url_invalid_data(self):
        data = {
            "redirect_url": "not-a-valid-url",
            "is_private": False
        }

        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type="application/json",
            **self.auth_header
        )

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertTrue("errors" in response_data)
        self.assertTrue("redirect_url" in response_data["errors"])

    def test_create_url_invalid_json(self):
        response = self.client.post(
            self.url,
            data="invalid-json",
            content_type="application/json",
            **self.auth_header
        )

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["error"], "Invalid JSON")

    def test_create_url_unauthorized(self):
        data = {
            "redirect_url": "https://test.com",
            "is_private": False
        }

        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)


class UrlListViewTests(UrlViewsTestBase):
    def setUp(self):
        super().setUp()
        self.url = "/url/redirect_rules"

    def test_list_urls_success(self):
        response = self.client.get(self.url, **self.auth_header)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data), 2)
        urls = [item["redirect_url"] for item in response_data]
        self.assertIn(self.redirect_rule1.redirect_url, urls)
        self.assertIn(self.redirect_rule2.redirect_url, urls)

    def test_list_urls_unauthorized(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)


class UrlDetailViewTests(UrlViewsTestBase):
    def setUp(self):
        super().setUp()
        self.url = f"/url/{self.redirect_rule1.id}"

    def test_get_url_detail_success(self):
        response = self.client.get(self.url, **self.auth_header)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["redirect_url"], self.redirect_rule1.redirect_url)
        self.assertEqual(response_data["is_private"], self.redirect_rule1.is_private)

    def test_patch_url_detail_success(self):
        data = {
            "redirect_url": "https://updated-example.com",
            "is_private": True
        }

        response = self.client.patch(
            self.url,
            data=json.dumps(data),
            content_type="application/json",
            **self.auth_header
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["redirect_url"], "https://updated-example.com")
        self.assertEqual(response_data["is_private"], True)

    def test_patch_url_detail_invalid_json(self):
        response = self.client.patch(
            self.url,
            data="invalid-json",
            content_type="application/json",
            **self.auth_header
        )

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["error"], "Invalid JSON")

    def test_delete_url_detail_success(self):
        response = self.client.delete(self.url, **self.auth_header)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content.decode(), "")

    def test_unauthorized_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

        data = {"redirect_url": "https://example.net"}
        response = self.client.patch(
            self.url,
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 401)

    def test_another_user_access(self):
        user2 = CustomUser.objects.create(
            username="anotheruser",
            password="testpassword456",
        )

        payload = {
            "user_id": user2.id,
            "username": user2.username,
            "type": "access"
        }
        token2 = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        auth_header2 = {"HTTP_AUTHORIZATION": f"Bearer {token2}"}

        response = self.client.get(self.url, **auth_header2)
        self.assertEqual(response.status_code, 404)

        data = {"redirect_url": "https://example.net"}
        response = self.client.patch(
            self.url,
            data=json.dumps(data),
            content_type="application/json",
            **auth_header2
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.delete(self.url, **auth_header2)
        self.assertEqual(response.status_code, 404)