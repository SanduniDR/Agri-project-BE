# This file contains the schemas for the database models
from flask_marshmallow import Marshmallow
# from app import ma
ma = Marshmallow()

# Schemas for the database models
class UserSchema(ma.Schema):
    class Meta:
        fields = ('user_id', 'first_name', 'middle_name', 'last_name', 'email', 'nic', 'dob', 'role')


class FarmSchema(ma.Schema):
    class Meta:
        fields = ('farm_id', 'farm_name', 'address', 'type', 'farmer_id', 'area_of_field', 'owner_nic', 'owner_name' )

class ContactSchema(ma.Schema):
    class Meta: 
        fields = ('contact_id', 'user_id', 'number', 'area_code')

class AddressSchema(ma.Schema):
    class Meta:
        fields = ('address_id', 'user_id', 'city', 'town', 'street', 'home_no', 'home_name')

class SuperAdminSchema(ma.Schema):
    class Meta:
        fields = ('user_id', 'employee_id', 'role_type')

class RegionalAdminSchema(ma.Schema):
    class Meta:
        fields = ('user_id', 'employee_id', 'managed_by_employee_id', 'district', 'province', 'agri_office_id', 'service_start_date')

class AgricultureOfficerSchema(ma.Schema):
    class Meta:
        fields = ('user_id', 'employee_id', 'managed_by_employee_id', 'agri_office_id', 'service_start_date', 'field_area_id')

class AgriOfficeSchema(ma.Schema):
    class Meta:
        fields = ('agri_office_id', 'name', 'city', 'province', 'district')

class FieldAreaSchema(ma.Schema):
    class Meta:
        fields = ('field_area_id', 'agri_office_id', 'name')

class ReportsSchema(ma.Schema):
    class Meta:
        fields = ('report_id', 'category', 'date', 'time', 'user_id', 'link')
        
class DataRequestSchema(ma.Schema):
    class Meta:
        fields = ('request_id', 'user_id', 'message', 'date', 'institute')

class FarmerSchema(ma.Schema):
    class Meta:
        fields = ('user_id', 'assigned_office_id', 'assigned_field_area_id', 'updated_by', 'added_by', 'registered_date', 'tax_file_no')

class LoginSchema(ma.Schema):
    class Meta:
        fields = ('user_id', 'username', 'encoded_pw')

class ResearcherSchema(ma.Schema):
    class Meta:
        fields = ('user_id', 'institute')

class AdvertisementSchema(ma.Schema):
    class Meta:
        fields = ('ad_id', 'published_by', 'type', 'title', 'category', 'description', 'date', 'time', 'user_id', 'unit_price', 'crop_id', 'amount', 'telephone_no', 'verified_officer_id', 'image_link')

# class FarmSchema(ma.Schema):
#     class Meta:
#         fields = ('farm_id', 'farmer_id', 'address', 'type', 'area_of_field', 'owner_nic', 'owner_name', 'recorded_by')

class CropSchema(ma.Schema):
    class Meta:
        fields = ('crop_id', 'crop_name', 'breed', 'description', 'updated_by', 'added_by')

class CultivationInfoSchema(ma.Schema):
    class Meta:
        fields = ('cultivation_info_id', 'display_name', 'farm_id', 'crop_id', 'longitude', 'latitude', 'area_of_cultivation', 'started_date', 'estimated_harvesting_date', 'estimated_harvest', 'agri_year', 'quarter', 'added_by', 'updated_by', 'harvested_date', 'harvested_amount', 'added_date')

class DisasterInfoSchema(ma.Schema):
    class Meta:
        fields = ('disaster_info_id', 'cultivation_info_id', 'date', 'time', 'damaged_area', 'estimated_damaged_harvest', 'estimated_damaged_harvest_value', 'type')

class AidSchema(ma.Schema):
    class Meta:
        fields = ('aid_id', 'aid_name', 'aid_batch', 'year', 'in_charged_office_id', 'description')

class FertilizerSchema(ma.Schema):
    class Meta:
        fields = ('fertilizer_id', 'aid_id', 'manufactured_date', 'brand', 'batch_no', 'expiry_date', 'name', 'type', 'description')

class PesticidesSchema(ma.Schema):
    class Meta:
        fields = ('pesticides_id', 'aid_id', 'manufactured_date', 'brand', 'batch_no', 'expiry_date', 'name', 'type', 'description')

class MonetaryAidSchema(ma.Schema):
    class Meta:
        fields = ('monetaryAid_id', 'aid_id', 'description', 'reason')

class FuelSchema(ma.Schema):
    class Meta:
        fields = ('fuelAid_id', 'aid_id', 'reason', 'description', 'fuel_type')

class MiscellaneousAidsSchema(ma.Schema):
    class Meta:
        fields = ('miscellaneousAids_id', 'aid_id', 'type', 'reason', 'description')

class AidDistributionSchema(ma.Schema):
    class Meta:
        fields = ('distribution_id', 'aid_id', 'agri_office_id', 'date', 'time', 'in_charged_officer_id', 'cultivation_info_id', 'farmer_id', 'amount_received', 'amount_approved', 'description')

class EmailRecordSchema(ma.Schema):
    class Meta:
        fields = ('id', 'email', 'subject', 'message_text', 'sent_at', 'sent_by', 'sent_to', 'status_sent', 'response')

user_schema = UserSchema()
contact_schema = ContactSchema()
address_schema = AddressSchema()
super_admin_schema = SuperAdminSchema()
regional_admin_schema = RegionalAdminSchema()
agriculture_officer_schema = AgricultureOfficerSchema()
agri_office_schema = AgriOfficeSchema()
field_area_schema = FieldAreaSchema()
report_schema = ReportsSchema()
farmer_schema = FarmerSchema()
login_schema = LoginSchema()
researcher_schema = ResearcherSchema()
advertisement_schema = AdvertisementSchema()
farm_schema = FarmSchema()
crop_schema = CropSchema()
cultivation_info_schema = CultivationInfoSchema()
disaster_info_schema = DisasterInfoSchema()
aid_schema = AidSchema()
fertilizer_schema = FertilizerSchema()
pesticide_schema = PesticidesSchema()
monetary_aid_schema = MonetaryAidSchema()
fuel_schema = FuelSchema()
miscellaneous_aids_schema = MiscellaneousAidsSchema()
aid_distribution_schema = AidDistributionSchema()
email_record_schema = EmailRecordSchema()
data_request_schema=DataRequestSchema()

# For schemas representing multiple instances
users_schema = UserSchema(many=True)
contacts_schema = ContactSchema(many=True)
addresses_schema = AddressSchema(many=True)
super_admins_schema = SuperAdminSchema(many=True)
regional_admins_schema = RegionalAdminSchema(many=True)
agriculture_officers_schema = AgricultureOfficerSchema(many=True)
agri_offices_schema = AgriOfficeSchema(many=True)
field_areas_schema = FieldAreaSchema(many=True)
reports_schemas = ReportsSchema(many=True)
farmers_schema = FarmerSchema(many=True)
logins_schema = LoginSchema(many=True)
researchers_schema = ResearcherSchema(many=True)
advertisements_schema = AdvertisementSchema(many=True)
farms_schema = FarmSchema(many=True)
crops_schema = CropSchema(many=True)
cultivation_infos_schema = CultivationInfoSchema(many=True)
disaster_infos_schema = DisasterInfoSchema(many=True)
aids_schema = AidSchema(many=True)
fertilizers_schema = FertilizerSchema(many=True)
pesticides_schema = PesticidesSchema(many=True)
monetary_aids_schema = MonetaryAidSchema(many=True)
fuels_schema = FuelSchema(many=True)
miscellaneous_aids_schemas = MiscellaneousAidsSchema(many=True)
aid_distributions_schema = AidDistributionSchema(many=True)
email_records_schema = EmailRecordSchema(many=True)
data_requests_schema=DataRequestSchema(many=True)

