"""Aircraft data tool for MCP server."""

from sqlalchemy.orm import Session

from ..database.models import Aircraft


def get_aircraft(db: Session, aircraft_id: str) -> dict:
    """
    Retrieve aircraft registration and status.

    Args:
        db: Database session
        aircraft_id: Aircraft ID or FAA registration

    Returns:
        Aircraft data including registration and maintenance status
    """
    # Try to find by ID first, then by registration
    aircraft = db.query(Aircraft).filter(Aircraft.id == aircraft_id).first()
    if not aircraft:
        aircraft = db.query(Aircraft).filter(Aircraft.registration == aircraft_id).first()

    if not aircraft:
        return {"error": f"Aircraft not found: {aircraft_id}"}

    return {
        "aircraft_id": aircraft.id,
        "registration": aircraft.registration,
        "make_model": aircraft.make_model,
        "serial_number": aircraft.serial_number,
        "registration_expiry": aircraft.registration_expiry.isoformat(),
        "registration_valid": aircraft.registration_valid,
        "total_flight_hours": aircraft.total_flight_hours,
        "last_maintenance_date": aircraft.last_maintenance_date.isoformat(),
        "hours_since_maintenance": aircraft.hours_since_maintenance,
        "maintenance_interval_hours": aircraft.maintenance_interval_hours,
        "battery_cycles": aircraft.battery_cycles,
        "firmware_version": aircraft.firmware_version,
    }
