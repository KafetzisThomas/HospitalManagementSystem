# reference: https://docs.python.org/3/library/sqlite3.html

import datetime
import platform
import sqlite3
import subprocess
import sys

import colorama
from colorama import Fore

colorama.init(autoreset=True)

banner = r"""
██╗  ██╗ ██████╗ ███████╗██████╗ ██╗████████╗ █████╗ ██╗         ██████╗ ██████╗ 
██║  ██║██╔═══██╗██╔════╝██╔══██╗██║╚══██╔══╝██╔══██╗██║         ██╔══██╗██╔══██╗
███████║██║   ██║███████╗██████╔╝██║   ██║   ███████║██║         ██║  ██║██████╔╝
██╔══██║██║   ██║╚════██║██╔═══╝ ██║   ██║   ██╔══██║██║         ██║  ██║██╔══██╗
██║  ██║╚██████╔╝███████║██║     ██║   ██║   ██║  ██║███████╗    ██████╔╝██████╔╝
╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝     ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝    ╚═════╝ ╚═════╝ 
                                                                                 
A Hospital Patient Management System / Σύστημα Διαχείρισης Ασθενών Νοσοκομείου

Project Team:
Thomas Kafetzis | Dimitrios Giamos | Ermis Sofos | Dimitrios Kariotis | Spyridon Vletsos
Eleftherios Tirnenopoulos | Alexandros-Argyris Anezinis | Dimitra Kontogianni
"""

clear_command = "cls" if platform.system() == "Windows" else "clear"
subprocess.run(clear_command, shell=True, check=False)

connection = sqlite3.connect("hospital.db")
cursor = connection.cursor()
cursor.execute("PRAGMA foreign_keys = ON")  # enable foreign keys

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

def display_records(db_table):
    print(f"\n--- {db_table.upper()} ---")
    for row in cursor.execute(f"SELECT * FROM {db_table}"):
        print(row)

def add_new_patient(amka, onoma, epitheto, imerominia_gennisis, filo, tipos_aimotos, arithmos_tilefwnou, email, diefthinsi, is_active):
    cursor.execute("INSERT INTO patients (amka, onoma, epitheto, imerominia_gennisis, filo, tipos_aimotos, arithmos_tilefwnou, email, diefthinsi, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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

def main():
    print(banner)
    print("1. Show all tables")
    print("2. Add new patient")
    print("3. Add new doctor")
    print("4. Add new appointment")
    print("5. Exit")

    try:
        choice = input("\nChoice: ")
    except KeyboardInterrupt:
        print(f"\n{Fore.LIGHTCYAN_EX}[!] Exiting...")
        connection.close()
        sys.exit()

    if choice == '1':
        display_records("patients")
        display_records("doctors")
        display_records("appointments")

    elif choice == '2':
        amka = input("AMKA: ")
        onoma = input("Onoma: ")
        epitheto = input("Epitheto: ")
        imerominia_gennisis = input("Imerominia Gennisis: ")
        filo = input("Filo: ")
        tipos_aimotos = input("Tipos Aimotos: ")
        arithmos_tilefwnou = input("Arithmos Tilefwnou: ")
        email = input("Email: ")
        diefthinsi = input("Diefthinsi: ")
        is_active = 1

        try:
            add_new_patient(amka, onoma, epitheto, imerominia_gennisis, filo, tipos_aimotos, arithmos_tilefwnou, email, diefthinsi, is_active)
            print(f"{Fore.GREEN}[+] Patient added successfully.")
        except sqlite3.IntegrityError:
            print(f"{Fore.RED}[-] Patient already exists.")

    elif choice == '3':
        onoma = input("Onoma: ")
        epitheto = input("Epitheto: ")
        eidikotita = input("Eidikotita: ")
        arithmos_tilefwnou = input("Arithmos Tilefwnou: ")
        email = input("Email: ")
        
        try:
            add_new_doctor(onoma, epitheto, eidikotita, arithmos_tilefwnou, email)
            print(f"{Fore.GREEN}[+] Doctror added successfully.")
        except sqlite3.IntegrityError:
            print(f"{Fore.RED}[-] Doctor already exists.")

    elif choice == '4':
        patient_amka = input("Patient AMKA: ")
        doctor_id = input("Doctor ID: ")
        imerominia_episkepsis = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        aitia = input("Aitia: ")
        is_active = 1

        try:
            add_new_appointment(patient_amka, int(doctor_id), imerominia_episkepsis, aitia, is_active)
            print(f"{Fore.GREEN}[+] Appointment added successfully.")
        except sqlite3.IntegrityError:
            print(f"{Fore.RED}[-] Invalid patient amka or doctor id.")

    elif choice == '5':
        print(f"{Fore.LIGHTCYAN_EX}[!] Exiting...")
        connection.close()
        sys.exit()

    else:
        print(f"{Fore.RED}[-] Invalid choice.")

if __name__ == '__main__':
    main()
