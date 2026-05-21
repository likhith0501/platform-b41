from flask import Blueprint, request, jsonify
from backend.services.composition_service import get_coach_position
from backend.models import MAJOR_JUNCTIONS
from backend.auth import require_api_key


bp = Blueprint('platform', __name__, url_prefix='/api')

@bp.route('/platformposition', methods=['GET'])
@require_api_key
def get_position():
    train_number = request.args.get('train_number')
    coach = request.args.get('coach')
    station_code = request.args.get('station')

    if not train_number or not coach or not station_code:
        return jsonify({'error': 'train_number, coach, and station are required'}), 400

    pos_data = get_coach_position(train_number, coach, station_code=station_code)

    if not pos_data:
        return jsonify({'error': 'Could not determine position'}), 404

    station_name = MAJOR_JUNCTIONS.get(station_code.upper(), station_code)
    
    coach_type = ''.join([i for i in coach if not i.isdigit()]).upper()
    coach_types_map = {
        'H': 'AC 1st Class', 'A': 'AC 2nd Class', 'B': 'AC 3rd Class',
        'M': 'AC 3rd Economy', 'S': 'Sleeper Class', 'GS': 'General',
        'UR': 'Unreserved', 'CC': 'AC Chair Car', 'EC': 'Exec. Chair Car'
    }
    
    response = {
        'train': {
            'number': train_number,
            'name': (pos_data.get('journey') or {}).get('name', f"Train {train_number}")
        },
        'station': {'code': station_code.upper(), 'name': station_name},
        'coach': {'id': coach.upper(), 'type': coach_types_map.get(coach_type, "Express Coach")},
        'platform_position': pos_data,
        'coach_layout': pos_data.get('coach_layout', []),
        'highlighted_coach': coach.upper(),
        'highlighted_zone': pos_data['position']
    }
    return jsonify(response), 200

@bp.route('/platformguide/<train_number>/<coach_id>/<station_code>', methods=['GET'])
@require_api_key
def get_guide(train_number, coach_id, station_code):
    pos_data = get_coach_position(train_number, coach_id, station_code=station_code)
    if not pos_data:
        return jsonify({'error': 'Invalid combination'}), 404
        
    return jsonify({
        'train_number': train_number,
        'train_name': (pos_data.get('journey') or {}).get('name', f"Train {train_number}"),
        'station_code': station_code.upper(),
        'station_name': MAJOR_JUNCTIONS.get(station_code.upper(), station_code),
        'coach_id': coach_id.upper(),
        'platform_position': pos_data['position'],
        'emoji': pos_data['emoji'],
        'ascii_marker': pos_data['ascii'],
        'instruction': pos_data['instruction'],
        'tip': pos_data['tip']
    }), 200
