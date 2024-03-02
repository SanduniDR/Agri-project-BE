import unittest
from app import app
from app.route import user_routes
from app.models import db, User
from app.service.users.user_service import register_user
from app.service.users.util_service import parse_date


class TestRegisterUser(unittest.TestCase):
    def test_register_user_success(self):
        # Define test user data
        test_user_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'password',
            'nic': '1234567890',
            'dob': '2000-01-01',
            'role': 2
        }

        # Call the register_user function with test data
        success, message = register_user(test_user_data)

        # Assert that the registration was successful
        self.assertTrue(success)
        self.assertEqual(message, 'Registration success!')

    def test_register_user_failure(self):
        # Define invalid test user data (e.g., missing required fields)
        invalid_user_data = {}

        # Call the register_user function with invalid data
        success, message = register_user(invalid_user_data)

        # Assert that the registration failed
        self.assertFalse(success)
        self.assertIn('An error occurred', message)


if __name__ == '__main__':
    unittest.main()
