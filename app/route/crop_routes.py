from flask import Blueprint, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models import Crop, db
from app.schemas import crops_schema, crop_schema

crop_routes = Blueprint('crop', __name__)
CORS(crop_routes)

################Add Crops####################################
@crop_routes.route('/add_crop', methods=['POST'])
@jwt_required()
def add_crop():
    if request.is_json:
        data = request.get_json()
        crop_name = data['crop_name']
        breed = data['breed']
        description = data['description']
        updated_by = ''
        added_by = get_jwt_identity()
        existing_crop = Crop.query.filter_by(crop_name=crop_name).first()
        if existing_crop:
            return jsonify(message="There is already a crop registered by that name"), 409
        else:
            crop = Crop(crop_name=crop_name,
                        breed=breed,
                        description=description,
                        updated_by=updated_by,
                        added_by=added_by)
            db.session.add(crop)
            db.session.commit()
            return jsonify(message="New crop was registered successfully"), 201
    else:
        return jsonify(message="Invalid request format"), 400


@crop_routes.route('/crop_details/<int:crop_id>', methods=['GET'])
@jwt_required()
def get_crop_details(crop_id: int):
    crop = Crop.query.filter_by(crop_id=crop_id).first()
    if crop:
        result = crop_schema.dump(crop)
        return jsonify(result)
    else:
        return jsonify(message="No crop was found for the given ID, Please check the ID and try again"), 404


@crop_routes.route('/update/<int:crop_id>', methods=['PUT'])
@jwt_required()
def update_crop(crop_id: int):
    if request.is_json:
        data = request.get_json()
        crop = Crop.query.filter_by(crop_id=crop_id).first()
        if crop:
            if 'crop_name' in data:
                crop.crop_name = data['crop_name']
            if 'breed' in data:
                crop.breed = data['breed']
            if 'description' in data:
                crop.description = data['description']
            if 'updated_by' in data:
                crop.updated_by = data['updated_by']
            db.session.commit()
            return jsonify(message="Crop was updated successfully"), 202
        else:
            return jsonify(message="The crop does not exist in the System, Please register"), 404
    else:
        return jsonify(message="Invalid request format"), 400


@crop_routes.route('/remove/<int:crop_id>', methods=['DELETE'])
@jwt_required()
def remove_crop(crop_id: int):
    crop = Crop.query.filter_by(crop_id=crop_id).first()
    if crop:
        db.session.delete(crop)
        db.session.commit()
        return jsonify(message = "Crop was removed!"), 202
    else:
        return jsonify(message="No crop was found for the given ID, Please check the ID and try again"), 404

@crop_routes.route('/crops', methods=['GET'])
@jwt_required()
def crops():
    crop_list = Crop.query.all()
    result = crops_schema.dump(crop_list)
    return jsonify(result)

@crop_routes.route('/search', methods=['GET'])
@jwt_required()
def search_crop():
    search_query = request.args.get('q')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 2))

    query = Crop.query.filter(Crop.breed.ilike(f'%{search_query}%') | Crop.crop_name.ilike(f'%{search_query}%') | Crop.crop_id.ilike(f'%{search_query}%'))

    crops = query.paginate(page=page, per_page=per_page)

    result = {
        'page': page,
        'per_page': per_page,
        'total_pages': crops.pages,
        'total_crops': crops.total,
        'crops': crops_schema.dump(crops.items)
    }

    return jsonify(result)

# @crop_routes.route("/search", methods=['GET'])
# @jwt_required()
# def search_crops():
#     # Get the query parameters
#     filters = request.args.to_dict()
#     page = int(filters.pop('page', 1))
#     per_page = int(filters.pop('per_page', 2))

#     # Build the query based on the filters
#     query = Crop.query
#     for key, value in filters.items():
#         if value:
#             query = query.filter(getattr(Crop, key) == value)
#     # logging.debug('query: %s', query)

#     # Apply pagination
#     crops = query.paginate(page=page, per_page=per_page)

#     # Prepare the response
#     result = {
#         'page': page,
#         'per_page': per_page,
#         'total_pages': crops.pages,
#         'total_users': crops.total,
#         'crops': crops_schema.dump(crops.items)
#     }

#     return jsonify(result)