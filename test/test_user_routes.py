import os
import unittest
import json
from flask import Flask
from flask.testing import FlaskClient
from app import app
from app.route import user_routes
from app.models import db, User
from app.service.users.user_service import register_user
from app.service.users.util_service import parse_date
from flask_jwt_extended import JWTManager
import xmlrunner


app = Flask(__name__)
jwt = JWTManager(app)

class TestUserRoutes(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        jwt = JWTManager(self.app)
        self.app.config['JWT_SECRET_KEY'] = 'super_key'
        basedir = os.path.abspath(os.path.dirname(__file__))
        # Set Flask SQLAlchemy config of the DB file location
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'agriInfo.db')
        self.app.register_blueprint(user_routes.user_routes)
        self.client = self.app.test_client()
        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()

    # def tearDown(self):
    #     with self.app.app_context():
    #         # db.session.remove()
    #         # db.drop_all()

    def login(self):
        user = User(email='test@example.com', first_name='Test', last_name='User', password='password', nic='1234567890', dob=parse_date('2000-01-01'), role=2)
        with self.app.app_context():
            # register_user(user)
            response = self.client.post('/login', json={
                'email': 'test@example.com',
                'password': 'password'
            })
        token = json.loads(response.data).get('token')
        print(token)
        return(token)

    # def test_register(self):
    #     response = self.client.post('/register', json={
    #         'email': 'test@example22.com',
    #         'first_name': 'Test',
    #         'last_name': 'User',
    #         'password': 'password',
    #         'nic': '123456789052',
    #         'dob': '2000-01-01',
    #         'role': 2
    #     })
    #     self.assertEqual(response.status_code, 201)
    #     self.assertEqual(response.get_json()['message'], 'Registration success!')
    
    def test_get_user_by_id(self):
        user_id = 4 
        with self.app.app_context():
            token = self.login()
            print(token)
            headers = {'Authorization': f'Bearer {token}'}
            response = self.client.get(f'/{user_id}', headers=headers)
            print(response.get_json())
        self.assertEqual(response.status_code, 200)
    
    def test_update_user(self):
        token = self.login()
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.put('/update/4', headers=headers, json={
           "first_name": 'Test2',
        })
        print(response.data)
        print(os.getcwd())
        self.assertEqual(response.status_code, 200)

    # def test_delete_user(self):
    #     token = self.login()
    #     headers = {'Authorization': f'Bearer {token}'}
    #     response = self.client.delete('/1', headers=headers)
    #     print(response.data)
    #     self.assertEqual(response.status_code, 200)
        
if __name__ == '__main__':
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    runner.run(suite())
    


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestUserRoutes('test_register'))
    test_suite.addTest(TestUserRoutes('test_get_user_by_id')) 
    test_suite.addTest(TestUserRoutes('test_update_user'))  

    return test_suite