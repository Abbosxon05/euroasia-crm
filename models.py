"""Data models for the EuroAsia Education CRM (Python/CLI edition).

Mirrors the same domain used by the web version (guruh/o'quvchi/davomat):
Group, Student, Attendance -- kept as plain dataclasses so they serialize
to/from JSON without any extra dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Attendance:
    id: int
    student_id: int
    date: str  # YYYY-MM-DD
    time: str  # HH:MM

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "Attendance":
        return Attendance(
            id=data["id"],
            student_id=data["student_id"],
            date=data["date"],
            time=data["time"],
        )


@dataclass
class Group:
    id: int
    name: str
    schedule: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "Group":
        return Group(id=data["id"], name=data["name"], schedule=data.get("schedule"))


@dataclass
class User:
    """A person who can log into the CLI with their own access code.

    role is either "admin" (sees everything, manages accounts) or
    "teacher" (o'qituvchi -- only sees/manages their own group_id).
    """

    id: int
    name: str
    role: str  # "admin" | "teacher"
    code: str  # kirish kodi (PIN)
    group_id: Optional[int] = None  # faqat o'qituvchi uchun: biriktirilgan guruh

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "User":
        return User(
            id=data["id"],
            name=data["name"],
            role=data["role"],
            code=data["code"],
            group_id=data.get("group_id"),
        )


@dataclass
class Student:
    id: int
    name: str
    group_id: Optional[int] = None
    parent_phone: Optional[str] = None
    monthly_fee: float = 0.0
    paid: bool = False
    note: Optional[str] = None
    homework_missed: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "Student":
        return Student(
            id=data["id"],
            name=data["name"],
            group_id=data.get("group_id"),
            parent_phone=data.get("parent_phone"),
            monthly_fee=data.get("monthly_fee", 0.0),
            paid=data.get("paid", False),
            note=data.get("note"),
            homework_missed=data.get("homework_missed", 0),
        )