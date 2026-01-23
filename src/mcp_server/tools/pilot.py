"""Pilot data tool for MCP server."""

import json
from sqlalchemy.orm import Session

from ..database.models import Pilot


def get_pilot(db: Session, pilot_id: str) -> dict:
    """
    Retrieve pilot certification and credentials.

    Args:
        db: Database session
        pilot_id: Pilot identifier or certificate number

    Returns:
        Pilot data including certification status
    """
    # Try to find by ID first, then by certificate number
    pilot = db.query(Pilot).filter(Pilot.id == pilot_id).first()
    if not pilot:
        pilot = db.query(Pilot).filter(Pilot.certificate_number == pilot_id).first()

    if not pilot:
        return {"error": f"Pilot not found: {pilot_id}"}

    return {
        "pilot_id": pilot.id,
        "name": pilot.name,
        "certificate_type": pilot.certificate_type,
        "certificate_number": pilot.certificate_number,
        "certificate_expiry": pilot.certificate_expiry.isoformat(),
        "certificate_valid": pilot.certificate_valid,
        "waivers": json.loads(pilot.waivers) if pilot.waivers else [],
        "flight_hours_90_days": pilot.flight_hours_90_days,
        "total_flight_hours": pilot.total_flight_hours,
    }
