import datetime

def parse_date(date_str, date_format='%Y-%m-%d'):
    try:
        return datetime.datetime.strptime(date_str, date_format).date()
    except ValueError:
        return datetime.datetime.strptime(date_str,  '%Y-%m-%dT%H:%M:%S.%fZ').date()

# Usage:
# dob = request.json['dob']
# parsed_dob = parse_date(dob, '%Y-%m-%d')
