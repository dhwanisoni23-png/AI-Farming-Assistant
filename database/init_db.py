import sqlite3

DATABASE_PATH = "database/farming.db"

connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()


# ============================================================
# CROP HISTORY
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS crop_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nitrogen REAL,
    phosphorus REAL,
    potassium REAL,
    temperature REAL,
    humidity REAL,
    ph REAL,
    rainfall REAL,
    recommendation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


# ============================================================
# DISEASE HISTORY
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS disease_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_name TEXT,
    disease TEXT,
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


# ============================================================
# WEATHER HISTORY
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS weather_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT,
    temperature REAL,
    humidity REAL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


# ============================================================
# CONTACT / FEEDBACK
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


# ============================================================
# USER RATINGS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


connection.commit()
connection.close()

print("Database Created Successfully!")