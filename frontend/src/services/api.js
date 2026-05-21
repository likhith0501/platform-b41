// Frontend-only mode: no backend calls.
// This module provides the same API surface expected by App.jsx.

const MAJOR_JUNCTIONS = {
  NDLS: 'New Delhi',
  DLI: 'Delhi',
  ASR: 'Amritsar',
  JAT: 'Jammu Tawi',
  CDG: 'Chandigarh',
  LKO: 'Lucknow',
  JP: 'Jaipur',
  HWH: 'Howrah',
  PNBE: 'Patna',
  BBS: 'Bhubaneswar',
  GHY: 'Guwahati',
  BCT: 'Mumbai Central',
  CSMT: 'Chhatrapati Shivaji Maharaj Terminus',
  ADI: 'Ahmedabad',
  PUNE: 'Pune',
  MAS: 'Chennai Central',
  SBC: 'Bengaluru City',
  SC: 'Secunderabad',
  TVC: 'Thiruvananthapuram',
  ERS: 'Ernakulam',
  BPL: 'Bhopal',
  NGP: 'Nagpur',
};

const COACH_LAYOUT_PRESET = [
  'LOCO',
  'H1', 'H2', 'H3',
  'A1', 'A2', 'A3',
  'B3', 'B4', 'B5',
  'S6', 'S7',
  'CC1', 'CC2',
  'S8',
];

function stableHash(input) {
  // Deterministic small hash for stable visuals.
  let h = 2166136261;
  const s = String(input);
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return Math.abs(h);
}

function normalizeCoachId(coach) {
  const c = String(coach || '').trim();
  return c.toUpperCase();
}

function coachTypeFromId(coachId) {
  const upper = normalizeCoachId(coachId);
  const coachType = upper.replace(/[0-9]/g, '').toUpperCase();
  const coachTypesMap = {
    H: 'AC 1st Class',
    A: 'AC 2nd Class',
    B: 'AC 3rd Class',
    M: 'AC 3rd Economy',
    S: 'Sleeper Class',
    GS: 'General',
    UR: 'Unreserved',
    CC: 'AC Chair Car',
    EC: 'Exec. Chair Car',
  };
  return coachTypesMap[coachType] || 'Express Coach';
}

function engineAtFrontForStation(stationCode) {
  // Simple deterministic rule so visuals differ across stations.
  const code = String(stationCode || '').toUpperCase();
  const h = stableHash(code);
  return h % 2 === 0;
}

function computePosition({ trainNumber, coach, station }) {
  const train = String(trainNumber || '').trim();
  const coachId = normalizeCoachId(coach);
  const stationCode = String(station || '').trim().toUpperCase();

  if (!train || !coachId || !stationCode) return null;

  const engine_at_front = engineAtFrontForStation(stationCode);

  // Build a deterministic coach layout around a preset so
  // highlighted_coach always exists.
  const base = [...COACH_LAYOUT_PRESET];
  if (!base.includes(coachId)) base.splice(6, 0, coachId);

  // Ensure LOCO exists at index 0 for the layout strip logic.
  if (base[0] !== 'LOCO') {
    const idx = base.indexOf('LOCO');
    if (idx >= 0) {
      base.splice(idx, 1);
      base.unshift('LOCO');
    }
  }

  const total = base.length;
  const idx = Math.max(0, base.findIndex((c) => c === coachId));
  const relative = idx / Math.max(1, total);

  let train_zone = 'middle';
  if (relative < 0.33) train_zone = 'front';
  else if (relative >= 0.66) train_zone = 'rear';

  // Map train zone to platform zone based on engine side.
  const zone_map = { front: 'front', middle: 'middle', rear: 'rear' };
  const platform_zone = engine_at_front ? zone_map[train_zone] : zone_map[train_zone] === 'front' ? 'rear' : zone_map[train_zone] === 'rear' ? 'front' : 'middle';

  const pos = platform_zone;

  const emoji_map = { front: '🟢', middle: '🟡', rear: '🔴' };
  const ascii_map = {
    front: '[COACH] --------',
    middle: '-------- [COACH] --------',
    rear: '-------- [COACH]',
  };

  let explanation = `Your coach ${coachId} is in the ${pos} part of the train.`;
  if (pos === 'front') explanation += ' Look for the engine; your coach will be nearby.';
  else if (pos === 'rear') explanation += ' Your coach will be towards the end of the platform.';
  else explanation += ' Wait near the center of the platform.';

  let move_direction = 'CENTER';
  if (engine_at_front) {
    move_direction = pos === 'front' ? 'LEFT' : pos === 'rear' ? 'RIGHT' : 'CENTER';
  } else {
    move_direction = pos === 'front' ? 'RIGHT' : pos === 'rear' ? 'LEFT' : 'CENTER';
  }

  const dist = pos === 'front' ? '50m' : pos === 'middle' ? '250m' : '450m';
  const direction = pos === 'middle'
    ? `Wait near the CENTER (approx. ${dist} from entrance)`
    : `Move ${move_direction} (approx. ${dist} walk)`;

  return {
    position: pos,
    train_zone,
    emoji: emoji_map[pos],
    ascii: ascii_map[pos],
    instruction: explanation,
    explanation,
    journey: null,
    direction,
    move_direction,
    distance: dist,
    tip: `At ${stationCode}, the engine usually stops at the ${engine_at_front ? 'front' : 'rear'} end.`,
    coach_layout: base,
    engine_at_front,
  };
}

export const fetchStations = async () => {
  const major = Object.entries(MAJOR_JUNCTIONS).map(([code, name]) => ({ code, name }));
  return { major_stations: major };
};

export const fetchPosition = async (trainNumber, coach, station) => {
  const stationCode = String(station || '').trim().toUpperCase();
  const pos_data = computePosition({ trainNumber, coach, station: stationCode });
  if (!pos_data) throw new Error('Could not find position for this combination');

  const station_name = MAJOR_JUNCTIONS[stationCode] || stationCode;

  return {
    train: {
      number: String(trainNumber),
      name: `Train ${trainNumber}`,
    },
    station: { code: stationCode, name: station_name },
    coach: {
      id: normalizeCoachId(coach),
      type: coachTypeFromId(coach),
    },
    platform_position: pos_data,
    coach_layout: pos_data.coach_layout,
    highlighted_coach: normalizeCoachId(coach),
    highlighted_zone: pos_data.position,
  };
};

// Not used by current App.jsx, but kept to avoid breaking public API.
export const fetchGuide = async (trainNumber, coach, station) => {
  const data = await fetchPosition(trainNumber, coach, station);
  return {
    train_number: data.train.number,
    train_name: data.train.name,
    station_code: data.station.code,
    station_name: data.station.name,
    coach_id: data.coach.id,
    platform_position: data.platform_position.position,
    emoji: data.platform_position.emoji,
    ascii_marker: data.platform_position.ascii,
    instruction: data.platform_position.instruction,
    tip: data.platform_position.tip,
  };
};

