from backend.models import RAKE_TYPES, STATION_CONFIG, TRAIN_JOURNEYS


def get_train_journey(train_number):
    """Retrieve static journey info for a train"""
    return TRAIN_JOURNEYS.get(train_number)

def get_coach_position(train_number, coach_id, station_code=None):
    """
    Compute coach position relative to the platform front/middle/rear.
    """
    # Determine Rake Type
    if train_number.startswith(('22', '12')):
        rake_key = "LHB_REGULAR"
        if train_number in ['12951', '12952', '22691', '22692', '12301', '12302']:
            rake_key = "LHB_PREMIUM"
    else:
        rake_key = "ICF_EXPRESS"
    
    rake = RAKE_TYPES.get(rake_key, RAKE_TYPES["ICF_EXPRESS"])
    coach_type = ''.join([i for i in coach_id if not i.isdigit()]).upper()
    
    try:
        # 1. Determine Coach Zone relative to Engine
        index = -1
        for i, c in enumerate(rake):
            if c == coach_id.upper():
                index = i
                break
        
        if index == -1:
            for i, c in enumerate(rake):
                if c.startswith(coach_type):
                    index = i
                    break
        
        if index == -1: return None
            
        total_coaches = len(rake)
        relative_pos = index / total_coaches
        
        if relative_pos < 0.33: train_zone = "front"
        elif relative_pos < 0.66: train_zone = "middle"
        else: train_zone = "rear"
            
        # 2. Journey and Direction Lookup
        journey = get_train_journey(train_number)
        direction_msg = "standard direction"
        engine_at_front = True # Default
        
        if journey and station_code:
            origin = journey['origin']
            dest = journey['destination']
            direction_msg = f"heading from {origin} to {dest}"
            
            st_cfg = STATION_CONFIG.get(station_code.upper(), {'engine_at_entry': True})
            engine_at_front = st_cfg['engine_at_entry']
        
        # 3. Map Train Zone to Platform Position
        zone_map = {"front": "front", "middle": "middle", "rear": "rear"}
        if not engine_at_front:
            zone_map = {"front": "rear", "middle": "middle", "rear": "front"}
            
        platform_zone = zone_map[train_zone]
        
        # Visuals and Explanation
        emoji_map = {"front": "🟢", "middle": "🟡", "rear": "🔴"}
        ascii_map = {
            "front": "[COACH] --------",
            "middle": "-------- [COACH] --------",
            "rear": "-------- [COACH]"
        }
        
        explanation = f"Your coach {coach_id.upper()} is in the {platform_zone} part of the train."
        if platform_zone == "front":
            explanation += " Look for the engine; your coach will be nearby."
        elif platform_zone == "rear":
            explanation += " Your coach will be towards the end of the platform."
        else:
            explanation += " Wait near the center of the platform."

        # 4. Navigation (Left/Right + Distance)
        # Assuming user enters from a central point or main gate.
        # Orientation: Platform Front = LEFT, Platform Rear = RIGHT.
        if engine_at_front:
            # Engine is at Front (LEFT). 
            # Train Front = Platform Front.
            move_dir = "LEFT" if train_zone == "front" else "RIGHT" if train_zone == "rear" else "CENTER"
        else:
            # Engine is at Rear (RIGHT).
            # Train Front = Platform Rear.
            move_dir = "RIGHT" if train_zone == "front" else "LEFT" if train_zone == "rear" else "CENTER"
            
        dist = "50m" if platform_zone == "front" else "250m" if platform_zone == "middle" else "450m"
        
        if platform_zone == "middle":
            nav_instruction = f"Wait near the CENTER (approx. {dist} from entrance)"
        else:
            nav_instruction = f"Move {move_dir} (approx. {dist} walk)"

        return {
            "position": platform_zone,
            "train_zone": train_zone,
            "emoji": emoji_map[platform_zone],
            "ascii": ascii_map[platform_zone],
            "instruction": explanation,
            "explanation": explanation,
            "journey": journey,
            "direction": nav_instruction,
            "move_direction": move_dir,
            "distance": dist,
            "tip": f"At {station_code}, the engine usually stops at the {'front' if engine_at_front else 'rear'} end.",
            "coach_layout": rake,
            "engine_at_front": engine_at_front
        }
        
    except Exception:
        return None
