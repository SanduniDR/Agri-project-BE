from datetime import datetime, timedelta
import datetime
from app import app
import jwt
import os
import unittest
from unittest.mock import patch
from flask import Flask
from flask import current_app  # Use Flask's current_app for app context specific configurations

from app.models import db, User
from app.service.users.user_service import Check_User_Token_Expiration, Get_User_Information, Search_User, Update_User, Validate_User, deleteUser, get_access_token, getUserBy_Email, getUserBy_Id, register_user, user_login, isExistingUser
from app.service.users.util_service import parse_date
from flask_jwt_extended import JWTManager
import xmlrunner
from app.route import user_routes


class TestUserRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = Flask(__name__)
        cls.app.config['TESTING'] = True
        cls.app.config['JWT_SECRET_KEY'] = 'super_key'
        basedir = os.path.abspath(os.path.dirname(__file__))
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test_agriInfo.db')
        cls.app.register_blueprint(user_routes.user_routes)
        db.init_app(cls.app)

        with cls.app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()

    def setUp(self):
        # Ensure each test has a clean database
        with self.app.app_context():
            db.session.query(User).delete()
            db.session.commit()

    def test_user_registration(self):
        with self.app.app_context():
            user = User(
                first_name='fName',
                middle_name='mName',
                last_name='lName',
                nic='testNIC',
                email='test@example.com',
                password='test',
                dob=parse_date('1990-01-01'),
                role=1,
            )
            isSuccess, message = register_user(user)
            self.assertTrue(isSuccess)
            self.assertEqual(message, 'Registration success!')

    def test_user_login(self):
        with self.app.app_context():
            user = User(
                first_name='Jane',
                middle_name='Doe',
                last_name='Smith',
                nic='987654321V',
                email='jane@example.com',
                password='password',
                dob=parse_date('1992-02-02'),
                role=1,
            )
            db.session.add(user)
            db.session.commit()

            login_user = User(email='jane@example.com', password='password')
            loggedInUser = user_login(login_user)
            self.assertEqual(loggedInUser.email, 'jane@example.com')

    def test_access_token_generation(self):
        with self.app.app_context():
            user = User.query.filter_by(email='test@example.com').first()
            if user:
                token = get_access_token(user)
                self.assertIsNotNone(token)

    def test_user_deletion(self):
        with self.app.app_context():
            user = User.query.filter_by(email='jane@example.com').first()
            if user:
                isDeleted, message, _ = deleteUser(user.id)
                self.assertTrue(isDeleted)
                self.assertEqual(message, "User successfully deleted.")

    def test_get_user_by_id(self):
        with self.app.app_context():
            # Setup: create two users, one as the 'current user' and another as the target user
            current_user = User(
                user_id=1,
                email='current@example.com',
                password='password',
                role=1  # Assuming role 1 is allowed to fetch other users
            )
            target_user = User(
                user_id=2,
                email='target@example.com',
                password='password',
                role=2
            )
            db.session.add(current_user)
            db.session.add(target_user)
            db.session.commit()

            # Test: Attempt to get the target user by ID using the current user's ID
            retrieved_user = getUserBy_Id(2, 1)

            # Verify: Check that the retrieved user is the target user
            self.assertIsNotNone(retrieved_user)
            self.assertEqual(retrieved_user.user_id, target_user.user_id)
            self.assertEqual(retrieved_user.email, target_user.email)

    def test_get_user_by_id_unauthorized_role(self):
        with self.app.app_context():
            # Setup: create two users, one as the 'current user' with an unauthorized role and another as the target user
            current_user = User(
                user_id=3,
                email='unauthorized@example.com',
                password='password',
                role=5  # Assuming role 5 is not allowed to fetch other users
            )
            target_user = User(
                user_id=4,
                email='another_target@example.com',
                password='password',
                role=2
            )
            db.session.add(current_user)
            db.session.add(target_user)
            db.session.commit()

            # Test: Attempt to get the target user by ID using the unauthorized current user's ID
            retrieved_user = getUserBy_Id(4, 3)

            # Verify: Check that the retrieved user is None or access is denied based on your function logic
            self.assertIsNone(retrieved_user)

    def test_get_user_by_email_authorized(self):
        # Test retrieving a user by email with an authorized current user.
        with self.app.app_context():
            # Setup: create an authorized current user and another user to retrieve
            authorized_user = User(
                user_id=10,  # Ensure unique user_id
                email='authorized@example.com',
                password='password',
                role=1  # Assuming roles 1, 3, 4 are authorized
            )
            target_user = User(
                user_id=20,  # Ensure unique user_id
                email='targetuser@example.com',
                password='password',
                role=2
            )
            db.session.add(authorized_user)
            db.session.add(target_user)
            db.session.commit()

            # Act: Attempt to get the target user by email using the authorized current user's ID
            retrieved_user = getUserBy_Email('targetuser@example.com', 10)

            # Assert: Verify that the correct user is retrieved
            self.assertIsNotNone(retrieved_user)
            self.assertEqual(retrieved_user.email, 'targetuser@example.com')

    def test_get_user_by_email_unauthorized(self):
        # Test retrieving a user by email with an unauthorized current user.
        with self.app.app_context():
            # Setup: create an unauthorized current user and another user to retrieve
            unauthorized_user = User(
                user_id=30,  # Ensure unique user_id
                email='unauthorized@example.com',
                password='password',
                role=5  # Assuming this role is unauthorized
            )
            another_target_user = User(
                user_id=40,  # Ensure unique user_id
                email='another_target@example.com',
                password='password',
                role=2
            )
            db.session.add(unauthorized_user)
            db.session.add(another_target_user)
            db.session.commit()

            # Act: Attempt to get the target user by email using the unauthorized current user's ID
            retrieved_user = getUserBy_Email('another_target@example.com', 30)

            # Assert: Verify that the user is not retrieved due to unauthorized access
            self.assertIsNone(retrieved_user)
            
    def test_update_user(self):
        # Test updating user information.
        with self.app.app_context():
            # Setup: Create a user to update
            original_user = User(
                email='update@example.com',
                password='originalPassword',
                first_name='Original',
                last_name='User',
                nic='123456789V',
                dob=parse_date('1990-01-01'),
                role=1,
                middle_name='Middle'
            )
            db.session.add(original_user)
            db.session.commit()

            # Define the update data
            update_data = {
                'password': 'newPassword',
                'first_name': 'Updated',
                'last_name': 'User',
                'nic': '987654321V',
                'dob': '1995-05-05',
                'role': 2,
                'middle_name': 'UpdatedMiddle'
            }

            # Act: Call the Update_User function with the update data
            Update_User(update_data, original_user)

            # Fetch the updated user from the database
            updated_user = User.query.filter_by(email='update@example.com').first()

            # Assert: Verify the user's information has been updated
            self.assertEqual(updated_user.password, update_data['password'])
            self.assertEqual(updated_user.first_name, update_data['first_name'])
            self.assertEqual(updated_user.last_name, update_data['last_name'])
            self.assertEqual(updated_user.nic, update_data['nic'])
            self.assertEqual(updated_user.dob, parse_date(update_data['dob']))
            self.assertEqual(updated_user.role, update_data['role'])
            self.assertEqual(updated_user.middle_name, update_data['middle_name'])
            
    def test_search_user_with_filters(self):
        # Test searching users with specific filters.
        with self.app.app_context():
            # Setup: Add multiple users to test the filter and pagination
            users_to_add = [
                User(email='user1@example.com', first_name='Test', last_name='User', role=1),
                User(email='user2@example.com', first_name='Test', last_name='User2', role=2),
                User(email='user3@example.com', first_name='Another', last_name='User3', role=1),
            ]
            for user in users_to_add:
                db.session.add(user)
            db.session.commit()

            # Define filters to search for users with a specific first name
            filters = {'first_name': 'Test', 'page': 1, 'per_page': 2}

            # Act: Search users using the filters
            result = Search_User(filters)

            # Assert: Check that the result matches expected structure and content
            self.assertEqual(result['page'], 1)
            self.assertEqual(result['per_page'], 2)
            self.assertTrue(result['total_pages'] >= 1)
            self.assertTrue(result['total_users'] >= 2)
            self.assertEqual(len(result['users']), 2)
            self.assertTrue(all(user['first_name'] == 'Test' for user in result['users']))

    # def test_search_user_pagination(self):
    #     """Test searching users with pagination."""
    #     with self.app.app_context():
    #         # Assume users are added from a previous test or during setup

    #         # Define filters to search for all users, but only get the second page
    #         filters = {'page': 2, 'per_page': 1}

    #         # Act: Search users using the filters for pagination
    #         result = Search_User(filters)

    #         # Assert: Validate pagination works as expected
    #         self.assertEqual(result['page'], 2)
    #         self.assertEqual(result['per_page'], 1)
    #         self.assertTrue(result['total_pages'] >= 2)  # Assuming at least 2 users exist
    #         self.assertTrue(result['total_users'] >= 2)  # Assuming at least 2 users exist
    #         self.assertEqual(len(result['users']), 1)  # Should have 1 user on the second page if per_page is 1
    
    
    def test_validate_user_success(self):
        # Test user validation succeeds when email and user_id match.
        with self.app.app_context():
            # Setup: Create a user to validate
            user = User(
                user_id=100,  # Ensure a unique user_id
                email='valid@example.com',
                password='password',
                role='1'
                
            )
            db.session.add(user)
            db.session.commit()

            # Act: Attempt to validate the created user by user_id and email
            is_valid, validated_user = Validate_User(100, 'valid@example.com')

            # Assert: Verify that validation succeeds
            self.assertTrue(is_valid)
            self.assertIsNotNone(validated_user)
            self.assertEqual(validated_user.email, 'valid@example.com')

    def test_validate_user_failure(self):
        # Test user validation fails when email does not match user_id.
        with self.app.app_context():
            # Setup: Create a user to attempt to validate incorrectly
            user = User(
                user_id='101',  # Ensure a unique user_id
                email='invalid@example.com',
                password='password',
                role='1'
            )
            db.session.add(user)
            db.session.commit()

            # Act: Attempt to validate the user with a correct user_id but incorrect email
            is_valid, validated_user = Validate_User(101, 'wrong@example.com')

            # Assert: Verify that validation fails
            self.assertFalse(is_valid)
            self.assertIsNone(validated_user)

    def test_get_user_information(self):
        # Test retrieving information for a specific user.
        with self.app.app_context():
            # Setup: Create a user whose information will be retrieved
            new_user = User(
                user_id=123,  # Make sure this ID is unique or auto-generated
                email='info@example.com',
                password='securePassword',
                first_name='Test',
                last_name='User',
                role=2,  # Example role
                # Add any other required fields
            )
            db.session.add(new_user)
            db.session.commit()

            # Get the user's ID (if not manually set)
            user_id = new_user.user_id

            # Act: Retrieve the user information using the function under test
            retrieved_user = Get_User_Information(user_id)

            # Assert: Verify that the retrieved information matches the created user
            self.assertIsNotNone(retrieved_user)
            self.assertEqual(retrieved_user.email, 'info@example.com')
            self.assertEqual(retrieved_user.first_name, 'Test')
            self.assertEqual(retrieved_user.last_name, 'User')
            self.assertEqual(retrieved_user.role, 2)
            # Add any other assertions for fields you care about
            
            
    # @patch('app.service.users.user_service.decode_token')
    # def test_check_user_token_not_expired(self, mock_decode_token):
    #     """Test checking a user token that has not expired."""
    #     with self.app.app_context():
    #         # Correct import used here
    #         future_expiration = datetime.utcnow() + timedelta(hours=1)
    #         mock_decode_token.return_value = {'exp': future_expiration.timestamp()}

    #         # Assuming jwt.encode is used correctly with the current application context
    #         token = jwt.encode({'exp': future_expiration}, current_app.config['JWT_SECRET_KEY'], algorithm="HS256")

    #         # Assuming Check_User_Token_Expiration is defined correctly and imported
    #         is_expired = Check_User_Token_Expiration(token)

    #         # Assert the token is not expired
    #         self.assertFalse(is_expired)


    # @patch('app.service.users.user_service.decode_token')
    # def test_check_user_token_expired(self, mock_decode_token):
    #     """Test checking a user token that has expired."""
    #     with self.app.app_context():
    #         # Mock the decode_token to return a past expiration timestamp
    #         past_expiration = datetime.utcnow() - timedelta(hours=1)
    #         mock_decode_token.return_value = {'exp': past_expiration.timestamp()}

    #         # Use Flask's current_app to access the app configuration
    #         token = jwt.encode({'exp': past_expiration}, current_app.config['JWT_SECRET_KEY'], algorithm="HS256")

    #         # Call the Check_User_Token_Expiration function
    #         is_expired = Check_User_Token_Expiration(token)

    #         # Assert the token is expired
    #         self.assertTrue(is_expired)
    
    
    
#     add_farmer_to_system function within your TestUserRoutes class, we'll write unit tests to verify that:

# An admin user can successfully add a farmer.
# A non-admin user cannot add a farmer and receives an unauthorized access message.



if __name__ == '__main__':
    unittest.main(verbosity=2, testRunner=xmlrunner.XMLTestRunner(output='test-reports'))
