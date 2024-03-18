from flask import Blueprint, jsonify, request, abort
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import CultivationInfo, db
from app.schemas import cultivation_info_schema, cultivation_infos_schema
from app.models import Farm, Crop
from  app.service.users.util_service import parse_date
from app.models import CultivationInfo
import datetime

cultivation_routes = Blueprint('cultivation', __name__)
CORS(cultivation_routes)

########################  Add Cultivation ################################

@cultivation_routes.route('/info', methods=['POST'])
@jwt_required()
def add_CultivationInfo():
    # Get the request data
    data = request.get_json()

    # Check if farm_id exists in the Farm table
    farm = Farm.query.get(data['farm_id'])
    if not farm:
        return jsonify(message='Invalid farm_id'), 400

    crop = Crop.query.get(data['crop_id'])
    if not crop:
        return jsonify(message='Invalid crop_id'), 400

    # Create a new cultivation info record
    cultivation_info = CultivationInfo(
        display_name=data['display_name'],
        farm_id=data['farm_id'],
        crop_id=data['crop_id'],
        longitude=data['longitude'],
        latitude=data['latitude'],
        area_of_cultivation=data['area_of_cultivation'],
        started_date=parse_date(data['started_date']),
        estimated_harvesting_date=parse_date(data['estimated_harvesting_date']),
        estimated_harvest=data['estimated_harvest'],
        agri_year=data['agri_year'],
        quarter=data['quarter'],
        added_by=get_jwt_identity(),
        updated_by=get_jwt_identity(),
        added_date=datetime.date.today()
    )

    # Add the cultivation info record to the database
    db.session.add(cultivation_info)
    db.session.commit()

    # Return a response
    return jsonify(message='Cultivation info added successfully'), 201


########################  Get CultivationInfo by Id ################################

@cultivation_routes.route('/<int:cultivation_id>', methods=['GET'])
@jwt_required()
def get_CultivationInfo(cultivation_id):
    # Get the cultivation info record by ID
    cultivation_info = CultivationInfo.query.get(cultivation_id)
    if not cultivation_info:
        return jsonify(message='Cultivation info not found'), 404

    # Return the cultivation info
    result = cultivation_info_schema.dump(cultivation_info)
    return jsonify(cultivation_Info=result), 200


########################  Update CultivationInfo by Id ################################

@cultivation_routes.route('/<int:cultivation_id>', methods=['PUT'])
@jwt_required()
def update_CultivationInfo(cultivation_id):
    # Get the request data
    data = request.get_json()

    # Check if the cultivation info record exists
    cultivation_info = CultivationInfo.query.get(cultivation_id)
    if not cultivation_info:
        return jsonify(message='Cultivation info not found'), 404

    # Check if farm_id exists in the Farm table
    farm = Farm.query.get(data['farm_id'])
    if not farm:
        return jsonify(message='Invalid farm_id'), 400

    crop = Crop.query.get(data['crop_id'])
    if not crop:
        return jsonify(message='Invalid crop_id'), 400

    # Update the cultivation info record
    cultivation_info.display_name = data['display_name']
    cultivation_info.farm_id = data['farm_id']
    cultivation_info.crop_id = data['crop_id']
    cultivation_info.longitude = data['longitude']
    cultivation_info.latitude = data['latitude']
    cultivation_info.area_of_cultivation = data['area_of_cultivation']
    cultivation_info.started_date = parse_date(data['started_date'])
    cultivation_info.estimated_harvesting_date = parse_date(data['estimated_harvesting_date'])
    cultivation_info.estimated_harvest = data['estimated_harvest']
    cultivation_info.agri_year = data['agri_year']
    cultivation_info.quarter = data['quarter']
    cultivation_info.updated_by = get_jwt_identity()

    # Check if harvested_date and harvested_amount are provided
    if 'harvested_date' in data and 'harvested_amount' in data:
        # Set harvested_date and harvested_amount if they are not empty
        if data['harvested_date'] != '':
            cultivation_info.harvested_date = parse_date(data['harvested_date'])
        if data['harvested_amount'] != '':
            cultivation_info.harvested_amount = data['harvested_amount']

    # Commit the changes to the database
    db.session.commit()

    # Return a response
    return jsonify(message='Cultivation info updated successfully'), 200


########################  Search CultivationInfo by Id ################################

@cultivation_routes.route('/search', methods=['GET'])
@jwt_required()
def search_CultivationInfo():
    # Get the filter parameters
    farm_id = request.args.get('farm_id')
    crop_id = request.args.get('crop_id')
    agri_year = request.args.get('agri_year')
    quarter = request.args.get('quarter')
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=100, type=int)

    # Build the filter conditions
    filter_conditions = []
    if farm_id:
        filter_conditions.append(CultivationInfo.farm_id == farm_id)
    if crop_id:
        filter_conditions.append(CultivationInfo.crop_id == crop_id)
    if agri_year:
        filter_conditions.append(CultivationInfo.agri_year == agri_year)
    if quarter:
        filter_conditions.append(CultivationInfo.quarter == quarter)

    # Search for cultivation info records based on the filters
    query = CultivationInfo.query.filter(
        *filter_conditions
    )
    pagination = query.paginate(page=page, per_page=per_page)
    cultivation_info = pagination.items

    # Return the search results
    result = cultivation_infos_schema.dump(cultivation_info)
    return jsonify({
        'data': result,
        'total_pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': pagination.per_page,
        'total_items': pagination.total
    }), 200

########################  Delete CultivationInfo by Id ################################

@cultivation_routes.route('/<int:cultivation_id>', methods=['DELETE'])
@jwt_required()
def delete_CultivationInfo(cultivation_id):
    # Get the cultivation info record by ID
    cultivation_info = CultivationInfo.query.get(cultivation_id)

    # Check if the record exists
    if not cultivation_info:
        return jsonify({'message': 'Cultivation info not found'}), 404

    # Delete the record
    db.session.delete(cultivation_info)
    db.session.commit()

    return jsonify({'message': 'Cultivation info deleted successfully'}), 200


