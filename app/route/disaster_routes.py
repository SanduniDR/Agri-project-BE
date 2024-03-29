
from app.schemas import disaster_info_schema
from app.service.users.util_service import parse_date
from flask import Blueprint, jsonify, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import CORS
import datetime
from sqlalchemy import extract
from app.models import DisasterInfo, AgriOffice, CultivationInfo, Crop, Farm, Farmer,CultivationInfo,db



disaster_routes = Blueprint('disaster', __name__)
CORS(disaster_routes)

############################## Add Disaster Information  ###################################


@disaster_routes.route('/info', methods=['POST'])
@jwt_required()
def addDisasterInfo():
    # Get the request data
    data = request.get_json()

    # Check if farm_id exists in the Farm table
    cultivation_info_id = CultivationInfo.query.get(data['cultivation_info_id'])
    if not cultivation_info_id:
        return jsonify(message='Invalid cultivation_info_id'), 400

    
    # Create a new disaster info record
    disaster_info = DisasterInfo(
        cultivation_info_id=data['cultivation_info_id'],
        damaged_area=data['damaged_area'],
        estimated_damaged_harvest=data['estimated_damaged_harvest'],
        estimated_damaged_harvest_value=data['estimated_damaged_harvest_value'],
        type=data['type'],
        # time=datetime.time(),
        # date=datetime.date.today(),
        time = datetime.datetime.now().strftime('%H:%M:%S'),
        date=parse_date(data['date']),

    )

    # Add the disaster info record to the database
    db.session.add(disaster_info)
    db.session.commit()
    
    disaser_data=disaster_info_schema.dump(disaster_info)


    # Return a response
    return jsonify(disasterRecord=disaser_data,message='Disaster info added successfully'), 200

############################## Get Disaster Types  ###################################

@disaster_routes.route('/disasters/type', methods=['GET'])
def getTypes():
    # Query the disaster_info table
    disaster_info_records = DisasterInfo.query.all()

    # Get all unique disaster types bcz of converting of set (_set_;uniq)
    disaster_types = list(set([record.type for record in disaster_info_records]))

    # Return a response
    return jsonify(disasterTypes=disaster_types), 200

############################## Disaster Information Search ###################################

@disaster_routes.route('/disaster-info/search', methods=['GET'])
def search_disaster_info():
    year = request.args.get('year')
    month = request.args.get('month')
    crop_id = request.args.get('crop_id')
    type = request.args.get('type')
    district = request.args.get('district')
    office_id = request.args.get('office_id')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = db.session.query(DisasterInfo, CultivationInfo, Crop, Farm, Farmer, AgriOffice).join(
        CultivationInfo, DisasterInfo.cultivation_info_id == CultivationInfo.cultivation_info_id).join(
        Crop, CultivationInfo.crop_id == Crop.crop_id).join(
        Farm, CultivationInfo.farm_id == Farm.farm_id).join(
        Farmer, Farm.farmer_id == Farmer.user_id).join(
        AgriOffice, Farm.office_id == AgriOffice.agri_office_id)

    if year:
        query = query.filter(extract('year', DisasterInfo.date) == year)
    if month:
        query = query.filter(extract('month', DisasterInfo.date) == month)
    if crop_id:
        query = query.filter(Crop.crop_id == crop_id)
    if type:
        query = query.filter(DisasterInfo.type == type)
    if district:
        query = query.filter(AgriOffice.district == district)
    if office_id:
        query = query.filter(AgriOffice.agri_office_id == office_id)

    pagination = query.paginate(page=page, per_page=per_page)
    results = pagination.items

    return jsonify({
        'disasters': [{
            'disaster_info_id': result.DisasterInfo.disaster_info_id,
            'farmer_id':result.Farmer.user_id,
            'date': result.DisasterInfo.date,
            'type': result.DisasterInfo.type,
            'crop_id': result.Crop.crop_id,
            'crop_name': result.Crop.crop_name,
            'district': result.AgriOffice.district,
            'office_id': result.AgriOffice.agri_office_id
        } for result in results],
        'total_pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': pagination.per_page,
        'total_items': pagination.total
    }), 200
    
############################## Get Disaster  Records by record id ###################################

@disaster_routes.route('/disaster-info/<int:disaster_info_id>', methods=['GET'])
@jwt_required()
def getDisasterRecords(disaster_info_id):
    disaster_info=DisasterInfo.query.get(disaster_info_id)
    if not disaster_info:
        return jsonify(message='No record found'),404
    result=disaster_info_schema.dump(disaster_info)
    return jsonify(disasterInfo = result), 200
  
############################## Update Disaster  Records by record id ###################################

@disaster_routes.route('/disaster-info/<int:disaster_info_id>', methods=['PUT'])
@jwt_required()
def update_disaster_record(disaster_info_id):
    
    disaster_record = DisasterInfo.query.get(disaster_info_id)
    
    if not disaster_record:
        return jsonify(message='Record info not found'), 404 

    if 'cultivation_info_id' in request.json:
        disaster_record.cultivation_info_id = request.json['cultivation_info_id']

    if 'damaged_area' in request.json:
        disaster_record.damaged_area = request.json['damaged_area']

    if 'date' in request.json:
        disaster_record.date = parse_date(request.json['date'])

    if 'disaster_info_id' in request.json:
        disaster_record.disaster_info_id = request.json['disaster_info_id']

    if 'estimated_damaged_harvest' in request.json:
        disaster_record.estimated_damaged_harvest = request.json['estimated_damaged_harvest']

    if 'estimated_damaged_harvest_value' in request.json:
        disaster_record.estimated_damaged_harvest_value = request.json['estimated_damaged_harvest_value']

    if 'type' in request.json:
        disaster_record.type = request.json['type']

  
    db.session.commit()

    return jsonify({'message': 'Record updated successfully!'}),200

  ############################## Update Disaster  Records by record id ###################################
  
@disaster_routes.route('/disaster-info/<int:disaster_info_id>',methods = ['DELETE'])
@jwt_required()
def delete_disaster_record(disaster_info_id):
    disaster_record = DisasterInfo.query.get(disaster_info_id)
    if not disaster_record:
        return jsonify(message = 'Record not found'),404
    db.session.delete(disaster_record)
    db.session.commit()
    return jsonify({'message':'Record was deleted successfully!'}), 200
    
    
    
    
    
    
 