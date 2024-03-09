from flask import Flask, request
from flask import Blueprint, jsonify, request, abort
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Advertisement, db
from app.schemas import advertisement_schema, advertisements_schema
import os
import uuid

file_routes = Blueprint('file', __name__)
CORS(file_routes)

@file_routes.route('/upload/product/<int:advertisement_id>', methods=['POST'])
def upload_file(advertisement_id):
    if 'file' not in request.files:
        return 'No file found', 400

    file = request.files['file']
    if file.filename == '':
        return 'No file selected', 400

    # Generate a UUID file name
    ext = os.path.splitext(file.filename)[1]  # Get the file extension
    if (ext == '.jpg') or (ext == '.jpeg') or (ext == '.png') or (ext == '.gif') or (ext == '.bmp'):
        uuid_filename = str(uuid.uuid4()) + ext  # Generate a UUID and append the file extension
    else:
        return 'Invalid file type:' + ext, 400

    # Save the file with the UUID file name
    file_path = os.path.join('app', 'images', 'advertisement', uuid_filename)
    file.save(file_path)

    # Update the image_link field of the Advertisement record
    advertisement = Advertisement.query.get(advertisement_id)
    if advertisement is None:
        return 'Advertisement not found', 404

    advertisement.image_link = uuid_filename
    db.session.commit()

    return jsonify(message='File saved and Advertisement updated successfully'), 200