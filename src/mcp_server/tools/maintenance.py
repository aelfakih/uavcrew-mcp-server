"""Maintenance history tool for MCP server."""

import json
from sqlalchemy.orm import Session

from ..database.models import MaintenanceRecord, Aircraft


def get_maintenance_history(db: Session, aircraft_id: str, limit: int = 10) -> dict:
    """
    Retrieve maintenance records for an aircraft.

    Args:
        db: Database session
        aircraft_id: Aircraft identifier
        limit: Maximum number of records to return

    Returns:
        Maintenance history including recent records and component status
    """
    # Get aircraft first for component hours calculation
    aircraft = db.query(Aircraft).filter(Aircraft.id == aircraft_id).first()
    if not aircraft:
        # Try by registration
        aircraft = db.query(Aircraft).filter(Aircraft.registration == aircraft_id).first()

    if not aircraft:
        return {"error": f"Aircraft not found: {aircraft_id}"}

    # Get maintenance records
    records = (
        db.query(MaintenanceRecord)
        .filter(MaintenanceRecord.aircraft_id == aircraft.id)
        .order_by(MaintenanceRecord.date.desc())
        .limit(limit)
        .all()
    )

    maintenance_records = []
    for record in records:
        maintenance_records.append({
            "date": record.date.isoformat(),
            "type": record.type,
            "description": record.description,
            "components_serviced": json.loads(record.components_serviced) if record.components_serviced else [],
            "components_replaced": json.loads(record.components_replaced) if record.components_replaced else [],
            "technician": record.technician,
            "hours_at_service": record.hours_at_service,
            "reason": record.reason,
        })

    # Calculate component hours (simplified - in production would track per component)
    hours_since_last_service = aircraft.hours_since_maintenance

    return {
        "aircraft_id": aircraft.id,
        "total_flight_hours": aircraft.total_flight_hours,
        "hours_since_maintenance": hours_since_last_service,
        "maintenance_interval_hours": aircraft.maintenance_interval_hours,
        "maintenance_due_in_hours": aircraft.maintenance_interval_hours - hours_since_last_service,
        "maintenance_records": maintenance_records,
        "known_issues": [],  # Would come from issue tracking in production
        "component_hours": {
            "airframe": aircraft.total_flight_hours,
            "battery": aircraft.battery_cycles,  # cycles not hours
            "motors": hours_since_last_service,  # assumes motors replaced at service
        },
    }
