import unittest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import *

class UserRegistrationAndLoginTest(APITestCase):
    
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "password": "password123"
        }
    
    def test_register_user_successfully_with_default_organisation(self):
        response = self.client.post(self.register_url, data=self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        
        # Check for access token
        self.assertIn('accessToken', data['data'])
        
        # Check user data
        self.assertIn('user', data['data'])
        user_data = data['data']['user']
        self.assertEqual(user_data['firstName'], 'John')
        self.assertEqual(user_data['lastName'], 'Doe')
        self.assertEqual(user_data['email'], 'john@example.com')
        self.assertIn('userId', user_data)
        
        # Check organisation data
        # self.assertIn('organisation', data['data'])
        # org_data = data['data']['organisation']
        # self.assertEqual(org_data['name'], "John's Organisation")
        # self.assertIn('orgId', org_data)
        
        # Verify database entries
        user = User.objects.get(email="john@example.com")
        self.assertIsNotNone(user)
        
        organisation = Organisation.objects.filter(created_by=user).first()
        self.assertIsNotNone(organisation)
        self.assertEqual(organisation.name, f"{user.firstName}'s Organisation")
        self.assertIn(user, organisation.members.all())
    
    def test_login_user_successfully(self):
        self.client.post(self.register_url, data=self.user_data, format='json')
        login_response = self.client.post(self.login_url, data=self.user_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        login_data = login_response.json()
        self.assertIn('accessToken', login_data['data'])

    def test_login_fail_with_invalid_credentials(self):
        self.client.post(self.register_url, data=self.user_data, format='json')
        wrong_data = self.user_data.copy()
        wrong_data['password'] = 'wrongpassword'
        login_response = self.client.post(self.login_url, data=wrong_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fail_if_required_fields_are_missing(self):
        required_fields = ["firstName", "lastName", "email", "password"]
        for field in required_fields:
            data = self.user_data.copy()
            data.pop(field)
            response = self.client.post(self.register_url, data=data, format='json')
            self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
            response_data = response.json()
            self.assertIn('errors', response_data)

    def test_fail_if_duplicate_email(self):
        self.client.post(self.register_url, data=self.user_data, format='json')
        duplicate_email_response = self.client.post(self.register_url, data=self.user_data, format='json')
        self.assertEqual(duplicate_email_response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        duplicate_email_data = duplicate_email_response.json()
        self.assertIn('errors', duplicate_email_data)

if __name__ == "__main__":
    unittest.main()
