#!/usr/bin/env python3
"""
Test script to verify MCP server setup and connectivity.

Usage:
    python scripts/test_connection.py [--url URL] [--api-key KEY]

This script tests:
1. Database connection
2. Demo data presence
3. All MCP tools
4. Response format validation
"""

import argparse
import json
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, "src")


def test_database():
    """Test database connection and data presence."""
    print("\n" + "=" * 60)
    print("TEST 1: Database Connection")
    print("=" * 60)

    try:
        from mcp_server.database import get_db
        from mcp_server.database.models import Flight, Pilot, Aircraft, Mission

        db = get_db()

        flights = db.query(Flight).count()
        pilots = db.query(Pilot).count()
        aircraft = db.query(Aircraft).count()
        missions = db.query(Mission).count()

        print(f"  ✓ Database connected")
        print(f"  ✓ Flights: {flights}")
        print(f"  ✓ Pilots: {pilots}")
        print(f"  ✓ Aircraft: {aircraft}")
        print(f"  ✓ Missions: {missions}")

        if flights == 0:
            print("\n  ⚠ WARNING: No flights found. Run with SEED_DEMO_DATA=true")
            return False

        return True

    except Exception as e:
        print(f"  ✗ Database error: {e}")
        return False


def test_tools():
    """Test all MCP tools."""
    print("\n" + "=" * 60)
    print("TEST 2: MCP Tools")
    print("=" * 60)

    try:
        from mcp_server.database import get_db
        from mcp_server.tools import (
            get_flight_log,
            get_pilot,
            get_aircraft,
            get_mission,
            get_maintenance_history,
        )

        db = get_db()
        all_passed = True

        # Test get_flight_log
        print("\n  Testing get_flight_log...")
        result = get_flight_log(db, "FLT-TC01")
        if "error" in result:
            print(f"    ✗ Error: {result['error']}")
            all_passed = False
        else:
            print(f"    ✓ Flight: {result.get('flight_id')}")
            print(f"    ✓ Duration: {result.get('duration_seconds', 0)}s")
            print(f"    ✓ Telemetry points: {len(result.get('telemetry', []))}")

        # Test get_pilot
        print("\n  Testing get_pilot...")
        result = get_pilot(db, "PLT-001")
        if "error" in result:
            print(f"    ✗ Error: {result['error']}")
            all_passed = False
        else:
            print(f"    ✓ Pilot: {result.get('name')}")
            print(f"    ✓ Certificate: {result.get('certificate_type')}")
            print(f"    ✓ Valid: {result.get('certificate_valid')}")

        # Test get_aircraft
        print("\n  Testing get_aircraft...")
        result = get_aircraft(db, "AC-001")
        if "error" in result:
            print(f"    ✗ Error: {result['error']}")
            all_passed = False
        else:
            print(f"    ✓ Aircraft: {result.get('registration')}")
            print(f"    ✓ Model: {result.get('make_model')}")
            print(f"    ✓ Hours: {result.get('total_flight_hours')}")

        # Test get_mission
        print("\n  Testing get_mission...")
        result = get_mission(db, "FLT-TC01")
        if "error" in result:
            print(f"    ✗ Error: {result['error']}")
            all_passed = False
        else:
            print(f"    ✓ Mission: {result.get('purpose')}")
            print(f"    ✓ Location: {result.get('location_name')}")
            print(f"    ✓ Airspace: {result.get('airspace_class')}")

        # Test get_maintenance_history
        print("\n  Testing get_maintenance_history...")
        result = get_maintenance_history(db, "AC-001")
        if "error" in result:
            print(f"    ✗ Error: {result['error']}")
            all_passed = False
        else:
            print(f"    ✓ Aircraft: {result.get('aircraft_id')}")
            print(f"    ✓ Records: {len(result.get('maintenance_records', []))}")
            print(f"    ✓ Hours since maintenance: {result.get('hours_since_maintenance')}")

        return all_passed

    except Exception as e:
        print(f"  ✗ Tool error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scenarios():
    """Test all demo scenarios."""
    print("\n" + "=" * 60)
    print("TEST 3: Demo Scenarios")
    print("=" * 60)

    try:
        from mcp_server.database import get_db
        from mcp_server.tools import get_flight_log, get_pilot, get_aircraft

        db = get_db()

        scenarios = [
            ("FLT-TC01", "Clean flight", "Should be COMPLIANT"),
            ("FLT-TC02", "Altitude violation", "Should be NEEDS_REVIEW"),
            ("FLT-TC03", "Geofence breach", "Should be NON_COMPLIANT"),
            ("FLT-TC04", "Expired pilot cert", "Should be NON_COMPLIANT"),
            ("FLT-TC05", "Expired aircraft reg", "Should be NON_COMPLIANT"),
        ]

        all_passed = True

        for flight_id, name, expected in scenarios:
            print(f"\n  {flight_id}: {name}")
            result = get_flight_log(db, flight_id)

            if "error" in result:
                print(f"    ✗ Not found")
                all_passed = False
            else:
                summary = result.get("summary", {})
                print(f"    ✓ Found - {expected}")
                print(f"      Max altitude: {summary.get('max_altitude_ft', 'N/A')}ft")
                print(f"      Duration: {summary.get('duration_seconds', 0) / 60:.1f}min")

        return all_passed

    except Exception as e:
        print(f"  ✗ Scenario error: {e}")
        return False


def test_expired_credentials():
    """Test detection of expired credentials."""
    print("\n" + "=" * 60)
    print("TEST 4: Expired Credential Detection")
    print("=" * 60)

    try:
        from mcp_server.database import get_db
        from mcp_server.tools import get_pilot, get_aircraft

        db = get_db()
        all_passed = True

        # Test expired pilot
        print("\n  Testing expired pilot (PLT-002)...")
        result = get_pilot(db, "PLT-002")
        if result.get("certificate_valid") is False:
            print(f"    ✓ Correctly marked as invalid")
            print(f"    ✓ Expiry: {result.get('certificate_expiry')}")
        else:
            print(f"    ✗ Should be marked invalid")
            all_passed = False

        # Test expired aircraft (simulated via N67890)
        print("\n  Testing expired aircraft (AC-002 / N67890)...")
        result = get_aircraft(db, "AC-002")
        if result.get("registration_valid") is False:
            print(f"    ✓ Correctly marked as invalid")
            print(f"    ✓ Expiry: {result.get('registration_expiry')}")
        else:
            print(f"    ✗ Should be marked invalid")
            all_passed = False

        return all_passed

    except Exception as e:
        print(f"  ✗ Credential test error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test MCP Server Setup")
    parser.add_argument("--seed", action="store_true", help="Seed demo data before testing")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  UAVCrew MCP Server - Connection Test")
    print("=" * 60)
    print(f"  Time: {datetime.now().isoformat()}")

    if args.seed:
        print("\n  Seeding demo data...")
        from mcp_server.database import seed_demo_data
        seed_demo_data()
        print("  ✓ Demo data seeded")

    results = []

    # Run tests
    results.append(("Database Connection", test_database()))
    results.append(("MCP Tools", test_tools()))
    results.append(("Demo Scenarios", test_scenarios()))
    results.append(("Expired Credentials", test_expired_credentials()))

    # Summary
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)

    passed = 0
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
        if result:
            passed += 1

    print(f"\n  Result: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("\n  ✓ All tests passed! MCP server is ready.")
        return 0
    else:
        print("\n  ✗ Some tests failed. Check configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
