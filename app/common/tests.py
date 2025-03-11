import json
import jwt

from django.test import TestCase

from custom_users.models import CustomUser
from zone3000.settings import JWT_SECRET, JWT_ALGORITHM
from common.constatnts.constants import ACCESS_TYPE, REFRESH_TYPE


class RetrieveTokenViewTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            username="testuser",
            password="testpassword123"
        )
        self.url = "/retrieve-token/"

    def test_successful_token_retrieval(self):
        data = {
            "username": "testuser",
            "password": "testpassword123"
        }

        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn(ACCESS_TYPE, response_data)
        self.assertIn(REFRESH_TYPE, response_data)

    def test_invalid_credentials(self):
        data = {
            "username": "testuser",
            "password": "wrongpassword"
        }

        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.json())

    def test_token_payload_validation(self):
        data = {
            "username": "testuser",
            "password": "testpassword123"
        }

        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type="application/json"
        )

        self.assertEqual(
            response.status_code, 
            200,
            f"Response status was {response.status_code}, content: {response.content}"
        )

        response_data = response.json()

        decoded_access = jwt.decode(
            response_data[ACCESS_TYPE],
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        decoded_refresh = jwt.decode(
            response_data[REFRESH_TYPE],
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        self.assertEqual(decoded_access["type"], ACCESS_TYPE)
        self.assertEqual(decoded_refresh["type"], REFRESH_TYPE)
        self.assertEqual(decoded_access["user_id"], self.user.id)

    def test_invalid_json(self):
        response = self.client.post(
            self.url,
            data="invalid json",
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_missing_credentials(self):
        data = {}

        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("errors", response.json())