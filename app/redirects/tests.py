import json
import jwt

from django.test import TestCase

from zone3000.settings import JWT_SECRET, JWT_ALGORITHM
from custom_users.models import CustomUser
from links.models import RedirectRule


class RedirectViewsTestBase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            username="testuser",
            password="testpassword123",
        )

        self.public_rule = RedirectRule.objects.create(
            user=self.user,
            redirect_url="https://example.com",
            is_private=False
        )

        self.private_rule = RedirectRule.objects.create(
            user=self.user,
            redirect_url="https://private-example.com",
            is_private=True
        )

        payload = {
            "user_id": self.user.id,
            "username": self.user.username,
            "type": "access"
        }
        self.token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        self.auth_header = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

        self.public_url = f"/redirect/public/{self.public_rule.redirect_identifier}"
        self.private_url = f"/redirect/private/{self.private_rule.redirect_identifier}"


class PublicRedirectViewTests(RedirectViewsTestBase):
    def test_public_redirect_success(self):
        response = self.client.get(self.public_url)

        self.assertEqual(response.status_code, 302)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["redirect_url"], self.public_rule.redirect_url)
        self.assertEqual(response_data["redirect_identifier"], self.public_rule.redirect_identifier)

    def test_private_redirect_through_public_endpoint_fails(self):
        public_url_to_private_rule = f"/redirect/public/{self.private_rule.redirect_identifier}"
        response = self.client.get(public_url_to_private_rule)

        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["error"], "RedirectRule not found")


class PrivateRedirectViewTests(RedirectViewsTestBase):
    def test_private_redirect_success_with_auth(self):
        response = self.client.get(self.private_url, **self.auth_header)

        self.assertEqual(response.status_code, 302)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["redirect_url"], self.private_rule.redirect_url)
        self.assertEqual(response_data["redirect_identifier"], self.private_rule.redirect_identifier)

    def test_public_redirect_through_private_endpoint_with_auth(self):
        private_url_to_public_rule = f"/redirect/private/{self.public_rule.redirect_identifier}"
        response = self.client.get(private_url_to_public_rule, **self.auth_header)

        self.assertEqual(response.status_code, 302)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["redirect_url"], self.public_rule.redirect_url)

    def test_private_redirect_fails_without_auth(self):
        response = self.client.get(self.private_url)
        self.assertEqual(response.status_code, 401)
