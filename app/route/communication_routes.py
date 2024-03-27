from app.service.users.communication_service import add_address, add_contacts, add_sentDataRecord_to_system, delete_address_by_id, delete_contact_by_id, delete_request_by_id, get_all_addresses, search_address_by_Id, search_by_userId, update_address_by_id
from flask import Blueprint, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models import Crop, db, User, AgricultureOfficer, AgriOffice, EmailRecord,DataRequest,Reports
from app.schemas import address_schema,addresses_schema,contact_schema, email_records_schema,data_requests_schema,report_schema
import datetime
from app.service.users.util_service import send_gmail
import config
import json

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

@com_routes.route('/bulk-mail/officer/send', methods=['POST'])
def send_bulk_mail_officers_by_province():
    data = request.get_json()
    province = data.get('province')
    message_text = data.get('message')
    subject = data.get('subject')
    if not province:
        return jsonify({'error': 'Province parameter is missing'})
    
    emails = db.session.query(User.email).\
        join(AgricultureOfficer, User.user_id == AgricultureOfficer.user_id).\
        join(AgriOffice, AgricultureOfficer.agri_office_id == AgriOffice.agri_office_id).\
        filter(AgriOffice.province == province).\
        all()

    emails_list = [email[0] for email in emails]
    for receiver in emails_list:
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
        print("msg",response)
        # Create a new EmailRecord
        record = EmailRecord(
            email=config.MAIL_SENDER,
            subject=subject,
            message_text=message_text,
            sent_at=datetime.datetime.now(),
            sent_by=config.MAIL_SENDER,
            sent_to=receiver,
            status_sent = 'SENT' in response['labelIds'],
            response = json.dumps(response)
        )
        db.session.add(record)

    # Commit the changes to the database
    db.session.commit()

    return jsonify(emails_list)
               

@com_routes.route('/mail/search', methods=['POST'])
def search_mail():
    data = request.get_json()
    sent_by = data.get('email') or None
    subject = data.get('subject') or None
    status_sent = data.get('status_sent') or None
    sent_to = data.get('sent_to') or None
    page = data.get('page', 1)
    per_page = data.get('per_page', 30)

    filter_conditions = []
    if sent_to:
        filter_conditions.append(EmailRecord.sent_to.ilike(f'%{sent_to}%'))
    if sent_by:
        filter_conditions.append(EmailRecord.sent_by.ilike(f'%{sent_by}%'))
    if subject:
        filter_conditions.append(EmailRecord.subject.ilike(f'%{subject}%'))
    if status_sent is not None:
        filter_conditions.append(EmailRecord.status_sent == status_sent)

    if not filter_conditions:
        return jsonify({'error': 'At least one parameter is required'}), 400

    pagination = db.session.query(EmailRecord).filter(*filter_conditions).paginate(page=page, per_page=per_page)
    records = pagination.items
    result = email_records_schema.dump(records)

    return jsonify({
        'messages': result,
        'total_pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': pagination.per_page,
        'total_items': pagination.total,
    })

@com_routes.route('/data-request', methods=['POST'])
# @jwt_required()
def requestData():
    user_id = request.json['user_id']
    message = request.json['message']
    institute= request.json['institute']
    date=datetime.date.today()
    
    request_data = DataRequest(
        user_id=user_id,
        message=message,
        institute=institute,
        date=date
    )

    db.session.add(request_data)
    db.session.commit()

    # Return a response
    return jsonify(message='Request Data info added successfully'), 201
            
@com_routes.route('/get-data-requests', methods=['POST'])
def get_requests():
    data = request.get_json()
    page = data.get('page', 1)
    per_page = data.get('per_page', 10)

    filter_conditions = []
    pagination = db.session.query(DataRequest).filter(*filter_conditions).paginate(page=page, per_page=per_page)
    records = pagination.items
    result = data_requests_schema.dump(records)

    return jsonify({
        'requests': result,
        'total_pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': pagination.per_page,
        'total_items': pagination.total,
    })
    
@com_routes.route('/data-request/delete/<request_id>',methods=['DELETE'])
@jwt_required()
def delete_request(request_id):
            isSucceed,data=delete_request_by_id(request_id)
            if isSucceed:
                return jsonify(address=data, deleted=True), 200
            else:
                return jsonify(message="This request_id  is not valid"), 400

@com_routes.route('/sent-data', methods=['POST'])
@jwt_required()
def update_requestData_sent():
    data = request.get_json()
    date=datetime.date.today()
    isSucceed, message, new_record=add_sentDataRecord_to_system(data,date)
    if isSucceed:
        return report_schema.jsonify(new_record),200
    elif not isSucceed and message=="Unauthorized to access this resource":
        jsonify(message=message), 403
    else:
        return jsonify(message=message), 500