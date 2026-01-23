"""Flight log tool for MCP server."""

import json
from sqlalchemy.orm import Session

from ..database.models import Flight


def get_flight_log(db: Session, flight_id: str) -> dict:
    """
    Retrieve parsed flight log data.

    Args:
        db: Database session
        flight_id: Unique flight identifier

    Returns:
        Flight log data including telemetry, events, and summary
    """
    flight = db.query(Flight).filter(Flight.id == flight_id).first()

    if not flight:
        return {"error": f"Flight not found: {flight_id}"}

    return {
        "flight_id": flight.id,
        "pilot_id": flight.pilot_id,
        "aircraft_id": flight.aircraft_id,
        "log_format": flight.log_format,
        "flight_datetime": flight.flight_datetime.isoformat(),
        "duration_seconds": flight.duration_seconds,
        "telemetry": json.loads(flight.telemetry_json) if flight.telemetry_json else [],
        "events": json.loads(flight.events_json) if flight.events_json else [],
        "summary": json.loads(flight.summary_json) if flight.summary_json else {},
    }
