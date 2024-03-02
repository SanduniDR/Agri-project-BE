from datetime import timedelta
import datetime
import logging
from app.schemas import user_schema
from app.service.users.util_service import parse_date
from flask_jwt_extended import create_access_token,decode_token
from app.models import AgricultureOfficer, AgriOffice, FieldArea
from app.models import Address, AidDistribution, Contact, CultivationInfo, DisasterInfo, Farm, User, Farmer,Vendor, db
from flask_mail import Message, Mail
from app.schemas import users_schema,farmer_schema,vendor_schema, agriculture_officer_schema, agri_office_schema, field_area_schema
from app.schemas import disaster_infos_schema,aid_distributions_schema,addresses_schema,contacts_schema,users_schema,farmer_schema,vendor_schema,farm_schema,cultivation_info_schema,disaster_info_schema,aid_distribution_schema,contact_schema,address_schema
from sqlalchemy import or_, cast, String, and_
from sqlalchemy.orm.exc import NoResultFound


mail=Mail()

########################################################################################
                            #     User 
########################################################################################

def register_user(user):
    try:
        db.session.add(user)
        db.session.commit()
        return True, user, 'Registration success!'
    except Exception as e:
        db.session.rollback()  # Rollback the transaction in case of error
        error_message = f"An error occurred while registering the user: {str(e)}"
        return False,{}, error_message

def isExistingUser(user):
    isExist = User.query.filter_by(email=user.email).first()
    return isExist
    
def  user_login(user):
    user=User.query.filter_by(email=user.email, password=user.password).first()
    return user  

def get_access_token(user):
        access_token = create_access_token(identity=user.user_id, expires_delta=timedelta(days=1))
        return access_token

def deleteUser(user_id):
    data = None
    try:
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
             return False,'User Not Found',data
        
        db.session.delete(user)
        db.session.commit()
        data = user_schema.dump(user)
        logging.debug('user deleted: %s', data)
        return True,"User successfully deleted.",data

    except Exception as e:
        db.session.rollback()
        error_message = f"An error occurred while registering the user: {str(e)}"
        return False, error_message, data
    
def retrieve_user_password(email):
    user = User.query.filter_by(email=email).first()
    if user:
        msg = Message("User password is " + user.password,
                      sender="mailtrap@dhanushkas.tech",
                      recipients=[email])
        mail.send(msg)
        return True
    else:
        return False 
    
def getUserBy_Id(userid,current_user_id):
     # Get the current user information from the token or database
    current_user = User.query.filter_by(user_id=current_user_id).first()
    logging.debug('current_user: %s', current_user)
    if current_user:
        user = User.query.filter_by(user_id=userid).first()
        if current_user.role in [1, 3, 4]:
            return user

def getUserBy_Email(email,current_user_id):
     # Get the current user information from the token or database
    current_user = User.query.filter_by(user_id=current_user_id).first()
    logging.debug('current_user: %s', current_user)
    if current_user:
        user = User.query.filter_by(email=email).first()
        if current_user.role in [1, 3, 4]:
            return user
        
def getUserBy_Role(role,current_user_id):
    current_user=User.query.filter_by(user_id=current_user_id).first()
    logging.debug('current_user: %s', current_user)
    if current_user.role in [1, 3, 4]:
        users = User.query.filter_by(role=role).all()
        return users
    
        
def Update_User(data, user):
    if 'password' in data:
        user.password = data['password']
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'nic' in data:
        user.nic = data['nic']
    if 'dob' in data:
        user.dob = parse_date(data['dob'])
    if 'role' in data:
        user.role = data['role']
    if 'middle_name' in data:
        user.middle_name = data['middle_name']
    if 'email' in data:
        user.email= data['email']
    # Save the changes to the database
    db.session.commit()
    

def Search_User(filters):
    page = int(filters.pop('page', 1))
    per_page = int(filters.pop('per_page', 50))

    # Build the query based on the filters
    query = User.query
    for key, value in filters.items():
        if value:
            query = query.filter(getattr(User, key) == value)
    logging.debug('query: %s', query)

    # Apply pagination
    users = query.paginate(page=page, per_page=per_page)

    # Prepare the response
    result = {
        'page': page,
        'per_page': per_page,
        'total_pages': users.pages,
        'total_users': users.total,
        'users': users_schema.dump(users.items)
    }
    return result

def Validate_User(current_user_id,email):
    current_user_ByEmail = User.query.filter_by(email=email).first()
    if current_user_ByEmail and current_user_ByEmail.user_id == current_user_id:
        return True,current_user_ByEmail
    else:
        return False,None
    
def Get_User_Information(current_user_id):
    current_user_ByEmail = User.query.filter_by(user_id=current_user_id).first()
    return current_user_ByEmail

def  Check_User_Token_Expiration(token):
    decoded_token = decode_token(token)
    expiration_timestamp = decoded_token['exp']
    current_timestamp = datetime.utcnow().timestamp()
    is_expired = current_timestamp > expiration_timestamp
    return is_expired

def get_all_users():
    data=None
    try:
        all_users = User.query.all()
        data=all_users
        message = f"Success fetching All Users"
        return True, message, data
        
    except Exception as e:
        error_message = f"An error occurred while fetching Users:  {str(e)}"
        logging.error(error_message)
        return False, error_message, {}

########################################################################################
                            #    User:Farmer 
########################################################################################


def add_farmer_to_system(data, user_id):
    
    try:
        # Check if the current user is an admin (modify 'admin' to your actual admin role)
        current_user = User.query.filter_by(user_id=user_id).first()
        if current_user.role not in [1, 3, 4]:
            message="Unauthorized to access this resource"
            return False, message, {}
        else:      
            # Create a new instance of the Farmer model with the data
            new_farmer = Farmer(**data)

            new_farmer.added_by = current_user.user_id
            new_farmer.updated_by = current_user.user_id
            new_farmer.registered_date = parse_date(datetime.datetime.now().strftime('%Y-%m-%d'))

            
            # Add the new farmer to the database session
            db.session.add(new_farmer)
            user = User.query.get(new_farmer.user_id)
            data = {'role': 5}
            Update_User(data, user)
            
            # Commit the changes to the database
            db.session.commit()
            message="Successfully added farmer"

            # Return the JSON representation of the new farmer
            return True, message, new_farmer
        
    except Exception as e:
        db.session.rollback()
        logging.error(e)
        message=f"Farmer registration failure, please check this user is already registered, Ping Admin service:{str(e)}"
        return False, message, {}
    

def get_all_farmers():
    
    data=None
    try:
        all_farmers = Farmer.query.all()
        data=all_farmers
        message = f"Success fetching farmers"
        return True, message, data
        
    except Exception as e:
        error_message = f"An error occurred while fetching farmers:  {str(e)}"
        logging.error(error_message)
        return False, error_message, {}
    
    
def get_farmer_by_Id(user_id):
    data=None
    try:
        farmer = Farmer.query.get(user_id)
        
        if not farmer:
            message = "Farmer not found"
            return False, message, data
        
        user =User.query.get(farmer.user_id)
        # data=farmer
        message = f"Success fetching farmers"
        return True, message, user, farmer
            
    except Exception as e:
        error_message = f"An error occurred while fetching farmer:  {str(e)}"
        logging.error(error_message)
        return False, error_message, {},{}
            
def update_farmer_details(id,current_user,data):
    try:
        farmer = Farmer.query.get(id)
        farmer.updated_by = current_user.user_id
        
        if 'registered_date' in data:
            data['registered_date'] = parse_date(data['registered_date'])
            
        for key, value in data.items():
            setattr(farmer, key, value)
            
        db.session.commit() 
        return farmer
    
    except Exception as e:
        error_message = f"An error occurred while updating farmer details:  {str(e)}"
        logging.error(error_message)
        
        
def delete_farmer_from(id): 
    try:
        
        farmer = Farmer.query.get(id)
        user = User.query.get(farmer.user_id)  # Fetch the associated user
        
               
        farmer_data = farmer_schema.dump(farmer)
        user_data = user_schema.dump(user)  # Dump the user data
        db.session.delete(farmer)
        # db.session.delete(user)  # Delete the user
        db.session.commit()
        return True, farmer_data, user_data
    except Exception as e:
            db.session.rollback()
            error_message = f"An error occurred while deleting farmer details:  {str(e)}"
            logging.error(error_message)
            return False, {}, {}
    
        
def search_existing_farmers(office_id, tax_file_no, field_area_id, user_id, page, per_page):

    # Start with a query that selects all farmers
    query = Farmer.query

    # If a user_id is provided, add a filter for it
    if user_id:
        query = query.filter(cast(Farmer.user_id, String).ilike(f'%{user_id}%'))

    # If a tax_file_no is provided, add a filter for it
    if tax_file_no:
        query = query.filter(Farmer.tax_file_no.ilike(f'%{tax_file_no}%'))

    # If an office_id is provided, add a filter for it
    if office_id:
        query = query.filter(cast(Farmer.assigned_office_id, String).ilike(f'%{office_id}%'))

    # If a field_area_id is provided, add a filter for it
    if field_area_id:
        query = query.filter(cast(Farmer.assigned_field_area_id, String).ilike(f'%{field_area_id}%'))

    # Execute the query and get all matching farmers
    farmers = query.paginate(page=page, per_page=per_page)

    result = {
        'page': page,
        'per_page': per_page,
        'total_pages': farmers.pages,
        'total_farmers': farmers.total,
        'farmers': [{
            'farmer': farmer_schema.dump(farmer),
            'user': user_schema.dump(farmer.user)
        } for farmer in farmers.items]
    }   
    return result


def get_farmer_details_by_Id(user_id):
    try:
        farmer = Farmer.query.get(user_id)
        user = User.query.filter_by(user_id=farmer.user_id).first()
        farms = Farm.query.filter_by(farmer_id=farmer.user_id).all()
        aid_distributions = AidDistribution.query.filter_by(farmer_id=farmer.user_id).all()
        contacts = Contact.query.filter_by(user_id=farmer.user_id).all()
        addresses = Address.query.filter_by(user_id=farmer.user_id).all()

        user_data = user_schema.dump(user)
        farmer_data = farmer_schema.dump(farmer)
        aid_distribution_data = aid_distributions_schema.dump(aid_distributions)
        contact_data = contacts_schema.dump(contacts)
        address_data = addresses_schema.dump(addresses)

        # Loop through each farm and fetch its cultivations
        farm_data = []
        for farm in farms:
            cultivations = CultivationInfo.query.filter_by(farm_id=farm.farm_id).all()
            farm_dict = farm_schema.dump(farm)
            farm_dict["cultivations"] = []

            # Loop through each cultivation and fetch its disasters
            for cultivation in cultivations:
                disasters = DisasterInfo.query.filter_by(cultivation_info_id=cultivation.cultivation_info_id).all()
                disaster_info_data = disaster_infos_schema.dump(disasters)
                cultivation_dict = cultivation_info_schema.dump(cultivation)
                cultivation_dict["disasters"] = disaster_info_data
                farm_dict["cultivations"].append(cultivation_dict)

            farm_data.append(farm_dict)

        data = {
            "user": user_data,
            "farmer": farmer_data,
            "farms": farm_data,
            "aid_distributions": aid_distribution_data,
            "contacts": contact_data,
            "addresses": address_data,
        }

        message = "Success fetching detailed farmer info"
        return True, message, data

    except Exception as e:
        error_message = f"An error occurred while fetching detailed farmer info:  {str(e)}"
        return False, error_message, {}









########################################################################################
                            #    User:Vendor 
########################################################################################
           
 ###Add Vendor
def add_vendor_to_system(user_id, current_user_id, data):
    
    try:
       db.session.query(User).filter_by(user_id=user_id).one()
    except NoResultFound:
        message = "Vendor not registered as a user, Register in the system first."
        logging.error(message)
        return False, message, {}
    
    try:
        # Check if the current user is an admin (modify 'admin' to your actual admin role)
        current_user = User.query.filter_by(user_id=current_user_id).first()
        if current_user.role not in [1, 3, 4]:
            message="Unauthorized to access this resource"
            return False, message, {}
        else:      
            # Create a new instance of the Farmer model with the data
            new_vendor = Vendor(**data)
            new_vendor.user_id=user_id

            # Add the new farmer to the database session
            db.session.add(new_vendor)
            
            # Commit the changes to the database
            db.session.commit()
            message="Successfully added vendor details"

            # Return the JSON representation of the new farmer
            return True, message, new_vendor
        
    except Exception as e:
        db.session.rollback()
        logging.error(e)
        message=f" Adding vendor failure, Already has records from this user_id in vendor table:{str(e)}"
        return False, message, {}
    
 ###Delete Vendor
def delete_vendor_by_UserId(user_id): 
    
    try:
        vendor = Vendor.query.get(user_id)
        user = User.query.get(vendor.user_id)  # Fetch the associated user
        
        # farmers = Farmer.query.filter_by(user_id=user.user_id).all()
        # for farmer in farmers:
        #     db.session.delete(farmer)
        
        vendor_data = vendor_schema.dump(vendor)
        user_data = user_schema.dump(user)  # Dump the user data
        db.session.delete(vendor)
        db.session.delete(user)  # Delete the user
        db.session.commit()
        return True, vendor_data, user_data
    except Exception as e:
            db.session.rollback()
            error_message = f"An error occurred while deleting vendor :  {str(e)}"
            logging.error(error_message)
            return False, {}, {}
 ###Get Vendor 
 ###Update Vendor
 ###Search Vendor  
def search_existing_farmers_By_Append(office_id, tax_file_no, field_area_id, user_id, page, per_page):

    # Start with a query that selects all farmers
    query = Farmer.query

    # Create a list to hold all the filter conditions
    conditions = []

    # If a user_id is provided, add a filter for it
    if user_id:
        conditions.append(Farmer.user_id == user_id)

    # If a tax_file_no is provided, add a filter for it
    if tax_file_no:
        conditions.append(Farmer.tax_file_no == tax_file_no)

    # If an office_id is provided, add a filter for it
    if office_id:
        conditions.append(Farmer.assigned_office_id == office_id)

    # If a field_area_id is provided, add a filter for it
    if field_area_id:
        conditions.append(Farmer.assigned_field_area_id == field_area_id)

    # Apply all the conditions to the query
    query = query.filter(and_(*conditions))

    # Execute the query and get all matching farmers
    farmers = query.paginate(page=page, per_page=per_page)

    result = {
        'page': page,
        'per_page': per_page,
        'total_pages': farmers.pages,
        'total_farmers': farmers.total,
        'farmers': [{
            'farmer': farmer_schema.dump(farmer),
            'user': user_schema.dump(farmer.user)
        } for farmer in farmers.items]
    }   
    return result
                        

                         
########################Add Agri Officers
def add_new_agri_officer(data, user_id):
    # Check if user exists
    user = User.query.get(user_id)
    if not user:
        return False, {}, "First register as a user"

    # Create new Agriculture Officer
    data['service_start_date'] = parse_date(data['service_start_date'])
    new_agri_officer = AgricultureOfficer(**data)
    result  = agriculture_officer_schema.dump(new_agri_officer)
    # Add new Agriculture Officer to the session
    db.session.add(new_agri_officer)

    # Commit the record the database
    db.session.commit()

    # Close the session
    db.session.close()

    return True, result , "Agriculture Officer added successfully"

###########################################
def update_agri_officer(user_id, data):
    # Check if officer exists
    officer = AgricultureOfficer.query.get(user_id)
    if not officer:
        return False, {}, "Officer not found"

    # Update officer details
    for key, value in data.items():
        if key == 'service_start_date':
            value = parse_date(value)
        setattr(officer, key, value)

    # Commit the changes to the database
    db.session.commit()

  

    result = agriculture_officer_schema.dump(officer)
      # Close the session
    db.session.close()
    return True, result, "Agriculture Officer updated successfully"

def search_officers(office_id, employee_id, field_area_id, user_id, district, page, per_page):

    # Build the filter conditions
    filter_conditions = []

    if user_id:
        filter_conditions.append(AgricultureOfficer.user_id.ilike(f'%{user_id}%'))

    if employee_id:
        filter_conditions.append(AgricultureOfficer.employee_id.ilike(f'%{employee_id}%'))

    if office_id:
        filter_conditions.append(cast(AgricultureOfficer.agri_office_id, String).ilike(f'%{office_id}%'))

    if field_area_id:
        filter_conditions.append(cast(AgricultureOfficer.field_area_id, String).ilike(f'%{field_area_id}%'))

    if district:
        filter_conditions.append(AgriOffice.district.ilike(f'%{district}%'))

    query = db.session.query(AgricultureOfficer, AgriOffice, FieldArea).join(AgriOffice, AgricultureOfficer.agri_office_id == AgriOffice.agri_office_id).join(FieldArea, AgricultureOfficer.field_area_id == FieldArea.field_area_id).filter(*filter_conditions)
    officers = query.paginate(page=page, per_page=per_page)

    result = {
        'page': page,
        'per_page': per_page,
        'total_pages': officers.pages,
        'total_officers': officers.total,
        'officers': [{
            'officer': agriculture_officer_schema.dump(officer[0]),
            'user': user_schema.dump(officer[0].user),
            'office': agri_office_schema.dump(officer[1]),
            'field_area': field_area_schema.dump(officer[2])
        } for officer in officers.items]
    }   
    return result

def search_existing_farmers_By_Append(office_id, tax_file_no, field_area_id, user_id, page, per_page):

    # Start with a query that selects all farmers
    query = Farmer.query

    # Create a list to hold all the filter conditions
    conditions = []

    # If a user_id is provided, add a filter for it
    if user_id:
        conditions.append(Farmer.user_id == user_id)

    # If a tax_file_no is provided, add a filter for it
    if tax_file_no:
        conditions.append(Farmer.tax_file_no == tax_file_no)

    # If an office_id is provided, add a filter for it
    if office_id:
        conditions.append(Farmer.assigned_office_id == office_id)

    # If a field_area_id is provided, add a filter for it
    if field_area_id:
        conditions.append(Farmer.assigned_field_area_id == field_area_id)

    # Apply all the conditions to the query
    query = query.filter(and_(*conditions))

    # Execute the query and get all matching farmers
    farmers = query.paginate(page=page, per_page=per_page)

    result = {
        'page': page,
        'per_page': per_page,
        'total_pages': farmers.pages,
        'total_farmers': farmers.total,
        'farmers': [{
            'farmer': farmer_schema.dump(farmer),
            'user': user_schema.dump(farmer.user)
        } for farmer in farmers.items]
    }   
    return result
