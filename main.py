#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
A Hospital Patient Management System / Σύστημα Διαχείρισης Ασθενών Νοσοκομείου

Project Team:
Thomas Kafetzis | Dimitrios Giamos | Ermis Sofos | Dimitrios Kariotis | Spyridon Vletsos
Eleftherios Tirnenopoulos | Alexandros-Argyris Anezinis | Dimitra Kontogianni

Sources:
- https://docs.python.org/3/library/sqlite3.html
- https://doc.qt.io/qtforpython-6/
"""

import datetime
import sqlite3
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

connection = sqlite3.connect("hospital.db")
cursor = connection.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

cursor.execute("""
CREATE TABLE IF NOT EXISTS patients(
    amka TEXT PRIMARY KEY,
    onoma TEXT NOT NULL,
    epitheto TEXT NOT NULL,
    imerominia_gennisis TEXT NOT NULL,
    filo TEXT NOT NULL,
    tipos_aimotos TEXT,
    arithmos_tilefwnou TEXT NOT NULL,
    email TEXT,
    diefthinsi TEXT,
    is_active INTEGER NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS doctors(
    doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    onoma TEXT NOT NULL,
    epitheto TEXT NOT NULL,
    eidikotita TEXT NOT NULL,
    arithmos_tilefwnou TEXT NOT NULL,
    email TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments(
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_amka TEXT NOT NULL,
    doctor_id INTEGER NOT NULL,
    imerominia_episkepsis TEXT NOT NULL,
    aitia TEXT NOT NULL,
    is_active INTEGER NOT NULL,
    FOREIGN KEY (patient_amka) REFERENCES patients (amka) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id)
)
""")

connection.commit()

# db helpers

def add_new_patient(amka, onoma, epitheto, imerominia_gennisis, filo, tipos_aimotos, arithmos_tilefwnou, email, diefthinsi, is_active):
    cursor.execute("INSERT INTO patients VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (amka, onoma, epitheto, imerominia_gennisis, filo, tipos_aimotos, arithmos_tilefwnou, email, diefthinsi, is_active))
    connection.commit()

def add_new_doctor(onoma, epitheto, eidikotita, arithmos_tilefwnou, email):
    cursor.execute("INSERT INTO doctors (onoma, epitheto, eidikotita, arithmos_tilefwnou, email) VALUES (?, ?, ?, ?, ?)",
        (onoma, epitheto, eidikotita, arithmos_tilefwnou, email))
    connection.commit()

def add_new_appointment(patient_amka, doctor_id, imerominia_episkepsis, aitia, is_active):
    cursor.execute("INSERT INTO appointments (patient_amka, doctor_id, imerominia_episkepsis, aitia, is_active) VALUES (?, ?, ?, ?, ?)",
        (patient_amka, doctor_id, imerominia_episkepsis, aitia, is_active))
    connection.commit()


class HospitalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hospital DB — Σύστημα Διαχείρισης Ασθενών Νοσοκομείου")
        self.resize(1100, 680)
        self.setMinimumSize(900, 550)

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # sidebar
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 0, 0, 0)
        sb_layout.setSpacing(0)

        # logo area
        logo_area = QVBoxLayout()
        logo_area.setContentsMargins(0, 30, 0, 0)
        logo_area.setSpacing(2)
        icon = QLabel("🏥")
        icon.setFont(QFont("Segoe UI", 28))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_area.addWidget(icon)
        title = QLabel("Hospital DB")
        title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_area.addWidget(title)
        sub = QLabel("Management System")
        sub.setFont(QFont("Segoe UI", 9))
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_area.addWidget(sub)
        sb_layout.addLayout(logo_area)

        sb_layout.addSpacing(20)

        # nav buttons
        self._nav_buttons: list[QPushButton] = []
        nav_items = [
            ("📋  Προβολή Εγγραφών", 0),
            ("🧑  Νέος Ασθενής", 1),
            ("🩺  Νέος Γιατρός", 2),
            ("📅  Νέο Ραντεβού", 3),
        ]

        for label, page_index in nav_items:
            btn = QPushButton(label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, i=page_index: self._show_page(i))
            sb_layout.addWidget(btn)
            self._nav_buttons.append(btn)

        sb_layout.addStretch()
        root_layout.addWidget(sidebar)

        # stacked pages
        self.stack = QStackedWidget()
        self.stack.setObjectName("content")
        root_layout.addWidget(self.stack)

        self._build_records_page()
        self._build_patient_form()
        self._build_doctor_form()
        self._build_appointment_form()

        self._show_page(0)

    # == navigation ==

    def _show_page(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self._nav_buttons):
            btn.setChecked(i == index)
        if index == 0:
            self._refresh_records()

    # records page
    def _build_records_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 25, 30, 25)

        heading = QLabel("Όλες οι Εγγραφές")
        heading.setObjectName("pageTitle")
        layout.addWidget(heading)
        sub = QLabel("Προβολή ασθενών, γιατρών και ραντεβού")
        sub.setObjectName("pageSubtitle")
        layout.addWidget(sub)
        layout.addSpacing(10)

        # tab bar
        tab_bar = QWidget()
        tab_bar.setObjectName("tabBar")
        tb_layout = QHBoxLayout(tab_bar)
        tb_layout.setContentsMargins(0, 0, 0, 0)
        tb_layout.setSpacing(4)

        self._tab_btns: list[QPushButton] = []
        self._current_table = "patients"
        for label, table in [("Ασθενείς", "patients"), ("Γιατροί", "doctors"), ("Ραντεβού", "appointments")]:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, t=table: self._switch_tab(t))
            tb_layout.addWidget(btn)
            self._tab_btns.append(btn)
        tb_layout.addStretch()
        layout.addWidget(tab_bar)

        # table
        self._table = QTableWidget()
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.verticalHeader().setVisible(False)
        layout.addWidget(self._table)

        self.stack.addWidget(page)

    def _switch_tab(self, table: str):
        self._current_table = table
        self._refresh_records()

    def _refresh_records(self):
        table = self._current_table
        tables = ["patients", "doctors", "appointments"]
        for i, btn in enumerate(self._tab_btns):
            btn.setChecked(tables[i] == table)

        cols_map = {
            "patients": ("ΑΜΚΑ", "Όνομα", "Επίθετο", "Ημερομηνία Γέννησης", "Φύλο", "Τύπος Αίματος", "Τηλέφωνο", "Email", "Διεύθυνση", "Κατάσταση"),
            "doctors": ("ID", "Όνομα", "Επίθετο", "Ειδικότητα", "Τηλέφωνο", "Email"),
            "appointments": ("ID", "AMKA Ασθενή", "ID Γιατρού", "Ημερομηνία Επίσκεψης", "Αιτιολογία", "Κατάσταση"),
        }
        cols = cols_map[table]
        rows = cursor.execute(f"SELECT * FROM {table}").fetchall()

        self._table.setColumnCount(len(cols))
        self._table.setRowCount(len(rows))
        self._table.setHorizontalHeaderLabels(cols)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                self._table.setItem(r, c, QTableWidgetItem(str(val)))

    # == form builder helper ==

    @staticmethod
    def _make_form(page_layout, title: str, subtitle: str, fields: list[tuple[str, str]]) -> dict[str, QLineEdit]:
        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        page_layout.addWidget(heading)
        sub = QLabel(subtitle)
        sub.setObjectName("pageSubtitle")
        page_layout.addWidget(sub)
        page_layout.addSpacing(14)

        card = QWidget()
        card.setObjectName("card")
        form = QFormLayout(card)
        form.setContentsMargins(24, 20, 24, 20)
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        entries: dict[str, QLineEdit] = {}
        for key, label_text in fields:
            line = QLineEdit()
            line.setMinimumHeight(32)
            form.addRow(label_text, line)
            entries[key] = line

        page_layout.addWidget(card)
        return entries

    # == patient form ==

    def _build_patient_form(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 25, 30, 25)

        fields = [
            ("amka", "ΑΜΚΑ *"),
            ("onoma", "Όνομα *"),
            ("epitheto", "Επίθετο *"),
            ("dob", "Ημερομηνία Γέννησης *"),
            ("filo", "Φύλο *"),
            ("blood", "Τύπος Αίματος"),
            ("phone", "Τηλέφωνο *"),
            ("email", "Email"),
            ("address", "Διεύθυνση"),
        ]
        self._pat_entries = self._make_form(layout, "Νέος Ασθενής", "Καταχώρηση νέου ασθενή", fields)
        btn = QPushButton("Προσθήκη Ασθενή")
        btn.setObjectName("submitBtn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self._submit_patient)
        layout.addSpacing(8)
        layout.addWidget(btn)
        layout.addStretch()
        self.stack.addWidget(page)

    def _submit_patient(self):
        e = self._pat_entries
        required = ["amka", "onoma", "epitheto", "dob", "filo", "phone"]
        for key in required:
            if not e[key].text().strip():
                QMessageBox.warning(self, "Missing field", "Παρακαλώ συμπληρώστε όλα τα υποχρεωτικά (*) πεδία.")
                return
        try:
            add_new_patient(
                e["amka"].text().strip(),
                e["onoma"].text().strip(),
                e["epitheto"].text().strip(),
                e["dob"].text().strip(),
                e["filo"].text().strip(),
                e["blood"].text().strip(),
                e["phone"].text().strip(),
                e["email"].text().strip(),
                e["address"].text().strip(), 1
            )

            QMessageBox.information(self, "Success", "Ο ασθενής προστέθηκε επιτυχώς.")

            for entry in e.values():
                entry.clear()
        except sqlite3.IntegrityError:
            QMessageBox.critical(self, "Error", "Υπάρχει ήδη ασθενής με αυτό το ΑΜΚΑ.")

    # == doctor form ==

    def _build_doctor_form(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 25, 30, 25)

        fields = [("onoma", "Όνομα *"), ("epitheto", "Επίθετο *"), ("eidikotita", "Ειδικότητα *"), ("phone", "Τηλέφωνο *"), ("email", "Email")]
        self._doc_entries = self._make_form(layout, "Νέος Γιατρός", "Καταχώρηση νέου γιατρού", fields)
        btn = QPushButton("Προσθήκη Γιατρού")
        btn.setObjectName("submitBtn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self._submit_doctor)
        layout.addSpacing(8)
        layout.addWidget(btn)
        layout.addStretch()
        self.stack.addWidget(page)

    def _submit_doctor(self):
        e = self._doc_entries
        required = ["onoma", "epitheto", "eidikotita", "phone"]
        for key in required:
            if not e[key].text().strip():
                QMessageBox.warning(self, "Missing field", "Παρακαλώ συμπληρώστε όλα τα υποχρεωτικά (*) πεδία.")
                return
        try:
            add_new_doctor(
                e["onoma"].text().strip(),
                e["epitheto"].text().strip(),
                e["eidikotita"].text().strip(),
                e["phone"].text().strip(),
                e["email"].text().strip()
            )

            QMessageBox.information(self, "Success", "Ο γιατρός προστέθηκε επιτυχώς.")

            for entry in e.values():
                entry.clear()
        except sqlite3.IntegrityError:
            QMessageBox.critical(self, "Error", "Ο γιατρός υπάρχει ήδη.")

    # == appointment form ==

    def _build_appointment_form(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 25, 30, 25)

        fields = [("amka", "AMKA Ασθενή *"), ("doctor_id", "ID Γιατρού *"), ("aitia", "Αιτιολογία *")]
        self._apt_entries = self._make_form(layout, "Νέο Ραντεβού", "Προγραμματισμός νέου ραντεβού", fields)
        btn = QPushButton("Προγραμματισμός")
        btn.setObjectName("submitBtn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self._submit_appointment)
        layout.addSpacing(8)
        layout.addWidget(btn)
        layout.addStretch()
        self.stack.addWidget(page)

    def _submit_appointment(self):
        e = self._apt_entries
        for key in ("amka", "doctor_id", "aitia"):
            if not e[key].text().strip():
                QMessageBox.warning(self, "Missing field", "Παρακαλώ συμπληρώστε όλα τα υποχρεωτικά (*) πεδία.")
                return
        try:
            time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            add_new_appointment(e["amka"].text().strip(), int(e["doctor_id"].text().strip()), time_now, e["aitia"].text().strip(), 1)
            QMessageBox.information(self, "Success", "Το ραντεβού καταχωρήθηκε επιτυχώς.")

            for entry in e.values():
                entry.clear()
        except (sqlite3.IntegrityError, ValueError):
            QMessageBox.critical(self, "Error", "Μη έγκυρο ΑΜΚΑ ασθενή ή ID γιατρού.")

    def closeEvent(self, event):
        connection.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("logo.png"))

    with open("styles.qss", "r", encoding="utf-8") as file:
        app.setStyleSheet(file.read())

    app.setFont(QFont("Segoe UI", 10))
    window = HospitalApp()
    window.show()
    sys.exit(app.exec())
