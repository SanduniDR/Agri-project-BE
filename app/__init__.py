import os
import random

from flask import Flask
from app.models import db,DisasterInfo, MiscellaneousAids, Fuel, MonetaryAid, Pesticides,Farm, User, Role, CultivationInfo, Crop, AgriOffice, Farmer, FieldArea, AgricultureOfficer,AidDistribution, Fertilizer, Aid
from app.schemas import ma, cultivation_info_schema
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
from app.route.file_management_routes import file_routes
import string

from flask_mail import Mail, Message
from datetime import datetime, timedelta

app = Flask(__name__)

# Set SQLite DB directory
basedir = os.path.abspath(os.path.dirname(__file__))
# Set Flask SQLAlchemy config of the DB file location
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'agriInfo.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/agriInfo'
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
app.register_blueprint(file_routes, url_prefix='/file')

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
    #################
    # Add 10 mock AgriOffices
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

    sri_lanka_districts = [
        "Ampara",
        "Anuradhapura",
        "Badulla",
        "Batticaloa",
        "Colombo",
        "Galle",
        "Gampaha",
        "Hambantota",
        "Jaffna",
        "Kalutara",
        "Kandy",
        "Kegalle",
        "Kilinochchi",
        "Kurunegala",
        "Mannar",
        "Matale",
        "Matara",
        "Monaragala",
        "Mullaitivu",
        "Nuwara Eliya",
        "Polonnaruwa",
        "Puttalam",
        "Ratnapura",
        "Trincomalee",
        "Vavuniya"
    ]

    # cities = ["city1", "city2", "city3", "city4", "city5", "city6", "city7", "city8", "city9", "city10"]
    # test_cities = ["test_" + city for city in cities]
    # provinces = ["Province1", "Province2", "Province3", "Province4", "Province5", "Province6", "Province7", "Province8", "Province9"]
    # test_provinces = ["test_" + province for province in provinces]

    sri_lanka = [
        {
            "province": "Western",
            "districts": [
                {"name": "Colombo", "cities": ["Colombo", "Dehiwala-Mount Lavinia", "Moratuwa"]},
                {"name": "Gampaha", "cities": ["Gampaha", "Negombo", "Wattala"]},
                {"name": "Kalutara", "cities": ["Kalutara", "Panadura", "Horana"]}
            ]
        },
        {
            "province": "Central",
            "districts": [
                {"name": "Kandy", "cities": ["Kandy", "Peradeniya", "Matale"]},
                {"name": "Matale", "cities": ["Matale", "Dambulla", "Sigiriya"]},
                {"name": "Nuwara Eliya", "cities": ["Nuwara Eliya", "Hatton", "Nanu Oya"]}
            ]
        },
        {
            "province": "Southern",
            "districts": [
                {"name": "Galle", "cities": ["Galle", "Ambalangoda", "Hikkaduwa"]},
                {"name": "Matara", "cities": ["Matara", "Weligama", "Mirissa"]},
                {"name": "Hambantota", "cities": ["Hambantota", "Tissamaharama", "Matara"]}
            ]
        },
        {
            "province": "Northern",
            "districts": [
                {"name": "Jaffna", "cities": ["Jaffna", "Point Pedro", "Nallur"]},
                {"name": "Kilinochchi", "cities": ["Kilinochchi", "Mankulam", "Oddusuddan"]},
                {"name": "Mannar", "cities": ["Mannar", "Nanattan", "Vidathaltheevu"]},
                {"name": "Mullaitivu", "cities": ["Mullaitivu", "Oddusuddan", "Puthukudiyiruppu"]},
                {"name": "Vavuniya", "cities": ["Vavuniya", "Nedunkeni", "Pampaimadu"]}
            ]
        },
        {
            "province": "Eastern",
            "districts": [
                {"name": "Batticaloa", "cities": ["Batticaloa", "Kattankudy", "Eravur"]},
                {"name": "Ampara", "cities": ["Ampara", "Kalmunai", "Sammanthurai"]},
                {"name": "Trincomalee", "cities": ["Trincomalee", "Kinniya", "Verugal"]}
            ]
        },
        {
            "province": "North Western",
            "districts": [
                {"name": "Kurunegala", "cities": ["Kurunegala", "Kuliyapitiya", "Nikaweratiya"]},
                {"name": "Puttalam", "cities": ["Puttalam", "Anamaduwa", "Chilaw"]}
            ]
        },
        {
            "province": "North Central",
            "districts": [
                {"name": "Anuradhapura", "cities": ["Anuradhapura", "Medawachchiya", "Tambuttegama"]},
                {"name": "Polonnaruwa", "cities": ["Polonnaruwa", "Hingurakgoda", "Medirigiriya"]}
            ]
        },
        {
            "province": "Uva",
            "districts": [
                {"name": "Badulla", "cities": ["Badulla", "Bandarawela", "Haputale"]},
                {"name": "Monaragala", "cities": ["Monaragala", "Bibile", "Buttala"]}
            ]
        },
        {
            "province": "Sabaragamuwa",
            "districts": [
                {"name": "Ratnapura", "cities": ["Ratnapura", "Embilipitiya", "Kuruwita"]},
                {"name": "Kegalle", "cities": ["Kegalle", "Mawanella", "Rambukkana"]}
            ]
        }
    ]

    ############################## Add mock AgriOffices
    for i in range(1, 100):
        province = random.choice(sri_lanka)
        district = random.choice(province['districts'])
        agri_office = AgriOffice(
            name=f'AgriOffice{i}',
            city=random.choice(district['cities']),
            province=province['province'],
            district=district['name'],
        )
        db.session.add(agri_office)

    db.session.commit()
    ############################################## Add Filed Areas
    agri_offices = AgriOffice.query.all()

    for office in agri_offices:
        # Generate a random number of FieldAreas for each office
        num_field_areas = random.randint(1, 5)

        for i in range(num_field_areas):
            # Create a new FieldArea record
            print(office.agri_office_id)
            new_field_area = FieldArea(
                agri_office_id=office.agri_office_id,
                name=f'Field Area {i+1}'
            )

            # Add the new FieldArea record to the session
            db.session.add(new_field_area)

    db.session.commit()
    ############################################## Add mock Crops
    # Add 5 mock Crops
    crops = ['Paddy', 'Tea', 'Carrot', 'Onion', 'Potato']
    for i, crop_name in enumerate(crops, 1):
        crop = Crop(
            crop_name=crop_name,
            breed=f'Breed{i}',
            description=f'Description of {crop_name}',
            updated_by='Seeder',
            added_by='Seeder'
        )
        db.session.add(crop)

    ##################################
    farmer_role = Role.query.filter_by(role_name='Farmer').first()
    if farmer_role is None:
        print("Farmer role not found!")
        return

    farmer_role_id = 5

    # Add 100 mock farmers
    for i in range(1, 200):
        dob = datetime.strptime('1990-01-01', '%Y-%m-%d').date()
        farmer = User(
            first_name=f'Farmer{i}',
            middle_name=f'Middle{i}',
            last_name=f'Last{i}',
            email=f'farmer{i}@example.com',
            nic=f'1990{i:08}',
            dob=dob,
            password='password',
            role=farmer_role_id
        )
        db.session.add(farmer)

    db.session.commit()

    # Get the IDs of all farmers
    farmer_ids = [farmer.user_id for farmer in User.query.filter_by(role=5).all()]
    farms = [farm.farm_id for farm in Farm.query.all()]
    field_areas = [field_area for field_area in FieldArea.query.all()]

    # # Add 80 mock Farms
    for i in range(1, 50):
        field_area = random.choice(field_areas)
        office_id = field_area.agri_office_id
        farm = Farm(
            farm_name=f'Farm{i}',
            address=f'Address{i}',
            type='Crop',
            farmer_id=random.choice(farmer_ids),
            area_of_field=f'{i}',
            owner_nic=f'1990{i:08}',
            owner_name=f'Owner{i}',
            field_area_id=field_area.field_area_id,
            office_id=office_id,
        )
        db.session.add(farm)

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
################################################################### Add Field officers
    # Fetch all field area IDs
    # Fetch all field area IDs
    field_area_ids = [field_area for field_area in FieldArea.query.all()]
    # agri_office_ids = [agri_office.agri_office_id for agri_office in AgriOffice.query.all()]

    for i in range(1, 101):
        new_user = User(
            first_name='FirstName' + str(i),
            middle_name='MiddleName' + str(i),
            last_name='LastName' + str(i),
            nic='NIC' + str(i),
            email='email' + str(i) + '@example.com',
            password='test_pwd',
            dob=datetime(1980, 1, 1),  # Set a default DOB
            role=4
        )
        db.session.add(new_user)

    db.session.commit()
    users_with_role_4 = User.query.filter_by(role=4).all()
    # for user in users_with_role_4:
        # print(user.first_name, user.last_name)
    # Add 60 mock officers
    for user in users_with_role_4:
        field_area = random.choice(field_areas)
        officer = AgricultureOfficer(
            user_id=user.user_id,
            employee_id=f'Employee{user.user_id}',
            managed_by_employee_id='1',
            agri_office_id=field_area.agri_office_id,
            service_start_date=datetime.now(),
            field_area_id=field_area.field_area_id,
        )
        db.session.add(officer)

    db.session.commit()
########################################################################################
    # Get the IDs of all farmers and farms
    farmer_ids1 = [farmer.user_id for farmer in User.query.filter_by(role=5).all()]
    farm_ids1 = [farm.farm_id for farm in Farm.query.all()]
    crop_ids1 = [crop.crop_id for crop in Crop.query.all()]
    agri_offices1 = AgriOffice.query.all()
    # Define the range of latitudes and longitudes for Sri Lanka
    # lat_range = (5.9248, 9.6615)
    # lon_range = (79.6520, 81.9297)
    ranges = [{'city': 'Colombo', 'latitude': 6.9388614, 'longitude': 79.8542005}, {'city': 'Dehiwala-Mount Lavinia', 'latitude': 6.8352314, 'longitude': 79.8673945}, {'city': 'Moratuwa', 'latitude': 6.7746821, 'longitude': 79.8826095}, {'city': 'Gampaha', 'latitude': 7.1190247499999995, 'longitude': 79.91598756451819}, {'city': 'Negombo', 'latitude': 7.2094282, 'longitude': 79.833117}, {'city': 'Wattala', 'latitude': 6.9898705, 'longitude': 79.8927094}, {'city': 'Kalutara', 'latitude': 6.5745305, 'longitude': 80.02863119765179}, {'city': 'Panadura', 'latitude': 6.7124685, 'longitude': 79.9044746}, {'city': 'Horana', 'latitude': 6.716628, 'longitude': 80.0619488}, {'city': 'Kandy', 'latitude': 7.2931208, 'longitude': 80.6350358}, {'city': 'Peradeniya', 'latitude': 7.2642107, 'longitude': 80.5930652}, {'city': 'Matale', 'latitude': 7.698211, 'longitude': 80.66090797017742}, {'city': 'Dambulla', 'latitude': 7.8742031, 'longitude': 80.6510917}, {'city': 'Sigiriya', 'latitude': 7.95638465, 'longitude': 80.759825710275}, {'city': 'Nuwara Eliya', 'latitude': 7.012402, 'longitude': 80.75716115484704}, {'city': 'Hatton', 'latitude': 47.6397087, 'longitude': -97.4534224}, {'city': 'Nanu Oya', 'latitude': 6.9453246, 'longitude': 80.7494588}, {'city': 'Galle', 'latitude': 6.0328139, 'longitude': 80.214955}, {'city': 'Ambalangoda', 'latitude': 6.2389059, 'longitude': 80.0541466}, {'city': 'Hikkaduwa', 'latitude': 6.140753, 'longitude': 80.1028181}, {'city': 'Matara', 'latitude': 5.947822, 'longitude': 80.5482919}, {'city': 'Weligama', 'latitude': 5.9754333, 'longitude': 80.4295612}, {'city': 'Mirissa', 'latitude': 5.9493634, 'longitude': 80.4558128}, {'city': 'Hambantota', 'latitude': 6.176392, 'longitude': 81.13211949976017}, {'city': 'Jaffna', 'latitude': 9.665093, 'longitude': 80.0093029}, {'city': 'Point Pedro', 'latitude': 9.8241007, 'longitude': 80.2361837}, {'city': 'Nallur', 'latitude': 9.4532099, 'longitude': 80.2608912}, {'city': 'Kilinochchi', 'latitude': 9.3840068, 'longitude': 80.4087224}, {'city': 'Mankulam', 'latitude': 8.5259214, 'longitude': 76.9458904}, {'city': 'Oddusuddan', 'latitude': 9.180866, 'longitude': 80.6625934}, {'city': 'Mannar', 'latitude': 7.674124750000001, 'longitude': 78.93709277882492}, {'city': 'Nanattan', 'latitude': 8.8356502, 'longitude': 79.967523}, {'city': 'Vidathaltheevu', 'latitude': 9.0215013, 'longitude': 80.0513896}, {'city': 'Mullaitivu', 'latitude': 9.2698532, 'longitude': 80.8145347}, {'city': 'Puthukudiyiruppu', 'latitude': 7.6201721, 'longitude': 81.7606231}, {'city': 'Vavuniya', 'latitude': 8.7593517, 'longitude': 80.5000778}, {'city': 'Nedunkeni', 'latitude': 9.0393539, 'longitude': 80.3698335}, {'city': 'Pampaimadu', 'latitude': 8.7889469, 'longitude': 80.4213922}, {'city': 'Batticaloa', 'latitude': 7.7356027, 'longitude': 81.6941956}, {'city': 'Kattankudy', 'latitude': 7.6804861, 'longitude': 81.7289676}, {'city': 'Eravur', 'latitude': 7.785563, 'longitude': 81.6045991}, {'city': 'Ampara', 'latitude': 7.0617095, 'longitude': 81.8466351552707}, {'city': 'Kalmunai', 'latitude': 7.4131557, 'longitude': 81.8269327}, {'city': 'Sammanthurai', 'latitude': 7.3703313, 'longitude': 81.812472}, {'city': 'Trincomalee', 'latitude': 8.576425, 'longitude': 81.2344952}, {'city': 'Kinniya', 'latitude': 8.5016494, 'longitude': 81.1912179}, {'city': 'Kurunegala', 'latitude': 7.4870464, 'longitude': 80.364908}, {'city': 'Kuliyapitiya', 'latitude': 7.4701428, 'longitude': 80.0440349}, {'city': 'Nikaweratiya', 'latitude': 7.750383, 'longitude': 80.1157229}, {'city': 'Puttalam', 'latitude': 7.981840249999999, 'longitude': 79.82933709234904}, {'city': 'Anamaduwa', 'latitude': 7.8776367, 'longitude': 80.0109366}, {'city': 'Chilaw', 'latitude': 7.5765074, 'longitude': 79.7956755}, {'city': 'Anuradhapura', 'latitude': 8.334985, 'longitude': 80.4106096}, {'city': 'Medawachchiya', 'latitude': 8.5387775, 'longitude': 80.492996}, {'city': 'Polonnaruwa', 'latitude': 7.9395357, 'longitude': 81.0003387}, {'city': 'Hingurakgoda', 'latitude': 8.0415145, 'longitude': 80.9531701}, {'city': 'Medirigiriya', 'latitude': 8.1423253, 'longitude': 80.971342}, {'city': 'Badulla', 'latitude': 6.9900353, 'longitude': 81.0570315}, {'city': 'Bandarawela', 'latitude': 6.8304821, 'longitude': 80.9888204}, {'city': 'Haputale', 'latitude': 6.7682444, 'longitude': 80.9576349}, {'city': 'Monaragala', 'latitude': 6.8725497, 'longitude': 81.3507069}, {'city': 'Bibile', 'latitude': 7.1600897, 'longitude': 81.2254141}, {'city': 'Buttala', 'latitude': 6.760246, 'longitude': 81.2470358}, {'city': 'Ratnapura', 'latitude': 6.6803691, 'longitude': 80.4022975}, {'city': 'Embilipitiya', 'latitude': 6.3340647, 'longitude': 80.8538325}, {'city': 'Kuruwita', 'latitude': 6.7761011, 'longitude': 80.3668957}, {'city': 'Kegalle', 'latitude': 7.11344465, 'longitude': 80.32173952070438}, {'city': 'Mawanella', 'latitude': 7.2523113, 'longitude': 80.4468038}, {'city': 'Rambukkana', 'latitude': 7.3239273, 'longitude': 80.3957479}]

    # # Add mock CultivationInfo records
    for i in range(1, 50000):
        print(i)
        started_date = datetime.now() - timedelta(days=random.randint(1, 365))
        estimated_harvesting_date = started_date + timedelta(days=random.randint(30, 120))
        farm_id= random.choice(farm_ids1)
        # farmOb = Farm.query.get(farm_id)
        offices_id = [farm.office_id for farm in Farm.query.filter(Farm.farm_id == farm_id).all()]
        # Get the city name of the office table from the office id
        print(offices_id[0])
        office = AgriOffice.query.get(offices_id[0])
        city = [office.city for office in AgriOffice.query.filter(AgriOffice.agri_office_id == offices_id[0]).all()]
        print(city)
        longitude = 0
        latitude = 0
        for item in ranges:
            # print(item['city'] , city[0])
            if item['city'] == city[0]:
                # print(item['city'] , city[0], 'found')
                longitude = item['longitude']
                latitude = item['latitude']
                break  # exit the loop once the city is found
        range__ = [0.001, 0.002, -0.001, -0.002]
        lon_range2= longitude + random.choice(range__)
        lat_range2 = latitude + random.choice(range__)        
        cultivation_info = CultivationInfo(
            display_name=f'Cultivation{i}',
            farm_id=farm_id,
            crop_id=random.choice(crop_ids1),
            longitude=lon_range2,
            latitude=lat_range2,
            area_of_cultivation=f'{i}',
            started_date=started_date,
            estimated_harvesting_date=estimated_harvesting_date,
            estimated_harvest=f'{i}',
            agri_year=random.choice(['2022', '2023', '2024']),
            season=random.choice(['Maha', 'Yala']),
            quarter=random.choice(['Q1', 'Q2', 'Q3', 'Q4']),
            added_by=random.choice(farmer_ids),
            updated_by=random.choice(farmer_ids),
            harvested_date=estimated_harvesting_date + timedelta(days=random.randint(1, 30)),
            harvested_amount=f'{i}',
            added_date=datetime.now()
        )
        # result= cultivation_info_schema.dump(cultivation_info)
        # print(result)
        db.session.add(cultivation_info)
    db.session.commit()
    
#################################################################33
    farmers = User.query.filter_by(role=5).all()

    # Fetch all office IDs
    office_ids = [office.agri_office_id for office in AgriOffice.query.all()]

    # Fetch all field area IDs
    field_area_ids = [field_area.field_area_id for field_area in FieldArea.query.all()]

    #########################################################
 


    #########################################################

    # Create a FarmerSchema instance
        # Fetch all AgriOffices
    agri_offices = AgriOffice.query.all()

    # Fetch all field area IDs
    field_area_ids = [field_area.field_area_id for field_area in FieldArea.query.all()]

    for farmer in farmers:
        # Assign to offices and field areas randomly
        assigned_office_id = random.choice(office_ids)
        assigned_field_area_id = random.choice(field_area_ids)
            # Create a new Farmer record
        new_farmer = Farmer(
            user_id=farmer.user_id,
            assigned_office_id=assigned_office_id,
            assigned_field_area_id=assigned_field_area_id,
            updated_by='Seeder',
            added_by='Seeder',
            registered_date=datetime.now(),
            tax_file_no=f'TAX{farmer.user_id:05}'
        )

        # Add the new Farmer record to the session
        db.session.add(new_farmer)

    # Commit the session to save the changes
    db.session.commit()
    ###################################################
########################################################################
 # Fetch all AgriOffices
    # Fetch all AgriOffices
    agri_offices = AgriOffice.query.all()

    # Fetch all Farms
    farms = Farm.query.all()

    # Fetch all Crops
    crops = Crop.query.all()

    # Fetch all farmers
    farmer_ids = [farmer.user_id for farmer in User.query.filter_by(role=5).all()]

    # For each office
    ##################################################################################
    # Generate random string
    print("aid started done")
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
        print("aid loop aids")
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
    print("aid adding done completed")
    ################################################################################

        # Fetch all AgriOffices
    agri_offices = AgriOffice.query.all()

    # Fetch all farmers
    farmer_ids = [farmer.user_id for farmer in User.query.filter_by(role=5).all()]

    # Fetch all officers
    officer_ids = [officer.user_id for officer in User.query.filter_by(role=4).all()]

    # Fetch all cultivation info
    cultivation_info_ids = [info.cultivation_info_id for info in CultivationInfo.query.all()]

    # Description options
    descriptions = ['Fuel', 'Fertilizer', 'Monetary', 'Pesticide', 'Other']

    # For each aid id
    for aid_id in [1, 2, 3]:
        # For each year
        for year in [2022, 2023, 2024]:
            # Add 100 mock AidDistribution records
            for i in range(1, 10):
                distribution_date = datetime(year, random.randint(1, 12), random.randint(1, 28))

                aid_distribution = AidDistribution(
                    aid_id=aid_id,
                    agri_office_id=random.choice(agri_offices).agri_office_id,
                    date=distribution_date,
                    in_charged_officer_id='1',
                    cultivation_info_id=random.choice(cultivation_info_ids),
                    farmer_id=random.choice(farmer_ids),
                    amount_received=random.uniform(100, 1000),
                    amount_approved=random.uniform(100, 1000),
                    description=random.choice(descriptions)
                )
                db.session.add(aid_distribution)

    db.session.commit()
    # Create mock data
    mock_data = [
        DisasterInfo(
            disaster_info_id=1,
            cultivation_info_id=1,
            date=date(2022, 1, 1),
            time="10:00 AM",
            damaged_area=100,
            estimated_damaged_harvest=50,
            estimated_damaged_harvest_value=5000,
            type="Flood"
        ),
        DisasterInfo(
            disaster_info_id=2,
            cultivation_info_id=2,
            date=date(2022, 2, 1),
            time="2:00 PM",
            damaged_area=200,
            estimated_damaged_harvest=100,
            estimated_damaged_harvest_value=10000,
            type="Drought"
        ),
        # Add more mock data here
    ]

    # Add mock data to session
    for item in mock_data:
        db.session.add(item)

    # Commit session
    db.session.commit()