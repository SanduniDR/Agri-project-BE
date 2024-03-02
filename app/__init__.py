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
from app.route.communication_routes import com_routes
from app.route.aid_routes import aid_routes
from app.route.marketplace_routes import market_routes
from app.route.disaster_routes import disaster_routes

from flask_mail import Mail, Message
from datetime import datetime

app = Flask(__name__)

# Set SQLite DB directory
basedir = os.path.abspath(os.path.dirname(__file__))
# Set Flask SQLAlchemy config of the DB file location
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'agriInfo.db')
app.config['JWT_SECRET_KEY'] = 'super_key'


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
app.register_blueprint(com_routes, url_prefix='/communication')
app.register_blueprint(market_routes, url_prefix='/market')
app.register_blueprint(disaster_routes, url_prefix='/disaster')


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
#     ##################
#     # Add 10 mock AgriOffices
#     roles = [
#         Role(role_id=1, role_name='Admin', role_description='Admin role'),
#         Role(role_id=2, role_name='User', role_description='Generic User role'),
#         Role(role_id=3, role_name='RegionalAdmin', role_description='Regional Admin role'),
#         Role(role_id=4, role_name='AgricultureOfficer', role_description='Agriculture Officer role'),
#         Role(role_id=5, role_name='Farmer', role_description='Farmer role'),
#         Role(role_id=6, role_name='Researcher', role_description='Researcher/Student role')
#     ]

#     for role in roles:
#         db.session.add(role)
#     db.session.commit()

#     sri_lanka_districts = [
#         "Ampara",
#         "Anuradhapura",
#         "Badulla",
#         "Batticaloa",
#         "Colombo",
#         "Galle",
#         "Gampaha",
#         "Hambantota",
#         "Jaffna",
#         "Kalutara",
#         "Kandy",
#         "Kegalle",
#         "Kilinochchi",
#         "Kurunegala",
#         "Mannar",
#         "Matale",
#         "Matara",
#         "Monaragala",
#         "Mullaitivu",
#         "Nuwara Eliya",
#         "Polonnaruwa",
#         "Puttalam",
#         "Ratnapura",
#         "Trincomalee",
#         "Vavuniya"
#     ]

#     ############################## Add 26 mock AgriOffices
#     for i, district in enumerate(sri_lanka_districts, 1):
#         agri_office = AgriOffice(
#             name=f'AgriOffice{i}',
#             city=f'City{i}',
#             province=f'Province{i}',
#             district=district
#         )
#         db.session.add(agri_office)

#     db.session.commit()

#     #####################
#     # Add 5 mock Crops
#     crops = ['Paddy', 'Tea', 'Carrot', 'Onion', 'Potato']
#     for i, crop_name in enumerate(crops, 1):
#         crop = Crop(
#             crop_name=crop_name,
#             breed=f'Breed{i}',
#             description=f'Description of {crop_name}',
#             updated_by='Seeder',
#             added_by='Seeder'
#         )
#         db.session.add(crop)

#     ##################################
#     farmer_role = Role.query.filter_by(role_name='Farmer').first()
#     if farmer_role is None:
#         print("Farmer role not found!")
#         return

#     farmer_role_id = 5

#     # Add 100 mock farmers
#     for i in range(1, 1000):
#         dob = datetime.strptime('1990-01-01', '%Y-%m-%d').date()
#         farmer = User(
#             first_name=f'Farmer{i}',
#             middle_name=f'Middle{i}',
#             last_name=f'Last{i}',
#             email=f'farmer{i}@example.com',
#             nic=f'1990{i:08}',
#             dob=dob,
#             password='password',
#             role=farmer_role_id
#         )
#         db.session.add(farmer)

#     db.session.commit()

#     # Get the IDs of all farmers
#     farmer_ids = [farmer.user_id for farmer in User.query.filter_by(role=5).all()]

#     # # Add 80 mock Farms
#     for i in range(1, 1000):
#         farm = Farm(
#             farm_name=f'Farm{i}',
#             address=f'Address{i}',
#             type='Crop',
#             farmer_id=random.choice(farmer_ids),
#             area_of_field=f'{i} acres',
#             owner_nic=f'1990{i:08}',
#             owner_name=f'Owner{i}'
#         )
#         db.session.add(farm)

#     db.session.commit()

#     dob = datetime.strptime('1997-12-31', '%Y-%m-%d').date()
#     test_user = User(first_name='Dhanushka',
#                      middle_name='Pahalage',
#                      last_name='Sandaruwan',
#                      email='sandaruwandanushka@gmail.com',
#                      nic='199712345678',
#                      dob=dob,
#                      password='test@1234',
#                      role=2)
#     admin_user = User(first_name='Admin',
#                       middle_name='Admin',
#                       last_name='Admin',
#                       email='a',
#                       nic='199712345670',
#                       dob=dob,
#                       password='a',
#                       role=1)
#     db.session.add(test_user)
#     db.session.add(admin_user)
#     db.session.commit()
# ########################################################################################
#     print("DB seeded!")
#     # Get the IDs of all farmers and farms
#     farmer_ids = [farmer.user_id for farmer in User.query.filter_by(role=5).all()]
#     farm_ids = [farm.farmer_id for farm in Farm.query.all()]
#     crop_ids = [crop.crop_id for crop in Crop.query.all()]
#     # Define the range of latitudes and longitudes for Sri Lanka
#     lat_range = (5.9248, 9.6615)
#     lon_range = (79.6520, 81.9297)

#     # # Add 100 mock CultivationInfo records
#     for i in range(1, 101):
#         started_date = datetime.now() - timedelta(days=random.randint(1, 365))
#         estimated_harvesting_date = started_date + timedelta(days=random.randint(30, 120))

#         cultivation_info = CultivationInfo(
#             display_name=f'Cultivation{i}',
#             farm_id=random.choice(farm_ids),
#             crop_id=random.choice(crop_ids),
#             longitude=random.uniform(*lon_range),
#             latitude=random.uniform(*lat_range),
#             area_of_cultivation=f'{i}',
#             started_date=started_date,
#             estimated_harvesting_date=estimated_harvesting_date,
#             estimated_harvest=f'{i}',
#             agri_year=random.choice(['2022', '2023', '2024']),
#             quarter=random.choice(['Q1', 'Q2', 'Q3', 'Q4']),
#             added_by=random.choice(farmer_ids),
#             updated_by=random.choice(farmer_ids),
#             harvested_date=estimated_harvesting_date + timedelta(days=random.randint(1, 30)),
#             harvested_amount=f'{i}',
#             added_date=datetime.now()
#         )
#         db.session.add(cultivation_info)
    
#     # Fetch all AgriOffices
#     agri_offices = AgriOffice.query.all()

#     for office in agri_offices:
#         # Generate a random number of FieldAreas for each office
#         num_field_areas = random.randint(1, 5)

#         for i in range(num_field_areas):
#             # Create a new FieldArea record
#             new_field_area = FieldArea(
#                 agri_office_id=office.agri_office_id,
#                 name=f'Field Area {i+1}'
#             )

#             # Add the new FieldArea record to the session
#             db.session.add(new_field_area)

#     db.session.commit()
# #################################################################33
#     farmers = User.query.filter_by(role=5).all()

#     # Fetch all office IDs
#     office_ids = [office.agri_office_id for office in AgriOffice.query.all()]

#     # Fetch all field area IDs
#     field_area_ids = [field_area.field_area_id for field_area in FieldArea.query.all()]

#     #########################################################
#     # Fetch all field area IDs
#     # Fetch all field area IDs
#     field_area_ids = [field_area.field_area_id for field_area in FieldArea.query.all()]
#     agri_office_ids = [agri_office.agri_office_id for agri_office in AgriOffice.query.all()]

#     # Add 60 mock officers
#     for i in range(1, 61):
#         officer = AgricultureOfficer(
#             user_id=i,
#             employee_id=f'Employee{i}',
#             managed_by_employee_id=f'Manager{i}',
#             agri_office_id=random.choice(agri_office_ids),
#             service_start_date=datetime.now(),
#             field_area_id=random.choice(field_area_ids),
#         )
#         db.session.add(officer)

#     db.session.commit()


#     #########################################################

#     # Create a FarmerSchema instance
#         # Fetch all AgriOffices
#     agri_offices = AgriOffice.query.all()

#     # Fetch all field area IDs
#     field_area_ids = [field_area.field_area_id for field_area in FieldArea.query.all()]

#     for farmer in farmers:
#         # Assign to offices and field areas randomly
#         assigned_office_id = random.choice(office_ids)
#         assigned_field_area_id = random.choice(field_area_ids)
#             # Create a new Farmer record
#         new_farmer = Farmer(
#             user_id=farmer.user_id,
#             assigned_office_id=assigned_office_id,
#             assigned_field_area_id=assigned_field_area_id,
#             updated_by='Seeder',
#             added_by='Seeder',
#             registered_date=datetime.now(),
#             tax_file_no=f'TAX{farmer.user_id:05}'
#         )

#         # Add the new Farmer record to the session
#         db.session.add(new_farmer)

#     # Commit the session to save the changes
#     db.session.commit()
#     ###################################################
# ########################################################################
#  # Fetch all AgriOffices
#     # Fetch all AgriOffices
#     agri_offices = AgriOffice.query.all()

#     # Fetch all Farms
#     farms = Farm.query.all()

#     # Fetch all Crops
#     crops = Crop.query.all()

#     # Fetch all farmers
#     farmer_ids = [farmer.user_id for farmer in User.query.filter_by(role=5).all()]

#     # For each office
#     for office in agri_offices:
#         # For each farm
#         for farm in farms:
#             # For each crop
#             print(farm.farm_id)
#             for crop in crops:
#                 # Add 1000 mock CultivationInfo records
#                 for i in range(1, 10):
#                     started_date = datetime.now() - timedelta(days=random.randint(1, 365))
#                     estimated_harvesting_date = started_date + timedelta(days=random.randint(30, 120))

#                     cultivation_info = CultivationInfo(
#                         display_name=f'Cultivation{i}',
#                         farm_id=farm.farm_id,  # Use the farm ID
#                         crop_id=crop.crop_id,  # Use the crop ID
#                         longitude=random.uniform(*lon_range),
#                         latitude=random.uniform(*lat_range),
#                         area_of_cultivation=f'{i}',
#                         started_date=started_date,
#                         estimated_harvesting_date=estimated_harvesting_date,
#                         estimated_harvest=f'{i}',
#                         agri_year=random.choice(['2022', '2023', '2024']),
#                         quarter=random.choice(['Q1', 'Q2', 'Q3', 'Q4']),
#                         added_by=random.choice(farmer_ids),
#                         updated_by=random.choice(farmer_ids),
#                         harvested_date=estimated_harvesting_date + timedelta(days=random.randint(1, 30)),
#                         harvested_amount=f'{i}',
#                         added_date=datetime.now()
#                     )
#                     db.session.add(cultivation_info)

#     db.session.commit()
    ##################################################################################
    # Generate random string
    def random_string(length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    # Generate random date
    def random_date():
        return datetime.now() - timedelta(days=random.randint(1,365))
    
    def random_aid_type():
        aid_types = ['Seeds', 'Plastic', 'Plants', 'Tools', 'Other']
        return random.choice(aid_types)

    # Seed Aid table
    aid_ids = []
    for year in range(2021, 2025):
        for i in range(20):
            aid = Aid(
                aid_name=random_string(10),
                aid_batch=random_string(5),
                year=year,
                in_charged_office_id=random.randint(1, 10),  # replace with actual office ids
                description=random_string(50)
            )
            db.session.add(aid)
            db.session.commit()
            aid_ids.append(aid.aid_id)

    # Seed other tables
    for aid_id in aid_ids:
        for _ in range(50):
            fertilizer = Fertilizer(
                aid_id=aid_id,
                manufactured_date=random_date(),
                brand=random_string(10),
                batch_no=random_string(5),
                expiry_date=random_date(),
                name=random_string(10),
                type=random_string(5),
                description="Fertilizer"
            )
            db.session.add(fertilizer)

            pesticides = Pesticides(
                aid_id=aid_id,
                manufactured_date=random_date(),
                brand=random_string(10),
                batch_no=random_string(5),
                expiry_date=random_date(),
                name=random_string(10),
                type=random_string(5),
                description="Pesticides"
            )
            db.session.add(pesticides)

            monetary_aid = MonetaryAid(
                aid_id=aid_id,
                description=random_string(50),
                reason=random_string(20)
            )
            db.session.add(monetary_aid)

            fuel = Fuel(
                aid_id=aid_id,
                reason=random_string(20),
                description=random_string(50),
                fuel_type=random_string(10)
            )
            db.session.add(fuel)

            miscellaneous_aids = MiscellaneousAids(
                aid_id=aid_id,
                type=random_string(10),
                reason=random_string(20),
                description=random_aid_type()
            )
            db.session.add(miscellaneous_aids)

            aid_distribution = AidDistribution(
                aid_id=aid_id,
                agri_office_id=random.randint(1, 10),  # replace with actual office ids
                date=random_date(),
                time="10:00",  # replace with actual time
                in_charged_officer_id=random.randint(1, 10),  # replace with actual officer ids
                cultivation_info_id=random.randint(1, 10),  # replace with actual cultivation info ids
                farmer_id=random.randint(1, 10),  # replace with actual farmer ids
                amount_received=random.randint(1000, 5000),
                amount_approved=random.randint(5000, 10000),
                description=random_string(50)
            )
            db.session.add(aid_distribution)

        db.session.commit()

    #################################################################################

    #     # Fetch all AgriOffices
    # agri_offices = AgriOffice.query.all()

    # # Fetch all farmers
    # farmer_ids = [farmer.user_id for farmer in User.query.filter_by(role=5).all()]

    # # Fetch all officers
    # officer_ids = [officer.user_id for officer in User.query.filter_by(role=4).all()]

    # # Fetch all cultivation info
    # cultivation_info_ids = [info.cultivation_info_id for info in CultivationInfo.query.all()]

    # # Description options
    # descriptions = ['Fuel', 'Fertilizer', 'Monetary', 'Pesticide', 'Other']

    # # For each aid id
    # for aid_id in [1, 2, 3]:
    #     # For each year
    #     for year in [2022, 2023, 2024]:
    #         # Add 100 mock AidDistribution records
    #         for i in range(1, 10):
    #             distribution_date = datetime(year, random.randint(1, 12), random.randint(1, 28))

    #             aid_distribution = AidDistribution(
    #                 aid_id=aid_id,
    #                 agri_office_id=random.choice(agri_offices).agri_office_id,
    #                 date=distribution_date,
    #                 in_charged_officer_id='1',
    #                 cultivation_info_id=random.choice(cultivation_info_ids),
    #                 farmer_id=random.choice(farmer_ids),
    #                 amount_received=random.uniform(100, 1000),
    #                 amount_approved=random.uniform(100, 1000),
    #                 description=random.choice(descriptions)
    #             )
    #             db.session.add(aid_distribution)

    # db.session.commit()