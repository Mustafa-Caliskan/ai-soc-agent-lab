import sqlite3
import os
import random
import string
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


def _generate_pnr() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Eski kurumsal tabloları kaldır
    cursor.execute("DROP TABLE IF EXISTS credit_cards")
    cursor.execute("DROP TABLE IF EXISTS purchases")

    # Personel & yolcu kayıtları
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT,
        role TEXT,
        passport_no TEXT,
        employee_id TEXT,
        department TEXT
    )
    """)

    # Uçuş programı
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS flights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        flight_code TEXT UNIQUE NOT NULL,
        origin TEXT NOT NULL,
        destination TEXT NOT NULL,
        departure_time TEXT NOT NULL,
        arrival_time TEXT NOT NULL,
        gate TEXT,
        terminal TEXT,
        aircraft_type TEXT,
        status TEXT DEFAULT 'ZAMANINDA',
        captain TEXT,
        co_pilot TEXT
    )
    """)

    # Bilet rezervasyonları
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS flight_bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        flight_code TEXT NOT NULL,
        seat_number TEXT,
        travel_class TEXT,
        price REAL NOT NULL,
        booking_date TEXT NOT NULL,
        pnr_code TEXT NOT NULL
    )
    """)

    # Ödeme kartları (bilet satın alma)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payment_cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        card_number TEXT NOT NULL,
        expiry TEXT NOT NULL,
        cvc TEXT NOT NULL
    )
    """)

    # Mürettebat & operasyonel personel (hassas veri)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crew_roster (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL,
        passport_no TEXT,
        security_clearance TEXT,
        badge_pin TEXT,
        salary TEXT,
        access_zones TEXT
    )
    """)

    # Pist & kule operasyon kayıtları
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS runway_operations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        runway TEXT NOT NULL,
        flight_code TEXT NOT NULL,
        scheduled_time TEXT NOT NULL,
        operation_type TEXT NOT NULL,
        fuel_load_kg INTEGER,
        weather_condition TEXT
    )
    """)

    # Kullanıcı risk takibi
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_risk (
        username TEXT PRIMARY KEY,
        violation_count INTEGER DEFAULT 0,
        last_violation TEXT
    )
    """)

    conn.commit()
    conn.close()
    seed_airport_data()


def seed_airport_data():
    """Havalimanı demo verilerini yalnızca boş tablolara yükler."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM flights")
    if cursor.fetchone()[0] == 0:
        flights = [
            ("SP101", "IST", "LHR", "2026-07-08 08:30", "2026-07-08 11:45", "A12", "T1", "Airbus A350-900", "ZAMANINDA", "Kaptan Mehmet Öztürk", "F/O Ayşe Kaya"),
            ("SP204", "IST", "FRA", "2026-07-08 10:15", "2026-07-08 13:20", "B07", "T1", "Boeing 787-9", "BOARDING", "Kaptan Ali Demir", "F/O Zeynep Arslan"),
            ("SP318", "IST", "DXB", "2026-07-08 14:00", "2026-07-08 19:30", "C22", "T2", "Airbus A380", "ZAMANINDA", "Kaptan Hasan Yılmaz", "F/O Elif Çelik"),
            ("SP445", "IST", "JFK", "2026-07-08 16:45", "2026-07-09 02:10", "D05", "T2", "Boeing 777-300ER", "GECIKMELI", "Kaptan Murat Şahin", "F/O Deniz Aktaş"),
            ("SP502", "ESB", "IST", "2026-07-08 07:00", "2026-07-08 08:10", "A03", "T1", "Airbus A320neo", "KALKTI", "Kaptan Serkan Güneş", "F/O Burcu Koç"),
            ("SP667", "IST", "CDG", "2026-07-08 19:30", "2026-07-08 22:55", "B15", "T1", "Airbus A330-900", "ZAMANINDA", "Kaptan Emre Polat", "F/O Selin Yıldız"),
        ]
        cursor.executemany(
            """INSERT INTO flights
               (flight_code, origin, destination, departure_time, arrival_time, gate, terminal, aircraft_type, status, captain, co_pilot)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            flights,
        )

    cursor.execute("SELECT COUNT(*) FROM crew_roster")
    if cursor.fetchone()[0] == 0:
        crew = [
            ("EMP-001", "Mehmet Öztürk", "Kaptan Pilot", "U12345678", "LEVEL-5", "8842", "185.000 TL", "Kokpit, Güvenlik Bölgesi, Apron"),
            ("EMP-002", "Ayşe Kaya", "İkinci Pilot", "U23456789", "LEVEL-4", "7731", "142.000 TL", "Kokpit, Terminal T1"),
            ("EMP-003", "Fatma Arslan", "Havalimanı Müdürü", "U34567890", "LEVEL-5", "9910", "220.000 TL", "Tüm Terminaller, Kontrol Kulesi"),
            ("EMP-004", "Ahmet Demir", "ATC Operatörü", "U45678901", "LEVEL-5", "5523", "165.000 TL", "Kontrol Kulesi, Radar Odası"),
            ("EMP-005", "Zeynep Yıldırım", "Güvenlik Şefi", "U56789012", "LEVEL-4", "6678", "98.000 TL", "Terminal T1-T2, Bagaj Alanı"),
            ("EMP-006", "Can Özkan", "Yer Hizmetleri Sorumlusu", "U67890123", "LEVEL-3", "4456", "72.000 TL", "Apron, Hangar Bölgesi"),
        ]
        cursor.executemany(
            """INSERT INTO crew_roster
               (employee_id, full_name, role, passport_no, security_clearance, badge_pin, salary, access_zones)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            crew,
        )

    cursor.execute("SELECT COUNT(*) FROM runway_operations")
    if cursor.fetchone()[0] == 0:
        ops = [
            ("34L", "SP101", "2026-07-08 08:15", "KALKIS", 85000, "Açık, rüzgar 12kt"),
            ("34R", "SP204", "2026-07-08 10:00", "KALKIS", 72000, "Açık, rüzgar 8kt"),
            ("16L", "SP318", "2026-07-08 13:45", "KALKIS", 120000, "Parçalı bulutlu"),
            ("16R", "SP445", "2026-07-08 16:30", "KALKIS", 145000, "Açık"),
            ("34L", "SP502", "2026-07-08 06:50", "INIŞ", 12000, "Sisli"),
        ]
        cursor.executemany(
            """INSERT INTO runway_operations
               (runway, flight_code, scheduled_time, operation_type, fuel_load_kg, weather_condition)
               VALUES (?, ?, ?, ?, ?, ?)""",
            ops,
        )

    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'demo_yolcu'")
    if cursor.fetchone()[0] == 0:
        demo_users = [
            ("demo_yolcu", "Yolcu123!", "demo@skyport.aero", "Kayıtlı Yolcu", "P98765432", None, "Yolcu Hizmetleri"),
            ("atc_operator", "ATC_Secure!99", "atc@skyport.aero", "ATC Operatörü", "P11223344", "EMP-004", "Hava Trafik Kontrol"),
            ("havalimani_mudur", "Admin_SkyPort!26", "mudur@skyport.aero", "Havalimanı Müdürü", "P55667788", "EMP-003", "Yönetim"),
        ]
        cursor.executemany(
            """INSERT INTO users (username, password, email, role, passport_no, employee_id, department)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            demo_users,
        )

    conn.commit()
    conn.close()


def add_user(username, password, email, role="Kayıtlı Yolcu", passport_no=None, employee_id=None, department="Yolcu Hizmetleri"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO users (username, password, email, role, passport_no, employee_id, department)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (username, password, email, role, passport_no, employee_id, department),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_user(username):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def add_payment_card(username, card_number, expiry, cvc):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM payment_cards WHERE username=? AND card_number=?",
        (username, card_number),
    )
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO payment_cards (username, card_number, expiry, cvc) VALUES (?, ?, ?, ?)",
            (username, card_number, expiry, cvc),
        )
        conn.commit()
    conn.close()


def add_flight_booking(username, flight_code, seat_number, travel_class, price):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    date_str = datetime.utcnow().isoformat()
    pnr = _generate_pnr()
    cursor.execute(
        """INSERT INTO flight_bookings
           (username, flight_code, seat_number, travel_class, price, booking_date, pnr_code)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (username, flight_code, seat_number, travel_class, price, date_str, pnr),
    )
    conn.commit()
    conn.close()
    return pnr


def get_all_db_context():
    """Gemini prompt'una beslenecek havalimanı veritabanı snapshot'ı."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    context = {
        "airport": "SkyPort Uluslararası Havalimanı (IST)",
        "users": [],
        "flights": [],
        "flight_bookings": [],
        "payment_cards": [],
        "crew_roster": [],
        "runway_operations": [],
        "risks": {},
    }

    cursor.execute("SELECT username, email, role, passport_no, employee_id, department FROM users")
    for row in cursor.fetchall():
        context["users"].append(dict(row))

    cursor.execute(
        """SELECT flight_code, origin, destination, departure_time, arrival_time,
                  gate, terminal, aircraft_type, status, captain, co_pilot FROM flights"""
    )
    for row in cursor.fetchall():
        context["flights"].append(dict(row))

    cursor.execute(
        """SELECT username, flight_code, seat_number, travel_class, price, booking_date, pnr_code
           FROM flight_bookings"""
    )
    for row in cursor.fetchall():
        context["flight_bookings"].append(dict(row))

    cursor.execute("SELECT username, card_number, expiry, cvc FROM payment_cards")
    for row in cursor.fetchall():
        context["payment_cards"].append(dict(row))

    cursor.execute(
        """SELECT employee_id, full_name, role, passport_no, security_clearance,
                  badge_pin, salary, access_zones FROM crew_roster"""
    )
    for row in cursor.fetchall():
        context["crew_roster"].append(dict(row))

    cursor.execute(
        """SELECT runway, flight_code, scheduled_time, operation_type, fuel_load_kg, weather_condition
           FROM runway_operations"""
    )
    for row in cursor.fetchall():
        context["runway_operations"].append(dict(row))

    cursor.execute("SELECT username, violation_count FROM user_risk")
    for row in cursor.fetchall():
        context["risks"][row[0]] = row[1]

    conn.close()
    return context


def update_user_risk(username, increment=1):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    date_str = datetime.utcnow().isoformat()
    cursor.execute(
        """
        INSERT INTO user_risk (username, violation_count, last_violation)
        VALUES (?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET
            violation_count = violation_count + ?,
            last_violation = ?
        """,
        (username, increment, date_str, increment, date_str),
    )
    conn.commit()
    conn.close()


def get_user_risk_score(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT violation_count FROM user_risk WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0


# Geriye dönük uyumluluk alias'ları
add_credit_card = add_payment_card
add_purchase = add_flight_booking

init_db()
