import unittest
from app import create_app

class BasicTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({'TESTING': True, 'SECRET_KEY': 'test'})
        self.client = self.app.test_client()
        with self.app.app_context():
            pass

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to Orumba North', response.data)

    def test_register_login_logout(self):
        # Register a new user
        response = self.client.post('/api/register', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'success', response.data)

        # Login with the new user
        response = self.client.post('/api/login', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'success', response.data)

        # Check auth status
        response = self.client.get('/api/check-auth')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'testuser', response.data)

        # Logout
        response = self.client.post('/api/logout')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'success', response.data)

    def test_protected_route_requires_auth(self):
        response = self.client.get('/create-post')
        self.assertEqual(response.status_code, 401)  # Unauthorized

if __name__ == '__main__':
    unittest.main()
