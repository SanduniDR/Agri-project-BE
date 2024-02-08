import os

from flask import Flask
from app.models import db, Farm, User, Role
from app.schemas import ma
from app.routes import app as app_blueprint
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from app.route.user_routes import user_routes, configure_mail
from app.route.farm_routes import farm_routes
from app.route.crop_routes import crop_routes
from app.route.mis_report import report_routes
from app.route.cultivation_routes import cultivation_routes
from app.route.aid_routes import aid_routes

from flask_mail import Mail, Message
from datetime import datetime

app = Flask(__name__)

# Load app configurations from config.py if needed
# app.config.from_pyfile('config.py')

# Set SQLite DB directory
basedir = os.path.abspath(os.path.dirname(__file__))
# Set Flask SQLAlchemy config of the DB file location
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'agriInfo.db')
app.config['JWT_SECRET_KEY'] = 'super_key'

# Mail sending with mail trap
app.config['MAIL_SERVER'] = 'sandbox.smtp.mailtrap.io' # 'live.smtp.mailtrap.io' 
app.config['MAIL_PORT'] = 2525 # 587 
app.config['MAIL_USERNAME'] = '1df254ae2a5632'
app.config['MAIL_PASSWORD'] = '9f1406b11941e8' # '1db8cb3672f98834458426ea50222fd9'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

# mail sending with GMAIL
# mail_settings = {
#     "MAIL_SERVER": 'smtp.gmail.com',
#     "MAIL_PORT": 465,
#     "MAIL_USE_TLS": False,
#     "MAIL_USE_SSL": True,
#     "MAIL_USERNAME": 'sandaruwandanushka@gmail.com' # os.environ['EMAIL_USER'],
#     "MAIL_PASSWORD": os.environ['EMAIL_PASSWORD']
# }
# app.config.update(mail_settings)

# Initialize SQLAlchemy and Marshmallow
db.init_app(app)
ma.init_app(app)
jwt = JWTManager(app)
configure_mail(app)

# Register the app_blueprint
app.register_blueprint(app_blueprint)
app.register_blueprint(user_routes, url_prefix='/user')
app.register_blueprint(farm_routes, url_prefix='/farm')
app.register_blueprint(crop_routes, url_prefix='/crop')
app.register_blueprint(cultivation_routes, url_prefix='/cultivation')
app.register_blueprint(aid_routes, url_prefix='/aid')
app.register_blueprint(report_routes, url_prefix='/report')

if __name__ == '__main__':
    app.run()


@app.cli.command('db_create')
def db_create():
    db.create_all()
    print("DB created!")


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print("DB dropped!")


@app.cli.command('db_seed')
def db_seed():
    # default_farm01 = Farm(farm_name='Nilwala Agri products',
    #                       farm_address='Yatiyana Road, Matara',
    #                       farm_type='Animal',
    #                       farm_phone_no='0756485071')
    # default_farm02 = Farm(farm_name='Kandy products',
    #                       farm_address='Mula Road, Kandy',
    #                       farm_type='Plants',
    #                       farm_phone_no='0756485072')
    # db.session.add(default_farm01)
    # db.session.add(default_farm02)

    # adding initial roles
    roles = [
        Role(role_id=1, role_name='Admin', role_description='Admin role'),
        Role(role_id=2, role_name='User', role_description='Generic User role'),
        Role(role_id=3, role_name='RegionalAdmin', role_description='Regional Admin role'),
        Role(role_id=4, role_name='AgricultureOfficer', role_description='Agriculture Officer role'),
        Role(role_id=5, role_name='Farmer', role_description='Farmer role'),
        Role(role_id=6, role_name='Researcher', role_description='Researcher/Student role')
    ]

    for role in roles:
        db.session.add(role)
    db.session.commit()

    dob = datetime.strptime('1997-12-31', '%Y-%m-%d').date()
    test_user = User(first_name='Dhanushka',
                     middle_name='Pahalage',
                     last_name='Sandaruwan',
                     email='sandaruwandanushka@gmail.com',
                     nic='199712345678',
                     dob=dob,
                     password='test@1234',
                     role=2)
    admin_user = User(first_name='Admin',
                      middle_name='Admin',
                      last_name='Admin',
                      email='a',
                      nic='199712345670',
                      dob=dob,
                      password='a',
                      role=1)
    db.session.add(test_user)
    db.session.add(admin_user)
    db.session.commit()
