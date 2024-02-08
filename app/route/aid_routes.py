from flask import Blueprint, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models import Aid, Pesticides, Fertilizer,MonetaryAid, Fuel, AidDistribution,  db
from app.schemas import aid_schema, aids_schema, pesticides_schema, pesticide_schema, fertilizers_schema, fertilizer_schema, monetary_aid_schema, monetary_aids_schema, fuels_schema, fuel_schema, aid_distribution_schema, aid_distributions_schema
from app.service.users.util_service import parse_date

aid_routes = Blueprint('aid', __name__)
CORS(aid_routes)

@aid_routes.route('', methods=['POST'])
@jwt_required()
def add_aid():
    aid_batch = request.json['aid_batch']
    year = request.json['year']
    in_charged_office_id = request.json['in_charged_office_id']
    description = request.json['description']
    aid_name = request.json['aid_name']

    existing_aid = Aid.query.filter_by(aid_name=aid_name).first()
    if existing_aid:
        return jsonify({'message': 'An aid with the same batch, year, and in-charged office already exists!'}), 409

    new_aid = Aid(aid_name=aid_name, aid_batch=aid_batch, year=year, in_charged_office_id=in_charged_office_id, description=description)

    db.session.add(new_aid)
    db.session.commit()

    return jsonify({'message': 'New aid added successfully!'})

@aid_routes.route('', methods=['GET'])
@jwt_required()
def get_aid():
    all_aid = Aid.query.all()
    result = aids_schema.dump(all_aid)
    return jsonify(result)

@aid_routes.route('/<id>', methods=['GET'])
@jwt_required()
def get_aid_by_id(id):
    aid = Aid.query.get(id)
    return aid_schema.jsonify(aid)

@aid_routes.route('/search', methods=['GET'])
@jwt_required()
def search_aid():
    # Get the filter parameters
    year = request.args.get('year')
    aid_batch = request.args.get('aid_batch')
    aid_id = request.args.get('aid_id')
    aid_name = request.args.get('aid_name')
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    # Build the filter conditions
    filter_conditions = []
    if aid_batch:
        filter_conditions.append(Aid.aid_batch.ilike(f'%{aid_batch}%'))
    if year:
        filter_conditions.append(Aid.year.ilike(f'%{year}%'))
    if aid_id:
        filter_conditions.append(Aid.aid_id.ilike(f'%{aid_id}%'))
    if aid_name:
        filter_conditions.append(Aid.aid_name.ilike(f'%{aid_name}%'))
    
    # Search for aid records based on the filters
    query = Aid.query.filter(*filter_conditions)
    pagination = query.paginate(page=page, per_page=per_page)
    aids = pagination.items

    # Return the search results
    result = aids_schema.dump(aids)
    return jsonify({
        'data': result,
        'total_pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': pagination.per_page,
        'total_items': pagination.total
    }), 200

@aid_routes.route('/<id>', methods=['DELETE'])
@jwt_required()
def delete_aid(id):
    aid = Aid.query.get(id)
    db.session.delete(aid)
    db.session.commit()
    return jsonify({'message': 'Aid deleted successfully!'})

@aid_routes.route('/<id>', methods=['PUT'])
@jwt_required()
def update_aid(id):
    aid = Aid.query.get(id)

    if 'aid_batch' in request.json:
        aid_batch = request.json['aid_batch']
        aid.aid_batch = aid_batch

    if 'year' in request.json:
        year = request.json['year']
        aid.year = year

    if 'in_charged_office_id' in request.json:
        in_charged_office_id = request.json['in_charged_office_id']
        aid.in_charged_office_id = in_charged_office_id

    if 'description' in request.json:
        description = request.json['description']
        aid.description = description
    
    if 'aid_name' in request.json:
        aid_name = request.json['aid_name']
        aid.aid_name = aid_name

    db.session.commit()

    return jsonify({'message': 'Aid updated successfully!'})

@aid_routes.route('/pesticides', methods=['POST'])
@jwt_required()
def add_pesticides():
    aid_id = request.json['aid_id']
    manufactured_date = parse_date(request.json['manufactured_date'])
    brand = request.json['brand']
    batch_no = request.json['batch_no']
    expiry_date = parse_date(request.json['expiry_date'])
    name = request.json['name']
    type = request.json['type']
    description = request.json['description']

    new_pesticides = Pesticides(aid_id=aid_id, manufactured_date=manufactured_date, brand=brand, batch_no=batch_no, expiry_date=expiry_date, name=name, type=type, description=description)

    db.session.add(new_pesticides)
    db.session.commit()

    return jsonify({'message': 'New pesticides added successfully!'})

@aid_routes.route('/pesticides/<id>', methods=['PUT'])
@jwt_required()
def update_pesticides(id):
    pesticides = Pesticides.query.get(id)

    if 'aid_id' in request.json:
        aid_id = request.json['aid_id']
        pesticides.aid_id = aid_id

    if 'manufactured_date' in request.json:
        manufactured_date = parse_date(request.json['manufactured_date'])
        pesticides.manufactured_date = manufactured_date

    if 'brand' in request.json:
        brand = request.json['brand']
        pesticides.brand = brand

    if 'batch_no' in request.json:
        batch_no = request.json['batch_no']
        pesticides.batch_no = batch_no

    if 'expiry_date' in request.json:
        expiry_date = parse_date(request.json['expiry_date'])
        pesticides.expiry_date = expiry_date

    if 'name' in request.json:
        name = request.json['name']
        pesticides.name = name

    if 'type' in request.json:
        type = request.json['type']
        pesticides.type = type

    if 'description' in request.json:
        description = request.json['description']
        pesticides.description = description

    db.session.commit()

    return jsonify({'message': 'Pesticides updated successfully!'})

@aid_routes.route('/pesticides/<id>', methods=['DELETE'])
@jwt_required()
def delete_pesticides(id):
    pesticides = Pesticides.query.get(id)
    db.session.delete(pesticides)
    db.session.commit()
    return jsonify({'message': 'Pesticides deleted successfully!'})

@aid_routes.route('/pesticides/search', methods=['GET'])
@jwt_required()
def search_pesticides():
    # Get the filter parameters
    aid_id = request.args.get('aid_id')
    brand = request.args.get('brand')
    name = request.args.get('name')
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    pesticides_id = request.args.get('pesticides_id')

    # Build the filter conditions
    filter_conditions = []
    if aid_id:
        filter_conditions.append(Pesticides.aid_id.ilike(f'%{aid_id}%'))
    if brand:
        filter_conditions.append(Pesticides.brand.ilike(f'%{brand}%'))
    if name:
        filter_conditions.append(Pesticides.name.ilike(f'%{name}%'))
    if pesticides_id:
        filter_conditions.append(Pesticides.pesticides_id.ilike(f'%{pesticides_id}%'))

    # Search for pesticides records based on the filters
    query = Pesticides.query.filter(*filter_conditions)
    pagination = query.paginate(page=page, per_page=per_page)
    pesticides = pagination.items

    # Return the search results
    result = pesticides_schema.dump(pesticides)
    return jsonify({
        'data': result,
        'total_pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': pagination.per_page,
        'total_items': pagination.total
    }), 200

@aid_routes.route('/fertilizer', methods=['POST'])
@jwt_required()
def add_fertilizer():
    aid_id = request.json['aid_id']
    manufactured_date = parse_date(request.json['manufactured_date'])
    brand = request.json['brand']
    batch_no = request.json['batch_no']
    expiry_date = parse_date(request.json['expiry_date'])
    name = request.json['name']
    type = request.json['type']
    description = request.json['description']

    new_fertilizer = Fertilizer(aid_id=aid_id, manufactured_date=manufactured_date, brand=brand, batch_no=batch_no, expiry_date=expiry_date, name=name, type=type, description=description)

    db.session.add(new_fertilizer)
    db.session.commit()

    return jsonify({'message': 'New fertilizer added successfully!'})

@aid_routes.route('/fertilizer/<id>', methods=['DELETE'])
@jwt_required()
def delete_fertilizer(id):
    fertilizer = Fertilizer.query.get(id)
    db.session.delete(fertilizer)
    db.session.commit()
    return jsonify({'message': 'Fertilizer deleted successfully!'})

@aid_routes.route('/fertilizer/search', methods=['GET'])
@jwt_required()
def search_fertilizer():
    # Get the filter parameters
    aid_id = request.args.get('aid_id')
    brand = request.args.get('brand')
    name = request.args.get('name')
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    fertilizer_id = request.args.get('fertilizer_id')

    # Build the filter conditions
    filter_conditions = []
    if aid_id:
        filter_conditions.append(Fertilizer.aid_id.ilike(f'%{aid_id}%'))
    if brand:
        filter_conditions.append(Fertilizer.brand.ilike(f'%{brand}%'))
    if name:
        filter_conditions.append(Fertilizer.name.ilike(f'%{name}%'))
    if fertilizer_id:
        filter_conditions.append(Fertilizer.fertilizer_id.ilike(f'%{fertilizer_id}%'))

    # Search for fertilizer records based on the filters
    query = Fertilizer.query.filter(*filter_conditions)
    pagination = query.paginate(page=page, per_page=per_page)
    fertilizers = pagination.items

    # Return the search results
    result = fertilizers_schema.dump(fertilizers)
    return jsonify({
        'data': result,
        'total_pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': pagination.per_page,
        'total_items': pagination.total
    }), 200

@aid_routes.route('/fertilizer/<id>', methods=['PUT'])
@jwt_required()
def update_fertilizer(id):
    fertilizer = Fertilizer.query.get(id)

    if 'aid_id' in request.json:
        aid_id = request.json['aid_id']
        fertilizer.aid_id = aid_id

    if 'manufactured_date' in request.json:
        manufactured_date = parse_date(request.json['manufactured_date'])
        fertilizer.manufactured_date = manufactured_date

    if 'brand' in request.json:
        brand = request.json['brand']
        fertilizer.brand = brand

    if 'batch_no' in request.json:
        batch_no = request.json['batch_no']
        fertilizer.batch_no = batch_no

    if 'expiry_date' in request.json:
        expiry_date = parse_date(request.json['expiry_date'])
        fertilizer.expiry_date = expiry_date

    if 'name' in request.json:
        name = request.json['name']
        fertilizer.name = name

    if 'type' in request.json:
        type = request.json['type']
        fertilizer.type = type

    if 'description' in request.json:
        description = request.json['description']
        fertilizer.description = description

    db.session.commit()

    return jsonify({'message': 'Fertilizer updated successfully!'})

@aid_routes.route('/monetary-aid', methods=['POST'])
@jwt_required()
def add_monetary_aid():
    aid_id = request.json['aid_id']
    description = request.json['description']
    reason = request.json['reason']

    new_monetary_aid = MonetaryAid(aid_id=aid_id, description=description, reason=reason)

    db.session.add(new_monetary_aid)
    db.session.commit()

    return jsonify({'message': 'New monetary aid added successfully!'})

@aid_routes.route('/monetary-aid/search', methods=['GET'])
@jwt_required()
def search_monetary_aid():
    # Get the filter parameters
    aid_id = request.args.get('aid_id')
    description = request.args.get('description')
    reason = request.args.get('reason')
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    monetary_aid_id = request.args.get('monetary_aid_id')

    # Build the filter conditions
    filter_conditions = []
    if aid_id:
        filter_conditions.append(MonetaryAid.aid_id.ilike(f'%{aid_id}%'))
    if description:
        filter_conditions.append(MonetaryAid.description.ilike(f'%{description}%'))
    if reason:
        filter_conditions.append(MonetaryAid.reason.ilike(f'%{reason}%'))
    if monetary_aid_id:
        filter_conditions.append(MonetaryAid.monetary_aid_id.ilike(f'%{monetary_aid_id}%'))

    # Search for monetary aid records based on the filters
    query = MonetaryAid.query.filter(*filter_conditions)
    pagination = query.paginate(page=page, per_page=per_page)
    monetary_aid = pagination.items

    # Return the search results
    result = monetary_aids_schema.dump(monetary_aid)
    return jsonify({
        'data': result,
        'total_pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': pagination.per_page,
        'total_items': pagination.total
    }), 200

@aid_routes.route('/monetary-aid/<id>', methods=['DELETE'])
@jwt_required()
def delete_monetary_aid(id):
    monetary_aid = MonetaryAid.query.get(id)
    db.session.delete(monetary_aid)
    db.session.commit()
    return jsonify({'message': 'Monetary aid deleted successfully!'})

@aid_routes.route('/monetary-aid/<id>', methods=['PUT'])
@jwt_required()
def update_monetary_aid(id):
    monetary_aid = MonetaryAid.query.get(id)

    if 'aid_id' in request.json:
        aid_id = request.json['aid_id']
        monetary_aid.aid_id = aid_id

    if 'description' in request.json:
        description = request.json['description']
        monetary_aid.description = description

    if 'reason' in request.json:
        reason = request.json['reason']
        monetary_aid.reason = reason

    db.session.commit()

    return jsonify({'message': 'Monetary aid updated successfully!'})

@aid_routes.route('/fuel-aid', methods=['POST'])
@jwt_required()
def add_fuel_aid():
    fuel_aid_data = request.json
    fuel_aid = Fuel(**fuel_aid_data)
    db.session.add(fuel_aid)
    db.session.commit()
    return jsonify({'message': 'Fuel aid added successfully!'})

@aid_routes.route('/fuel-aid/search', methods=['GET'])
@jwt_required()
def search_fuel_aid():
    # Get the filter parameters
    fuel_type = request.args.get('fuel_type')
    reason = request.args.get('reason')
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    # Build the filter conditions
    filter_conditions = []
    if fuel_type:
        filter_conditions.append(Fuel.fuel_type.ilike(f'%{fuel_type}%'))
    if reason:
        filter_conditions.append(Fuel.reason.ilike(f'%{reason}%'))

    # Search for fuel aid records based on the filters
    query = Fuel.query.filter(or_(*filter_conditions))
    pagination = query.paginate(page=page, per_page=per_page)
    fuels = pagination.items

    # Return the search results
    result = fuels_schema.dump(fuels)
    return jsonify({
        'data': result,
        'total_pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': pagination.per_page,
        'total_items': pagination.total
    }), 200

@aid_routes.route('/fuel-aid/<id>', methods=['DELETE'])
@jwt_required()
def delete_fuel_aid(id):
    fuel_aid = Fuel.query.get(id)
    db.session.delete(fuel_aid)
    db.session.commit()
    return jsonify({'message': 'Fuel aid deleted successfully!'})

@aid_routes.route('/fuel-aid/<id>', methods=['PUT'])
@jwt_required()
def update_fuel_aid(id):
    fuel_aid = Fuel.query.get(id)

    if 'aid_id' in request.json:
        aid_id = request.json['aid_id']
        fuel_aid.aid_id = aid_id

    if 'description' in request.json:
        description = request.json['description']
        fuel_aid.description = description

    if 'reason' in request.json:
        reason = request.json['reason']
        fuel_aid.reason = reason

    if 'fuel_type' in request.json:
        fuel_type = request.json['fuel_type']
        fuel_aid.fuel_type = fuel_type

    db.session.commit()

    return jsonify({'message': 'Fuel aid updated successfully!'})

@aid_routes.route('/aid-distribution', methods=['POST'])
@jwt_required()
def add_aid_distribution():
    aid_id = request.json['aid_id']
    agri_office_id = request.json['agri_office_id']
    date = parse_date(request.json['date'])
    in_charged_officer_id = request.json['in_charged_officer_id']
    cultivation_info_id = request.json['cultivation_info_id']
    farmer_id = request.json['farmer_id']
    amount_received = request.json['amount_received']
    amount_approved = request.json['amount_approved']
    description = request.json['description']

    new_aid_distribution = AidDistribution(aid_id=aid_id, agri_office_id=agri_office_id, date=date, in_charged_officer_id=in_charged_officer_id, cultivation_info_id=cultivation_info_id, farmer_id=farmer_id, amount_received=amount_received, amount_approved=amount_approved, description=description)

    db.session.add(new_aid_distribution)
    db.session.commit()

    return jsonify({'message': 'New aid distribution added successfully!'})

@aid_routes.route('/aid-distribution/<id>', methods=['DELETE'])
@jwt_required()
def delete_aid_distribution(id):
    aid_distribution = AidDistribution.query.get(id)
    db.session.delete(aid_distribution)
    db.session.commit()
    return jsonify({'message': 'Aid distribution deleted successfully!'})

@aid_routes.route('/aid-distribution/search', methods=['GET'])
@jwt_required()
def search_aid_distribution():
    # Get the filter parameters
    aid_id = request.args.get('aid_id')
    agri_office_id = request.args.get('agri_office_id')
    date = request.args.get('date')
    in_charged_officer_id = request.args.get('in_charged_officer_id')
    cultivation_info_id = request.args.get('cultivation_info_id')
    farmer_id = request.args.get('farmer_id')
    amount_received = request.args.get('amount_received')
    amount_approved = request.args.get('amount_approved')
    description = request.args.get('description')
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    # Build the filter conditions
    filter_conditions = []
    if aid_id:
        filter_conditions.append(AidDistribution.aid_id.ilike(f'%{aid_id}%'))
        
    if agri_office_id:
        filter_conditions.append(AidDistribution.agri_office_id.ilike(f'%{agri_office_id}%'))
        
    if date:
        filter_conditions.append(AidDistribution.date.ilike(f'%{date}%'))
                
    if in_charged_officer_id:
        filter_conditions.append(AidDistribution.in_charged_officer_id.ilike(f'%{in_charged_officer_id}%'))
        
    if cultivation_info_id:
        filter_conditions.append(AidDistribution.cultivation_info_id.ilike(f'%{cultivation_info_id}%'))
        
    if farmer_id:
        filter_conditions.append(AidDistribution.farmer_id.ilike(f'%{farmer_id}%'))
        
    if amount_received:
        filter_conditions.append(AidDistribution.amount_received.ilike(f'%{amount_received}%'))
        
    if amount_approved:
        filter_conditions.append(AidDistribution.amount_approved.ilike(f'%{amount_approved}%'))
        
    if description:
        filter_conditions.append(AidDistribution.description.ilike(f'%{description}%'))

    # Search for aid distribution records based on the filters
    query = AidDistribution.query.filter(*filter_conditions)
    pagination = query.paginate(page=page, per_page=per_page)
    aid_distributions = pagination.items

    # Return the search results
    result = aid_distributions_schema.dump(aid_distributions)
    return jsonify({
        'data': result,
        'total_pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': pagination.per_page,
        'total_items': pagination.total
    }), 200

@aid_routes.route('/aid-distribution/<id>', methods=['PUT'])
@jwt_required()
def update_aid_distribution(id):
    aid_distribution = AidDistribution.query.get(id)

    if 'aid_id' in request.json:
        aid_distribution.aid_id = request.json['aid_id']

    if 'agri_office_id' in request.json:
        aid_distribution.agri_office_id = request.json['agri_office_id']

    if 'date' in request.json:
        aid_distribution.date = parse_date(request.json['date'])

    if 'in_charged_officer_id' in request.json:
        aid_distribution.in_charged_officer_id = request.json['in_charged_officer_id']

    if 'cultivation_info_id' in request.json:
        aid_distribution.cultivation_info_id = request.json['cultivation_info_id']

    if 'farmer_id' in request.json:
        aid_distribution.farmer_id = request.json['farmer_id']

    if 'amount_received' in request.json:
        aid_distribution.amount_received = request.json['amount_received']

    if 'amount_approved' in request.json:
        aid_distribution.amount_approved = request.json['amount_approved']

    if 'description' in request.json:
        aid_distribution.description = request.json['description']

    db.session.commit()

    return jsonify({'message': 'Aid distribution updated successfully!'})
