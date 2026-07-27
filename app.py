"""EuroAsia Education CRM -- Python/CLI edition.

O'zbek tilidagi konsol interfeysi: guruhlar, o'quvchilar, davomat va to'lovlarni
boshqarish. Ma'lumotlar shu papkadagi ``data.json`` faylida saqlanadi -- baza
yoki internet aloqasi shart emas.

Ishga tushirish:

    python3 app.py
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from models import Group, Student, User
from storage import Store


def today_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def now_time() -> str:
    return datetime.now().strftime("%H:%M")


def fmt_money(amount: float) -> str:
    return f"{amount:,.0f}".replace(",", " ")


def prompt(label: str, default: Optional[str] = None) -> str:
    suffix = f" [{default}]" if default is not None else ""
    value = input(f"{label}{suffix}: ").strip()
    return value if value else (default or "")


def prompt_int(label: str, default: Optional[int] = None) -> Optional[int]:
    raw = prompt(label, str(default) if default is not None else None)
    if raw == "":
        return None
    try:
        return int(raw)
    except ValueError:
        print("Noto'g'ri raqam kiritildi.")
        return prompt_int(label, default)


def prompt_float(label: str, default: Optional[float] = None) -> float:
    raw = prompt(label, str(default) if default is not None else None)
    if raw == "":
        return default or 0.0
    try:
        return float(raw)
    except ValueError:
        print("Noto'g'ri son kiritildi.")
        return prompt_float(label, default)


def prompt_bool(label: str, default: bool = False) -> bool:
    raw = prompt(f"{label} (ha/yo'q)", "ha" if default else "yo'q").lower()
    return raw in ("ha", "h", "yes", "y", "true")


def pause() -> None:
    input("\nDavom etish uchun Enter tugmasini bosing...")


class App:
    def __init__(self) -> None:
        self.store = Store()
        self.current_user: Optional[User] = None

    # ------------------------------------------------------------------ #
    # Login
    # ------------------------------------------------------------------ #
    def login(self) -> bool:
        """Kirish kodini so'raydi. To'g'ri kod topilguncha (yoki chiqguncha) davom etadi."""
        print("=" * 50)
        print(" EuroAsia Education CRM (Python konsol versiyasi)")
        print("=" * 50)
        while True:
            raw = input("\nKirish kodingizni kiriting (chiqish uchun 'q'): ").strip()
            if raw.lower() == "q":
                return False
            user = self.store.authenticate(raw)
            if not user:
                print("Kod topilmadi. Qaytadan urinib ko'ring.")
                continue
            self.current_user = user
            role_label = "Administrator" if user.role == "admin" else "O'qituvchi"
            print(f"\nXush kelibsiz, {user.name}! ({role_label} sifatida kirdingiz)")
            return True

    def is_admin(self) -> bool:
        return bool(self.current_user and self.current_user.role == "admin")

    def my_group_id(self) -> Optional[int]:
        return self.current_user.group_id if self.current_user else None

    # ------------------------------------------------------------------ #
    # Main menu
    # ------------------------------------------------------------------ #
    def run(self) -> None:
        if not self.login():
            print("Xayr!")
            return

        while True:
            if self.is_admin():
                print(
                    "\nAsosiy menyu (Admin):\n"
                    " 1) Bosh sahifa (statistika)\n"
                    " 2) Guruhlar\n"
                    " 3) O'quvchilar\n"
                    " 4) Foydalanuvchilar (kirish kodlari)\n"
                    " 9) Chiqish (boshqa foydalanuvchi kirsin)\n"
                    " 0) Dasturdan chiqish"
                )
            else:
                group = self.store.get_group(self.my_group_id()) if self.my_group_id() else None
                group_label = group.name if group else "guruh biriktirilmagan"
                print(
                    f"\nAsosiy menyu (O'qituvchi -- {group_label}):\n"
                    " 1) Bosh sahifa (statistika)\n"
                    " 2) Mening guruhim\n"
                    " 3) O'quvchilarim\n"
                    " 9) Chiqish (boshqa foydalanuvchi kirsin)\n"
                    " 0) Dasturdan chiqish"
                )

            choice = input("Tanlang: ").strip()
            if choice == "0":
                print("Xayr!")
                return
            if choice == "9":
                self.current_user = None
                if not self.login():
                    print("Xayr!")
                    return
                continue
            if choice == "1":
                self.show_dashboard()
            elif choice == "2":
                self.menu_groups()
            elif choice == "3":
                self.menu_students()
            elif choice == "4" and self.is_admin():
                self.menu_users()
            else:
                print("Noto'g'ri tanlov.")

    # ------------------------------------------------------------------ #
    # Dashboard
    # ------------------------------------------------------------------ #
    def show_dashboard(self) -> None:
        store = self.store
        scope_group_id = None if self.is_admin() else self.my_group_id()
        students = store.list_students(scope_group_id) if scope_group_id else (
            store.students if self.is_admin() else []
        )
        groups_count = len(store.groups) if self.is_admin() else (1 if scope_group_id else 0)
        student_ids = {s.id for s in students}
        attendances_this_month = (
            store.attendance_count_this_month()
            if self.is_admin()
            else len(
                [
                    a
                    for a in store.attendance
                    if a.student_id in student_ids
                    and a.date.startswith(today_prefix())
                ]
            )
        )
        debtors = [s for s in students if not s.paid]
        total_fees = sum(s.monthly_fee for s in students)

        counts: dict[int, int] = {}
        for a in store.attendance:
            if a.student_id in student_ids and a.date.startswith(today_prefix()):
                counts[a.student_id] = counts.get(a.student_id, 0) + 1
        most_active = None
        if counts:
            top_id = max(counts, key=lambda sid: counts[sid])
            student = store.get_student(top_id)
            if student:
                most_active = (student.name, counts[top_id])

        title = "umumiy holat" if self.is_admin() else "mening guruhim"
        print(f"\n--- Bosh sahifa: {title} ---")
        if self.is_admin():
            print(f"Guruhlar soni:            {groups_count}")
        print(f"O'quvchilar soni:         {len(students)}")
        print(f"Davomat (bu oy):          {attendances_this_month}")
        print(f"Qarzdorlar soni:          {len(debtors)}")
        print(f"Oylik tushum kutuvi:      UZS {fmt_money(total_fees)}")
        if most_active:
            print(f"Eng faol o'quvchi:        {most_active[0]} ({most_active[1]} marta)")
        else:
            print("Eng faol o'quvchi:        -")
        pause()

    # ------------------------------------------------------------------ #
    # Groups
    # ------------------------------------------------------------------ #
    def menu_groups(self) -> None:
        if not self.is_admin():
            # O'qituvchi faqat o'z guruhi rosterini ko'radi, boshqa amal yo'q.
            self.view_group_roster(group_id=self.my_group_id())
            return

        while True:
            self.list_groups()
            print(
                "\nGuruhlar menyusi:\n"
                " 1) Yangi guruh qo'shish\n"
                " 2) Guruhni tahrirlash\n"
                " 3) Guruhni o'chirish\n"
                " 4) Guruh o'quvchilarini ko'rish\n"
                " 0) Orqaga"
            )
            choice = input("Tanlang: ").strip()
            if choice == "0":
                return
            elif choice == "1":
                self.add_group()
            elif choice == "2":
                self.edit_group()
            elif choice == "3":
                self.remove_group()
            elif choice == "4":
                self.view_group_roster()
            else:
                print("Noto'g'ri tanlov.")

    def list_groups(self) -> None:
        print("\n--- Guruhlar ro'yxati ---")
        if not self.store.groups:
            print("Hozircha guruhlar yo'q.")
            return
        for g in self.store.groups:
            student_count = len(self.store.list_students(g.id))
            print(
                f"[{g.id}] {g.name} -- {g.schedule or 'jadval belgilanmagan'} "
                f"({student_count} o'quvchi)"
            )

    def add_group(self) -> None:
        name = prompt("Guruh nomi")
        if not name:
            print("Guruh nomi bo'sh bo'lishi mumkin emas.")
            return
        schedule = prompt("Dars jadvali (masalan: Du-Chor-Juma 09:00)")
        group = self.store.add_group(name, schedule or None)
        print(f"Guruh qo'shildi: [{group.id}] {group.name}")

    def edit_group(self) -> None:
        group_id = prompt_int("Tahrirlanadigan guruh ID raqami")
        if group_id is None:
            return
        group = self.store.get_group(group_id)
        if not group:
            print("Bunday guruh topilmadi.")
            return
        name = prompt("Guruh nomi", group.name)
        schedule = prompt("Dars jadvali", group.schedule or "")
        self.store.update_group(group_id, name, schedule)
        print("Guruh yangilandi.")

    def remove_group(self) -> None:
        group_id = prompt_int("O'chiriladigan guruh ID raqami")
        if group_id is None:
            return
        if self.store.delete_group(group_id):
            print("Guruh o'chirildi (o'quvchilari 'guruhsiz' holatga o'tdi).")
        else:
            print("Bunday guruh topilmadi.")

    def view_group_roster(self, group_id: Optional[int] = None) -> None:
        if group_id is None:
            group_id = prompt_int("Guruh ID raqami")
        if group_id is None:
            return
        group = self.store.get_group(group_id)
        if not group:
            print("Sizga hech qanday guruh biriktirilmagan." if not self.is_admin() else "Bunday guruh topilmadi.")
            return
        students = self.store.list_students(group_id)
        print(f"\n--- {group.name} guruhi o'quvchilari ---")
        if not students:
            print("Bu guruhda hali o'quvchi yo'q.")
        self.print_student_table(students)
        pause()

    # ------------------------------------------------------------------ #
    # Students
    # ------------------------------------------------------------------ #
    def accessible_students(self) -> list[Student]:
        """Admin -- hammasi. O'qituvchi -- faqat o'ziga biriktirilgan guruh o'quvchilari."""
        if self.is_admin():
            return list(self.store.students)
        group_id = self.my_group_id()
        if group_id is None:
            return []
        return self.store.list_students(group_id)

    def can_access_student(self, student: Optional[Student]) -> bool:
        if student is None:
            return False
        if self.is_admin():
            return True
        return student.group_id == self.my_group_id()

    def menu_students(self) -> None:
        if not self.is_admin() and self.my_group_id() is None:
            print("\nSizga hech qanday guruh biriktirilmagan. Administrator bilan bog'laning.")
            pause()
            return

        while True:
            self.list_students()
            print(
                "\nO'quvchilar menyusi:\n"
                " 1) Yangi o'quvchi qo'shish\n"
                " 2) O'quvchini tahrirlash\n"
                " 3) O'quvchini o'chirish\n"
                " 4) Bugun keldi (tezkor davomat)\n"
                " 5) To'lov holatini almashtirish\n"
                " 6) O'quvchi profilini ko'rish (davomat tarixi, uy vazifasi)\n"
                " 0) Orqaga"
            )
            choice = input("Tanlang: ").strip()
            if choice == "0":
                return
            elif choice == "1":
                self.add_student()
            elif choice == "2":
                self.edit_student()
            elif choice == "3":
                self.remove_student()
            elif choice == "4":
                self.quick_attendance()
            elif choice == "5":
                self.toggle_paid()
            elif choice == "6":
                self.view_student_profile()
            else:
                print("Noto'g'ri tanlov.")

    def print_student_table(self, students: list[Student]) -> None:
        for s in students:
            group = self.store.get_group(s.group_id) if s.group_id else None
            status = "To'langan" if s.paid else "Qarzdor"
            print(
                f"[{s.id}] {s.name} -- {group.name if group else 'Guruhsiz'} -- "
                f"UZS {fmt_money(s.monthly_fee)} -- {status} -- "
                f"Uy vazifasi qoldirilgan: {s.homework_missed}"
            )

    def list_students(self) -> None:
        title = "O'quvchilar ro'yxati" if self.is_admin() else "Mening o'quvchilarim"
        print(f"\n--- {title} ---")
        students = self.accessible_students()
        if not students:
            print("Hozircha o'quvchilar yo'q.")
            return
        self.print_student_table(students)

    def choose_group_or_none(self, default_id: Optional[int] = None) -> Optional[int]:
        if not self.is_admin():
            # O'qituvchi o'quvchini faqat o'z guruhiga qo'shadi -- tanlash shart emas.
            return self.my_group_id()
        if self.store.groups:
            print("Mavjud guruhlar: " + ", ".join(f"[{g.id}] {g.name}" for g in self.store.groups))
        return prompt_int("Guruh ID raqami (bo'sh qoldirsangiz guruhsiz)", default_id)

    def add_student(self) -> None:
        name = prompt("O'quvchi F.I.O")
        if not name:
            print("Ism bo'sh bo'lishi mumkin emas.")
            return
        group_id = self.choose_group_or_none()
        if group_id is not None and not self.store.get_group(group_id):
            print("Bunday guruh topilmadi, o'quvchi guruhsiz qo'shiladi.")
            group_id = None
        phone = prompt("Ota-ona telefon raqami")
        fee = prompt_float("Oylik to'lov miqdori (UZS)", 0.0)
        note = prompt("Izoh")
        student = self.store.add_student(name, group_id, phone or None, fee, note or None)
        print(f"O'quvchi qo'shildi: [{student.id}] {student.name}")

    def edit_student(self) -> None:
        student_id = prompt_int("Tahrirlanadigan o'quvchi ID raqami")
        if student_id is None:
            return
        student = self.store.get_student(student_id)
        if not self.can_access_student(student):
            print("Bunday o'quvchi topilmadi.")
            return
        name = prompt("F.I.O", student.name)
        group_id = self.choose_group_or_none(student.group_id)
        phone = prompt("Ota-ona telefon raqami", student.parent_phone or "")
        fee = prompt_float("Oylik to'lov miqdori (UZS)", student.monthly_fee)
        note = prompt("Izoh", student.note or "")
        self.store.update_student(
            student_id,
            name=name,
            group_id=group_id,
            parent_phone=phone or None,
            monthly_fee=fee,
            note=note or None,
        )
        print("O'quvchi ma'lumotlari yangilandi.")

    def remove_student(self) -> None:
        student_id = prompt_int("O'chiriladigan o'quvchi ID raqami")
        if student_id is None:
            return
        student = self.store.get_student(student_id)
        if not self.can_access_student(student):
            print("Bunday o'quvchi topilmadi.")
            return
        if self.store.delete_student(student_id):
            print("O'quvchi o'chirildi.")
        else:
            print("Bunday o'quvchi topilmadi.")

    def quick_attendance(self) -> None:
        student_id = prompt_int("O'quvchi ID raqami")
        if student_id is None:
            return
        student = self.store.get_student(student_id)
        if not self.can_access_student(student):
            print("Bunday o'quvchi topilmadi.")
            return
        record = self.store.add_attendance(student_id, today_date(), now_time())
        print(f"Belgilandi: {student.name} bugun ({record.date} {record.time}) keldi.")

    def toggle_paid(self) -> None:
        student_id = prompt_int("O'quvchi ID raqami")
        if student_id is None:
            return
        student = self.store.get_student(student_id)
        if not self.can_access_student(student):
            print("Bunday o'quvchi topilmadi.")
            return
        self.store.update_student(student_id, paid=not student.paid)
        status = "to'langan" if not student.paid else "qarzdor"
        print(f"{student.name} endi: {status}.")

    def view_student_profile(self) -> None:
        student_id = prompt_int("O'quvchi ID raqami")
        if student_id is None:
            return
        student = self.store.get_student(student_id)
        if not self.can_access_student(student):
            print("Bunday o'quvchi topilmadi.")
            return

        group = self.store.get_group(student.group_id) if student.group_id else None
        records = self.store.list_attendance(student_id)
        this_month = self.store.attendance_count_this_month(student_id)

        print(f"\n--- {student.name} profili ---")
        print(f"Guruh:                 {group.name if group else 'Guruhsiz'}")
        print(f"Telefon:               {student.parent_phone or '-'}")
        print(f"Oylik to'lov:          UZS {fmt_money(student.monthly_fee)}")
        print(f"To'lov holati:         {'To`langan' if student.paid else 'Qarzdor'}")
        print(f"Bajarilmagan vazifalar: {student.homework_missed}")
        print(f"Bu oy qatnashdi:       {this_month} marta")
        print(f"Jami qatnashdi:        {len(records)} marta")
        print(f"Izoh:                  {student.note or '-'}")

        print("\nDavomat tarixi:")
        if not records:
            print("  Hali davomat qayd etilmagan.")
        for r in records:
            print(f"  [{r.id}] {r.date} {r.time}")

        print(
            "\n 1) Bugun keldi belgilash\n"
            " 2) Davomat yozuvini o'chirish\n"
            " 3) Uy vazifasi sonini +1\n"
            " 4) Uy vazifasi sonini -1\n"
            " 0) Orqaga"
        )
        choice = input("Tanlang: ").strip()
        if choice == "1":
            record = self.store.add_attendance(student_id, today_date(), now_time())
            print(f"Belgilandi: {record.date} {record.time}.")
        elif choice == "2":
            attendance_id = prompt_int("O'chiriladigan davomat ID raqami")
            if attendance_id is not None:
                if self.store.delete_attendance(attendance_id):
                    print("Davomat yozuvi o'chirildi.")
                else:
                    print("Bunday yozuv topilmadi.")
        elif choice == "3":
            self.store.update_student(student_id, homework_missed=student.homework_missed + 1)
            print("Yangilandi.")
        elif choice == "4":
            self.store.update_student(
                student_id, homework_missed=max(0, student.homework_missed - 1)
            )
            print("Yangilandi.")
        pause()

    # ------------------------------------------------------------------ #
    # Users (faqat admin uchun): kirish kodlarini boshqarish
    # ------------------------------------------------------------------ #
    def menu_users(self) -> None:
        while True:
            self.list_users()
            print(
                "\nFoydalanuvchilar menyusi:\n"
                " 1) Yangi hisob qo'shish (admin yoki o'qituvchi)\n"
                " 2) Kirish kodini o'zgartirish\n"
                " 3) O'qituvchiga guruh biriktirish\n"
                " 4) Hisobni o'chirish\n"
                " 0) Orqaga"
            )
            choice = input("Tanlang: ").strip()
            if choice == "0":
                return
            elif choice == "1":
                self.add_user()
            elif choice == "2":
                self.change_user_code()
            elif choice == "3":
                self.assign_teacher_group()
            elif choice == "4":
                self.remove_user()
            else:
                print("Noto'g'ri tanlov.")

    def list_users(self) -> None:
        print("\n--- Foydalanuvchilar va kirish kodlari ---")
        for u in self.store.list_users():
            if u.role == "admin":
                print(f"[{u.id}] {u.name} -- Administrator -- kod: {u.code}")
            else:
                group = self.store.get_group(u.group_id) if u.group_id else None
                print(
                    f"[{u.id}] {u.name} -- O'qituvchi -- kod: {u.code} -- "
                    f"guruhi: {group.name if group else 'biriktirilmagan'}"
                )

    def add_user(self) -> None:
        name = prompt("Ism")
        if not name:
            print("Ism bo'sh bo'lishi mumkin emas.")
            return
        role_raw = prompt("Roli (admin / oqituvchi)", "oqituvchi").lower()
        role = "admin" if role_raw.startswith("admin") else "teacher"

        group_id = None
        if role == "teacher":
            if self.store.groups:
                print("Mavjud guruhlar: " + ", ".join(f"[{g.id}] {g.name}" for g in self.store.groups))
            group_id = prompt_int("Biriktiriladigan guruh ID raqami (bo'sh qoldirish mumkin)")
            if group_id is not None and not self.store.get_group(group_id):
                print("Bunday guruh topilmadi, guruhsiz qo'shiladi.")
                group_id = None

        while True:
            code = prompt("Kirish kodi (PIN)")
            if not code:
                print("Kod bo'sh bo'lishi mumkin emas.")
                continue
            if self.store.code_taken(code):
                print("Bu kod band, boshqa kod kiriting.")
                continue
            break

        user = self.store.add_user(name, role, code, group_id)
        role_label = "Administrator" if user.role == "admin" else "O'qituvchi"
        print(f"Hisob qo'shildi: [{user.id}] {user.name} ({role_label}), kod: {user.code}")

    def change_user_code(self) -> None:
        user_id = prompt_int("Foydalanuvchi ID raqami")
        if user_id is None:
            return
        user = self.store.get_user(user_id)
        if not user:
            print("Bunday foydalanuvchi topilmadi.")
            return
        while True:
            code = prompt("Yangi kirish kodi", user.code)
            if self.store.code_taken(code, exclude_user_id=user_id):
                print("Bu kod band, boshqa kod kiriting.")
                continue
            break
        self.store.update_user(user_id, code=code)
        print("Kod yangilandi.")

    def assign_teacher_group(self) -> None:
        user_id = prompt_int("O'qituvchi ID raqami")
        if user_id is None:
            return
        user = self.store.get_user(user_id)
        if not user or user.role != "teacher":
            print("Bunday o'qituvchi topilmadi.")
            return
        if self.store.groups:
            print("Mavjud guruhlar: " + ", ".join(f"[{g.id}] {g.name}" for g in self.store.groups))
        group_id = prompt_int("Biriktiriladigan guruh ID raqami (bo'sh qoldirsangiz guruhsiz)")
        if group_id is not None and not self.store.get_group(group_id):
            print("Bunday guruh topilmadi.")
            return
        self.store.update_user(user_id, group_id=group_id)
        print("Guruh biriktirildi.")

    def remove_user(self) -> None:
        user_id = prompt_int("O'chiriladigan foydalanuvchi ID raqami")
        if user_id is None:
            return
        if self.current_user and user_id == self.current_user.id:
            print("O'zingizning joriy hisobingizni o'chira olmaysiz.")
            return
        if self.store.delete_user(user_id):
            print("Hisob o'chirildi.")
        else:
            print("Bunday foydalanuvchi topilmadi.")


def today_prefix() -> str:
    now = datetime.now()
    return f"{now.year:04d}-{now.month:02d}"


if __name__ == "__main__":
    App().run()