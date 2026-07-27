"""JSON-file persistence for the EuroAsia Education CRM (Python/CLI edition).

Everything lives in a single ``data.json`` next to this file so the app has
zero external dependencies (no database, no server) -- run it, and your data
survives between runs.
"""

from __future__ import annotations

import json
import os
from typing import Optional

from models import Attendance, Group, Student, User

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")


class Store:
    """In-memory data store, backed by a JSON file on disk."""

    def __init__(self, path: str = DATA_FILE) -> None:
        self.path = path
        self.groups: list[Group] = []
        self.students: list[Student] = []
        self.attendance: list[Attendance] = []
        self.users: list[User] = []
        self._next_group_id = 1
        self._next_student_id = 1
        self._next_attendance_id = 1
        self._next_user_id = 1
        self.load()

    # ------------------------------------------------------------------ #
    # Persistence
    # ------------------------------------------------------------------ #
    def load(self) -> None:
        if not os.path.exists(self.path):
            self._seed_demo_data()
            self.save()
            return

        with open(self.path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)

        self.groups = [Group.from_dict(g) for g in raw.get("groups", [])]
        self.students = [Student.from_dict(s) for s in raw.get("students", [])]
        self.attendance = [Attendance.from_dict(a) for a in raw.get("attendance", [])]
        self.users = [User.from_dict(u) for u in raw.get("users", [])]

        self._next_group_id = max([g.id for g in self.groups], default=0) + 1
        self._next_student_id = max([s.id for s in self.students], default=0) + 1
        self._next_attendance_id = (
            max([a.id for a in self.attendance], default=0) + 1
        )
        self._next_user_id = max([u.id for u in self.users], default=0) + 1

        if not self.users:
            # Eski data.json fayllarda users bo'lmasligi mumkin -- migratsiya.
            self._seed_default_users()
            self.save()

    def save(self) -> None:
        raw = {
            "groups": [g.to_dict() for g in self.groups],
            "students": [s.to_dict() for s in self.students],
            "attendance": [a.to_dict() for a in self.attendance],
            "users": [u.to_dict() for u in self.users],
        }
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(raw, fh, ensure_ascii=False, indent=2)

    def _seed_demo_data(self) -> None:
        """First run only: a couple of sample rows so the menu isn't empty."""
        self.groups = [
            Group(id=1, name="IELTS Morning", schedule="Du-Chor-Juma 09:00"),
            Group(id=2, name="General English", schedule="Sesh-Payshanba-Shanba 14:00"),
        ]
        self.students = [
            Student(
                id=1,
                name="Ali Valiyev",
                group_id=1,
                parent_phone="+998901234567",
                monthly_fee=500000,
                paid=True,
            ),
            Student(
                id=2,
                name="Madina Karimova",
                group_id=1,
                parent_phone="+998919876543",
                monthly_fee=500000,
                paid=False,
                homework_missed=1,
            ),
        ]
        self.attendance = []
        self._next_group_id = 3
        self._next_student_id = 3
        self._next_attendance_id = 1
        self._seed_default_users()

    def _seed_default_users(self) -> None:
        """First run only: bitta admin va bitta o'qituvchi hisobi bilan kod."""
        self.users = [
            User(id=1, name="Direktor (Admin)", role="admin", code="0000"),
            User(
                id=2,
                name="Ustoz (1-guruh o'qituvchisi)",
                role="teacher",
                code="1111",
                group_id=1 if self.groups else None,
            ),
        ]
        self._next_user_id = 3

    # ------------------------------------------------------------------ #
    # Groups
    # ------------------------------------------------------------------ #
    def add_group(self, name: str, schedule: Optional[str]) -> Group:
        group = Group(id=self._next_group_id, name=name, schedule=schedule)
        self._next_group_id += 1
        self.groups.append(group)
        self.save()
        return group

    def get_group(self, group_id: int) -> Optional[Group]:
        return next((g for g in self.groups if g.id == group_id), None)

    def update_group(self, group_id: int, name: Optional[str], schedule: Optional[str]) -> bool:
        group = self.get_group(group_id)
        if not group:
            return False
        if name is not None:
            group.name = name
        if schedule is not None:
            group.schedule = schedule
        self.save()
        return True

    def delete_group(self, group_id: int) -> bool:
        group = self.get_group(group_id)
        if not group:
            return False
        self.groups.remove(group)
        for student in self.students:
            if student.group_id == group_id:
                student.group_id = None
        self.save()
        return True

    # ------------------------------------------------------------------ #
    # Students
    # ------------------------------------------------------------------ #
    def add_student(
        self,
        name: str,
        group_id: Optional[int],
        parent_phone: Optional[str],
        monthly_fee: float,
        note: Optional[str],
    ) -> Student:
        student = Student(
            id=self._next_student_id,
            name=name,
            group_id=group_id,
            parent_phone=parent_phone,
            monthly_fee=monthly_fee,
            note=note,
        )
        self._next_student_id += 1
        self.students.append(student)
        self.save()
        return student

    def get_student(self, student_id: int) -> Optional[Student]:
        return next((s for s in self.students if s.id == student_id), None)

    def list_students(self, group_id: Optional[int] = None) -> list[Student]:
        if group_id is None:
            return list(self.students)
        return [s for s in self.students if s.group_id == group_id]

    def update_student(self, student_id: int, **fields) -> bool:
        student = self.get_student(student_id)
        if not student:
            return False
        for key, value in fields.items():
            if value is not None and hasattr(student, key):
                setattr(student, key, value)
        self.save()
        return True

    def delete_student(self, student_id: int) -> bool:
        student = self.get_student(student_id)
        if not student:
            return False
        self.students.remove(student)
        self.attendance = [a for a in self.attendance if a.student_id != student_id]
        self.save()
        return True

    # ------------------------------------------------------------------ #
    # Attendance
    # ------------------------------------------------------------------ #
    def add_attendance(self, student_id: int, date: str, time: str) -> Attendance:
        record = Attendance(
            id=self._next_attendance_id,
            student_id=student_id,
            date=date,
            time=time,
        )
        self._next_attendance_id += 1
        self.attendance.append(record)
        self.save()
        return record

    def list_attendance(self, student_id: int) -> list[Attendance]:
        records = [a for a in self.attendance if a.student_id == student_id]
        return sorted(records, key=lambda a: (a.date, a.time))

    def delete_attendance(self, attendance_id: int) -> bool:
        record = next((a for a in self.attendance if a.id == attendance_id), None)
        if not record:
            return False
        self.attendance.remove(record)
        self.save()
        return True

    # ------------------------------------------------------------------ #
    # Users (login / rollar)
    # ------------------------------------------------------------------ #
    def authenticate(self, code: str) -> Optional[User]:
        code = code.strip()
        return next((u for u in self.users if u.code == code), None)

    def get_user(self, user_id: int) -> Optional[User]:
        return next((u for u in self.users if u.id == user_id), None)

    def list_users(self) -> list[User]:
        return list(self.users)

    def add_user(self, name: str, role: str, code: str, group_id: Optional[int]) -> User:
        user = User(id=self._next_user_id, name=name, role=role, code=code, group_id=group_id)
        self._next_user_id += 1
        self.users.append(user)
        self.save()
        return user

    def code_taken(self, code: str, exclude_user_id: Optional[int] = None) -> bool:
        return any(u.code == code and u.id != exclude_user_id for u in self.users)

    def update_user(self, user_id: int, **fields) -> bool:
        user = self.get_user(user_id)
        if not user:
            return False
        for key, value in fields.items():
            if hasattr(user, key):
                setattr(user, key, value)
        self.save()
        return True

    def delete_user(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        if not user:
            return False
        self.users.remove(user)
        self.save()
        return True

    def attendance_count_this_month(self, student_id: Optional[int] = None) -> int:
        from datetime import date as _date

        today = _date.today()
        prefix = f"{today.year:04d}-{today.month:02d}"
        records = self.attendance
        if student_id is not None:
            records = [a for a in records if a.student_id == student_id]
        return len([a for a in records if a.date.startswith(prefix)])