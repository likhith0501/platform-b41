from flask import Blueprint, request, jsonify
from backend.services.railway_service import RailwayService
from backend.models import MAJOR_JUNCTIONS
from backend.auth import require_api_key


bp = Blueprint('trains', __name__, url_prefix='/api/trains')

@bp.route('/search', methods=['GET'])
@require_api_key
def search_trains():
    source = request.args.get('source')
    destination = request.args.get('destination')
    if not source or not destination:
        return jsonify({'error': 'source and destination are required'}), 400
    
    source_code = RailwayService.get_station_code(source)
    dest_code = RailwayService.get_station_code(destination)
    result = RailwayService.search_trains(source_code, dest_code)
    return jsonify(result), 200

@bp.route('/details/<train_number>', methods=['GET'])
@require_api_key
def get_train_details(train_number):
    result = RailwayService.get_train_details(train_number)
    return jsonify(result), 200

@bp.route('/stations', methods=['GET'])
@require_api_key
def list_stations():
    stations = [{'code': code, 'name': name} for code, name in MAJOR_JUNCTIONS.items()]
    return jsonify({'major_stations': stations}), 200
