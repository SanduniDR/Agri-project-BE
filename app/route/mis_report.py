from operator import and_
from flask import Blueprint, jsonify, request, abort
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from flask import request
from app.models import MiscellaneousAids, MonetaryAid, Fuel, Advertisement, Pesticides, AgricultureOfficer, AidDistribution, Farmer, Fertilizer, Pesticides, RegionalAdmin, Researcher, SuperAdmin, User, Vendor, Role, db
from app.schemas import fuel_schema, miscellaneous_aids_schema, aid_distribution_schema, monetary_aid_schema,pesticide_schema,farms_schema, farm_schema, fertilizers_schema, pesticides_schema, aids_schema, aid_schema, aid_schema, fertilizer_schema
from app.service.users.util_service import parse_date
from app.service.users.user_service import search_existing_farmers_By_Append
from sqlalchemy import func
from app.models import Farm, AgriOffice, Farmer, Crop, CultivationInfo, Aid
from sqlalchemy import extract


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

@report_routes.route('/aid-distributions/total-byfund', methods=['POST'])
def get_total_aid_distributions_byFund():
    data = request.get_json()
    aid_id = data.get('aid_id')

    aid_distributions = db.session.query(AidDistribution.description, func.sum(AidDistribution.amount_received)).filter(AidDistribution.aid_id==aid_id).group_by(AidDistribution.description).all()
    aid_distribution = {description: amount for description, amount in aid_distributions}
    return jsonify({'total_aid_distributions': aid_distribution})

@report_routes.route('/aid-distributions/yearly/<int:year>', methods=['GET'])
def get_total_aid_distributions_yearly(year):
    start_date = f'{year}-01-01'
    end_date = f'{year}-12-31'
    aid_distributions = db.session.query(AidDistribution.description, func.sum(AidDistribution.amount_received)).filter(AidDistribution.date.between(start_date, end_date)).group_by(AidDistribution.description).all()
    aid_distribution = {description: amount for description, amount in aid_distributions}
    return jsonify({'total_aid_distributions': aid_distribution})

@report_routes.route('/fertilizer-distributions/monthly/<int:year>', methods=['GET'])
def get_monthly_fertilizer_distributions(year):
    # Query the database for the total approved amount of fertilizer distributed each month
    fertilizer_distributions = db.session.query(
        extract('month', AidDistribution.date).label('month'),
        func.sum(AidDistribution.amount_approved).label('total_amount_approved')
    ).filter(
        AidDistribution.description == 'Fertilizer',
        extract('year', AidDistribution.date) == year
    ).group_by(
        'month'
    ).order_by(
        'month'
    ).all()

    # Initialize a list with 12 dictionaries, one for each month
    monthly_fertilizer_distributions = [{'month': month, 'total_amount_approved': 0.0} for month in range(1, 13)]

    # Update the dictionaries with the actual data
    for distribution in fertilizer_distributions:
        # The month in the distribution record is 1-based, so subtract 1 to get the 0-based index
        index = int(distribution.month) - 1

        # Update the total_amount_approved for the month
        monthly_fertilizer_distributions[index]['total_amount_approved'] = float(distribution.total_amount_approved)

    return jsonify(monthly_fertilizer_distributions)

@report_routes.route('/aid-distributions/monthly', methods=['GET'])
def get_monthly_aid_distributions( ):
    year = request.args.get('year')
    description = request.args.get('type')
    fertilizer_distributions = db.session.query(
        extract('month', AidDistribution.date).label('month'),
        func.sum(AidDistribution.amount_approved).label('total_amount_approved')
    ).filter(
        AidDistribution.description == description,
        extract('year', AidDistribution.date) == year
    ).group_by(
        'month'
    ).order_by(
        'month'
    ).all()

    # Initialize a list with 12 dictionaries, one for each month
    monthly_fertilizer_distributions = [{'month': month, 'total_amount_approved': 0.0} for month in range(1, 13)]

    # Update the dictionaries with the actual data
    for distribution in fertilizer_distributions:
        # The month in the distribution record is 1-based, so subtract 1 to get the 0-based index
        index = int(distribution.month) - 1

        # Update the total_amount_approved for the month
        monthly_fertilizer_distributions[index]['total_amount_approved'] = float(distribution.total_amount_approved)

    return jsonify(monthly_fertilizer_distributions)

#///////////////////////////////////////////
# Cultivation Info vs District
#///////////////////////////////////////////
@report_routes.route('/cultivation-info/cropByDistrict', methods=['POST'])
def get_crop_cultivation_by_district():
    data =  request.get_json()
    agri_year = data.get('agri_year')
    quarter = data.get('quarter')
    result = db.session.query(
        AgriOffice.district,
        Crop.crop_name,
        func.sum(CultivationInfo.area_of_cultivation).label('total_cultivated')
    ).join(
        Farm, Farm.farm_id == CultivationInfo.farm_id
    ).join(
        Farmer, Farmer.user_id == Farm.farmer_id
    ).join(
        AgriOffice, AgriOffice.agri_office_id == Farmer.assigned_office_id
    ).join(
        Crop, Crop.crop_id == CultivationInfo.crop_id
    ).filter(
        #CultivationInfo.started_date <= func.current_date(),
        CultivationInfo.agri_year == agri_year,
        CultivationInfo.quarter == quarter
    ).group_by(
        AgriOffice.district,
        Crop.crop_name
    ).all()

    return jsonify([row._asdict() for row in result])

@report_routes.route('/search/cultivation-info', methods=['POST'])
def search_crop_cultivation_by_year():
    data =  request.get_json()
    agri_year = data.get('year')
    crop_id = data.get('crop_id')
    result = db.session.query(
        AgriOffice.district,
        Crop.crop_name,
        func.sum(CultivationInfo.area_of_cultivation).label('total_cultivated_area'),
        func.sum(CultivationInfo.harvested_amount).label('total_harvested')
    ).join(
        Farm, Farm.farm_id == CultivationInfo.farm_id
    ).join(
        Farmer, Farmer.user_id == Farm.farmer_id
    ).join(
        AgriOffice, AgriOffice.agri_office_id == Farmer.assigned_office_id
    ).join(
        Crop, Crop.crop_id == CultivationInfo.crop_id
    ).filter(
        #CultivationInfo.started_date <= func.current_date(),
        CultivationInfo.agri_year == agri_year,
        CultivationInfo.crop_id == crop_id
    ).group_by(
        AgriOffice.district,
        Crop.crop_name
    ).all()

    return jsonify([row._asdict() for row in result])

@report_routes.route('/search/cultivation-info/monthly', methods=['POST'])
def search_crop_cultivation_by_monthly():
    data =  request.get_json()
    agri_year = data.get('year')
    month = data.get('month')
    crop_id = data.get('crop_id')
    result = db.session.query(
        AgriOffice.district,
        Crop.crop_name,
        func.sum(CultivationInfo.area_of_cultivation).label('total_cultivated_area'),
        func.sum(CultivationInfo.harvested_amount).label('total_harvested')
    ).join(
        Farm, Farm.farm_id == CultivationInfo.farm_id
    ).join(
        Farmer, Farmer.user_id == Farm.farmer_id
    ).join(
        AgriOffice, AgriOffice.agri_office_id == Farmer.assigned_office_id
    ).join(
        Crop, Crop.crop_id == CultivationInfo.crop_id
    ).filter(
        #CultivationInfo.started_date <= func.current_date(),
        CultivationInfo.agri_year == agri_year,
        CultivationInfo.crop_id == crop_id,
        extract('month', CultivationInfo.estimated_harvesting_date) == month
    ).group_by(
        AgriOffice.district,
        Crop.crop_name
    ).all()

    return jsonify([row._asdict() for row in result])

@report_routes.route('/search/cultivation-info/monthly/district', methods=['POST'])
def search_crop_cultivation_by_monthly_district():
    data =  request.get_json()
    agri_year = data.get('year')
    month = data.get('month')
    crop_id = data.get('crop_id')
    district = data.get('district')
    result = db.session.query(
        AgriOffice.district,
        Crop.crop_name,
        func.sum(CultivationInfo.area_of_cultivation).label('total_cultivated_area'),
        func.sum(CultivationInfo.harvested_amount).label('total_harvested')
    ).join(
        Farm, Farm.farm_id == CultivationInfo.farm_id
    ).join(
        Farmer, Farmer.user_id == Farm.farmer_id
    ).join(
        AgriOffice, AgriOffice.agri_office_id == Farmer.assigned_office_id
    ).join(
        Crop, Crop.crop_id == CultivationInfo.crop_id
    ).filter(
        #CultivationInfo.started_date <= func.current_date(),
        CultivationInfo.agri_year == agri_year,
        CultivationInfo.crop_id == crop_id,
        extract('month', CultivationInfo.estimated_harvesting_date) == month,
        AgriOffice.district == district
    ).group_by(
        AgriOffice.district,
        Crop.crop_name
    ).all()

    return jsonify([row._asdict() for row in result])

@report_routes.route('/search/cultivation-info/monthly/district/office', methods=['POST'])
def search_crop_cultivation_by_monthly_district_office():
    data =  request.get_json()
    agri_year = data.get('year')
    month = data.get('month')
    crop_id = data.get('crop_id')
    district = data.get('district')
    office_id = data.get('office')
    result = db.session.query(
        AgriOffice.district,
        Crop.crop_name,
        func.sum(CultivationInfo.area_of_cultivation).label('total_cultivated_area'),
        func.sum(CultivationInfo.harvested_amount).label('total_harvested')
    ).join(
        Farm, Farm.farm_id == CultivationInfo.farm_id
    ).join(
        Farmer, Farmer.user_id == Farm.farmer_id
    ).join(
        AgriOffice, AgriOffice.agri_office_id == Farm.office_id
    ).join(
        Crop, Crop.crop_id == CultivationInfo.crop_id
    ).filter(
        #CultivationInfo.started_date <= func.current_date(),
        CultivationInfo.agri_year == agri_year,
        CultivationInfo.crop_id == crop_id,
        extract('month', CultivationInfo.estimated_harvesting_date) == month,
        AgriOffice.district == district,
        AgriOffice.agri_office_id == office_id
    ).group_by(
        AgriOffice.district,
        Crop.crop_name
    ).all()

    return jsonify([row._asdict() for row in result])

@report_routes.route('/search/cultivation-map/monthly/district/office', methods=['POST'])
def search_crop_cultivation_map_by_monthly_district_office():
    # Get the request data
    data =  request.get_json()

    # Extract the required parameters from the data
    agri_year = data.get('year')
    month = data.get('month')
    crop_id = data.get('crop_id')
    district = data.get('district')
    office_id = data.get('office_id')

    # Query the database for the cultivation information
    result = db.session.query(
        AgriOffice.district,
        Crop.crop_name,
        CultivationInfo.cultivation_info_id,
        CultivationInfo.longitude,
        CultivationInfo.latitude,
        AgriOffice.agri_office_id,
    ).join(
        Farm, Farm.farm_id == CultivationInfo.farm_id  # Join with Farm table
    ).join(
        Farmer, Farmer.user_id == Farm.farmer_id  # Join with Farmer table
    ).join(
        AgriOffice, AgriOffice.agri_office_id == Farm.office_id  # Join with AgriOffice table
    ).join(
        Crop, Crop.crop_id == CultivationInfo.crop_id  # Join with Crop table
    ).filter(
        # Apply filters based on the request parameters
        CultivationInfo.agri_year == agri_year,
        CultivationInfo.crop_id == crop_id,
        extract('month', CultivationInfo.estimated_harvesting_date) == month,
        AgriOffice.district == district,
        AgriOffice.agri_office_id == office_id
    ).all()

    # Return the result as a JSON response
    return jsonify([row._asdict() for row in result])

@report_routes.route('users/count-by-role/<int:role_id>', methods=['GET'])
def get_total_user_count_by_role(role_id):
    user_count = db.session.query(func.count(User.user_id))\
        .join(Role, User.role == Role.role_id)\
        .filter(Role.role_id == role_id)\
        .scalar()

    return jsonify({'total_user_count': user_count})

@report_routes.route('/users/count-by-district', methods=['GET'])
def get_user_count_by_district():
    user_counts = db.session.query(
        AgriOffice.district,
        func.count(User.user_id)
    ).join(
        Farmer, User.user_id == Farmer.user_id
    ).join(
        AgriOffice, AgriOffice.agri_office_id == Farmer.assigned_office_id
    ).group_by(
        AgriOffice.district
    ).all()

    return jsonify({district: count for district, count in user_counts})

@report_routes.route('/users/farmer/count-by-district', methods=['GET'])
def get_total_user_count_by_district():
    user_counts = db.session.query(
        AgriOffice.district,
        func.count(User.user_id)
    ).join(
        Farmer, User.user_id == Farmer.user_id
    ).join(
        AgriOffice, AgriOffice.agri_office_id == Farmer.assigned_office_id
    ).group_by(
        AgriOffice.district
    ).all()

    return jsonify([{'district': district, 'count': count} for district, count in user_counts])

@report_routes.route('/harvest-amount-by-crop/<int:agri_year>', methods=['GET'])
def get_harvest_amount_by_crop(agri_year):
    # Query the database for the total harvested amount of each crop
    cultivation_infos = db.session.query(
        CultivationInfo.crop_id,
        func.sum(CultivationInfo.harvested_amount).label('total_harvested_amount'),
        func.sum (CultivationInfo.estimated_harvest).label('total_estimated_harvested_amount')
    ).filter(
        CultivationInfo.agri_year == agri_year
    ).group_by(
        CultivationInfo.crop_id
    ).all()

    # Convert the query results to a list of dictionaries
    harvest_amount_by_crop = [
        {'crop_id': info.crop_id, 'total_harvested_amount': info.total_harvested_amount, 'total_estimated_harvested_amount': info.total_estimated_harvested_amount} 
        for info in cultivation_infos
    ]

    # Get the crop names from the Crop table
    for data in harvest_amount_by_crop:
        crop = Crop.query.get(data['crop_id'])
        data['crop_name'] = crop.crop_name if crop else 'Unknown'

    return jsonify(harvest_amount_by_crop)

@report_routes.route('/estimated-harvest/<int:agri_year>', methods=['GET'])
def get_estimated_harvest(agri_year):
    # Query the database for the total estimated harvest of each crop for each month
    cultivation_infos = db.session.query(
        extract('month', CultivationInfo.estimated_harvesting_date).label('month'),
        Crop.crop_name,
        func.sum(CultivationInfo.estimated_harvest).label('total_estimated_harvest')
    ).join(
        Crop, Crop.crop_id == CultivationInfo.crop_id
    ).filter(
        extract('year', CultivationInfo.estimated_harvesting_date) == agri_year
    ).group_by(
        'month',
        Crop.crop_name
    ).all()

    # Initialize the response data
    response_data = {}

    # Update the response data with the query results
    for info in cultivation_infos:
        if info.crop_name not in response_data:
            response_data[info.crop_name] = [0]*12
        response_data[info.crop_name][info.month - 1] = info.total_estimated_harvest

    # Convert the response data to a list of dictionaries
    response = [{'label': crop_name, 'data': data} for crop_name, data in response_data.items()]

    return jsonify(response)

@report_routes.route('/aids/adminReports', methods=['GET'])
def get_aids():
    # start_date = request.args.get('start_date')
    # end_date = request.args.get('end_date')
    year = request.args.get('year')
    aid_id = request.args.get('aid_id')

    aids = Aid.query
    if year:
        aids = aids.filter(Aid.year == year)
    if aid_id:
        aids = aids.filter(Aid.aid_id == aid_id)
    aids = aids.all()

    result = []
    for aid in aids:
        aid_data = aid_schema.dump(aid)
        aid_data['fertilizers'] = fertilizer_schema.dump(Fertilizer.query.filter_by(aid_id=aid.aid_id).all())
        aid_data['pesticides'] = pesticides_schema.dump(Pesticides.query.filter_by(aid_id=aid.aid_id).all())
        aid_data['monetary_aids'] = monetary_aid_schema.dump(MonetaryAid.query.filter_by(aid_id=aid.aid_id).all())
        aid_data['fuels'] = fuel_schema.dump(Fuel.query.filter_by(aid_id=aid.aid_id).all())
        aid_data['miscellaneous_aids'] = miscellaneous_aids_schema.dump(MiscellaneousAids.query.filter_by(aid_id=aid.aid_id).all())
        result.append(aid_data)

    return jsonify({'aids': result})

@report_routes.route('/offices/total', methods=['GET'])
def get_all_officers():
    officers = AgriOffice.query.all()
    officers_list = []
    for officer in officers:
        officer_data = {
            'agri_office_id': officer.agri_office_id,
            'name': officer.name,
            'city': officer.city,
            'province': officer.province,
            'district': officer.district
        }
        officers_list.append(officer_data)
    return jsonify({'offices': officers_list})

@report_routes.route('/offices', methods=['GET'])
def get_all_officesByDistrictOrProvince():
    district = request.args.get('district')
    province = request.args.get('province')

    query = AgriOffice.query

    if district:
        query = query.filter(AgriOffice.district == district)
    if province:
        query = query.filter(AgriOffice.province == province)
    if district and province:
        query = query.filter(and_(AgriOffice.district == district, AgriOffice.province == province))

    offices = query.all()
    offices_list = []
    for officer in offices:
        officer_data = {
            'agri_office_id': officer.agri_office_id,
            'name': officer.name,
        }
        offices_list.append(officer_data)
    return jsonify({'offices': offices_list})

from flask import request

@report_routes.route('/farmer/count-by-Province', methods=['GET'])
def get_user_count_by_province():
    province = request.args.get('province')

    query = db.session.query(
        AgriOffice.province,
        func.count(User.user_id)
    ).join(
        Farmer, User.user_id == Farmer.user_id
    ).join(
        AgriOffice, AgriOffice.agri_office_id == Farmer.assigned_office_id
    )

    if province:
        query = query.filter(AgriOffice.province == province)

    user_counts = query.group_by(AgriOffice.province).all()

    return jsonify({province: count for province, count in user_counts})

# @report_routes.route('/offices/by-province-district', methods=['GET'])
# def get_offices_by__province_district():
#     province = request.args.get('province')
#     district = request.args.get('district')

#     query = AgriOffice.query

#     if province:
#         query = query.filter(AgriOffice.province == province)
#     if district:
#         query = query.filter(AgriOffice.district == district)

#     offices = query.all()
#     offices_list = []
#     for office in offices:
#         office_data = {
#             'agri_office_id': office.agri_office_id,
#             'name': office.name,
#             'city': office.city,
#             'province': office.province,
#             'district': office.district
#         }
#         offices_list.append(office_data)
#     return jsonify({'offices': offices_list})


@report_routes.route('/offices/by-province-district', methods=['GET'])
def get_offices_by_province_district():
    province = request.args.get('province')
    district = request.args.get('district')

    if not province or not district:
        return jsonify({'error': 'Both province and district must be provided'}), 400

    query = AgriOffice.query.filter(AgriOffice.province == province, AgriOffice.district == district)
    offices = query.all()
    offices_list = []
    for office in offices:
        office_data = {
            'agri_office_id': office.agri_office_id,
            'name': office.name,
            'city': office.city,
            'province': office.province,
            'district': office.district
        }
        offices_list.append(office_data)
    return jsonify({'offices': offices_list})

@report_routes.route('/offices-districts/by-province', methods=['GET'])
def get_all_offices_districts_by_given_province():
    province = request.args.get('province')

    if not province:
        return jsonify({'error': 'Province must be provided'}), 400

    query = AgriOffice.query.filter(AgriOffice.province == province)
    offices = query.all()
    offices_list = []
    districts_list = []
    for office in offices:
        office_data = {
            'agri_office_id': office.agri_office_id,
            'name': office.name,
            'city': office.city,
            'province': office.province,
            'district': office.district
        }
        offices_list.append(office_data)
        if office.district not in districts_list:
            districts_list.append(office.district)
    return jsonify({'offices': offices_list, 'districts': districts_list})

@report_routes.route('/farmer/total_count-by-district', methods=['GET'])
def get_farmer_count_by_district():
    district = request.args.get('district')

    query = db.session.query(
        AgriOffice.district,
        func.count(User.user_id)
    ).join(
        Farmer, User.user_id == Farmer.user_id
    ).join(
        AgriOffice, AgriOffice.agri_office_id == Farmer.assigned_office_id
    )

    if district:
        query = query.filter(AgriOffice.district == district)

    user_counts = query.group_by(AgriOffice.district).all()

    return jsonify({district: count for district, count in user_counts})

@report_routes.route('/users/farmer/count-by-district-and-province', methods=['GET'])
def get_total_user_count_by_district_and_province():
    province = request.args.get('province')
    district = request.args.get('district')

    if not province or not district:
        return jsonify({'error': 'Both province and district must be provided'}), 400

    user_counts = db.session.query(
        AgriOffice.name,
        func.count(User.user_id)
    ).join(
        Farmer, User.user_id == Farmer.user_id
    ).join(
        AgriOffice, AgriOffice.agri_office_id == Farmer.assigned_office_id
    ).filter(
        AgriOffice.province == province,
        AgriOffice.district == district
    ).group_by(
        AgriOffice.name
    ).all()

    
    return jsonify({office_name: count for office_name, count in user_counts})

@report_routes.route('/search_farmers', methods=['GET'])
def search_farmers():
    # Get the search parameters from the query string
    office_id = request.args.get('assigned_office_id')
    tax_file_no = request.args.get('tax_file_no')
    field_area_id = request.args.get('assigned_field_area_id')
    user_id = request.args.get('user_id')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    result=search_existing_farmers_By_Append(office_id, tax_file_no, field_area_id, user_id, page, per_page)
        # Return the result as JSON
    return jsonify(result)

@report_routes.route('/search_tax/acre_tax', methods=['GET'])
def get_farmer_tax_payer_count_by_district_year_office():
    district = request.args.get('district')
    office_id = request.args.get('office_id')

    # Start the query
    query = db.session.query(AgriOffice.district, func.count(Farmer.user_id)).join(AgriOffice, Farmer.assigned_office_id == AgriOffice.agri_office_id).filter(AgriOffice.district == district)

    # If office_id is not an empty string, add it to the filter
    if office_id != '':
        query = query.filter(Farmer.assigned_office_id == office_id)

    # Add the tax_file_no filter and group by district
    data = query.filter(Farmer.tax_file_no.isnot(None)).group_by(AgriOffice.district).all()

    chart_data = [{'district': district, 'farmer_count': count} for district, count in data]
    # Return the data as a response
    return jsonify(chart_data)

@report_routes.route('/search_tax/all_acre_tax', methods=['GET'])
def get_all_tax_payer_group_by_district():
    query = db.session.query(AgriOffice.district, func.count(Farmer.user_id)).join(AgriOffice, Farmer.assigned_office_id == AgriOffice.agri_office_id)

    # Add the tax_file_no filter and group by district
    data = query.filter(Farmer.tax_file_no.isnot(None)).group_by(AgriOffice.district).all()

    chart_data = [{'district': district, 'farmer_count': count} for district, count in data]
    # Return the data as a response
    return jsonify(chart_data)

@report_routes.route('/offices/by-district', methods=['GET'])
def get_offices_by_district():
    district = request.args.get('district')
    if not district:
        return jsonify({'error': 'District parameter is missing'})
    
    offices = AgriOffice.query.filter(AgriOffice.district == district).all()
    offices_list = []
    for office in offices:
        office_data = {
            'agri_office_id': office.agri_office_id,
            'name': office.name,
            'city': office.city,
            'province': office.province,
            'district': office.district
        }
        offices_list.append(office_data)
    
    return jsonify({'offices': offices_list})

@report_routes.route('/officers-by-office', methods=['GET'])
def get_officers_by_office():
    office_id = request.args.get('office_id')
    if not office_id:
        return jsonify({'error': 'Office ID parameter is missing'})
    
    officers = db.session.query(
        AgricultureOfficer.user_id,
        AgricultureOfficer.employee_id,
        AgricultureOfficer.managed_by_employee_id,
        AgricultureOfficer.agri_office_id,
        AgricultureOfficer.service_start_date,
        AgricultureOfficer.field_area_id,
        User.email,
        User.first_name,
    ).join(
        User, User.user_id == AgricultureOfficer.user_id
    ).filter(
        AgricultureOfficer.agri_office_id == office_id
    ).all()

    officers_list = [{'user_id': user_id, 'employee_id': employee_id, 'managed_by_employee_id': managed_by_employee_id, 'agri_office_id': agri_office_id, 'service_start_date': service_start_date, 'field_area_id': field_area_id, 'email': email, 'first_name': first_name} for user_id, employee_id, managed_by_employee_id, agri_office_id, service_start_date, field_area_id, email, first_name in officers]
    return jsonify({'officers': officers_list})

# @report_routes.route('/ads/monthly', methods=['GET'])
# def get_monthly_ads_distributions( ):
#     year = request.args.get('year')
#     description = request.args.get('type')
#     fertilizer_distributions = db.session.query(
#         extract('month', AidDistribution.date).label('month'),
#         func.sum(AidDistribution.amount_approved).label('total_amount_approved')
#     ).filter(
#         AidDistribution.description == description,
#         extract('year', AidDistribution.date) == year
#     ).group_by(
#         'month'
#     ).order_by(
#         'month'
#     ).all()

#     # Initialize a list with 12 dictionaries, one for each month
#     monthly_fertilizer_distributions = [{'month': month, 'total_amount_approved': 0.0} for month in range(1, 13)]

#     # Update the dictionaries with the actual data
#     for distribution in fertilizer_distributions:
#         # The month in the distribution record is 1-based, so subtract 1 to get the 0-based index
#         index = int(distribution.month) - 1

#         # Update the total_amount_approved for the month
#         monthly_fertilizer_distributions[index]['total_amount_approved'] = float(distribution.total_amount_approved)

#     return jsonify(monthly_fertilizer_distributions)

@report_routes.route('/ads/monthly', methods=['GET'])
def get_monthly_ads_officer_distributions():
    year = request.args.get('year')
    crop_id = request.args.get('crop_id')
    monthly_advertisements = db.session.query(
        extract('month', Advertisement.date).label('month'),
        func.count(Advertisement.ad_id).label('total_ads')
    ).filter(
        extract('year', Advertisement.date) == year,
        Advertisement.crop_id == crop_id
    ).group_by(
        'month'
    ).order_by(
        'month'
    ).all()

    # Initialize a list with 12 dictionaries, one for each month
    monthly_advertisements_counts = [{'month': month, 'total_ads': 0} for month in range(1, 13)]

    # Update the dictionaries with the actual data
    for ad in monthly_advertisements:
        # The month in the ad record is 1-based, so subtract 1 to get the 0-based index
        index = int(ad.month) - 1

        # Update the total_ads for the month
        monthly_advertisements_counts[index]['total_ads'] = ad.total_ads

    return jsonify(monthly_advertisements_counts)