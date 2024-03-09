from flask import Blueprint, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Advertisement, User, db, AgricultureOfficer,Farmer
from app.schemas import advertisement_schema, advertisements_schema
import logging
from datetime import datetime
from app.service.users.util_service import parse_date
from flask import request
from flask import send_from_directory

market_routes = Blueprint('market', __name__)
CORS(market_routes)

@market_routes.route('/advertisement', methods=['POST'])
@jwt_required()
def add_advertisement():
    # Get the current user's identity
    current_user = get_jwt_identity()

    # Get the advertisement data from the request
    data = request.get_json()

    # Create a new advertisement object
    advertisement = Advertisement(
        published_by=current_user,
        type=data['type'],
        title=data['title'],
        category=data['category'],
        description=data['description'],
        date=parse_date(datetime.now().strftime('%Y-%m-%d')),
        user_id=current_user,
        unit_price=data['unit_price'],
        crop_id=data['crop_id'],
        amount=data['amount'],
        telephone_no=data['telephone_no'],
        image_link=data['image_link']
    )

    # Add the advertisement to the database
    db.session.add(advertisement)
    db.session.commit()

    # Return the added advertisement as JSON response
    return advertisement_schema.jsonify(advertisement)

@market_routes.route('/advertisement/<int:advertisement_id>', methods=['PUT'])
@jwt_required()
def update_advertisement(advertisement_id):
    # Get the current user's identity
    current_user = get_jwt_identity()

    # Get the advertisement from the database
    advertisement = Advertisement.query.get(advertisement_id)

    # Check if the advertisement exists and belongs to the current user
    if advertisement is None or advertisement.user_id != current_user:
        return jsonify({'message': 'Advertisement not found or unauthorized'}), 404

    # Get the updated advertisement data from the request
    data = request.get_json()

    # Parse the date from the request data
    parsed_date = parse_date(data['date'])

    # Update the advertisement
    advertisement.published_by = data['published_by']
    advertisement.type = data['type']
    advertisement.title = data['title']
    advertisement.category = data['category']
    advertisement.description = data['description']
    advertisement.date = parsed_date
    advertisement.time = data['time']
    advertisement.unit_price = data['unit_price']
    advertisement.crop_id = data['crop_id']
    advertisement.amount = data['amount']
    advertisement.telephone_no = data['telephone_no']
    # advertisement.verified_officer_id = data['verified_officer_id']
    advertisement.image_link = data['image_link']

    # Commit the changes to the database
    db.session.commit()

    # Return the updated advertisement as JSON response
    return advertisement_schema.jsonify(advertisement)

@market_routes.route('/approve/advertisement', methods=['PUT'])
@jwt_required()
def approve_advertisement():
    # Get the current user's identity
    current_user_id = get_jwt_identity()
    ad_id = request.args.get('ad_id')

    # Get the current user's role
    current_user = User.query.get(current_user_id)
    current_user_role = current_user.role

    # Get the advertisement from the database
    advertisement = Advertisement.query.get(ad_id)

    # Check if the advertisement exists and belongs to the current user
    if advertisement is None:
        return jsonify({'message': 'Advertisement not found or unauthorized'}), 404

    # If the current user's role is 4, update the verified_officer_id field
    if current_user_role == 4:
        advertisement.verified_officer_id = current_user_id

    # Commit the changes to the database
    db.session.commit()

    # Return the updated advertisement as JSON response
    return advertisement_schema.jsonify(advertisement)

@market_routes.route('/advertisement/<int:advertisement_id>', methods=['GET'])
@jwt_required()
def get_advertisement(advertisement_id):
    # Get the advertisement from the database
    advertisement = Advertisement.query.get(advertisement_id)

    # Check if the advertisement exists
    if advertisement is None:
        return jsonify({'message': 'Advertisement not found'}), 404

    # Return the advertisement as JSON response
    return advertisement_schema.jsonify(advertisement)



@market_routes.route('/my_advertisement', methods=['GET'])
@jwt_required()
def get_my_advertisements():
    # Get the page number and size from the request parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Create the base query
    query = Advertisement.query

    token_user_id = get_jwt_identity()
    current_user = User.query.get(token_user_id)

    # Add the filter to the query if the user_id parameter is provided
    if token_user_id is not None:
        query = query.filter(Advertisement.user_id == current_user.user_id)

    # Get the advertisements from the database with pagination
    pagination = query.paginate(page=page, per_page=per_page)
    # Get the advertisements from the pagination object
    advertisements = pagination.items

    # Return the advertisements as JSON response
    return jsonify({
        'data': advertisements_schema.dump(advertisements),
        'total_pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': pagination.per_page,
        'total_items': pagination.total
    }), 200
from flask import request

@market_routes.route('/officer/regional/ads', methods=['GET'])
@jwt_required()
def get_regional_advertisements():
    # Get the current user's identity
    token_user_id = get_jwt_identity()

    # Get the current user's role
    current_user = User.query.get(token_user_id)
    print(current_user)
    current_user_role = current_user.role

    # Check if the current user is an Agriculture Officer
    if current_user_role != 4:
        return jsonify({'message': 'Unauthorized'}), 403

    # Get the Agriculture Officer's assigned office
    agri_officer = AgricultureOfficer.query.get(token_user_id)
    print(agri_officer)
    assigned_office_id = agri_officer.agri_office_id

    # Get all Farmers assigned to the same office
    farmers = Farmer.query.filter_by(assigned_office_id=assigned_office_id).all()

    # Get all user_ids of these farmers
    farmer_user_ids = [farmer.user_id for farmer in farmers]

    # Get page and per_page parameters from the request
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Get all advertisements posted by these farmers with pagination
    pagination = Advertisement.query.filter(Advertisement.user_id.in_(farmer_user_ids)).paginate(page=page, per_page=per_page)
    advertisements = pagination.items

    # Return the advertisements and pagination info as JSON response
    return jsonify({
        'data': advertisements_schema.dump(advertisements),
        'current_page': pagination.page,
        'per_page': pagination.per_page,
        'total_items': pagination.total,
        'total_pages': pagination.pages,
    }), 200

@market_routes.route('/advertisement/<int:advertisement_id>', methods=['DELETE'])
@jwt_required()
def delete_advertisement(advertisement_id):
    # Get the current user's identity
    current_user = get_jwt_identity()

    # Get the advertisement from the database
    advertisement = Advertisement.query.get(advertisement_id)

    # Check if the advertisement exists and belongs to the current user
    if advertisement is None or advertisement.user_id != current_user:
        return jsonify({'message': 'Advertisement not found or unauthorized'}), 404

    # Delete the advertisement from the database
    db.session.delete(advertisement)
    db.session.commit()

    # Return a success message
    return jsonify({'message': 'Advertisement deleted successfully'}), 200

@market_routes.route('/all_advertisements', methods=['GET'])
def get_all_advertisements():
    # Get the page number and size from the request parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Create the base query
    query = Advertisement.query
    query = query.filter(Advertisement.verified_officer_id != '')

    # Get the advertisements from the database with pagination
    pagination = query.paginate(page=page, per_page=per_page)
    # Get the advertisements from the pagination object
    advertisements = pagination.items

    # Check if there are any advertisements
    if not advertisements:
        return jsonify({'message': 'No advertisements found'}), 404

    # Return the advertisements as JSON response
    return jsonify({
        'data': advertisements_schema.dump(advertisements),
        'total_pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': pagination.per_page,
        'total_items': pagination.total
    }), 200

@market_routes.route('/advertisement/<int:advertisement_id>/image', methods=['GET'])
def get_advertisement_image(advertisement_id):
    # Get the advertisement from the database
    advertisement = Advertisement.query.get(advertisement_id)

    # Check if the advertisement exists
    if advertisement is None:
        return jsonify({'message': 'Advertisement not found'}), 404

    # Get the image filename from the advertisement
    image_filename = advertisement.image_link

    # Define the directory where your images are stored
    # Replace 'your_directory' with the path to the directory where your images are stored
    image_directory = 'app\images\advertisement'

    # Send the image file
    return send_from_directory(image_directory, image_filename)
