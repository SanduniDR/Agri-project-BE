from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

# This file contains the database models for the application.
db = SQLAlchemy()

# The following classes are the database models for the application.
class User(db.Model): # User class
    __tablename__ = 'user' # Table name
    user_id = Column(Integer, primary_key=True) # SQL Alchemy will auto-increment
    first_name = Column(String(100)) # Column name and type
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100))
    nic = Column(String(100), unique=True)
    email = Column(String(100), unique=True)
    password = Column(String(100))
    dob = Column(Date)
    role = Column(Integer, nullable=False)

class Role(db.Model):
    __tablename__ = 'role'
    role_id = Column(Integer, primary_key=True)
    role_name = Column(String(100))
    role_description = Column(String(100))


class Contact(db.Model):
    __tablename__ = 'contact'
    contact_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    number = Column(String(100))
    area_code = Column(String(100))
    user = relationship("User", backref="contacts")

class Address(db.Model):
    __tablename__ = 'address'
    address_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    city = Column(String(100))
    town = Column(String(100))
    street = Column(String(100))
    home_no = Column(String(100))
    home_name = Column(String(100))
    user = relationship("User", backref="addresses")

class SuperAdmin(db.Model):
    __tablename__ = 'super_admin'
    user_id = Column(Integer, ForeignKey('user.user_id'), primary_key=True)
    employee_id = Column(Integer)
    role_type = Column(String(100))
    user = relationship("User", backref="super_admins")

class RegionalAdmin(db.Model):
    __tablename__ = 'regional_admin'
    user_id = Column(Integer, ForeignKey('user.user_id'), primary_key=True)
    employee_id = Column(Integer)
    managed_by_employee_id = Column(Integer)
    district = Column(String(100))
    province = Column(String(100))
    agri_office_id = Column(Integer)
    service_start_date = Column(Date)
    user = relationship("User", backref="regional_admins")

class AgricultureOfficer(db.Model):
    __tablename__ = 'agriculture_officer'
    user_id = Column(Integer, ForeignKey('user.user_id'), primary_key=True)
    employee_id = Column(Integer)
    managed_by_employee_id = Column(Integer)
    agri_office_id = Column(Integer)
    service_start_date = Column(Date)
    field_area_id = Column(Integer)
    user = relationship("User", backref="agriculture_officers")

class AgriOffice(db.Model):
    __tablename__ = 'agri_office'
    agri_office_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    city = Column(String(100))
    province = Column(String(100))
    district = Column(String(100))

class FieldArea(db.Model):
    __tablename__ = 'field_area'
    field_area_id = Column(Integer, primary_key=True)
    agri_office_id = Column(Integer, ForeignKey('agri_office.agri_office_id'))
    name = Column(String(100))
    agri_office = relationship("AgriOffice", backref="field_areas")

class Reports(db.Model):
    __tablename__ = 'reports'
    report_id = Column(Integer, primary_key=True)
    category = Column(String(100))
    date = Column(Date)
    time = Column(String(100))
    user_id = Column(Integer, ForeignKey('user.user_id'))
    link = Column(String(100))
    user = relationship("User", backref="reports")
    
    
class DataRequest(db.Model):
    __tablename__ = 'datarequest'
    request_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    message = Column(String(100))
    date = Column(Date)
    institute = Column(String(100))
    user = relationship("User", backref="data_requests")

class Farmer(db.Model):
    __tablename__ = 'farmer'
    user_id = Column(Integer, ForeignKey('user.user_id'),primary_key=True)
    assigned_office_id = Column(Integer, ForeignKey('agri_office.agri_office_id'))
    assigned_field_area_id = Column(Integer, ForeignKey('field_area.field_area_id'))
    updated_by = Column(Integer)
    added_by = Column(Integer)
    registered_date = Column(Date)
    tax_file_no = Column(String(100))
    user = relationship("User", backref="farmers")
    assigned_office = relationship("AgriOffice", foreign_keys=[assigned_office_id])
    assigned_field_area = relationship("FieldArea", foreign_keys=[assigned_field_area_id])

class Login(db.Model):
    __tablename__ = 'login'
    user_id = Column(Integer, ForeignKey('user.user_id'),primary_key=True)
    username = Column(String(100))
    encoded_pw = Column(String(100))
    user = relationship("User", backref="logins")

class Researcher(db.Model):
    __tablename__ = 'researcher'
    user_id = Column(Integer, ForeignKey('user.user_id'),primary_key=True)
    institute = Column(String(100))
    user = relationship("User", backref="researchers")

class Advertisement(db.Model):
    __tablename__ = 'advertisement'
    ad_id = Column(Integer, primary_key=True)
    published_by = Column(String(100))
    type = Column(String(100))
    title = Column(String(100))
    category = Column(String(100))
    description = Column(String(100))
    date = Column(Date)
    time = Column(String(100))
    user_id = Column(Integer, ForeignKey('user.user_id'))
    unit_price = Column(Integer)
    crop_id = Column(Integer)
    amount = Column(Integer)
    telephone_no = Column(String(100))
    verified_officer_id = Column(Integer)
    image_link = Column(String(100))
    user = relationship("User", backref="advertisements")

class Farm(db.Model):
    __tablename__ = 'farm'
    farm_id = Column(Integer, primary_key=True)
    farm_name = Column(String(100))
    farmer_id = Column(Integer, ForeignKey('farmer.user_id'))
    address = Column(String(100))
    type = Column(String(100))
    area_of_field = Column(String(100))
    owner_nic = Column(String(100))
    owner_name = Column(String(100))
    recorded_by = Column(Integer)
    office_id = Column(Integer, ForeignKey('agri_office.agri_office_id'))
    field_area_id = Column(Integer, ForeignKey('field_area.field_area_id'))
    farmer = relationship("Farmer", backref="farms")

class Crop(db.Model):
    __tablename__ = 'crop'
    crop_id = Column(Integer, primary_key=True)
    crop_name = Column(String(100))
    breed = Column(String(100))
    description = Column(String(100))
    updated_by = Column(Integer)
    added_by = Column(Integer)

class CultivationInfo(db.Model):
    __tablename__ = 'cultivation_info'
    cultivation_info_id = Column(Integer, primary_key=True)
    display_name = Column(String(100))
    farm_id = Column(Integer, ForeignKey('farm.farm_id'))
    crop_id = Column(Integer, ForeignKey('crop.crop_id'))
    longitude = Column(String(100))
    latitude = Column(String(100))
    area_of_cultivation = Column(Integer)
    started_date = Column(Date)
    estimated_harvesting_date = Column(Date)
    estimated_harvest = Column(Integer)
    agri_year = Column(Integer)
    season = Column(String(50))
    quarter = Column(Integer)
    added_by = Column(Integer)
    updated_by = Column(Integer)
    harvested_date = Column(Date)
    harvested_amount = Column(Integer)
    added_date = Column(Date)

class DisasterInfo(db.Model):
    __tablename__ = 'disaster_info'
    disaster_info_id = Column(Integer, primary_key=True)
    cultivation_info_id = Column(Integer, ForeignKey('cultivation_info.cultivation_info_id'))
    date = Column(Date)
    time = Column(String(100))
    damaged_area = Column(Integer)
    estimated_damaged_harvest = Column(Integer)
    estimated_damaged_harvest_value = Column(Integer)
    type = Column(String(100))

class Aid(db.Model):
    __tablename__ = 'aid'
    aid_id = Column(Integer, primary_key=True)
    aid_name = Column(String(100))
    aid_batch = Column(String(100))
    year = Column(Integer)
    in_charged_office_id = Column(Integer, ForeignKey('agri_office.agri_office_id'))
    description = Column(String(100))
    in_charged_office = relationship("AgriOffice", foreign_keys=[in_charged_office_id])

class Fertilizer(db.Model):
    __tablename__ = 'fertilizer'
    fertilizer_id = Column(Integer, primary_key=True)
    aid_id = Column(Integer, ForeignKey('aid.aid_id'))
    manufactured_date = Column(Date)
    brand = Column(String(100))
    batch_no = Column(String(100))
    expiry_date = Column(Date)
    name = Column(String(100))
    type = Column(String(100))
    description = Column(String(100))

class Pesticides(db.Model):
    __tablename__ = 'pesticides'
    pesticides_id = Column(Integer, primary_key=True)
    aid_id = Column(Integer, ForeignKey('aid.aid_id'))
    manufactured_date = Column(Date)
    brand = Column(String(100))
    batch_no = Column(String(100))
    expiry_date = Column(Date)
    name = Column(String(100))
    type = Column(String(100))
    description = Column(String(100))

class MonetaryAid(db.Model):
    __tablename__ = 'monetary_aid'
    monetaryAid_id = Column(Integer, primary_key=True)
    aid_id = Column(Integer, ForeignKey('aid.aid_id'))
    description = Column(String(100))
    reason = Column(String(100))

class Fuel(db.Model):
    __tablename__ = 'fuel'
    fuelAid_id = Column(Integer, primary_key=True)
    aid_id = Column(Integer, ForeignKey('aid.aid_id'))
    reason = Column(String(100))
    description = Column(String(100))
    fuel_type = Column(String(100))

class MiscellaneousAids(db.Model):
    __tablename__ = 'miscellaneous_aids'
    miscellaneousAids_id = Column(Integer, primary_key=True)
    aid_id = Column(Integer,ForeignKey('aid.aid_id'))
    type = Column(String(100))
    reason = Column(String(100))
    description = Column(String(100))

class AidDistribution(db.Model):
    __tablename__ = 'aid_distribution'
    distribution_id = Column(Integer, primary_key=True)
    aid_id = Column(Integer, ForeignKey('aid.aid_id'))
    agri_office_id = Column(Integer, ForeignKey('agri_office.agri_office_id'))
    date = Column(Date)
    time = Column(String(100))
    in_charged_officer_id = Column(Integer)
    cultivation_info_id = Column(Integer, ForeignKey('cultivation_info.cultivation_info_id'))
    farmer_id = Column(Integer, ForeignKey('farmer.user_id'))
    amount_received = Column(Integer)
    amount_approved = Column(Integer)
    description = Column(String(100))

class EmailRecord(db.Model):
    __tablename__ = 'email_record'
    id = Column(Integer, primary_key=True)
    email = Column(String(100))
    subject = Column(String(100))
    message_text = Column(String(500))
    sent_at = Column(DateTime)
    sent_by = Column(String(100))
    sent_to = Column(String(100))
    status_sent = Column(Boolean)
    response = Column(String(500))