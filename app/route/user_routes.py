from app.route.aid_routes import update_fertilizer
from flask import Blueprint, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, decode_token
from app.models import User, Farmer, db, AgricultureOfficer
from flask_mail import Message, Mail
from app.schemas import user_schema, farmer_schema, farmers_schema, users_schema,researcher_schema
import logging
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.service.users.user_service import  Update_Researcher, add_new_agri_officer,update_agri_officer,search_officers,Check_User_Token_Expiration, Get_User_Information, Search_User, Update_User, Validate_User, add_farmer_to_system, delete_farmer_from, get_all_farmers, get_all_users, get_farmer_by_Id, get_farmer_details_by_Id, getUserBy_Email, getUserBy_Id, deleteUser, get_access_token, getUserBy_Role, register_user, isExistingUser, retrieve_user_password, search_existing_farmers, update_farmer_details, user_login
from app.service.users.util_service import parse_date
from datetime import timedelta

#######################################################
# User route
########################################################

user_routes = Blueprint('user', __name__)
mail = Mail()
CORS(user_routes)

logging.basicConfig(level=logging.DEBUG)


def configure_mail(app):
    mail.init_app(app)
    
######################## User Registration  ################################
@user_routes.route("/register", methods=['POST'])
def register():
    if request.is_json:
        email = request.json['email']
        first_name = request.json['first_name']
        middle_name = request.json['middle_name']
        last_name = request.json['last_name']
        password = request.json['password']
        nic =  request.json['nic']
        dob = parse_date(request.json['dob'])
        role = 2
        if 'role' in request.json:
            role = request.json['role']
        user = User(first_name=first_name, middle_name=middle_name, last_name=last_name, email=email, password=password, nic=nic, dob=dob, role=role)
        isExistUser = isExistingUser(user) 
        if isExistUser:
            return jsonify(message='That email already exists.'), 409
        else:
            isSuccess, data, message = register_user(user)
            if isSuccess:
                userData = user_schema.dump(data) #do serializing
                return jsonify(user=userData, message=message), 201
            else:
                return jsonify(message=message), 400
    else:
        return jsonify(message='Invalid request. Only JSON data is supported.'), 400
    
########################  User Login ################################
@user_routes.route("/login", methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']

    user = User( email=email, password=password)
    user = user_login(user)
    
    if user:
        userEmail=user.email
        userFname=user.first_name
        userLname=user.last_name
        user_id=user.user_id
    else:
        return jsonify(message='Login Failed! ,Error in Username or Password'), 404
    
    if user:
        access_token = get_access_token(user)
        #access_token = create_access_token(identity=user.user_id, expires_delta=timedelta(days=1))
        return jsonify(message="Login succeeded!", token=access_token, role=user.role, firstname=userFname,lastname=userLname,email=userEmail, user_id=user_id), 200
    else:
        return jsonify(message='error in email or password', result=user), 401
    

 ########################  Retrieve Password ################################
 
@user_routes.route('/retrieve_password/<string:email>', methods=['GET'])
def retrieve_password(email: str):
    isMailSent=retrieve_user_password(email)
   
    if isMailSent:
        # msg = Message("User password is " + user.password,
        #               sender="mailtrap@dhanushkas.tech",
        #               recipients=[email])
        # mail.send(msg)
        return jsonify(message="Password sent to " + email), 201
    else:
        return jsonify(message="That email doesn't exist"), 401
    
 
  ########################  Retrieve User By Id ################################
   
@user_routes.route("/<int:userid>", methods=['GET'])
@jwt_required()
def get_user(userid):
    logging.debug('get_user called with userid: %s', userid)
    current_user_id = get_jwt_identity()
    logging.debug('current_user_id: %s', current_user_id)
    result=getUserBy_Id(userid, current_user_id)
    if result:
        response = user_schema.dump(result)
        return jsonify(response)
    else:
        return jsonify(message="Unauthorized to access this resource"), 403    

########################  Retrieve User By Email ################################
   
@user_routes.route('/find_by_email', methods=['GET'])
@jwt_required()
def find_user_by_email():
    # Get the email from the query string
    email = request.args.get('email')
    logging.debug('get_user called with email: %s', email)
    current_user_id = get_jwt_identity()
    result=getUserBy_Email(email,current_user_id)
    # Get the current user information from the token or database
   
    if result:
        response = user_schema.dump(result)
        return jsonify(response)
    else:
        return jsonify(message="Unauthorized to access this resource"), 403
    
########################  Retrieve User By role ################################
@user_routes.route('/find_by_role', methods=['GET'])
@jwt_required()
def find_user_by_role():
    # Get the email from the query string
    role = request.args.get('role')
    logging.debug('get_user called with role: %s', role)
    current_user_id = get_jwt_identity()
    result=getUserBy_Role(role,current_user_id)
    # Get the current user information from the token or database
   
    if result:
        response = users_schema.dump(result)
        return jsonify(users=response)
    else:
        return jsonify(message="Unauthorized to access this resource"), 403


########################  Delete User ################################
@user_routes.route('/<int:userid>', methods=['DELETE'])
@jwt_required()
def delete_user(userid):
    isDeleted,message,data=deleteUser(userid)
    if isDeleted:
        return jsonify(user=data, deleted=True), 200
    else: 
        return jsonify(message=message, deleted=False), 400


########################  Update User ################################

@user_routes.route('/update/<int:userid>', methods=['PUT'])
@jwt_required()
def update_user(userid):
    # Fetch the user from the database
    user = User.query.get(userid)
    logging.info(user.email)
    # If the user does not exist, return an error
    if user is None:
        return jsonify(message="No User was found for the given ID"), 404
    # Get the new data from the request
    data = request.get_json()
    Update_User(data, user)
    return jsonify(message="User updated successfully"), 200


########################  Search User ################################

@user_routes.route("/search", methods=['GET'])
@jwt_required()
def search_users():
    # Get the query parameters
    filters = request.args.to_dict()
    result=Search_User(filters)
    return jsonify(result)

########################  Validate User ################################

@user_routes.route("/validate", methods=['POST'])
@jwt_required()
def validateUser():
    current_user_id = get_jwt_identity()
    if request.is_json:
        email = request.json['email']
    else:
        email = request.form['email']
    
    response,current_user_ByEmail=Validate_User(current_user_id,email)

    if response:
        return jsonify(user=user_schema.dump(current_user_ByEmail), valid=True)
    else:
        return jsonify(valid=False), 401

########################  Get User Info ################################

@user_routes.route("/info", methods=['GET'])
@jwt_required()
def getUserInfo():
    current_user_id = get_jwt_identity()
    current_user=Get_User_Information(current_user_id)
    return jsonify(user=user_schema.dump(current_user))

########################  Get All User Info ################################
@user_routes.route("/all", methods=['GET'])
@jwt_required()
def getAllUserInfo():
    isSuccess,message,data= get_all_users()
    if isSuccess:
        return jsonify(allUsers=users_schema.dump(data))
    else:
        return jsonify(message=message)

# #All Users##################################
# @user_routes.route(' ', methods=['GET'])
# @jwt_required()
# def get_farmers():
#     isSuccess,message,data= get_all_users()
#     if isSuccess:
#         return jsonify(allUsers=user_schema.dump(data))
#     else:
#         return jsonify(message=message)
########################  Check User Token Expiration ################################

@user_routes.route("/check_token", methods=['GET'])
@jwt_required()
def checkTokenExpiration():
    token = request.headers.get('Authorization').split()[1]
    is_expired=Check_User_Token_Expiration(token)
   
    return jsonify(is_expired=is_expired)



###########################################################################
#Farmer Routes
###########################################################################                         


############################ Add Farmer ###################################

@user_routes.route('/farmer', methods=['POST'])
@jwt_required()
def add_farmer():
        # Get the data from the request
        data = request.get_json()
        user_id = get_jwt_identity()
        isSucceed, message, new_farmer=add_farmer_to_system(data, user_id)
        if isSucceed:
            return farmer_schema.jsonify(new_farmer),200
        elif not isSucceed and message=="Unauthorized to access this resource":
            jsonify(message=message), 403
        else:
            return jsonify(message=message), 500

#################################### Get All Farmer Details ########################################
@user_routes.route('/farmer', methods=['GET'])
@jwt_required()
def get_farmers():
    isSuccess,message,data= get_all_farmers()
    if isSuccess:
        return jsonify(farmers=farmers_schema.dump(data))
    else:
        return jsonify(message=message)

##################################### Get Farmer By Id #############################
@user_routes.route('/farmer/<id>', methods=['GET'])
@jwt_required()
def get_farmer(id):
    isSuccess,message,dataUser,dataFarmer = get_farmer_by_Id(id)
    user=user_schema.dump(dataUser)
    farmer=farmer_schema.dump(dataFarmer)
    if isSuccess:
        return jsonify(user=user, farmer=farmer),200
    else:
        return jsonify(message=message),400

#################################### Update Farmer Details ########################################

@user_routes.route('/farmer/<id>', methods=['PUT'])
@jwt_required()
def update_farmer(id):
    current_user = User.query.filter_by(user_id=get_jwt_identity()).first()
    data = request.get_json()
    farmer=update_farmer_details(id,current_user,data)
    return farmer_schema.jsonify(farmer)

#################################### Delete Farmer Details ########################################
@user_routes.route('/farmer/<id>', methods=['DELETE'])
@jwt_required()
def delete_farmer(id):
    isSucceed,farmer_data,user_data = delete_farmer_from(id)
    if isSucceed:
        return jsonify(farmer=farmer_data, user=user_data, deleted=True), 200
    else:
        return jsonify(message="This farmer does not exist !"), 400

#################################### Search Farmer Details ########################################

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
    
    result=search_existing_farmers(office_id, tax_file_no, field_area_id, user_id, page, per_page)
        # Return the result as JSON
    return jsonify(result)

#################################### get Farmer Full Details  ########################################

@user_routes.route('/farmer/details/<id>', methods=['GET'])
@jwt_required()
def get_detailed_farmer(id):
    isSuccess, message, data = get_farmer_details_by_Id(id)
    if isSuccess:
        return jsonify(data), 200
    else:
        return jsonify(message=message), 400




    
###################Get farmers in officer field area and office################
@user_routes.route('/officer/<int:officer_id>/farmer', methods=['GET'])
def get_farmers_by_officer(officer_id):
    officer = AgricultureOfficer.query.get(officer_id)
    if not officer:
        return jsonify({'error': 'Officer not found'}), 404

    users = db.session.query(User).join(
        Farmer, User.user_id == Farmer.user_id
    ).join(
        AgricultureOfficer, 
        db.and_(
            Farmer.assigned_office_id == officer.agri_office_id,
            Farmer.assigned_field_area_id == officer.field_area_id
        )
    ).all()
    response = users_schema.dump(users)
    return jsonify(farmers=response)

###############################Get Officers By District############################################
@user_routes.route('/officers/<district>', methods=['GET'])
def get_officers_by_district(district):
    officers = User.query.filter_by(district=district, role=4).all()
    return users_schema.jsonify(officers)

###############################Update Officer details By District############################################
@user_routes.route('/officers', methods=['POST'])
def register_new_officer():
    data = request.get_json()
    user_id = data.get('user_id')
    # check whether already registered office
    officer = AgricultureOfficer.query.get(user_id)
    if (officer) :
        return 'Already registered user as officer', 409     
    print(user_id)
    success, new_officer, message = add_new_agri_officer(data, user_id)
    print(success, new_officer, message)
    if not success:
        return jsonify({"error": message}), 400

    return jsonify(new_officer), 201

#########################################Officer Routes############################
####################### Delete Officer ###########################################
@user_routes.route('/officer/<int:user_id>', methods=['DELETE'])
def delete_officer(user_id):
    # Get the officer
    officer = AgricultureOfficer.query.get(user_id)

    if officer is None:
        return jsonify({"error": "Officer not found"}), 404

    # Delete the officer
    db.session.delete(officer)
    db.session.commit()

    return jsonify({"message": "Officer deleted successfully"}), 200


@user_routes.route('/officer/<user_id>', methods=['PUT'])
def update_officer(user_id):
    data = request.get_json()
    success, result, message = update_agri_officer(user_id, data)
    if success:
        return jsonify(result), 200
    else:
        return jsonify({"error": message}), 404

@user_routes.route('/search/officers', methods=['GET'])
def search():
    office_id = request.args.get('office_id')
    employee_id = request.args.get('employee_id')
    field_area_id = request.args.get('field_area_id')
    user_id = request.args.get('user_id')
    district = request.args.get('district')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    result = search_officers(office_id, employee_id, field_area_id, user_id, district, page, per_page)
    return jsonify(result), 200

@user_routes.route('/add-researcher', methods=['POST'])
@jwt_required()
def add_researcher():

        # Get the data from the request
        data = request.get_json()
        isSucceed, message, new_researcher=Update_Researcher(data)
        if isSucceed:
            return farmer_schema.jsonify(new_researcher),200
        else:
            return jsonify(message=message), 500
