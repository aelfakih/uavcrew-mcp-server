# MCP Server Data Formats

This document describes the data formats expected and returned by the MCP server tools.

---

## get_flight_log

Retrieves flight telemetry and events for a specific flight.

### Request
```json
{
  "flight_id": "FLT-2025-001"
}
```

### Response
```json
{
  "flight_id": "FLT-2025-001",
  "pilot_id": "PLT-001",
  "aircraft_id": "AC-001",
  "log_format": "ardupilot_bin",
  "flight_datetime": "2025-01-07T14:30:00Z",
  "duration_seconds": 1500,
  "telemetry": [
    {
      "timestamp": "2025-01-07T14:30:05Z",
      "latitude": 37.7749,
      "longitude": -122.4194,
      "altitude_agl_ft": 150,
      "altitude_msl_ft": 180,
      "ground_speed_mph": 25,
      "heading_deg": 180,
      "battery_percent": 95,
      "battery_voltage": 22.4,
      "gps_satellites": 14,
      "gps_hdop": 0.9
    }
  ],
  "events": [
    {
      "timestamp": "2025-01-07T14:30:00Z",
      "type": "ARM",
      "details": {}
    },
    {
      "timestamp": "2025-01-07T14:30:05Z",
      "type": "TAKEOFF",
      "details": {"altitude_ft": 0}
    },
    {
      "timestamp": "2025-01-07T14:55:00Z",
      "type": "LAND",
      "details": {}
    }
  ],
  "summary": {
    "duration_seconds": 1500,
    "distance_km": 2.4,
    "max_altitude_ft": 355,
    "avg_altitude_ft": 280,
    "max_speed_mph": 35,
    "min_battery_percent": 32
  }
}
```

### Telemetry Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `timestamp` | ISO8601 | Yes | UTC timestamp |
| `latitude` | float | Yes | Decimal degrees (-90 to 90) |
| `longitude` | float | Yes | Decimal degrees (-180 to 180) |
| `altitude_agl_ft` | float | Yes | Altitude above ground level in feet |
| `altitude_msl_ft` | float | No | Altitude above mean sea level |
| `ground_speed_mph` | float | No | Ground speed in mph |
| `heading_deg` | float | No | Heading in degrees (0-360) |
| `battery_percent` | float | Yes | Battery remaining (0-100) |
| `battery_voltage` | float | No | Battery voltage |
| `gps_satellites` | int | Yes | Number of GPS satellites |
| `gps_hdop` | float | No | Horizontal dilution of precision |

### Event Types

| Type | Description |
|------|-------------|
| `ARM` | Motors armed |
| `DISARM` | Motors disarmed |
| `TAKEOFF` | Aircraft took off |
| `LAND` | Aircraft landed |
| `MODE_CHANGE` | Flight mode changed |
| `ALTITUDE_WARNING` | Altitude limit approached/exceeded |
| `FENCE_BREACH` | Geofence boundary crossed |
| `FAILSAFE_BATTERY` | Low battery failsafe triggered |
| `FAILSAFE_GPS` | GPS failsafe triggered |
| `RTL` | Return to launch initiated |

---

## get_pilot

Retrieves pilot certification and credentials.

### Request
```json
{
  "pilot_id": "PLT-001"
}
```

### Response
```json
{
  "pilot_id": "PLT-001",
  "name": "John Smith",
  "certificate_type": "Part 107",
  "certificate_number": "4123456",
  "certificate_expiry": "2026-05-15",
  "certificate_valid": true,
  "waivers": ["Night Operations", "BVLOS"],
  "flight_hours_90_days": 45.5,
  "total_flight_hours": 234.0
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `pilot_id` | string | Yes | Unique pilot identifier |
| `name` | string | Yes | Pilot name |
| `certificate_type` | string | Yes | "Part 107", "Part 61", "Recreational" |
| `certificate_number` | string | Yes | FAA certificate number |
| `certificate_expiry` | date | Yes | Certificate expiration (YYYY-MM-DD) |
| `certificate_valid` | bool | Yes | Is certificate currently valid? |
| `waivers` | array | No | List of active waivers |
| `flight_hours_90_days` | float | No | Hours flown in last 90 days |
| `total_flight_hours` | float | No | Total career flight hours |

---

## get_aircraft

Retrieves aircraft registration and maintenance status.

### Request
```json
{
  "aircraft_id": "AC-001"
}
```

### Response
```json
{
  "aircraft_id": "AC-001",
  "registration": "N12345",
  "make_model": "Holybro X500 V2",
  "serial_number": "HB-X500-12345",
  "registration_expiry": "2027-03-15",
  "registration_valid": true,
  "total_flight_hours": 234.5,
  "last_maintenance_date": "2024-12-15",
  "hours_since_maintenance": 18.5,
  "maintenance_interval_hours": 100,
  "battery_cycles": 156,
  "firmware_version": "ArduCopter 4.5.1"
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `aircraft_id` | string | Yes | Unique aircraft identifier |
| `registration` | string | Yes | FAA N-number |
| `make_model` | string | Yes | Manufacturer and model |
| `serial_number` | string | Yes | Serial number |
| `registration_expiry` | date | Yes | Registration expiration |
| `registration_valid` | bool | Yes | Is registration currently valid? |
| `total_flight_hours` | float | Yes | Total airframe hours |
| `last_maintenance_date` | date | Yes | Last maintenance performed |
| `hours_since_maintenance` | float | Yes | Hours since last maintenance |
| `maintenance_interval_hours` | float | No | Maintenance interval (default 100) |
| `battery_cycles` | int | No | Battery charge cycles |
| `firmware_version` | string | No | Autopilot firmware version |

---

## get_mission

Retrieves mission planning and airspace data.

### Request
```json
{
  "flight_id": "FLT-2025-001"
}
```

### Response
```json
{
  "mission_id": "MSN-2025-018",
  "flight_id": "FLT-2025-001",
  "purpose": "Infrastructure Inspection",
  "client_name": "ACME Corp",
  "location_name": "Oakland Industrial Park",
  "location_coords": [37.7749, -122.4194],
  "airspace_class": "G",
  "laanc_required": false,
  "laanc_authorization_id": null,
  "planned_altitude_ft": 350,
  "planned_duration_min": 30,
  "planned_route": [
    [37.7749, -122.4194],
    [37.7760, -122.4180],
    [37.7749, -122.4194]
  ],
  "geofence": [
    [37.774, -122.420],
    [37.776, -122.420],
    [37.776, -122.418],
    [37.774, -122.418]
  ]
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mission_id` | string | Yes | Unique mission identifier |
| `flight_id` | string | Yes | Associated flight ID |
| `purpose` | string | Yes | Mission purpose |
| `client_name` | string | No | Client name (if applicable) |
| `location_name` | string | Yes | Location description |
| `location_coords` | [lat, lon] | Yes | Primary coordinates |
| `airspace_class` | string | Yes | FAA airspace class (A-G) |
| `laanc_required` | bool | Yes | Is LAANC authorization required? |
| `laanc_authorization_id` | string | No | LAANC authorization ID if obtained |
| `planned_altitude_ft` | float | Yes | Planned max altitude AGL |
| `planned_duration_min` | float | No | Planned duration in minutes |
| `planned_route` | array | No | Array of [lat, lon] waypoints |
| `geofence` | array | No | Array of [lat, lon] boundary points |

---

## get_maintenance_history

Retrieves maintenance records for an aircraft.

### Request
```json
{
  "aircraft_id": "AC-001",
  "limit": 10
}
```

### Response
```json
{
  "aircraft_id": "AC-001",
  "total_flight_hours": 234.5,
  "hours_since_maintenance": 18.5,
  "maintenance_interval_hours": 100,
  "maintenance_due_in_hours": 81.5,
  "maintenance_records": [
    {
      "date": "2024-12-15",
      "type": "Scheduled",
      "description": "100-hour inspection",
      "components_serviced": ["motors", "props", "battery"],
      "components_replaced": [],
      "technician": "Mike Johnson",
      "hours_at_service": 216.0,
      "reason": null
    },
    {
      "date": "2024-11-20",
      "type": "Unscheduled",
      "description": "Motor 3 replacement",
      "components_serviced": [],
      "components_replaced": ["motor_3"],
      "technician": "Mike Johnson",
      "hours_at_service": 200.0,
      "reason": "Overheating detected during flight"
    }
  ],
  "known_issues": [],
  "component_hours": {
    "airframe": 234.5,
    "battery": 156,
    "motors": 18.5
  }
}
```

### Maintenance Record Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `date` | date | Yes | Maintenance date |
| `type` | string | Yes | "Scheduled", "Unscheduled", "Inspection" |
| `description` | string | Yes | Description of work |
| `components_serviced` | array | No | Components that were serviced |
| `components_replaced` | array | No | Components that were replaced |
| `technician` | string | No | Technician name |
| `hours_at_service` | float | No | Aircraft hours at time of service |
| `reason` | string | No | Reason for unscheduled maintenance |

---

## Error Responses

All tools return an error object when data is not found:

```json
{
  "error": "Flight not found: FLT-UNKNOWN"
}
```

---

## Data Requirements for Compliance Analysis

For accurate compliance scoring, ensure your data includes:

### Critical (Required)
- Pilot certificate expiry date
- Aircraft registration expiry date
- Flight telemetry with altitude data
- GPS satellite count

### Important (Recommended)
- Geofence boundaries
- Event logs (arm/disarm, mode changes)
- Battery levels during flight
- Maintenance history

### Optional (Enhances Analysis)
- LAANC authorization IDs
- Planned vs actual route comparison
- Motor/ESC telemetry
- Vibration data
