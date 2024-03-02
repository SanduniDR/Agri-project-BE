
from app.schemas import disaster_info_schema
from app.service.users.util_service import parse_date
from flask import Blueprint, jsonify, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import CORS
import datetime
from app.models import CultivationInfo, DisasterInfo,db


disaster_routes = Blueprint('disaster', __name__)
CORS(disaster_routes)


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


 