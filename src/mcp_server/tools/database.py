"""
Generic database tools for MCP server.

Three simple tools that let AI explore and query any mapped data:
1. list_entities() - What data is available?
2. describe_entity(entity) - What fields does it have?
3. query_entity(entity, ...) - Get the data

All queries are READ-ONLY. Write operations go through API/webhooks.
"""

from typing import Optional

from ..data_adapter import get_adapter


def list_entities() -> dict:
    """
    List all available data entities.

    Returns:
        Dictionary with available entity types and their descriptions
    """
    adapter = get_adapter()

    # Get configured entities from mapping
    configured = adapter.get_configured_entities()

    # Standard entity descriptions
    descriptions = {
        "pilots": "Pilot certifications and credentials",
        "aircraft": "Aircraft registration and status",
        "flights": "Flight logs and telemetry",
        "missions": "Mission planning data",
        "maintenance_records": "Aircraft maintenance history",
    }

    entities = {}
    for name in configured:
        entities[name] = descriptions.get(name, f"{name} data")

    if not entities:
        return {
            "entities": {},
            "message": "No entities configured. Run 'uavcrew map-data' to set up data mapping.",
        }

    return {"entities": entities}


def describe_entity(entity: str) -> dict:
    """
    Describe the fields available for an entity.

    Args:
        entity: Entity name (pilots, aircraft, flights, etc.)

    Returns:
        Dictionary with field names and descriptions
    """
    adapter = get_adapter()
    config = adapter.get_entity_config(entity)

    if not config:
        available = adapter.get_configured_entities()
        return {
            "error": f"Entity '{entity}' not configured",
            "available_entities": available,
        }

    columns = config.get("columns", {})

    # Standard field descriptions
    field_descriptions = {
        # Pilots
        "id": "Unique identifier",
        "name": "Full name",
        "certificate_type": "Certificate type (Part 107, Part 61, etc.)",
        "certificate_number": "FAA certificate number",
        "certificate_expiry": "Certificate expiration date",
        "certificate_valid": "Whether certificate is currently valid",
        "waivers": "List of waivers held",
        "flight_hours_90_days": "Flight hours in last 90 days",
        "total_flight_hours": "Total career flight hours",
        # Aircraft
        "registration": "FAA registration number (N-number)",
        "make_model": "Aircraft make and model",
        "serial_number": "Manufacturer serial number",
        "registration_expiry": "Registration expiration date",
        "registration_valid": "Whether registration is currently valid",
        "last_maintenance_date": "Date of last maintenance",
        "hours_since_maintenance": "Flight hours since last maintenance",
        "maintenance_interval_hours": "Required maintenance interval",
        "battery_cycles": "Battery charge cycles",
        "firmware_version": "Current firmware version",
        # Flights
        "pilot_id": "Pilot identifier",
        "aircraft_id": "Aircraft identifier",
        "flight_datetime": "Flight date and time",
        "duration_seconds": "Flight duration in seconds",
        "max_altitude_ft": "Maximum altitude reached (feet)",
        "max_speed_mph": "Maximum speed reached (mph)",
        "takeoff_lat": "Takeoff latitude",
        "takeoff_lon": "Takeoff longitude",
        # Missions
        "flight_id": "Associated flight identifier",
        "purpose": "Mission purpose",
        "client_name": "Client name",
        "location_name": "Location name",
        "location_lat": "Location latitude",
        "location_lon": "Location longitude",
        "airspace_class": "Airspace classification",
        "laanc_required": "Whether LAANC authorization required",
        "laanc_authorization_id": "LAANC authorization ID",
        "planned_altitude_ft": "Planned altitude (feet)",
        "planned_duration_min": "Planned duration (minutes)",
        # Maintenance
        "date": "Maintenance date",
        "type": "Maintenance type",
        "description": "Maintenance description",
        "technician": "Technician name",
        "hours_at_service": "Aircraft hours at time of service",
        "reason": "Reason for maintenance",
    }

    fields = {}
    for field_name in columns.keys():
        fields[field_name] = field_descriptions.get(field_name, field_name)

    return {
        "entity": entity,
        "fields": fields,
        "source_table": config.get("source_table"),
    }


def query_entity(
    entity: str,
    id: Optional[str] = None,
    filters: Optional[dict] = None,
    fields: Optional[list[str]] = None,
    limit: int = 100,
) -> dict:
    """
    Query data from an entity.

    Args:
        entity: Entity name (pilots, aircraft, flights, etc.)
        id: Optional - get single record by ID
        filters: Optional - filter conditions as {field: value}
        fields: Optional - specific fields to return (default: all)
        limit: Maximum records to return (default: 100)

    Returns:
        Query results
    """
    adapter = get_adapter()

    if not adapter.is_entity_configured(entity):
        available = adapter.get_configured_entities()
        return {
            "error": f"Entity '{entity}' not configured",
            "available_entities": available,
        }

    # Single record by ID
    if id is not None:
        result = adapter.query_one(entity, id)
        if result:
            if fields:
                result = {k: v for k, v in result.items() if k in fields}
            return {"data": result}
        return {"data": None, "message": f"No {entity} found with id '{id}'"}

    # Build WHERE clause from filters
    where_clause = None
    where_params = {}

    if filters:
        conditions = []
        for i, (field, value) in enumerate(filters.items()):
            param_name = f"p{i}"
            conditions.append(f"{field} = :{param_name}")
            where_params[param_name] = value
        where_clause = " AND ".join(conditions)

    # Query multiple records
    results = adapter.query_many(
        entity,
        where_clause=where_clause,
        where_params=where_params,
        limit=limit,
    )

    # Filter fields if specified
    if fields and results:
        results = [
            {k: v for k, v in row.items() if k in fields}
            for row in results
        ]

    return {
        "data": results,
        "count": len(results),
        "limit": limit,
    }
