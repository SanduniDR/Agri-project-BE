from operator import and_
from flask import Blueprint, jsonify, request, abort
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from flask import request
from app.models import AgricultureOfficer, AidDistribution, Farmer, Fertilizer, Pesticides, RegionalAdmin, Researcher, SuperAdmin, User, Vendor, Role, db
from app.schemas import farms_schema, farm_schema, fertilizers_schema, pesticides_schema
from app.service.users.util_service import parse_date

report_routes = Blueprint('report', __name__)
CORS(report_routes)

@report_routes.route('users/count-by-role', methods=['GET'])
def get_user_count_by_role():
    role_counts = db.session.query(Role.role_name, func.count(User.user_id))\
        .join(Role, User.role == Role.role_id)\
        .outerjoin(Farmer, User.user_id == Farmer.user_id)\
        .outerjoin(SuperAdmin, User.user_id == SuperAdmin.user_id)\
        .outerjoin(RegionalAdmin, User.user_id == RegionalAdmin.user_id)\
        .outerjoin(AgricultureOfficer, User.user_id == AgricultureOfficer.user_id)\
        .outerjoin(Vendor, User.user_id == Vendor.user_id)\
        .outerjoin(Researcher, User.user_id == Researcher.user_id)\
        .group_by(Role.role_name)\
        .all()

    return jsonify({role_name: count for role_name, count in role_counts})

@report_routes.route('/aid-distributions/total', methods=['POST'])
def get_total_aid_distributions():
    data = request.get_json()
    start_date = parse_date(data.get('start_date'))
    end_date = parse_date(data.get('end_date'))

    aid_distributions = db.session.query(AidDistribution.description, func.sum(AidDistribution.amount_received)).filter(AidDistribution.date.between(start_date, end_date)).group_by(AidDistribution.description).all()
    aid_distribution = {description: amount for description, amount in aid_distributions}
    return jsonify({'total_aid_distributions': aid_distribution})
