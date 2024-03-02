from app.service.users.communication_service import add_address, add_contacts, delete_address_by_id, delete_contact_by_id, get_all_addresses, search_address_by_Id, search_by_userId, update_address_by_id
from flask import Blueprint, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models import Crop, db
from app.schemas import address_schema,addresses_schema,contact_schema
from app.service.users.util_service import send_gmail
import config

com_routes = Blueprint('communication', __name__)
CORS(com_routes)

####Add Address          
@com_routes.route("/address", methods=['POST'])
@jwt_required()
def add_user_address():
    # Get the data from the request
        user_id = request.json['user_id']
        data = request.get_json()
        isSucceed,message,address=add_address(user_id,data)
        
        if isSucceed:
            return address_schema.jsonify(address)
        else:
            return jsonify(message=message), 422

# 'address_id', 'user_id', 'city', 'town', 'street', 'home_no', 'home_name'

####Retrieve Address          
@com_routes.route("/address", methods=['GET'])
@jwt_required()
def get_user_addresses():
    isSuccess,message,data= get_all_addresses()
    if isSuccess:
        return addresses_schema.jsonify(data)
    else:
        return jsonify(message=message)

####Search Address          
@com_routes.route('/address/search', methods=['GET'])
@jwt_required()
def search_address():
    # Get the search parameters from the query string
    user_id = request.args.get('user_id','')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    result=search_address_by_Id(user_id, page, per_page)
        # Return the result as JSON
    return jsonify(result)

####Delete Address          
@com_routes.route('/address/<id>',methods=['DELETE'])
@jwt_required()
def delete_address(id):
            isSucceed,data=delete_address_by_id(id)
            if isSucceed:
                return jsonify(address=data, deleted=True), 200
            else:
                return jsonify(message="This address_id  is not valid"), 400
            
####Update Address          
@com_routes.route('/address/update/<address_id>',methods=['POST'])
@jwt_required()
def update_address(address_id):
    data = request.get_json()
    isSucceed,message,result=update_address_by_id(address_id,data)
    if isSucceed:
        return jsonify(address=address_schema.dump(result),message=message, updated=True), 200
    else:
        return jsonify(message=message), 400
    
########################### Contacts ####################################

####Add Contacts          
@com_routes.route('/contacts',methods=['POST'])
@jwt_required()
def add_user_contacts():
    # Get the data from the request
        user_id = request.json['user_id']
        data = request.get_json()
        isSucceed,message,contacts=add_contacts(user_id,data)
        
        if isSucceed:
            return jsonify(contacts=contact_schema.dump(contacts),message=message),200
        else:
            return jsonify(message=message), 422

####Delete Contacts          
@com_routes.route('/contacts/delete/<contact_id>',methods=['DELETE'])
@jwt_required()
def delete_contact(contact_id):
            isSucceed,data=delete_contact_by_id(contact_id)
            if isSucceed:
                return jsonify(address=data, deleted=True), 200
            else:
                return jsonify(message="This contact_id  is not valid"), 400
            
####Search Contacts          
@com_routes.route('/contacts/search/',methods=['GET'])
@jwt_required()
def search_contacts():
    # Get the search parameters from the query string
    user_id = request.args.get('user_id','')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    result=search_by_userId(user_id, page, per_page)
        # Return the result as JSON
    return jsonify(result)


####Email Sending
@com_routes.route('/send', methods=['POST'])
def send_email():
    data = request.get_json()
    message_text = data.get('message')
    receivers = data.get('receivers')
    subject = data.get('subject')
    for receiver in receivers:
        response = send_gmail(
            access_token=config.ACCESS_TOKEN,
            refresh_token=config.REFRESH_TOKEN,
            client_id=config.CLIENT_ID,
            client_secret=config.CLIENT_SECRET,
            sender=config.MAIL_SENDER,
            to=receiver,
            subject=subject,
            message_text=message_text
        )

    return jsonify(response='Emails sent successfully'), 200
               

                
            