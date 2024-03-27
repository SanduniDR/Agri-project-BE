from datetime import timedelta
import datetime
import logging
from app.schemas import user_schema
from app.service.users.user_service import Update_Researcher, Update_User
from app.service.users.util_service import parse_date
from flask_jwt_extended import create_access_token,decode_token
from app.models import Address, Contact, User, Farmer,DataRequest,Reports, db
from flask_mail import Message, Mail
from app.schemas import users_schema,farmer_schema,address_schema,addresses_schema,contact_schema,contacts_schema,data_request_schema
from sqlalchemy import or_, cast, String
from sqlalchemy.orm.exc import NoResultFound



##################################### Address #######################################


def add_address(user_id, data):
    
    try:
        user = db.session.query(User).filter_by(user_id=user_id).one()
    except NoResultFound:
        message = "User not found."
        logging.error(message)
        return False, message, {}
    
    try:
        address=Address(**data)
        address.user_id=user_id
        db.session.add(address)
        db.session.commit()
        return True,None,address
    
    except Exception as e:
        db.session.rollback()
        logging.error(e)
        message=f"Address inserting failure:{str(e)}"
        return False, message, {}
    
def get_all_addresses():
    
    data=None
    try:
        all_addresses = Address.query.all()
        data=all_addresses
        message = f"Success fetching all addresses"
        return True, message, data
        
    except Exception as e:
        error_message = f"An error occurred while fetching addresses:  {str(e)}"
        logging.error(error_message)
        return False, error_message, {}
    
    
def search_address_by_Id(user_id, page, per_page):
    
    # Start with a query that selects all addresses
    query = Address.query

    # If a user_id is provided, add a filter for it
    if user_id:
        query = query.filter(cast(Address.user_id, String).ilike(f'%{user_id}%'))

    # Execute the query and get all matching farmers
    addresses = query.paginate(page=page, per_page=per_page)

    result = {
        'page': page,
        'per_page': per_page,
        'total_pages': addresses.pages,
        'total_addresses': addresses.total,
        'addresses': [{
            'address': address_schema.dump(address),
            'user': user_schema.dump(address.user)
        } for address in addresses.items]
    }   
    return result
           
def delete_address_by_id(id): 
    
    try:
        address = Address.query.get(id)
        address_data=address_schema.dump(address)
        db.session.delete(address)
        db.session.commit()
        return True, address_data
    except Exception as e:
            db.session.rollback()
            error_message = f"An error occurred while deleting address details:  {str(e)}"
            logging.error(error_message)
            return False, {}  

def update_address_by_id(address_id,data):
    try:
        address = Address.query.get(address_id)
        
        if not address:
            return False, "Address not found",{}
                   
        for key, value in data.items():
            setattr(address, key, value)
            
        db.session.commit() 
        return True, "Address Updated",address
    
    except Exception as e:
        error_message = f"An error occurred while updating address :  {str(e)}"
        logging.error(error_message)
        db.session.rollback() 
        return False, error_message,{}

##################################### Contacts  #######################################

def add_contacts(user_id, data):
    
    try:
        user = db.session.query(User).filter_by(user_id=user_id).one() #fetch one result-->'.one()'
    except NoResultFound:
        message = "User not found."
        logging.error(message)
        return False, message, {}
    
    try:
        contact=Contact(**data)
        contact.user_id=user_id
        db.session.add(contact)
        db.session.commit()
        return True,"Successfully Added the Contact.",contact
    
    except Exception as e:
        db.session.rollback()
        logging.error(e)
        message=f"Contact inserting failure:{str(e)}"
        return False, message, {}
    
    
def delete_contact_by_id(contact_id):
    try:
        contact = Contact.query.get(contact_id)
        contact_data=contact_schema.dump(contact)
        db.session.delete(contact)
        db.session.commit()
        return True, contact_data
    except Exception as e:
            db.session.rollback()
            error_message = f"An error occurred while deleting contact details:  {str(e)}"
            logging.error(error_message)
            return False, {}  
        
def search_by_userId(user_id, page, per_page):
     
    # Start with a query that selects all addresses
    query = Contact.query

    # If a user_id is provided, add a filter for it
    if user_id:
        query = query.filter(cast(Contact.user_id, String).ilike(f'%{user_id}%'))

    # Execute the query and get all matching farmers
    contacts = query.paginate(page=page, per_page=per_page,error_out=False)

    result = {
        'page': page,
        'per_page': per_page,
        'total_pages': contacts.pages,
        'total_contacts': contacts.total,
        'contacts': [{
            'contact': contact_schema.dump(contact),
            'user': user_schema.dump(contact.user)
        } for contact in contacts.items]
    }   
    return result  

def delete_request_by_id(request_id):
    try:
        request = DataRequest.query.get(request_id)
        request_data=data_request_schema.dump(request)
        db.session.delete(request)
        db.session.commit()
        return True, request_data
    except Exception as e:
            db.session.rollback()
            error_message = f"An error occurred while deleting request details:  {str(e)}"
            logging.error(error_message)
            return False, {} 
    
def add_sentDataRecord_to_system (data,date):
    new_record = Reports(**data)
    new_record.date=parse_date(date.strftime('%Y-%m-%d'))
      
    # Add the new record to the database session
    db.session.add(new_record)
    
    db.session.commit()
    message="Successfully added record !"

    # Return the JSON representation of the new farmer
    return True, message, new_record

    
# def get_all_contacts():
    
#     data=None
#     try:
#         all_contacts = Contact.query.all()
#         data=all_contacts
#         message = f"Success fetching all contacts"
#         return True, message, data
        
#     except Exception as e:
#         error_message = f"An error occurred while fetching contacts:  {str(e)}"
#         logging.error(error_message)
#         return False, error_message, {}
    
    
# def search_address_by_Id(user_id, page, per_page):
    
#     # Start with a query that selects all addresses
#     query = Address.query

#     # If a user_id is provided, add a filter for it
#     if user_id:
#         query = query.filter(cast(Address.user_id, String).ilike(f'%{user_id}%'))

#     # Execute the query and get all matching farmers
#     addresses = query.paginate(page=page, per_page=per_page)

#     result = {
#         'page': page,
#         'per_page': per_page,
#         'total_pages': addresses.pages,
#         'total_addresses': addresses.total,
#         'addresses': [{
#             'address': address_schema.dump(address),
#             'user': user_schema.dump(address.user)
#         } for address in addresses.items]
#     }   
#     return result
           
# def delete_address_by_id(id): 
    
#     try:
#         address = Address.query.get(id)
#         address_data=address_schema.dump(address)
#         db.session.delete(address)
#         db.session.commit()
#         return True, address_data
#     except Exception as e:
#             db.session.rollback()
#             error_message = f"An error occurred while deleting address details:  {str(e)}"
#             logging.error(error_message)
#             return False, {}  

# def update_address_by_id(address_id,data):
#     try:
#         address = Address.query.get(address_id)
        
#         if not address:
#             return False, "Address not found",{}
                   
#         for key, value in data.items():
#             setattr(address, key, value)
            
#         db.session.commit() 
#         return True, "Address Updated",address
    
#     except Exception as e:
#         error_message = f"An error occurred while updating address :  {str(e)}"
#         logging.error(error_message)
#         db.session.rollback() 
#         return False, error_message,{}












