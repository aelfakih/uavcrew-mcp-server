"""SQLAlchemy models for compliance data."""

from datetime import datetime, date
from typing import Optional

from sqlalchemy import String, Integer, Float, Boolean, DateTime, Date, Text, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass


class Pilot(Base):
    """Pilot certification and credentials."""
    __tablename__ = "pilots"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    certificate_type: Mapped[str] = mapped_column(String(50))
    certificate_number: Mapped[str] = mapped_column(String(50))
    certificate_expiry: Mapped[date] = mapped_column(Date)
    certificate_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    waivers: Mapped[str] = mapped_column(Text, default="[]")  # JSON array
    flight_hours_90_days: Mapped[float] = mapped_column(Float, default=0)
    total_flight_hours: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Aircraft(Base):
    """Aircraft registration and status."""
    __tablename__ = "aircraft"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    registration: Mapped[str] = mapped_column(String(20))
    make_model: Mapped[str] = mapped_column(String(100))
    serial_number: Mapped[str] = mapped_column(String(50))
    registration_expiry: Mapped[date] = mapped_column(Date)
    registration_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    total_flight_hours: Mapped[float] = mapped_column(Float, default=0)
    last_maintenance_date: Mapped[date] = mapped_column(Date)
    hours_since_maintenance: Mapped[float] = mapped_column(Float, default=0)
    maintenance_interval_hours: Mapped[float] = mapped_column(Float, default=100)
    battery_cycles: Mapped[int] = mapped_column(Integer, default=0)
    firmware_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Flight(Base):
    """Flight record with telemetry summary."""
    __tablename__ = "flights"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    pilot_id: Mapped[str] = mapped_column(String(50))
    aircraft_id: Mapped[str] = mapped_column(String(50))
    flight_datetime: Mapped[datetime] = mapped_column(DateTime)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    log_format: Mapped[str] = mapped_column(String(20), default="ardupilot_bin")
    telemetry_json: Mapped[str] = mapped_column(Text, default="[]")  # JSON array
    events_json: Mapped[str] = mapped_column(Text, default="[]")  # JSON array
    summary_json: Mapped[str] = mapped_column(Text, default="{}")  # JSON object
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Mission(Base):
    """Mission planning data."""
    __tablename__ = "missions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    flight_id: Mapped[str] = mapped_column(String(50))
    purpose: Mapped[str] = mapped_column(String(200))
    client_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    location_name: Mapped[str] = mapped_column(String(200))
    location_lat: Mapped[float] = mapped_column(Float)
    location_lon: Mapped[float] = mapped_column(Float)
    airspace_class: Mapped[str] = mapped_column(String(5), default="G")
    laanc_required: Mapped[bool] = mapped_column(Boolean, default=False)
    laanc_authorization_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    planned_altitude_ft: Mapped[float] = mapped_column(Float, default=400)
    planned_duration_min: Mapped[float] = mapped_column(Float, default=30)
    planned_route_json: Mapped[str] = mapped_column(Text, default="[]")  # JSON array
    geofence_json: Mapped[str] = mapped_column(Text, default="[]")  # JSON array
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MaintenanceRecord(Base):
    """Maintenance history for aircraft."""
    __tablename__ = "maintenance_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    aircraft_id: Mapped[str] = mapped_column(String(50))
    date: Mapped[date] = mapped_column(Date)
    type: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text)
    components_serviced: Mapped[str] = mapped_column(Text, default="[]")  # JSON
    components_replaced: Mapped[str] = mapped_column(Text, default="[]")  # JSON
    technician: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    hours_at_service: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
