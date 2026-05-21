from backend.models import MAJOR_JUNCTIONS, TRAIN_JOURNEYS


class RailwayService:
    @staticmethod
    def get_station_code(name_or_code):
        name_or_code = name_or_code.upper()
        if name_or_code in MAJOR_JUNCTIONS:
            return name_or_code
        for code, name in MAJOR_JUNCTIONS.items():
            if name_or_code in name.upper():
                return code
        return name_or_code

    @staticmethod
    def search_trains(source, destination, date=None):
        # Mock search based on static data
        trains = []
        for number, info in TRAIN_JOURNEYS.items():
            if source in info['stops'] and destination in info['stops']:
                # Ensure source comes before destination
                if info['stops'].index(source) < info['stops'].index(destination):
                    trains.append({
                        'train_number': number,
                        'name': info['name'],
                        'departure': '10:00',
                        'arrival': '18:00',
                        'duration': '8h 0m'
                    })
        return {'trains': trains}

    @staticmethod
    def get_train_details(train_number):
        info = TRAIN_JOURNEYS.get(train_number)
        if info:
            return {
                'train_number': train_number,
                'name': info['name'],
                'origin': info['origin'],
                'destination': info['destination'],
                'stops': info['stops']
            }
        return {'error': 'Train not found'}
