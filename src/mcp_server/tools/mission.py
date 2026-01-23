"""Mission data tool for MCP server."""

import json
from sqlalchemy.orm import Session

from ..database.models import Mission


def get_mission(db: Session, flight_id: str) -> dict:
    """
    Retrieve mission planning data.

    Args:
        db: Database session
        flight_id: Flight identifier

    Returns:
        Mission data including location, airspace, and LAANC status
    """
    mission = db.query(Mission).filter(Mission.flight_id == flight_id).first()

    if not mission:
        return {"error": f"Mission not found for flight: {flight_id}"}

    return {
        "mission_id": mission.id,
        "flight_id": mission.flight_id,
        "purpose": mission.purpose,
        "client_name": mission.client_name,
        "location_name": mission.location_name,
        "location_coords": [mission.location_lat, mission.location_lon],
        "airspace_class": mission.airspace_class,
        "laanc_required": mission.laanc_required,
        "laanc_authorization_id": mission.laanc_authorization_id,
        "planned_altitude_ft": mission.planned_altitude_ft,
        "planned_duration_min": mission.planned_duration_min,
        "planned_route": json.loads(mission.planned_route_json) if mission.planned_route_json else [],
        "geofence": json.loads(mission.geofence_json) if mission.geofence_json else [],
    }
