from flask import Blueprint, jsonify, request, abort
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Farm, Farmer, db
from app.schemas import farms_schema, farm_schema

farm_routes = Blueprint('farm', __name__)
CORS(farm_routes)

########################  Add Farm ################################

@farm_routes.route('', methods=['POST'])
@jwt_required()
def add_farm():
    farm_data = request.get_json()
    farmer_id = farm_data['farmer_id']
    farmer = Farmer.query.filter_by(user_id=farmer_id).first()
    if not farmer:
        return jsonify(message="No farmer was found"), 404
    farm_name = farm_data['farm_name']
    existing_farm = Farm.query.filter_by(farm_name=farm_name).first()
    if existing_farm:
        return jsonify(message="There is already a farm registered by that name"), 409
    else:
        address = farm_data['address']
        type = farm_data['type']
        farmer_id = farm_data['farmer_id']
        area_of_field = farm_data['area_of_field']
        owner_nic = farm_data['owner_nic']
        owner_name = farm_data['owner_name']

        
        farm = Farm(
                    farm_name=farm_name,
                    address=address,
                    type=type,
                    farmer_id=farmer_id,
                    area_of_field=area_of_field,
                    owner_nic=owner_nic,
                    owner_name=owner_name,
                    recorded_by=get_jwt_identity())
        
        db.session.add(farm)
        db.session.commit()
        
        return jsonify(message="New farm was registered successfully"), 201


@farm_routes.route('/<int:farm_id>', methods=['GET'])
@jwt_required()
def get_farm_details(farm_id: int):
    farm = Farm.query.filter_by(farm_id=farm_id).first()
    if farm:
        result = farm_schema.dump(farm)
        return jsonify(result)
    else:
        return jsonify(message="No farm was found for the given ID, Please check the ID and try again"), 404


@farm_routes.route('/<int:farm_id>', methods=['PUT'])
@jwt_required()
def update_farm(farm_id):
    farm = Farm.query.filter_by(farm_id=farm_id).first()
    if farm:
        farm_data = request.get_json()
        farm.farm_name = farm_data['farm_name']
        farm.address = farm_data['address']
        farm.type = farm_data['type']
        farm.farmer_id = farm_data['farmer_id']
        farm.area_of_field = farm_data['area_of_field']
        farm.owner_nic = farm_data['owner_nic']
        farm.owner_name = farm_data['owner_name']
        db.session.commit()
        return jsonify(message="Farm was updated successfully"), 202
    else:
        return jsonify(message="The farm does not exist in the system, please register"), 404


@farm_routes.route('/<int:farm_id>', methods=['DELETE'])
@jwt_required()
def remove_farm(farm_id: int):
    farm = Farm.query.filter_by(farm_id=farm_id).first()
    if farm:
        db.session.delete(farm)
        db.session.commit()
        return jsonify(message = "Farm was removed!"), 202
    else:
        return jsonify(message="No farm was found for the given ID, Please check the ID and try again"), 404

@farm_routes.route('/farms', methods=['GET'])
@jwt_required()
def farms():
    farm_list = Farm.query.all()
    result = farms_schema.dump(farm_list)
    return jsonify(result)

@farm_routes.route('/search', methods=['GET'])
@jwt_required()
def search_farm():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    query = Farm.query

    if 'farm_name' in request.args:
        query = query.filter(Farm.farm_name.ilike(f'%{request.args.get("farm_name")}%'))
    if 'address' in request.args:
        query = query.filter(Farm.address.ilike(f'%{request.args.get("address")}%'))
    if 'farmer_id' in request.args:
        query = query.filter(Farm.farmer_id.ilike(f'%{request.args.get("farmer_id")}%'))
    if 'farm_id' in request.args:
        query = query.filter(Farm.farm_id.ilike(f'%{request.args.get("farm_id")}%'))
    if 'type' in request.args:
        query = query.filter(Farm.type.ilike(f'%{request.args.get("type")}%'))
    if 'area_of_field' in request.args:
        query = query.filter(Farm.area_of_field.ilike(f'%{request.args.get("area_of_field")}%'))
    if 'owner_nic' in request.args:
        query = query.filter(Farm.owner_nic.ilike(f'%{request.args.get("owner_nic")}%'))
    if 'owner_name' in request.args:
        query = query.filter(Farm.owner_name.ilike(f'%{request.args.get("owner_name")}%'))

    farms = query.paginate(page=page, per_page=per_page)

    result = {
        'page': page,
        'per_page': per_page,
        'total_pages': farms.pages,
        'total_farms': farms.total,
        'farms': farms_schema.dump(farms.items)
    }

    return jsonify(result),200