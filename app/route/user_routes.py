from flask import Blueprint, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, decode_token
from app.models import User, Farmer, db
from flask_mail import Message, Mail
from app.schemas import user_schema, farmer_schema, farmers_schema, users_schema
import logging
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy import or_, cast, String

from app.service.users.user_service import register_user
from app.service.users.util_service import parse_date
from datetime import timedelta

########################################################
# User routes
########################################################

user_routes = Blueprint('user', __name__)
mail = Mail()
CORS(user_routes)

logging.basicConfig(level=logging.DEBUG)


def configure_mail(app):
    mail.init_app(app)

@user_routes.route("/register", methods=['POST'])
def register():
    if request.is_json:
        email = request.json['email']
        test = User.query.filter_by(email=email).first()
        if test:
            return jsonify(message='That email already exists.'), 409
        else:
            first_name = request.json['first_name']
            last_name = request.json['last_name']
            password = request.json['password']
            nic =  request.json['nic']
            dob = parse_date(request.json['dob'])
            role = 2
            if 'role' in request.json:
                role = request.json['role']

            user = User(first_name=first_name, last_name=last_name, email=email, password=password, nic=nic, dob=dob, role=role)
            success, message = register_user(user)
            if success:
                return jsonify(message=message), 201
            else:
                return jsonify(message=message), 400
    else:
        return jsonify(message='Invalid request. Only JSON data is supported.'), 400
    
@user_routes.route("/login", methods=['POST'])

def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']

    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=test.user_id, expires_delta=timedelta(days=1))
        return jsonify(message="Login succeeded!", token=access_token, role=test.role)
    else:
        return jsonify(message='error in email or password', result=test), 401
    
@user_routes.route('/retrieve_password/<string:email>', methods=['GET'])
def retrieve_password(email: str):
    user = User.query.filter_by(email=email).first()
    if user:
        msg = Message("User password is " + user.password,
                      sender="mailtrap@dhanushkas.tech",
                      recipients=[email])
        mail.send(msg)
        return jsonify(message="Password sent to " + email), 201
    else:
        return jsonify(message="That email doesn't exist"), 401
    
@user_routes.route("/<int:userid>", methods=['GET'])
@jwt_required()
def get_user(userid):
    logging.debug('get_user called with userid: %s', userid)
    current_user_id = get_jwt_identity()
    logging.debug('current_user_id: %s', current_user_id)

    # Get the current user information from the token or database
    current_user = User.query.filter_by(user_id=current_user_id).first()
    logging.debug('current_user: %s', current_user)
    if current_user:
        user = User.query.filter_by(user_id=userid).first()
        if user:
            # Check if the current user is an admin (modify 'admin' to your actual admin role)
            if current_user.role in [1, 3, 4]:
                result = user_schema.dump(user)
                return jsonify(result)
            # Non-admin users can only access their own information
            elif current_user.user_id == userid:
                result = user_schema.dump(user)
                return jsonify(result)
            else:
                return jsonify(message="Unauthorized to access this resource"), 403
        else:
            return jsonify(message="No User was found for the given ID"), 404
    else:
        return jsonify(message="Unauthorized to access this resource"), 403

@user_routes.route('/find_by_email', methods=['GET'])
@jwt_required()
def find_user_by_email():
    # Get the email from the query string
    email = request.args.get('email')
    logging.debug('get_user called with email: %s', email)
    current_user_id = get_jwt_identity()
    logging.debug('current_user_id: %s', current_user_id)

    # Get the current user information from the token or database
    current_user = User.query.filter_by(user_id=current_user_id).first()
    logging.debug('current_user: %s', current_user)
    if current_user:
        user = User.query.filter_by(email=email).first()
        if user:
            # Check if the current user is an admin (modify 'admin' to your actual admin role)
            if current_user.role in [1, 3, 4] :
                result = user_schema.dump(user)
                return jsonify(result)
            # Non-admin users can only access their own information
            elif current_user.user_id == user.userid:
                result = user_schema.dump(user)
                return jsonify(result)
            else:
                return jsonify(message="Unauthorized to access this resource"), 403
        else:
            return jsonify(message="No User was found for the given ID"), 404
    else:
        return jsonify(message="Unauthorized to access this resource"), 403

# Delete
@user_routes.route('/<int:userid>', methods=['DELETE'])
@jwt_required()
def delete_user(userid):
    user = User.query.get(userid)
    data = user_schema.dump(user)
    db.session.delete(user)
    db.session.commit()
    logging.debug('user deleted: %s', data)
    return jsonify(user=data, deleted=True), 200



@user_routes.route('/update/<int:userid>', methods=['PUT'])
@jwt_required()
def update_user(userid):
    # Fetch the user from the database
    user = User.query.get(userid)

    # If the user does not exist, return an error
    if user is None:
        return jsonify(message="No User was found for the given ID"), 404

    # Get the new data from the request
    data = request.get_json()

    # Update the user's fields
    if 'email' in data:
        user.email = data['email']
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

    # Save the changes to the database
    db.session.commit()

    # Return a success message
    return jsonify(message="User updated successfully"), 200

@user_routes.route("/search", methods=['GET'])
@jwt_required()
def search_users():
    # Get the query parameters
    filters = request.args.to_dict()
    page = int(filters.pop('page', 1))
    per_page = int(filters.pop('per_page', 2))

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

    return jsonify(result)


@user_routes.route("/validate", methods=['POST'])
@jwt_required()
def validateUser():
    current_user_id = get_jwt_identity()
    if request.is_json:
        email = request.json['email']
    else:
        email = request.form['email']
    current_user_ByEmail = User.query.filter_by(email=email).first()
    if current_user_ByEmail and current_user_ByEmail.user_id == current_user_id:
        return jsonify(user=user_schema.dump(current_user_ByEmail), valid=True)
    else:
        return jsonify(valid=False), 401

@user_routes.route("/info", methods=['GET'])
@jwt_required()
def getUserInfo():
    current_user_id = get_jwt_identity()
    current_user_ByEmail = User.query.filter_by(user_id=current_user_id).first()
    return jsonify(user=user_schema.dump(current_user_ByEmail))

@user_routes.route("/check_token", methods=['GET'])
@jwt_required()
def checkTokenExpiration():
    token = request.headers.get('Authorization').split()[1]
    decoded_token = decode_token(token)
    expiration_timestamp = decoded_token['exp']
    current_timestamp = datetime.utcnow().timestamp()
    is_expired = current_timestamp > expiration_timestamp
    return jsonify(is_expired=is_expired)

###########################################################
# Farmer routes
###########################################################

# @user_routes.route('/search_farmers', methods=['GET'])
# @jwt_required()
# def search_farmers():
#     # Get the search parameters from the query string
#     office_id = request.args.get('office_id')
#     field_area_id = request.args.get('field_area_id')

#     # Start with a query that selects all farmers
#     query = Farmer.query

#     # If an office ID was provided, add a filter for it
#     if office_id is not None:
#         query = query.filter(Farmer.assigned_office_id == office_id)

#     # If a field area ID was provided, add a filter for it
#     if field_area_id is not None:
#         query = query.filter(Farmer.assigned_field_area_id == field_area_id)

#     # Execute the query and get all matching farmers
#     farmers = query.all()

#     # Convert the list of Farmer objects to a list of dictionaries
#     # This assumes you have a farmer_schema that can dump Farmer objects
#     farmers_dict = farmer_schema.dump(farmers, many=True)

#     # Return the result as JSON
#     return jsonify(farmers_dict)


@user_routes.route('/farmer', methods=['POST'])
@jwt_required()
def add_farmer():
    try:
        # Get the data from the request
        data = request.get_json()
        
        # Check if the current user is an admin (modify 'admin' to your actual admin role)
        current_user = User.query.filter_by(user_id=get_jwt_identity()).first()
        if current_user.role not in [1, 3, 4]:
            return jsonify(message="Unauthorized to access this resource"), 403
              
        # Create a new instance of the Farmer model with the data
        new_farmer = Farmer(**data)

        new_farmer.added_by = current_user.user_id
        new_farmer.updated_by = current_user.user_id
        new_farmer.registered_date = datetime.now()

        
        # Add the new farmer to the database session
        db.session.add(new_farmer)
        
        # Commit the changes to the database
        db.session.commit()
        
        # Return the JSON representation of the new farmer
        return farmer_schema.jsonify(new_farmer)
    except Exception as e:
        logging.error(e)
        return jsonify(message="Farmer registration failure, please check this user is already registered, Ping Admin service"), 500
    
# Read
@user_routes.route('/farmer', methods=['GET'])
@jwt_required()
def get_farmers():
    all_farmers = Farmer.query.all()
    return farmers_schema.jsonify(all_farmers)

@user_routes.route('/farmer/<id>', methods=['GET'])
@jwt_required()
def get_farmer(id):
    farmer = Farmer.query.get(id)
    return farmer_schema.jsonify(farmer)

# Update
@user_routes.route('/farmer/<id>', methods=['PUT'])
@jwt_required()
def update_farmer(id):
    farmer = Farmer.query.get(id)
    data = request.get_json()
    if 'registered_date' in data:
        data['registered_date'] = parse_date(data['registered_date'])
    # Check if 'user_id' is present in the data dictionary
    # if 'user_id' in data:
    #     # Check if the 'user_id' is similar to the <id> obtained from the path parameters
    #     if data['user_id'] != farmer.user_id:
    #         return jsonify(message="Cannot update 'user_id' to a different value"), 400
    for key, value in data.items():
        setattr(farmer, key, value)
    db.session.commit()
    return farmer_schema.jsonify(farmer)

# Delete
@user_routes.route('/farmer/<id>', methods=['DELETE'])
@jwt_required()
def delete_farmer(id):
    farmer = Farmer.query.get(id)
    user = User.query.get(farmer.user_id)  # Fetch the associated user

    farmer_data = farmer_schema.dump(farmer)
    user_data = user_schema.dump(user)  # Dump the user data

    db.session.delete(farmer)
    db.session.delete(user)  # Delete the user
    db.session.commit()

    return jsonify(farmer=farmer_data, user=user_data, deleted=True), 200

@user_routes.route('/search_farmers', methods=['GET'])
@jwt_required()
def search_farmers():
    # Get the search parameters from the query string
    office_id = request.args.get('assigned_office_id')
    tax_file_no = request.args.get('tax_file_no')
    field_area_id = request.args.get('assigned_field_area_id')
    user_id = request.args.get('user_id')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

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

    # Return the result as JSON
    return jsonify(result)