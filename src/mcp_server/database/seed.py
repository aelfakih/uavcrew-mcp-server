"""Seed database with demo data for testing."""

import json
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from .models import Pilot, Aircraft, Flight, Mission, MaintenanceRecord


def seed_demo_data(db: Session):
    """Seed database with demo data for all test cases."""

    # Check if already seeded
    if db.query(Pilot).first():
        return

    # ============================================================
    # PILOTS
    # ============================================================

    pilots = [
        Pilot(
            id="PLT-001",
            name="John Smith",
            certificate_type="Part 107",
            certificate_number="4123456",
            certificate_expiry=date(2026, 5, 15),
            certificate_valid=True,
            waivers=json.dumps(["Night Operations"]),
            flight_hours_90_days=45.5,
            total_flight_hours=234.0,
        ),
        Pilot(
            id="PLT-002",
            name="Jane Doe",
            certificate_type="Part 107",
            certificate_number="4789012",
            certificate_expiry=date(2024, 12, 15),  # EXPIRED
            certificate_valid=False,
            waivers=json.dumps([]),
            flight_hours_90_days=30.0,
            total_flight_hours=150.0,
        ),
        Pilot(
            id="PLT-003",
            name="Bob Wilson",
            certificate_type="Part 107",
            certificate_number="4555666",
            certificate_expiry=date(2027, 3, 1),
            certificate_valid=True,
            waivers=json.dumps(["Night Operations", "BVLOS"]),
            flight_hours_90_days=85.0,
            total_flight_hours=500.0,
        ),
    ]

    for pilot in pilots:
        db.add(pilot)

    # ============================================================
    # AIRCRAFT
    # ============================================================

    aircraft_list = [
        Aircraft(
            id="AC-001",
            registration="N12345",
            make_model="Holybro X500 V2",
            serial_number="HB-X500-12345",
            registration_expiry=date(2027, 3, 15),
            registration_valid=True,
            total_flight_hours=234.5,
            last_maintenance_date=date(2024, 12, 15),
            hours_since_maintenance=18.5,
            maintenance_interval_hours=100,
            battery_cycles=156,
            firmware_version="ArduCopter 4.5.1",
        ),
        Aircraft(
            id="AC-002",
            registration="N67890",
            make_model="DJI Matrice 300",
            serial_number="DJ-M300-67890",
            registration_expiry=date(2024, 6, 1),  # EXPIRED
            registration_valid=False,
            total_flight_hours=500.0,
            last_maintenance_date=date(2024, 10, 1),
            hours_since_maintenance=50.0,
            maintenance_interval_hours=100,
            battery_cycles=300,
            firmware_version="DJI v02.00.0000",
        ),
        Aircraft(
            id="AC-003",
            registration="N11223",
            make_model="Holybro X500 V2",
            serial_number="HB-X500-11223",
            registration_expiry=date(2026, 12, 31),
            registration_valid=True,
            total_flight_hours=95.0,
            last_maintenance_date=date(2024, 6, 15),
            hours_since_maintenance=95.0,  # Almost due for maintenance
            maintenance_interval_hours=100,
            battery_cycles=290,  # Near end of life
            firmware_version="ArduCopter 4.4.0",
        ),
    ]

    for aircraft in aircraft_list:
        db.add(aircraft)

    # ============================================================
    # FLIGHTS with various scenarios
    # ============================================================

    base_datetime = datetime(2025, 1, 7, 14, 30, 0)

    # TC-01: Clean flight
    db.add(Flight(
        id="FLT-TC01",
        pilot_id="PLT-001",
        aircraft_id="AC-001",
        flight_datetime=base_datetime,
        duration_seconds=1500,
        log_format="ardupilot_bin",
        telemetry_json=json.dumps(_generate_clean_telemetry()),
        events_json=json.dumps(_generate_clean_events()),
        summary_json=json.dumps({
            "duration_seconds": 1500,
            "distance_km": 2.1,
            "max_altitude_ft": 350,
            "avg_altitude_ft": 280,
            "max_speed_mph": 35,
            "min_battery_percent": 35,
        }),
    ))

    # TC-02: Altitude violation
    db.add(Flight(
        id="FLT-TC02",
        pilot_id="PLT-001",
        aircraft_id="AC-001",
        flight_datetime=base_datetime - timedelta(days=1),
        duration_seconds=1200,
        log_format="ardupilot_bin",
        telemetry_json=json.dumps(_generate_altitude_violation_telemetry()),
        events_json=json.dumps([
            {"timestamp": str(base_datetime), "type": "ARM", "details": {}},
            {"timestamp": str(base_datetime + timedelta(minutes=10)), "type": "ALTITUDE_WARNING", "details": {"altitude_ft": 485}},
        ]),
        summary_json=json.dumps({
            "duration_seconds": 1200,
            "distance_km": 1.8,
            "max_altitude_ft": 485,
            "avg_altitude_ft": 380,
            "max_speed_mph": 30,
            "min_battery_percent": 42,
        }),
    ))

    # TC-03: Geofence breach
    db.add(Flight(
        id="FLT-TC03",
        pilot_id="PLT-001",
        aircraft_id="AC-001",
        flight_datetime=base_datetime - timedelta(days=2),
        duration_seconds=900,
        log_format="ardupilot_bin",
        events_json=json.dumps([
            {"timestamp": str(base_datetime), "type": "ARM", "details": {}},
            {"timestamp": str(base_datetime + timedelta(minutes=5)), "type": "FENCE_BREACH", "details": {"distance_m": 150}},
            {"timestamp": str(base_datetime + timedelta(minutes=6)), "type": "RTL", "details": {"reason": "GEOFENCE"}},
        ]),
        summary_json=json.dumps({
            "duration_seconds": 900,
            "distance_km": 1.5,
            "max_altitude_ft": 320,
            "avg_altitude_ft": 250,
            "max_speed_mph": 40,
            "min_battery_percent": 55,
        }),
    ))

    # TC-04: Expired pilot certificate
    db.add(Flight(
        id="FLT-TC04",
        pilot_id="PLT-002",  # Expired certificate
        aircraft_id="AC-001",
        flight_datetime=base_datetime - timedelta(days=3),
        duration_seconds=1800,
        log_format="ardupilot_bin",
        summary_json=json.dumps({
            "duration_seconds": 1800,
            "distance_km": 3.0,
            "max_altitude_ft": 380,
            "avg_altitude_ft": 300,
            "max_speed_mph": 35,
            "min_battery_percent": 28,
        }),
    ))

    # TC-05: Expired aircraft registration
    db.add(Flight(
        id="FLT-TC05",
        pilot_id="PLT-001",
        aircraft_id="AC-002",  # Expired registration
        flight_datetime=base_datetime - timedelta(days=4),
        duration_seconds=1500,
        log_format="dji",
        summary_json=json.dumps({
            "duration_seconds": 1500,
            "distance_km": 2.5,
            "max_altitude_ft": 350,
            "avg_altitude_ft": 280,
            "max_speed_mph": 40,
            "min_battery_percent": 32,
        }),
    ))

    # TC-06: Maintenance overdue
    db.add(Flight(
        id="FLT-TC06",
        pilot_id="PLT-001",
        aircraft_id="AC-003",  # Near maintenance due
        flight_datetime=base_datetime - timedelta(days=5),
        duration_seconds=1200,
        log_format="ardupilot_bin",
        summary_json=json.dumps({
            "duration_seconds": 1200,
            "distance_km": 2.0,
            "max_altitude_ft": 300,
            "avg_altitude_ft": 250,
            "max_speed_mph": 30,
            "min_battery_percent": 40,
        }),
    ))

    # TC-08: Battery critical event
    db.add(Flight(
        id="FLT-TC08",
        pilot_id="PLT-001",
        aircraft_id="AC-001",
        flight_datetime=base_datetime - timedelta(days=7),
        duration_seconds=1680,  # 28 minutes
        log_format="ardupilot_bin",
        events_json=json.dumps([
            {"timestamp": str(base_datetime), "type": "ARM", "details": {}},
            {"timestamp": str(base_datetime + timedelta(minutes=25)), "type": "FAILSAFE_BATTERY", "details": {"percent": 12}},
            {"timestamp": str(base_datetime + timedelta(minutes=25, seconds=5)), "type": "RTL", "details": {"reason": "CRITICAL_BATTERY"}},
        ]),
        summary_json=json.dumps({
            "duration_seconds": 1680,
            "distance_km": 2.8,
            "max_altitude_ft": 320,
            "avg_altitude_ft": 280,
            "max_speed_mph": 35,
            "min_battery_percent": 12,
        }),
    ))

    # ============================================================
    # MISSIONS
    # ============================================================

    missions = [
        Mission(
            id="MSN-TC01",
            flight_id="FLT-TC01",
            purpose="Infrastructure Inspection",
            client_name="ACME Corp",
            location_name="Oakland Industrial Park",
            location_lat=37.7749,
            location_lon=-122.4194,
            airspace_class="G",
            laanc_required=False,
            planned_altitude_ft=350,
            planned_duration_min=30,
            geofence_json=json.dumps([
                [37.774, -122.420],
                [37.776, -122.420],
                [37.776, -122.418],
                [37.774, -122.418],
            ]),
        ),
        Mission(
            id="MSN-TC02",
            flight_id="FLT-TC02",
            purpose="Cell Tower Inspection",
            client_name="TeleCom Inc",
            location_name="Downtown Tower Site",
            location_lat=37.7849,
            location_lon=-122.4094,
            airspace_class="G",
            laanc_required=False,
            planned_altitude_ft=400,  # At limit
            planned_duration_min=25,
        ),
        Mission(
            id="MSN-TC12",
            flight_id="FLT-TC12",  # Will create if needed
            purpose="Aerial Photography",
            client_name="Media Co",
            location_name="SFO Adjacent Area",
            location_lat=37.6213,
            location_lon=-122.3790,
            airspace_class="B",
            laanc_required=True,
            laanc_authorization_id=None,  # NOT OBTAINED
            planned_altitude_ft=200,
            planned_duration_min=20,
        ),
    ]

    for mission in missions:
        db.add(mission)

    # ============================================================
    # MAINTENANCE RECORDS
    # ============================================================

    maintenance_records = [
        MaintenanceRecord(
            aircraft_id="AC-001",
            date=date(2024, 12, 15),
            type="Scheduled",
            description="100-hour inspection",
            components_serviced=json.dumps(["motors", "props", "battery"]),
            components_replaced=json.dumps([]),
            technician="Mike Johnson",
            hours_at_service=216.0,
        ),
        MaintenanceRecord(
            aircraft_id="AC-001",
            date=date(2024, 11, 20),
            type="Unscheduled",
            description="Motor 3 replacement",
            components_serviced=json.dumps([]),
            components_replaced=json.dumps(["motor_3"]),
            technician="Mike Johnson",
            hours_at_service=200.0,
            reason="Overheating detected during flight",
        ),
        MaintenanceRecord(
            aircraft_id="AC-003",
            date=date(2024, 6, 15),
            type="Scheduled",
            description="Initial setup and calibration",
            components_serviced=json.dumps(["compass", "accelerometer", "gyro"]),
            components_replaced=json.dumps([]),
            technician="Factory",
            hours_at_service=0.0,
        ),
    ]

    for record in maintenance_records:
        db.add(record)

    db.commit()


def _generate_clean_telemetry() -> list:
    """Generate clean flight telemetry data."""
    base_time = datetime(2025, 1, 7, 14, 30, 0)
    telemetry = []

    for i in range(50):  # 50 data points
        t = base_time + timedelta(seconds=i * 30)
        alt = 280 + (70 * (i / 25)) if i < 25 else 350 - (70 * ((i - 25) / 25))

        telemetry.append({
            "timestamp": t.isoformat(),
            "latitude": 37.7749 + (0.0001 * i),
            "longitude": -122.4194 + (0.0001 * i),
            "altitude_agl_ft": alt,
            "ground_speed_mph": 25 + (i % 10),
            "battery_percent": 95 - i,
            "gps_satellites": 14,
        })

    return telemetry


def _generate_clean_events() -> list:
    """Generate clean flight events (arm, takeoff, land, disarm)."""
    base_time = datetime(2025, 1, 7, 14, 30, 0)
    return [
        {"timestamp": base_time.isoformat(), "type": "ARM", "details": {}},
        {"timestamp": (base_time + timedelta(seconds=5)).isoformat(), "type": "TAKEOFF", "details": {}},
        {"timestamp": (base_time + timedelta(minutes=24, seconds=55)).isoformat(), "type": "LAND", "details": {}},
        {"timestamp": (base_time + timedelta(minutes=25)).isoformat(), "type": "DISARM", "details": {}},
    ]


def _generate_altitude_violation_telemetry() -> list:
    """Generate telemetry with altitude violation."""
    base_time = datetime(2025, 1, 6, 14, 30, 0)
    telemetry = []

    for i in range(40):
        t = base_time + timedelta(seconds=i * 30)

        # Altitude ramps up past 400ft
        if i < 15:
            alt = 200 + (20 * i)
        elif i < 25:
            alt = 485  # Violation zone
        else:
            alt = 485 - (20 * (i - 25))

        telemetry.append({
            "timestamp": t.isoformat(),
            "latitude": 37.7849 + (0.0001 * i),
            "longitude": -122.4094 + (0.0001 * i),
            "altitude_agl_ft": alt,
            "ground_speed_mph": 30,
            "battery_percent": 95 - i,
            "gps_satellites": 12,
        })

    return telemetry
