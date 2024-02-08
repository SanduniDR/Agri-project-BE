from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True) # SQL Alchemy will auto-increment
    first_name = Column(String)
    middle_name = Column(String, nullable=True)
    last_name = Column(String)
    nic = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    dob = Column(Date)
    role = Column(Integer, nullable=False)

class Role(db.Model):
    __tablename__ = 'role'
    role_id = Column(Integer, primary_key=True)
    role_name = Column(String)
    role_description = Column(String)


class Contact(db.Model):
    __tablename__ = 'contact'
    contact_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    number = Column(String)
    area_code = Column(String)
    user = relationship("User", backref="contacts")

class Address(db.Model):
    __tablename__ = 'address'
    address_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    city = Column(String)
    town = Column(String)
    street = Column(String)
    home_no = Column(String)
    home_name = Column(String)
    user = relationship("User", backref="addresses")

class SuperAdmin(db.Model):
    __tablename__ = 'super_admin'
    user_id = Column(Integer, ForeignKey('user.user_id'), primary_key=True)
    employee_id = Column(Integer)
    role_type = Column(String)
    user = relationship("User", backref="super_admins")

class RegionalAdmin(db.Model):
    __tablename__ = 'regional_admin'
    user_id = Column(Integer, ForeignKey('user.user_id'), primary_key=True)
    employee_id = Column(Integer)
    managed_by_employee_id = Column(Integer)
    district = Column(String)
    province = Column(String)
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
    name = Column(String)
    city = Column(String)
    province = Column(String)
    district = Column(String)

class FieldArea(db.Model):
    __tablename__ = 'field_area'
    field_area_id = Column(Integer, primary_key=True)
    agri_office_id = Column(Integer, ForeignKey('agri_office.agri_office_id'))
    name = Column(String)
    agri_office = relationship("AgriOffice", backref="field_areas")

class Reports(db.Model):
    __tablename__ = 'reports'
    report_id = Column(Integer, primary_key=True)
    category = Column(String)
    date = Column(Date)
    time = Column(String)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    link = Column(String)
    user = relationship("User", backref="reports")

class Farmer(db.Model):
    __tablename__ = 'farmer'
    user_id = Column(Integer, ForeignKey('user.user_id'),primary_key=True)
    assigned_office_id = Column(Integer, ForeignKey('agri_office.agri_office_id'))
    assigned_field_area_id = Column(Integer, ForeignKey('field_area.field_area_id'))
    updated_by = Column(Integer)
    added_by = Column(Integer)
    registered_date = Column(Date)
    tax_file_no = Column(String)
    user = relationship("User", backref="farmers")
    assigned_office = relationship("AgriOffice", foreign_keys=[assigned_office_id])
    assigned_field_area = relationship("FieldArea", foreign_keys=[assigned_field_area_id])

class Login(db.Model):
    __tablename__ = 'login'
    user_id = Column(Integer, ForeignKey('user.user_id'),primary_key=True)
    username = Column(String)
    encoded_pw = Column(String)
    user = relationship("User", backref="logins")

class Vendor(db.Model):
    __tablename__ = 'vendor'
    user_id = Column(Integer, ForeignKey('user.user_id'),primary_key=True)
    business_reg_no = Column(String)
    tax_file_no = Column(String)
    user = relationship("User", backref="vendors")

class Researcher(db.Model):
    __tablename__ = 'researcher'
    user_id = Column(Integer, ForeignKey('user.user_id'),primary_key=True)
    institute = Column(String)
    user = relationship("User", backref="researchers")

class Advertisement(db.Model):
    __tablename__ = 'advertisement'
    ad_id = Column(Integer, primary_key=True)
    published_by = Column(String)
    type = Column(String)
    title = Column(String)
    category = Column(String)
    description = Column(String)
    date = Column(Date)
    time = Column(String)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    unit_price = Column(Integer)
    crop_id = Column(Integer)
    amount = Column(Integer)
    telephone_no = Column(String)
    verified_officer_id = Column(Integer)
    image_link = Column(String)
    user = relationship("User", backref="advertisements")

class Farm(db.Model):
    __tablename__ = 'farm'
    farm_id = Column(Integer, primary_key=True)
    farm_name = Column(String)
    farmer_id = Column(Integer, ForeignKey('farmer.user_id'))
    address = Column(String)
    type = Column(String)
    area_of_field = Column(String)
    owner_nic = Column(String)
    owner_name = Column(String)
    recorded_by = Column(Integer)
    farmer = relationship("Farmer", backref="farms")

class Crop(db.Model):
    __tablename__ = 'crop'
    crop_id = Column(Integer, primary_key=True)
    crop_name = Column(String)
    breed = Column(String)
    description = Column(String)
    updated_by = Column(Integer)
    added_by = Column(Integer)

class CultivationInfo(db.Model):
    __tablename__ = 'cultivation_info'
    cultivation_info_id = Column(Integer, primary_key=True)
    display_name = Column(String)
    farm_id = Column(Integer, ForeignKey('farm.farm_id'))
    crop_id = Column(Integer, ForeignKey('crop.crop_id'))
    longitude = Column(String)
    latitude = Column(String)
    area_of_cultivation = Column(Integer)
    started_date = Column(Date)
    estimated_harvesting_date = Column(Date)
    estimated_harvest = Column(Integer)
    agri_year = Column(Integer)
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
    time = Column(String)
    damaged_area = Column(Integer)
    estimated_damaged_harvest = Column(Integer)
    estimated_damaged_harvest_value = Column(Integer)
    type = Column(String)

class Aid(db.Model):
    __tablename__ = 'aid'
    aid_id = Column(Integer, primary_key=True)
    aid_name = Column(String)
    aid_batch = Column(String)
    year = Column(Integer)
    in_charged_office_id = Column(Integer, ForeignKey('agri_office.agri_office_id'))
    description = Column(String)
    in_charged_office = relationship("AgriOffice", foreign_keys=[in_charged_office_id])

class Fertilizer(db.Model):
    __tablename__ = 'fertilizer'
    fertilizer_id = Column(Integer, primary_key=True)
    aid_id = Column(Integer, ForeignKey('aid.aid_id'))
    manufactured_date = Column(Date)
    brand = Column(String)
    batch_no = Column(String)
    expiry_date = Column(Date)
    name = Column(String)
    type = Column(String)
    description = Column(String)

class Pesticides(db.Model):
    __tablename__ = 'pesticides'
    pesticides_id = Column(Integer, primary_key=True)
    aid_id = Column(Integer, ForeignKey('aid.aid_id'))
    manufactured_date = Column(Date)
    brand = Column(String)
    batch_no = Column(String)
    expiry_date = Column(Date)
    name = Column(String)
    type = Column(String)
    description = Column(String)

class MonetaryAid(db.Model):
    __tablename__ = 'monetary_aid'
    monetaryAid_id = Column(Integer, primary_key=True)
    aid_id = Column(Integer, ForeignKey('aid.aid_id'))
    description = Column(String)
    reason = Column(String)

class Fuel(db.Model):
    __tablename__ = 'fuel'
    fuelAid_id = Column(Integer, primary_key=True)
    aid_id = Column(Integer, ForeignKey('aid.aid_id'))
    reason = Column(String)
    description = Column(String)
    fuel_type = Column(String)

class MiscellaneousAids(db.Model):
    __tablename__ = 'miscellaneous_aids'
    miscellaneousAids_id = Column(Integer, primary_key=True)
    aid_id = Column(Integer,ForeignKey('aid.aid_id'))
    type = Column(String)
    reason = Column(String)
    description = Column(String)

class AidDistribution(db.Model):
    __tablename__ = 'aid_distribution'
    distribution_id = Column(Integer, primary_key=True)
    aid_id = Column(Integer, ForeignKey('aid.aid_id'))
    agri_office_id = Column(Integer, ForeignKey('agri_office.agri_office_id'))
    date = Column(Date)
    time = Column(String)
    in_charged_officer_id = Column(Integer)
    cultivation_info_id = Column(Integer, ForeignKey('cultivation_info.cultivation_info_id'))
    farmer_id = Column(Integer, ForeignKey('farmer.user_id'))
    amount_received = Column(Integer)
    amount_approved = Column(Integer)
    description = Column(String)