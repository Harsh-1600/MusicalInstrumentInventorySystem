import os
import sqlite3
import secrets
import hashlib
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

# Base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Database file name and path
DATABASE_FILE = 'musical_inventory.db'
DATABASE_PATH = os.path.join(BASE_DIR, DATABASE_FILE)


def get_db_connection(db_path=DATABASE_PATH):
    """
    Establishes and returns a connection to the SQLite database.
    Enables foreign key constraints and dictionary-like row access.
    """
    conn = sqlite3.connect(db_path)
    # Enable foreign key support in SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    # Allows accessing columns by name like a dictionary (e.g., row['name'])
    conn.row_factory = sqlite3.Row
    return conn


def close_db_connection(conn):
    """
    Safely closes the database connection.
    """
    if conn:
        conn.close()


# 30 Default Musical Instrument Records
DEFAULT_INSTRUMENTS = [
    {"instrument_id": "INS001", "name": "Guitar", "category": "String Instruments", "brand": "Yamaha", "price": 8500.0, "quantity": 10},
    {"instrument_id": "INS002", "name": "Piano", "category": "Keyboard Instruments", "brand": "Casio", "price": 45000.0, "quantity": 5},
    {"instrument_id": "INS003", "name": "Violin", "category": "String Instruments", "brand": "Stentor", "price": 12000.0, "quantity": 8},
    {"instrument_id": "INS004", "name": "Drum Kit", "category": "Percussion Instruments", "brand": "Pearl", "price": 35000.0, "quantity": 4},
    {"instrument_id": "INS005", "name": "Flute", "category": "Wind Instruments", "brand": "Yamaha", "price": 2500.0, "quantity": 15},
    {"instrument_id": "INS006", "name": "Keyboard", "category": "Keyboard Instruments", "brand": "Roland", "price": 18000.0, "quantity": 7},
    {"instrument_id": "INS007", "name": "Ukulele", "category": "String Instruments", "brand": "Kadence", "price": 3500.0, "quantity": 12},
    {"instrument_id": "INS008", "name": "Saxophone", "category": "Wind Instruments", "brand": "Jupiter", "price": 28000.0, "quantity": 3},
    {"instrument_id": "INS009", "name": "Trumpet", "category": "Wind Instruments", "brand": "Bach", "price": 22000.0, "quantity": 6},
    {"instrument_id": "INS010", "name": "Cello", "category": "String Instruments", "brand": "Yamaha", "price": 65000.0, "quantity": 2},
    {"instrument_id": "INS011", "name": "Tabla", "category": "Percussion Instruments", "brand": "Radhe", "price": 4500.0, "quantity": 10},
    {"instrument_id": "INS012", "name": "Mridangam", "category": "Percussion Instruments", "brand": "Handmade", "price": 7000.0, "quantity": 5},
    {"instrument_id": "INS013", "name": "Clarinet", "category": "Wind Instruments", "brand": "Yamaha", "price": 15000.0, "quantity": 4},
    {"instrument_id": "INS014", "name": "Harmonica", "category": "Wind Instruments", "brand": "Hohner", "price": 1200.0, "quantity": 20},
    {"instrument_id": "INS015", "name": "Banjo", "category": "String Instruments", "brand": "Deering", "price": 18000.0, "quantity": 3},
    {"instrument_id": "INS016", "name": "Mandolin", "category": "String Instruments", "brand": "Ibanez", "price": 9500.0, "quantity": 6},
    {"instrument_id": "INS017", "name": "Electric Guitar", "category": "String Instruments", "brand": "Fender", "price": 25000.0, "quantity": 5},
    {"instrument_id": "INS018", "name": "Bass Guitar", "category": "String Instruments", "brand": "Ibanez", "price": 22000.0, "quantity": 4},
    {"instrument_id": "INS019", "name": "Djembe", "category": "Percussion Instruments", "brand": "Meinl", "price": 6000.0, "quantity": 7},
    {"instrument_id": "INS020", "name": "Conga", "category": "Percussion Instruments", "brand": "LP", "price": 14000.0, "quantity": 3},
    {"instrument_id": "INS021", "name": "Xylophone", "category": "Percussion Instruments", "brand": "Yamaha", "price": 8500.0, "quantity": 5},
    {"instrument_id": "INS022", "name": "Accordion", "category": "Keyboard Instruments", "brand": "Hohner", "price": 32000.0, "quantity": 2},
    {"instrument_id": "INS023", "name": "Organ", "category": "Keyboard Instruments", "brand": "Yamaha", "price": 55000.0, "quantity": 2},
    {"instrument_id": "INS024", "name": "Oboe", "category": "Wind Instruments", "brand": "Yamaha", "price": 38000.0, "quantity": 2},
    {"instrument_id": "INS025", "name": "Trombone", "category": "Wind Instruments", "brand": "Bach", "price": 26000.0, "quantity": 3},
    {"instrument_id": "INS026", "name": "Tuba", "category": "Wind Instruments", "brand": "Jupiter", "price": 48000.0, "quantity": 2},
    {"instrument_id": "INS027", "name": "Sitar", "category": "String Instruments", "brand": "Handmade", "price": 18000.0, "quantity": 4},
    {"instrument_id": "INS028", "name": "Veena", "category": "String Instruments", "brand": "Saraswati", "price": 15000.0, "quantity": 5},
    {"instrument_id": "INS029", "name": "Tambourine", "category": "Percussion Instruments", "brand": "Meinl", "price": 1800.0, "quantity": 12},
    {"instrument_id": "INS030", "name": "Triangle", "category": "Percussion Instruments", "brand": "Stagg", "price": 900.0, "quantity": 15}
]


def create_tables(conn):
    """
    Creates the 'instruments' and 'sales' tables if they do not exist.
    Supports alphanumeric Instrument IDs (e.g. INS001) while preserving data.
    """
    cursor = conn.cursor()

    # Instruments Table with TEXT PRIMARY KEY
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS instruments (
            instrument_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            brand TEXT NOT NULL,
            price REAL NOT NULL CHECK (price >= 0),
            quantity INTEGER NOT NULL CHECK (quantity >= 0)
        );
    """)

    # Check if existing table had INTEGER PRIMARY KEY AUTOINCREMENT and migrate preserving data
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='instruments';")
    tbl_info = cursor.fetchone()
    if tbl_info and "AUTOINCREMENT" in tbl_info[0]:
        cursor.execute("PRAGMA foreign_keys = OFF;")
        cursor.execute("""
            CREATE TABLE instruments_migrated (
                instrument_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                brand TEXT NOT NULL,
                price REAL NOT NULL CHECK (price >= 0),
                quantity INTEGER NOT NULL CHECK (quantity >= 0)
            );
        """)
        cursor.execute("""
            INSERT INTO instruments_migrated (instrument_id, name, category, brand, price, quantity)
            SELECT CAST(instrument_id AS TEXT), name, category, brand, price, quantity FROM instruments;
        """)
        cursor.execute("DROP TABLE instruments;")
        cursor.execute("ALTER TABLE instruments_migrated RENAME TO instruments;")
        cursor.execute("PRAGMA foreign_keys = ON;")

    # Sales Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            instrument_id TEXT,
            instrument_name TEXT NOT NULL,
            quantity_sold INTEGER NOT NULL CHECK (quantity_sold >= 0),
            unit_price REAL NOT NULL CHECK (unit_price >= 0),
            total_amount REAL NOT NULL CHECK (total_amount >= 0),
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (instrument_id) REFERENCES instruments (instrument_id) ON DELETE SET NULL
        );
    """)

    # Users Table for Admin Authentication & Access Control
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL DEFAULT 'Store Administrator',
            email TEXT NOT NULL DEFAULT 'admin@soundcraft.com',
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Safe column migration for existing users table
    cursor.execute("PRAGMA table_info(users);")
    user_cols = [c[1] for c in cursor.fetchall()]
    if "full_name" not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT NOT NULL DEFAULT 'Store Administrator';")
    if "email" not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT NOT NULL DEFAULT 'admin@soundcraft.com';")

    # Safe column migration for existing instruments table (Customer Portal features)
    cursor.execute("PRAGMA table_info(instruments);")
    inst_cols = [c[1] for c in cursor.fetchall()]
    if "image_url" not in inst_cols:
        cursor.execute("ALTER TABLE instruments ADD COLUMN image_url TEXT DEFAULT '/static/images/instruments/generic.svg';")
    if "description" not in inst_cols:
        cursor.execute("ALTER TABLE instruments ADD COLUMN description TEXT DEFAULT '';")
    if "use_case" not in inst_cols:
        cursor.execute("ALTER TABLE instruments ADD COLUMN use_case TEXT DEFAULT '';")
    if "specifications" not in inst_cols:
        cursor.execute("ALTER TABLE instruments ADD COLUMN specifications TEXT DEFAULT '';")

    # Single-Use Password Reset Tokens Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_resets (
            reset_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_hash TEXT NOT NULL UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            used INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        );
    """)

    # Customer Orders Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            shipping_address TEXT NOT NULL,
            city TEXT NOT NULL DEFAULT '',
            pincode TEXT NOT NULL DEFAULT '',
            payment_method TEXT NOT NULL DEFAULT 'Cash on Delivery',
            total_amount REAL NOT NULL CHECK (total_amount >= 0),
            order_status TEXT NOT NULL DEFAULT 'Confirmed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        );
    """)

    # Customer Order Items Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            instrument_id TEXT,
            instrument_name TEXT NOT NULL,
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            unit_price REAL NOT NULL CHECK (unit_price >= 0),
            subtotal REAL NOT NULL CHECK (subtotal >= 0),
            image_url TEXT,
            FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE,
            FOREIGN KEY (instrument_id) REFERENCES instruments (instrument_id) ON DELETE SET NULL
        );
    """)

    # Customer SMS & WhatsApp Notification Logs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sms_notifications (
            notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            phone_number TEXT NOT NULL,
            message_text TEXT NOT NULL,
            gateway TEXT DEFAULT 'WhatsApp & Push',
            status TEXT DEFAULT 'Dispatched',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE
        );
    """)

    conn.commit()


def seed_default_instruments(conn):
    """
    Inserts the 30 default musical instrument records if they do not already exist.
    Prevents duplicates on application restarts by checking existing IDs.
    Does not delete or overwrite existing user records.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT instrument_id FROM instruments;")
    existing_ids = {str(row[0]) for row in cursor.fetchall()}

    inserted_count = 0
    for item in DEFAULT_INSTRUMENTS:
        if item["instrument_id"] not in existing_ids:
            cursor.execute("""
                INSERT INTO instruments (instrument_id, name, category, brand, price, quantity)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (
                item["instrument_id"],
                item["name"],
                item["category"],
                item["brand"],
                item["price"],
                item["quantity"]
            ))
            inserted_count += 1

    if inserted_count > 0:
        conn.commit()
        print(f"Seeded {inserted_count} default musical instruments into SQLite.")


def seed_default_admin(conn):
    """
    Seeds the default administrator account if the users table is empty.
    Username: admin | Password: Admin@123 (hashed using PBKDF2-SHA256).
    Ensures full_name and email are populated.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users;")
    if cursor.fetchone()[0] == 0:
        hashed_pw = generate_password_hash("Admin@123", method="pbkdf2:sha256")
        cursor.execute("""
            INSERT INTO users (username, full_name, email, password_hash, role)
            VALUES (?, ?, ?, ?, ?);
        """, ("admin", "Store Administrator", "admin@soundcraft.com", hashed_pw, "Admin"))
        conn.commit()
        print("Default admin account initialized: admin / Admin@123")
    else:
        # Ensure admin has valid full_name and email
        cursor.execute("""
            UPDATE users 
            SET full_name = 'Store Administrator', email = 'admin@soundcraft.com'
            WHERE username = 'admin' AND (email IS NULL OR email = '' OR email = 'admin@soundcraft.local');
        """)
        conn.commit()


def seed_default_customer(conn):
    """
    Seeds a default customer account for demonstration and testing if it does not exist.
    Username: customer | Password: Customer@123 (hashed using PBKDF2-SHA256).
    Role: Customer
    """
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE username = 'customer';")
    if not cursor.fetchone():
        hashed_pw = generate_password_hash("Customer@123", method="pbkdf2:sha256")
        cursor.execute("""
            INSERT INTO users (username, full_name, email, password_hash, role)
            VALUES (?, ?, ?, ?, 'Customer');
        """, ("customer", "Priya Sharma (Music Lover)", "customer@soundcraft.com", hashed_pw))
        conn.commit()
        print("Default customer account initialized: customer / Customer@123")


# Complete Data Dictionary for Instrument Images & "What is this instrument used for?" Guides
INSTRUMENTS_METADATA = {
    "INS001": {
        "image_url": "/static/images/instruments/guitar.svg",
        "description": "Premium 6-string acoustic guitar known for warm midrange projection, smooth fretting, and rich natural acoustic resonance.",
        "use_case": "Essential for acoustic live concerts, singer-songwriter solo sets, pop recordings, campfire sing-alongs, and chord accompaniment. Perfect for beginners, rhythm players, and touring musicians.",
        "specifications": "Spruce soundboard, Rosewood fretboard & bridge, Die-cast chrome tuners, Standard E-A-D-G-B-E tuning, 20 Frets."
    },
    "INS002": {
        "image_url": "/static/images/instruments/piano.svg",
        "description": "Full-size acoustic piano with responsive hammer action, vast dynamic range, and rich sympathetic string resonance.",
        "use_case": "Used for classical concertos, jazz trios, film scoring, church worship music, and foundational music education. The premier centerpiece for serious pianists and composers.",
        "specifications": "88 Weighted acoustic keys, Cast iron frame, Solid spruce soundboard, 3 Pedals (Soft, Sostenuto, Damper), Ebony high-gloss finish."
    },
    "INS003": {
        "image_url": "/static/images/instruments/violin.svg",
        "description": "Handcrafted 4-string orchestral violin renowned for its sweet singing vibrato, agile ornamentation, and resonant projection.",
        "use_case": "Used in symphony orchestras, classical string quartets, South Indian Carnatic kutcheris, Irish Celtic fiddling, and emotional movie scores.",
        "specifications": "Hand-carved solid spruce top, Flamed maple back, Ebony fingerboard and tuning pegs, Brazilwood horsehair bow and case included."
    },
    "INS004": {
        "image_url": "/static/images/instruments/drum_kit.svg",
        "description": "5-piece acoustic drum kit featuring birch shells, sensitive snare, high-dynamic toms, and heavy-duty double-braced hardware.",
        "use_case": "The core rhythm engine for rock, pop, jazz, metal, and funk bands. Drives song tempo, adds dramatic fills, and delivers dance energy.",
        "specifications": "22-inch Bass drum, 14-inch Snare, 10-inch & 12-inch Rack toms, 16-inch Floor tom, Hi-hat and Crash cymbals included."
    },
    "INS005": {
        "image_url": "/static/images/instruments/flute.svg",
        "description": "Precision-crafted concert C flute delivering a pure, sparkling tone, effortless airflow, and rapid fingering response.",
        "use_case": "Used in symphony orchestras, jazz flute solos, classical sonatas, Indian fusion recordings, and marching concert bands.",
        "specifications": "Cupronickel body with silver plating, 16 Closed-hole keys, Offset G with Split E mechanism, Stainless steel springs."
    },
    "INS006": {
        "image_url": "/static/images/instruments/keyboard_synth.svg",
        "description": "Versatile 61-key electronic arranger keyboard loaded with authentic instrument voices, drum rhythms, and recording capabilities.",
        "use_case": "Used for multi-genre stage gigs, home song production, band keyboards, music theory learning, and wedding band accompaniment.",
        "specifications": "61 Touch-sensitive keys, 500+ instrument tones, USB-MIDI audio interface, Built-in stereo speakers, Headphone output."
    },
    "INS007": {
        "image_url": "/static/images/instruments/guitar.svg",
        "description": "Traditional soprano ukulele offering bright, happy, Hawaiian acoustic sound with gentle nylon strings.",
        "use_case": "Used for acoustic pop strumming, folk tunes, beach campfire singing, travel accompaniment, and beginner friendly music learning.",
        "specifications": "Soprano 21-inch Mahogany body, Aquila Super Nylgut strings, Rosewood fretboard, G-C-E-A tuning."
    },
    "INS008": {
        "image_url": "/static/images/instruments/saxophone.svg",
        "description": "Eb Alto saxophone producing a sultry, rich brass voice with smooth key action and effortless low-register attack.",
        "use_case": "Essential for jazz big bands, blues clubs, funk horn sections, pop saxophone solos, and orchestral wind ensembles.",
        "specifications": "High-grade yellow brass, Gold lacquer finish, Leather pads with metal resonators, High F# key, Premium mouthpiece."
    },
    "INS009": {
        "image_url": "/static/images/instruments/trumpet.svg",
        "description": "Standard Bb brass trumpet with brilliant projection, crisp response, and smooth stainless steel valve action.",
        "use_case": "Used for heroic classical fanfares, jazz improvisation solos, mariachi brass, marching bands, and funk horn punches.",
        "specifications": "Standard Bb key, 123mm Yellow brass bell, Monel valves, 1st slide thumb saddle and 3rd slide ring, 7C mouthpiece."
    },
    "INS010": {
        "image_url": "/static/images/instruments/violin.svg",
        "description": "Full-size orchestral cello with a rich, sonorous baritone voice capable of profound warmth and soaring lyricism.",
        "use_case": "Used in orchestral string sections, cello rock ensembles (like Apocalyptica), chamber music, and evocative film themes.",
        "specifications": "Carved spruce top, Maple sides and neck, Ebony fittings, Height-adjustable steel endpin, Padded carry bag."
    },
    "INS011": {
        "image_url": "/static/images/instruments/tabla.svg",
        "description": "Master-grade North Indian classical twin-drum set featuring the wooden Dayan (treble) and metallic Bayan (bass).",
        "use_case": "Used in Hindustani classical music concerts, Ghazal accompaniments, Sufi Qawwali, Bollywood studio rhythms, and global fusion.",
        "specifications": "Dayan: Seasoned heavy Sheesham wood; Bayan: Deep brass kettle; Syahi black iron paste tuning; Bira cushions and tuning hammer."
    },
    "INS012": {
        "image_url": "/static/images/instruments/tabla.svg",
        "description": "Primary rhythm percussion instrument of Carnatic classical music, crafted from a single hollowed block of jackfruit wood.",
        "use_case": "Used in South Indian Carnatic classical vocal and instrumental concerts, Bharatanatyam dance performances, and Harikatha recitals.",
        "specifications": "Single piece Jackfruit wood body, Heavy layered goat hide membranes, Traditional leather thong tuning, Tuned to standard tonic pitch."
    },
    "INS013": {
        "image_url": "/static/images/instruments/flute.svg",
        "description": "Standard Bb soprano clarinet featuring a warm, woody acoustic tone, smooth register jumps, and airtight pad seal.",
        "use_case": "Used in symphony orchestras, jazz ensembles, Klezmer folk celebrations, wind quintets, and music conservatories.",
        "specifications": "Durable ABS resin body with wood-grain finish, 17 Nickel-plated keys, 6 Rings, Adjustable thumb rest."
    },
    "INS014": {
        "image_url": "/static/images/instruments/flute.svg",
        "description": "Professional 10-hole diatonic blues harmonica delivering expressive note bending, crunchy overblown reeds, and rich chords.",
        "use_case": "Used for authentic Chicago blues, Americana folk songs, country train rhythm, campfire playing, and rock harmonica solos.",
        "specifications": "Key of C, 10 Holes / 20 Brass reeds, Airtight moisture-resistant plastic comb, Stainless steel engraved covers."
    },
    "INS015": {
        "image_url": "/static/images/instruments/guitar.svg",
        "description": "5-string bluegrass banjo with a resonant mahogany drum body that produces lightning-fast, twangy, rhythmic notes.",
        "use_case": "Used for traditional Bluegrass picking (Scruggs style), American country, folk festivals, and old-time string bands.",
        "specifications": "11-inch Remo frosted head, Mahogany rim and resonator, Geared 5th tuning peg, 24 Tension brackets."
    },
    "INS016": {
        "image_url": "/static/images/instruments/guitar.svg",
        "description": "A-style teardrop acoustic mandolin featuring dual F-holes, ringing high-register sustain, and crisp chop chords.",
        "use_case": "Used in Bluegrass bands for percussive rhythm chops, Celtic reels, Italian folk tarantellas, and acoustic rock fills.",
        "specifications": "Spruce top, Mahogany back and sides, 8 Strings in pairs (G-D-A-E), Adjustable compensated bridge."
    },
    "INS017": {
        "image_url": "/static/images/instruments/electric_guitar.svg",
        "description": "Double-cutaway solid body electric guitar engineered for high-gain solos, punchy rhythm riffs, and expressive string bending.",
        "use_case": "Used extensively in rock bands, blues jams, heavy metal, pop studio sessions, and live arena concerts. Played through amplifiers and effect pedals for soaring lead solos.",
        "specifications": "Solid Alder body, Maple modern 'C' neck, 3 Single-Coil / Humbucker pickups, 5-way selector switch, Synchronized tremolo."
    },
    "INS018": {
        "image_url": "/static/images/instruments/electric_guitar.svg",
        "description": "4-string electric bass guitar providing the deep rhythmic foundation, driving groove, and harmonic spine of the band.",
        "use_case": "Vital for anchoring the rhythm section alongside drums in rock, funk, jazz, disco, and pop music. Delivers walking basslines and chest-thumping low-end frequencies.",
        "specifications": "Solid Basswood body, 34-inch long scale maple neck, Split single-coil pickups, Volume and Tone knobs, E-A-D-G tuning."
    },
    "INS019": {
        "image_url": "/static/images/instruments/drum_kit.svg",
        "description": "Authentic carved West African goblet drum capable of booming bass notes and sharp, crisp edge slaps.",
        "use_case": "Used for traditional African drumming circles, dance accompaniment, street busking, meditation rhythm, and world music festivals.",
        "specifications": "Carved plantation Mahogany wood, Selected natural goat skin head, Heavy-duty 4mm high-tensile alpine rope."
    },
    "INS020": {
        "image_url": "/static/images/instruments/drum_kit.svg",
        "description": "Single Cuban conga hand drum producing warm open tones and sharp muffle slaps for irresistible Latin dance rhythms.",
        "use_case": "Used in Salsa bands, Latin jazz ensembles, Afro-Cuban rumbas, reggae music, and contemporary pop percussion rigs.",
        "specifications": "28-inch tall Siam Oak shell, 11-inch Rawhide head, Chrome hardware with curved comfort rims."
    },
    "INS021": {
        "image_url": "/static/images/instruments/keyboard_synth.svg",
        "description": "Concert wooden xylophone with precision-tuned rosewood bars that produce bright, articulate, dry percussive notes.",
        "use_case": "Used in symphony orchestra programs, school percussion ensembles, marching drum corps pits, and theatrical scoring.",
        "specifications": "3.5 Octaves (F4 - C8), Hand-tuned African Padauk wood bars, Tubular resonators, Height-adjustable frame."
    },
    "INS022": {
        "image_url": "/static/images/instruments/keyboard_synth.svg",
        "description": "Piano-key acoustic accordion with multi-voice treble registers and full bass chord button accompaniment.",
        "use_case": "Used for European folk dances, French café musette, German polka, tango ensembles, and lively street performances.",
        "specifications": "34 Treble keys, 72 Bass buttons, 5 Treble couplers, Airtight multi-fold reinforced leather bellows."
    },
    "INS023": {
        "image_url": "/static/images/instruments/keyboard_synth.svg",
        "description": "Dual-manual electronic combo organ delivering legendary tonewheel roar, percussion harmonic clicks, and rotary swirl.",
        "use_case": "Used in gospel church services, rock bands (classic 60s/70s style), jazz Hammond trios, and blues jams.",
        "specifications": "Two 61-key waterfall keyboards, 9 Mechanical physical drawbars, Built-in DSP Leslie rotary speaker simulator."
    },
    "INS024": {
        "image_url": "/static/images/instruments/flute.svg",
        "description": "Double-reed woodwind instrument renowned for its soulful, penetrating, and poignant orchestral voice.",
        "use_case": "Used to sound the concert pitch A440 for orchestra tuning, classical concerto solos, and emotional cinematic pastoral themes.",
        "specifications": "Selected Grenadilla wood body, Full conservatory key system, Silver-plated keys, Left hand F key."
    },
    "INS025": {
        "image_url": "/static/images/instruments/trumpet.svg",
        "description": "Tenor slide brass trombone producing rich, warm low-brass harmonies and smooth, expressive chromatic glissandi.",
        "use_case": "Used in jazz swing big bands, symphony brass choirs, New Orleans brass bands, and ska brass sections.",
        "specifications": "Bb Tenor slide, 8.5-inch Yellow brass bell, Chrome-plated nickel inner slide, Lacquered finish, 6.5AL mouthpiece."
    },
    "INS026": {
        "image_url": "/static/images/instruments/trumpet.svg",
        "description": "Full-size BBb concert tuba offering thunderous bass projection, majestic pedal notes, and rich ensemble depth.",
        "use_case": "The foundational bass instrument for symphony orchestras, concert wind bands, brass quintets, and marching drum corps.",
        "specifications": "BBb key, 4 Rotary valves, 17.5-inch Upright bell, Clear lacquer over yellow brass, Wheeled flight case."
    },
    "INS027": {
        "image_url": "/static/images/instruments/sitar.svg",
        "description": "Classical North Indian plucked lute featuring curved metal frets, gourd resonator, and sympathetic resonant strings.",
        "use_case": "Used for Hindustani classical Ragas, Indian fusion concerts, meditative sitar-tabla duets, and global world music.",
        "specifications": "Double gourd (Kaddus), 7 Main playing strings, 13 Taraf (sympathetic) strings, 20 Brass frets, Bone bridges."
    },
    "INS028": {
        "image_url": "/static/images/instruments/sitar.svg",
        "description": "Sacred Saraswati Veena carved from seasoned jackfruit wood, held horizontally to produce microtonal Carnatic gamakas.",
        "use_case": "Used in South Indian Carnatic classical recitals, temple festivals, devotionals, and pure classical solo presentations.",
        "specifications": "Ekanda single-log carved Jackfruit wood, 24 Brass frets fixed on wax tracks, Dragon Yali head carving."
    },
    "INS029": {
        "image_url": "/static/images/instruments/drum_kit.svg",
        "description": "10-inch wooden hand tambourine with dual rows of bright nickel-silver jingles and natural calfskin head.",
        "use_case": "Used to add sparkle and rhythmic momentum in rock, pop, gospel choirs, acoustic folk, and orchestral dance movements.",
        "specifications": "Acousticon hardwood shell, Double row of 16 jingles, Calfskin natural head, Ergonomic grip."
    },
    "INS030": {
        "image_url": "/static/images/instruments/drum_kit.svg",
        "description": "Solid steel musical triangle producing a penetrating, crystalline metallic chime that cuts through full orchestras.",
        "use_case": "Used in classical orchestral climaxes, Brazilian Forró rhythms, opera pit orchestras, and school percussion ensembles.",
        "specifications": "8-inch Solid alloy steel, Mirror chrome plating, Braided hanging loop, Heavy steel striker with rubber grip."
    },
    "1": {
        "image_url": "/static/images/instruments/guitar.svg",
        "description": "Handcrafted custom acoustic instrument built with premium tonewoods for responsive touch and distinct acoustic voicing.",
        "use_case": "Used for acoustic songwriting, fingerstyle solo performance, home studio tracking, and personal musical exploration.",
        "specifications": "Custom tonewood body, Rosewood fretboard, Bone nut and saddle, Hand-rubbed satin oil finish."
    },
    "101": {
        "image_url": "/static/images/instruments/electric_guitar.svg",
        "description": "Iconic single-cutaway electric guitar with heavy mahogany body, dual humbuckers, and endless singing sustain.",
        "use_case": "Used in hard rock, classic rock, blues, and heavy metal live concerts. Renowned for fat, creamy lead tones and thick rhythm crunch.",
        "specifications": "Mahogany body with carved maple top, SlimTaper mahogany neck, Dual ProBucker pickups with coil-split, Gold hardware."
    },
    "102": {
        "image_url": "/static/images/instruments/flute.svg",
        "description": "World-renowned student concert flute crafted with ergonomic key placement and effortless tone production.",
        "use_case": "The top choice for music students, school concert bands, woodwind ensembles, and intermediate flute learners.",
        "specifications": "Nickel silver with durable silver plating, Closed hole keys, Offset G, Split E mechanism, Molded hard case."
    },
    "103": {
        "image_url": "/static/images/instruments/drum_kit.svg",
        "description": "Flagship electronic drum set featuring double-ply mesh heads, natural cymbal swing, and Bluetooth smartphone connectivity.",
        "use_case": "Used for quiet home apartment practice, music production studios, church worship stages, and versatile live gigging.",
        "specifications": "12-inch Mesh snare, 3 Mesh toms, VH-10 Floating hi-hat, TD-17 Sound engine with dynamic acoustic modeling."
    },
    "104": {
        "image_url": "/static/images/instruments/piano.svg",
        "description": "Slim, portable 88-key digital piano with Graded Hammer Standard (GHS) key action that mimics an acoustic grand piano.",
        "use_case": "Used for piano lessons, dorm room practice, rehearsal studios, and stage performance with external sound systems.",
        "specifications": "88 GHS Weighted keys, Advanced Wave Memory (AWM) stereo sampling, 64-voice polyphony, USB-to-Host port."
    }
}


def enrich_instruments_metadata(conn):
    """
    Updates or seeds image_url, description, use_case, and specifications
    for all instruments in SQLite if they are empty or missing.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT instrument_id, name, category FROM instruments;")
    rows = cursor.fetchall()

    for row in rows:
        iid = str(row['instrument_id'])
        name = row['name']
        cat = row['category']

        meta = INSTRUMENTS_METADATA.get(iid)
        if not meta:
            # Fallback by category
            if cat == "String Instruments":
                meta = {
                    "image_url": "/static/images/instruments/guitar.svg",
                    "description": f"{name} is a finely crafted stringed instrument designed for rich acoustic tone and melodic warmth.",
                    "use_case": "Used in acoustic concerts, studio tracking, classical recitals, and solo performances. Great for melodic expression and chord harmonies.",
                    "specifications": "Standard acoustic/electric string construction, resonant tonewood body, precision geared machine heads."
                }
            elif cat == "Wind Instruments":
                meta = {
                    "image_url": "/static/images/instruments/flute.svg",
                    "description": f"{name} is an expressive acoustic wind instrument designed for fluid breath control and clear acoustic projection.",
                    "use_case": "Used in orchestral arrangements, brass/woodwind sections, jazz solos, and classical concertos.",
                    "specifications": "Precision-bored acoustic body, airtight pad sealing, polished metallic finish."
                }
            elif cat == "Percussion Instruments":
                meta = {
                    "image_url": "/static/images/instruments/drum_kit.svg",
                    "description": f"{name} is a high-impact percussion instrument delivering crisp rhythmic drive and tempo control.",
                    "use_case": "Used to maintain tempo, anchor rhythm sections, drive dance music, and provide dynamic accents across all genres.",
                    "specifications": "Durable resonant shell, heavy-duty hardware, tuned acoustic heads."
                }
            elif cat == "Keyboard Instruments":
                meta = {
                    "image_url": "/static/images/instruments/piano.svg",
                    "description": f"{name} is a comprehensive keyboard instrument offering wide polyphony and expansive musical range.",
                    "use_case": "Used for songwriting, classical composition, band performance, and music theory education.",
                    "specifications": "Weighted/touch-sensitive keyboard bed, dynamic velocity response, stereo sound projection."
                }
            elif cat == "Electronic Instruments":
                meta = {
                    "image_url": "/static/images/instruments/keyboard_synth.svg",
                    "description": f"{name} is a cutting-edge electronic musical instrument featuring digital sound modeling and studio connectivity.",
                    "use_case": "Used in electronic music production, live modern stage shows, MIDI sequencing, and sound design.",
                    "specifications": "Digital sound generation engine, stereo audio outputs, USB-MIDI interface."
                }
            else:
                meta = {
                    "image_url": "/static/images/instruments/generic.svg",
                    "description": f"{name} is a specialized musical instrument crafted for expressive acoustic and stage performance.",
                    "use_case": "Used across diverse musical ensembles, studio recording projects, and solo acoustic sessions.",
                    "specifications": "High-durability craftsmanship, tuned to standard pitch, ergonomic design."
                }

        cursor.execute("""
            UPDATE instruments
            SET image_url = ?, description = ?, use_case = ?, specifications = ?
            WHERE instrument_id = ? AND (description IS NULL OR description = '' OR use_case IS NULL OR use_case = '');
        """, (meta["image_url"], meta["description"], meta["use_case"], meta["specifications"], iid))

    conn.commit()


def register_customer(full_name, username, email, password, db_path=DATABASE_PATH):
    """
    Registers a new customer account with role='Customer'.
    Validates username and email uniqueness.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        # Check username uniqueness
        cursor.execute("SELECT user_id FROM users WHERE LOWER(username) = LOWER(?);", (username.strip(),))
        if cursor.fetchone():
            return False, f"Username '{username}' is already taken. Please choose another username."

        # Check email uniqueness
        cursor.execute("SELECT user_id FROM users WHERE LOWER(email) = LOWER(?);", (email.strip(),))
        if cursor.fetchone():
            return False, f"Email '{email}' is already registered. Please sign in or use a different email."

        hashed_pw = generate_password_hash(password, method="pbkdf2:sha256")
        cursor.execute("""
            INSERT INTO users (username, full_name, email, password_hash, role)
            VALUES (?, ?, ?, ?, 'Customer');
        """, (username.strip(), full_name.strip(), email.strip(), hashed_pw))
        conn.commit()
        return True, "Customer account created successfully! You can now log in."
    except Exception as e:
        return False, f"Registration failed: {str(e)}"
    finally:
        close_db_connection(conn)


def get_store_instruments(category=None, search=None, db_path=DATABASE_PATH):
    """
    Fetches all instruments formatted for customer storefront:
    - Filters by category or search term if provided
    - Computes live stock status: 'in_stock' (>5), 'low_stock' (1-5), 'out_of_stock' (0)
    - Formats currency price
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        query = "SELECT * FROM instruments WHERE 1=1"
        params = []
        if category and category.lower() != 'all':
            query += " AND category = ?"
            params.append(category.strip())
        if search:
            query += " AND (name LIKE ? OR brand LIKE ? OR category LIKE ?)"
            s = f"%{search.strip()}%"
            params.extend([s, s, s])
        query += " ORDER BY name ASC;"
        cursor.execute(query, params)
        rows = cursor.fetchall()

        instruments = []
        for r in rows:
            item = dict(r)
            qty = item.get('quantity', 0)
            if qty > 5:
                item['stock_status'] = 'in_stock'
                item['stock_label'] = f'In Stock ({qty} available)'
                item['stock_badge_class'] = 'stock-badge-in'
            elif 1 <= qty <= 5:
                item['stock_status'] = 'low_stock'
                item['stock_label'] = f'Low Stock (Only {qty} left!)'
                item['stock_badge_class'] = 'stock-badge-low'
            else:
                item['stock_status'] = 'out_of_stock'
                item['stock_label'] = 'Out of Stock'
                item['stock_badge_class'] = 'stock-badge-out'

            if not item.get('image_url'):
                item['image_url'] = '/static/images/instruments/generic.svg'
            instruments.append(item)
        return instruments
    finally:
        close_db_connection(conn)


def get_instrument_with_details(instrument_id, db_path=DATABASE_PATH):
    """
    Fetches a single instrument with full metadata, images, and usage guide ("Ethuku use pannalam").
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM instruments WHERE instrument_id = ?;", (str(instrument_id),))
        row = cursor.fetchone()
        if not row:
            return None
        item = dict(row)
        qty = item.get('quantity', 0)
        if qty > 5:
            item['stock_status'] = 'in_stock'
            item['stock_label'] = f'In Stock ({qty} available)'
            item['stock_badge_class'] = 'stock-badge-in'
        elif 1 <= qty <= 5:
            item['stock_status'] = 'low_stock'
            item['stock_label'] = f'Low Stock (Only {qty} left!)'
            item['stock_badge_class'] = 'stock-badge-low'
        else:
            item['stock_status'] = 'out_of_stock'
            item['stock_label'] = 'Out of Stock'
            item['stock_badge_class'] = 'stock-badge-out'

        if not item.get('image_url'):
            item['image_url'] = '/static/images/instruments/generic.svg'
        return item
    finally:
        close_db_connection(conn)


def create_user(username, password, role="Admin", full_name="Store Staff", email="", db_path=DATABASE_PATH):
    """
    Registers a new user with a securely hashed password.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        hashed_pw = generate_password_hash(password, method="pbkdf2:sha256")
        cursor.execute("""
            INSERT INTO users (username, full_name, email, password_hash, role)
            VALUES (?, ?, ?, ?, ?);
        """, (username.strip(), full_name.strip(), email.strip(), hashed_pw, role))
        conn.commit()
        return True, "User created successfully!"
    except sqlite3.IntegrityError:
        return False, f"Username '{username}' already exists. Please choose a different username."
    except Exception as e:
        return False, f"Error creating user: {str(e)}"
    finally:
        close_db_connection(conn)


def get_user_by_username(username, db_path=DATABASE_PATH):
    """
    Retrieves user record by username.
    """
    if not username:
        return None
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE username = ?;", (username.strip(),))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        close_db_connection(conn)


def verify_user(username, password, db_path=DATABASE_PATH):
    """
    Verifies user credentials against stored PBKDF2-SHA256 hash.
    Returns user dict if valid, otherwise None.
    """
    user = get_user_by_username(username, db_path=db_path)
    if user and check_password_hash(user["password_hash"], password):
        return user
    return None


def get_user_profile(user_id, db_path=DATABASE_PATH):
    """
    Fetches user profile details (admin or customer).
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id, username, full_name, email, role, created_at FROM users WHERE user_id = ?;", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        close_db_connection(conn)


get_admin_profile = get_user_profile


def update_customer_profile(user_id, full_name, email, username=None, db_path=DATABASE_PATH):
    """
    Updates a customer's profile information.
    Enforces uniqueness for email and username across other accounts.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        if username:
            cursor.execute("SELECT user_id FROM users WHERE LOWER(username) = LOWER(?) AND user_id != ?;", (username.strip(), user_id))
            if cursor.fetchone():
                return False, f"Username '{username}' is already in use by another account."

        cursor.execute("SELECT user_id FROM users WHERE LOWER(email) = LOWER(?) AND user_id != ?;", (email.strip(), user_id))
        if cursor.fetchone():
            return False, f"Email '{email}' is already in use by another account."

        if username:
            cursor.execute("""
                UPDATE users
                SET full_name = ?, email = ?, username = ?
                WHERE user_id = ?;
            """, (full_name.strip(), email.strip(), username.strip(), user_id))
        else:
            cursor.execute("""
                UPDATE users
                SET full_name = ?, email = ?
                WHERE user_id = ?;
            """, (full_name.strip(), email.strip(), user_id))
        conn.commit()
        return True, "Profile updated successfully!"
    except Exception as e:
        return False, f"Failed to update profile: {str(e)}"
    finally:
        close_db_connection(conn)


def update_customer_password(user_id, current_password, new_password, db_path=DATABASE_PATH):
    """
    Validates current password and updates to a new PBKDF2-SHA256 hashed password for customer.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT password_hash FROM users WHERE user_id = ?;", (user_id,))
        row = cursor.fetchone()
        if not row:
            return False, "Customer account not found."

        if not check_password_hash(row["password_hash"], current_password):
            return False, "Incorrect current password. Please try again."

        new_hash = generate_password_hash(new_password, method="pbkdf2:sha256")
        cursor.execute("UPDATE users SET password_hash = ? WHERE user_id = ?;", (new_hash, user_id))
        conn.commit()
        return True, "Password changed successfully! Please use your new password on next sign-in."
    except Exception as e:
        return False, f"Failed to change password: {str(e)}"
    finally:
        close_db_connection(conn)


def update_admin_profile(user_id, full_name, email, username, db_path=DATABASE_PATH):
    """
    Updates the administrator's profile information.
    Enforces uniqueness for username and email across other accounts.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        # Check username uniqueness against other accounts
        cursor.execute("SELECT user_id FROM users WHERE LOWER(username) = LOWER(?) AND user_id != ?;", (username.strip(), user_id))
        if cursor.fetchone():
            return False, f"Username '{username}' is already in use by another account."

        # Check email uniqueness against other accounts
        cursor.execute("SELECT user_id FROM users WHERE LOWER(email) = LOWER(?) AND user_id != ?;", (email.strip(), user_id))
        if cursor.fetchone():
            return False, f"Email '{email}' is already in use by another account."

        cursor.execute("""
            UPDATE users
            SET full_name = ?, email = ?, username = ?
            WHERE user_id = ?;
        """, (full_name.strip(), email.strip(), username.strip(), user_id))
        conn.commit()
        return True, "Admin profile updated successfully!"
    except Exception as e:
        return False, f"Failed to update profile: {str(e)}"
    finally:
        close_db_connection(conn)


def update_admin_password(user_id, current_password, new_password, db_path=DATABASE_PATH):
    """
    Validates current password and updates to a new PBKDF2-SHA256 hashed password.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT password_hash FROM users WHERE user_id = ?;", (user_id,))
        row = cursor.fetchone()
        if not row:
            return False, "Administrator account not found."

        if not check_password_hash(row["password_hash"], current_password):
            return False, "Incorrect current password. Please try again."

        new_hash = generate_password_hash(new_password, method="pbkdf2:sha256")
        cursor.execute("UPDATE users SET password_hash = ? WHERE user_id = ?;", (new_hash, user_id))
        conn.commit()
        return True, "Password changed successfully! Please use your new password next time."
    except Exception as e:
        return False, f"Failed to change password: {str(e)}"
    finally:
        close_db_connection(conn)


def create_password_reset_token(email, db_path=DATABASE_PATH):
    """
    Generates a secure 32-byte one-time password reset token for the given registered email.
    Stores its SHA-256 hash in password_resets with a 30-minute expiry.
    Returns (raw_token, user_dict) or (None, None).
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?);", (email.strip(),))
        user_row = cursor.fetchone()
        if not user_row:
            return None, None

        user = dict(user_row)
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        expires_at = datetime.now() + timedelta(minutes=30)

        cursor.execute("""
            INSERT INTO password_resets (user_id, token_hash, expires_at, used)
            VALUES (?, ?, ?, 0);
        """, (user["user_id"], token_hash, expires_at.strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        return raw_token, user
    finally:
        close_db_connection(conn)


def validate_reset_token(raw_token, db_path=DATABASE_PATH):
    """
    Validates a password reset token.
    Returns (is_valid, user_id, message).
    """
    if not raw_token:
        return False, None, "Invalid reset token."

    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM password_resets WHERE token_hash = ?;", (token_hash,))
        reset_record = cursor.fetchone()
        if not reset_record:
            return False, None, "Invalid or unrecognized password reset link."

        if reset_record["used"] == 1:
            return False, None, "This password reset link has already been used. Please request a new one."

        expires_at = datetime.strptime(reset_record["expires_at"], "%Y-%m-%d %H:%M:%S")
        if datetime.now() > expires_at:
            return False, None, "This password reset link has expired. Please request a new one."

        return True, reset_record["user_id"], "Token valid."
    finally:
        close_db_connection(conn)


def reset_password_with_token(raw_token, new_password, db_path=DATABASE_PATH):
    """
    Validates token and updates user's password, marking token as used in an atomic transaction.
    """
    is_valid, user_id, msg = validate_reset_token(raw_token, db_path=db_path)
    if not is_valid:
        return False, msg

    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        new_hash = generate_password_hash(new_password, method="pbkdf2:sha256")
        cursor.execute("UPDATE users SET password_hash = ? WHERE user_id = ?;", (new_hash, user_id))
        cursor.execute("UPDATE password_resets SET used = 1 WHERE token_hash = ?;", (token_hash,))
        conn.commit()
        return True, "Password has been successfully reset! You can now log in with your new password."
    except Exception as e:
        conn.rollback()
        return False, f"Failed to reset password: {str(e)}"
    finally:
        close_db_connection(conn)


def init_db(db_path=DATABASE_PATH):
    """
    Initializes the database by establishing a connection,
    creating tables, seeding default records and accounts, enriching metadata, and properly closing the connection.
    """
    conn = get_db_connection(db_path)
    try:
        create_tables(conn)
        seed_default_instruments(conn)
        seed_default_admin(conn)
        seed_default_customer(conn)
        enrich_instruments_metadata(conn)
        print(f"Database initialized successfully at: {db_path}")
    finally:
        close_db_connection(conn)


def get_dashboard_stats(db_path=DATABASE_PATH):
    """
    Retrieves summary metrics and preview data for the dashboard:
    - Total Instruments
    - Total Stock Quantity
    - Total Inventory Value
    - Total Sales Amount
    - Recent Instruments
    - Low Stock Instruments
    - Category Overview
    Returns zeros and empty lists if the database has no records.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        # Total Instruments
        cursor.execute("SELECT COUNT(*) FROM instruments;")
        total_instruments = cursor.fetchone()[0] or 0

        # Total Stock Quantity
        cursor.execute("SELECT COALESCE(SUM(quantity), 0) FROM instruments;")
        total_quantity = cursor.fetchone()[0] or 0

        # Total Inventory Value (price * quantity)
        cursor.execute("SELECT COALESCE(SUM(price * quantity), 0.0) FROM instruments;")
        total_inventory_value = cursor.fetchone()[0] or 0.0

        # Total Sales Amount
        cursor.execute("SELECT COALESCE(SUM(total_amount), 0.0) FROM sales;")
        total_sales = cursor.fetchone()[0] or 0.0

        # Recent Instruments (latest 5 added)
        cursor.execute("SELECT * FROM instruments ORDER BY instrument_id DESC LIMIT 5;")
        recent_instruments = cursor.fetchall()

        # Low Stock Alert (instruments with quantity <= 5)
        cursor.execute("SELECT * FROM instruments WHERE quantity <= 5 ORDER BY quantity ASC LIMIT 5;")
        low_stock_instruments = cursor.fetchall()

        # Category-wise overview
        cursor.execute("""
            SELECT category, COUNT(*) as item_count, COALESCE(SUM(quantity), 0) as total_stock
            FROM instruments
            GROUP BY category
            ORDER BY total_stock DESC;
        """)
        category_summary = cursor.fetchall()

        return {
            'total_instruments': total_instruments,
            'total_quantity': total_quantity,
            'total_inventory_value': total_inventory_value,
            'total_sales': total_sales,
            'recent_instruments': recent_instruments,
            'low_stock_instruments': low_stock_instruments,
            'category_summary': category_summary
        }
    finally:
        close_db_connection(conn)


def get_instrument_by_id(instrument_id, db_path=DATABASE_PATH):
    """
    Fetches a single instrument by its unique instrument_id.
    Returns sqlite3.Row if found, or None.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM instruments WHERE instrument_id = ?;", (instrument_id,))
        return cursor.fetchone()
    finally:
        close_db_connection(conn)


def insert_instrument(instrument_id, name, category, brand, price, quantity, db_path=DATABASE_PATH):
    """
    Inserts a new instrument record into the instruments table using parameterized queries.
    Returns (success_boolean, message_string).
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO instruments (instrument_id, name, category, brand, price, quantity)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (instrument_id, name, category, brand, price, quantity))
        conn.commit()
        return True, "Instrument added successfully!"
    except sqlite3.IntegrityError as e:
        err_msg = str(e).lower()
        if "unique" in err_msg or "primary key" in err_msg:
            return False, f"Instrument ID #{instrument_id} already exists. Please choose a unique ID."
        elif "check" in err_msg:
            return False, "Price and Quantity must be non-negative values."
        return False, f"Database constraint error: {str(e)}"
    except Exception as e:
        return False, f"An unexpected error occurred: {str(e)}"
    finally:
        close_db_connection(conn)


def get_all_instruments(search_query=None, db_path=DATABASE_PATH):
    """
    Retrieves all instruments from the database.
    If search_query is provided, filters instruments by name using a parameterized query.
    Returns a list of sqlite3.Row objects.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        if search_query and search_query.strip():
            query_param = f"%{search_query.strip()}%"
            cursor.execute("""
                SELECT * FROM instruments
                WHERE name LIKE ?
                ORDER BY instrument_id ASC;
            """, (query_param,))
        else:
            cursor.execute("""
                SELECT * FROM instruments
                ORDER BY instrument_id ASC;
            """)
        return cursor.fetchall()
    finally:
        close_db_connection(conn)


def update_instrument(instrument_id, name, category, brand, price, quantity, db_path=DATABASE_PATH):
    """
    Updates an existing instrument's name, category, brand, price, and quantity.
    Ensures only the specified instrument is updated using parameterized SQL.
    Returns (success_boolean, message_string).
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        # Verify instrument existence before update
        cursor.execute("SELECT 1 FROM instruments WHERE instrument_id = ?;", (instrument_id,))
        if not cursor.fetchone():
            return False, f"Instrument #{instrument_id} does not exist in database."

        cursor.execute("""
            UPDATE instruments
            SET name = ?, category = ?, brand = ?, price = ?, quantity = ?
            WHERE instrument_id = ?;
        """, (name, category, brand, price, quantity, instrument_id))
        conn.commit()
        return True, "Instrument updated successfully!"
    except sqlite3.IntegrityError as e:
        err_msg = str(e).lower()
        if "check" in err_msg:
            return False, "Price and Quantity must be non-negative values."
        return False, f"Database integrity error: {str(e)}"
    except Exception as e:
        return False, f"An unexpected error occurred while updating: {str(e)}"
    finally:
        close_db_connection(conn)


def delete_instrument(instrument_id, db_path=DATABASE_PATH):
    """
    Deletes a single instrument by its instrument_id using a parameterized SQL query.
    Ensures only the specified instrument is deleted.
    Returns (success_boolean, message_string).
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        # Check if the instrument exists
        cursor.execute("SELECT name FROM instruments WHERE instrument_id = ?;", (instrument_id,))
        row = cursor.fetchone()
        if not row:
            return False, f"Instrument #{instrument_id} does not exist in inventory."

        inst_name = row['name']
        cursor.execute("DELETE FROM instruments WHERE instrument_id = ?;", (instrument_id,))
        conn.commit()
        return True, f"Instrument '{inst_name}' (ID: #{instrument_id}) deleted successfully!"
    except Exception as e:
        return False, f"Failed to delete instrument: {str(e)}"
    finally:
        close_db_connection(conn)


def search_instruments(query=None, criteria='all', db_path=DATABASE_PATH):
    """
    Searches instruments across name, category, brand, or instrument_id.
    Supports partial and case-insensitive matching using parameterized SQL queries.
    If query is empty, returns all instruments.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        if not query or not query.strip():
            cursor.execute("SELECT * FROM instruments ORDER BY instrument_id ASC;")
            return cursor.fetchall()

        cleaned_query = query.strip()
        # Handle cases where user types "#101" for ID
        if cleaned_query.startswith('#') and len(cleaned_query) > 1:
            cleaned_query = cleaned_query[1:].strip()

        param = f"%{cleaned_query}%"

        if criteria == 'name':
            cursor.execute("""
                SELECT * FROM instruments
                WHERE name LIKE ?
                ORDER BY instrument_id ASC;
            """, (param,))
        elif criteria == 'category':
            cursor.execute("""
                SELECT * FROM instruments
                WHERE category LIKE ?
                ORDER BY instrument_id ASC;
            """, (param,))
        elif criteria == 'brand':
            cursor.execute("""
                SELECT * FROM instruments
                WHERE brand LIKE ?
                ORDER BY instrument_id ASC;
            """, (param,))
        elif criteria == 'id':
            cursor.execute("""
                SELECT * FROM instruments
                WHERE CAST(instrument_id AS TEXT) LIKE ?
                ORDER BY instrument_id ASC;
            """, (param,))
        else:
            # Default 'all': search across name, category, brand, or ID
            cursor.execute("""
                SELECT * FROM instruments
                WHERE name LIKE ? 
                   OR category LIKE ? 
                   OR brand LIKE ? 
                   OR CAST(instrument_id AS TEXT) LIKE ?
                ORDER BY instrument_id ASC;
            """, (param, param, param, param))

        return cursor.fetchall()
    finally:
        close_db_connection(conn)


# =========================================================
# STEP 10: SALES AND STOCK MANAGEMENT FUNCTIONS
# =========================================================

def record_sale(instrument_id, quantity_sold, db_path=DATABASE_PATH):
    """
    Executes a transactional sale operation:
    1. Validates input and verifies instrument existence.
    2. Checks that quantity_sold is a positive integer and does not exceed available stock.
    3. Rejects out-of-stock instruments.
    4. Inserts a new record into the sales table.
    5. Atomically decrements the instrument's quantity in the instruments table.
    6. Automatically rolls back on any error.
    Returns (success_bool, message, sale_id_or_none).
    """
    try:
        quantity_sold = int(quantity_sold)
        if quantity_sold <= 0:
            return False, "Quantity to sell must be greater than zero (positive integer).", None
    except (ValueError, TypeError):
        return False, "Quantity must be a valid whole number.", None

    conn = get_db_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            
            # 1. Fetch current instrument details
            cursor.execute("""
                SELECT name, price, quantity FROM instruments WHERE instrument_id = ?;
            """, (instrument_id,))
            inst = cursor.fetchone()
            if not inst:
                return False, f"Instrument #{instrument_id} does not exist in inventory.", None

            inst_name = inst['name']
            unit_price = float(inst['price'])
            available_qty = int(inst['quantity'])

            # 2. Check stock constraints
            if available_qty <= 0:
                return False, f"Cannot sell '{inst_name}'. This instrument is currently out of stock.", None

            if quantity_sold > available_qty:
                return False, f"Insufficient stock for '{inst_name}'. Requested {quantity_sold}, but only {available_qty} unit(s) available.", None

            total_amount = round(quantity_sold * unit_price, 2)

            # 3. Insert into sales table
            cursor.execute("""
                INSERT INTO sales (instrument_id, instrument_name, quantity_sold, unit_price, total_amount, sale_date)
                VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'));
            """, (instrument_id, inst_name, quantity_sold, unit_price, total_amount))
            sale_id = cursor.lastrowid

            # 4. Atomically deduct inventory
            cursor.execute("""
                UPDATE instruments
                SET quantity = quantity - ?
                WHERE instrument_id = ?;
            """, (quantity_sold, instrument_id))

            return True, f"Sale #{sale_id} completed successfully! Sold {quantity_sold}x {inst_name} for ${total_amount:,.2f}.", sale_id
    except sqlite3.IntegrityError as e:
        return False, f"Database integrity error during sale: {str(e)}", None
    except Exception as e:
        return False, f"Transaction failed: {str(e)}", None
    finally:
        close_db_connection(conn)


def get_sales_history(limit=None, db_path=DATABASE_PATH):
    """
    Retrieves all sales records ordered by latest first (sale_id DESC).
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        if limit:
            cursor.execute("SELECT * FROM sales ORDER BY sale_id DESC LIMIT ?;", (limit,))
        else:
            cursor.execute("SELECT * FROM sales ORDER BY sale_id DESC;")
        return cursor.fetchall()
    finally:
        close_db_connection(conn)


def get_next_sale_id(db_path=DATABASE_PATH):
    """
    Returns the prospective next sale ID for display in the sales form.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COALESCE(MAX(sale_id), 0) + 1 FROM sales;")
        return cursor.fetchone()[0]
    finally:
        close_db_connection(conn)


def get_all_instruments_for_sales(db_path=DATABASE_PATH):
    """
    Retrieves all instruments formatted for sales dropdown selection.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT instrument_id, name, category, brand, price, quantity
            FROM instruments
            ORDER BY name ASC;
        """)
        return cursor.fetchall()
    finally:
        close_db_connection(conn)


# =========================================================
# STEP 11: REPORTS AND ANALYTICS FUNCTIONS
# =========================================================

def get_inventory_report_summary(db_path=DATABASE_PATH):
    """
    Retrieves comprehensive inventory metrics for Reports:
    - Total Number of Instruments
    - Total Stock Quantity
    - Total Inventory Value
    - Number of Available Instruments (quantity > 5)
    - Number of Low Stock Instruments (1 <= quantity <= 5)
    - Number of Out-of-Stock Instruments (quantity = 0)
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM instruments;")
        total_instruments = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COALESCE(SUM(quantity), 0) FROM instruments;")
        total_quantity = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COALESCE(SUM(price * quantity), 0.0) FROM instruments;")
        total_inventory_value = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT COUNT(*) FROM instruments WHERE quantity > 5;")
        available_count = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM instruments WHERE quantity BETWEEN 1 AND 5;")
        low_stock_count = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM instruments WHERE quantity = 0;")
        out_of_stock_count = cursor.fetchone()[0] or 0

        return {
            'total_instruments': total_instruments,
            'total_quantity': total_quantity,
            'total_inventory_value': total_inventory_value,
            'available_count': available_count,
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count
        }
    finally:
        close_db_connection(conn)


def get_category_report(db_path=DATABASE_PATH):
    """
    Aggregates inventory by category:
    Category Name, Number of Instruments, Total Quantity, Total Stock Value.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                category,
                COUNT(*) as instrument_count,
                COALESCE(SUM(quantity), 0) as total_quantity,
                COALESCE(SUM(price * quantity), 0.0) as total_value
            FROM instruments
            GROUP BY category
            ORDER BY total_value DESC;
        """)
        return cursor.fetchall()
    finally:
        close_db_connection(conn)


def get_low_stock_and_out_of_stock(db_path=DATABASE_PATH):
    """
    Returns separate lists for low-stock instruments (1-5 units)
    and out-of-stock instruments (0 units).
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT * FROM instruments
            WHERE quantity BETWEEN 1 AND 5
            ORDER BY quantity ASC, name ASC;
        """)
        low_stock = cursor.fetchall()

        cursor.execute("""
            SELECT * FROM instruments
            WHERE quantity = 0
            ORDER BY name ASC;
        """)
        out_of_stock = cursor.fetchall()

        return low_stock, out_of_stock
    finally:
        close_db_connection(conn)


def get_sales_report(date_filter='all', db_path=DATABASE_PATH):
    """
    Retrieves filtered sales metrics and sales history:
    Supported date filters:
    - 'today': date(sale_date) = date('now', 'localtime')
    - '7days': date(sale_date) >= date('now', '-7 days', 'localtime')
    - '30days': date(sale_date) >= date('now', '-30 days', 'localtime')
    - 'all': All sales records
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        where_clause = ""
        params = ()

        if date_filter == 'today':
            where_clause = "WHERE date(sale_date) = date('now', 'localtime')"
        elif date_filter == '7days':
            where_clause = "WHERE date(sale_date) >= date('now', '-7 days', 'localtime')"
        elif date_filter == '30days':
            where_clause = "WHERE date(sale_date) >= date('now', '-30 days', 'localtime')"

        # Summary Metrics
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total_sales,
                COALESCE(SUM(quantity_sold), 0) as total_items_sold,
                COALESCE(SUM(total_amount), 0.0) as total_sales_amount
            FROM sales {where_clause};
        """, params)
        summary = cursor.fetchone()

        # Detailed History (newest first)
        cursor.execute(f"""
            SELECT * FROM sales {where_clause} ORDER BY sale_id DESC;
        """, params)
        sales_records = cursor.fetchall()

        return {
            'total_sales': summary['total_sales'] or 0,
            'total_items_sold': summary['total_items_sold'] or 0,
            'total_sales_amount': summary['total_sales_amount'] or 0.0,
            'sales_records': sales_records
        }
    finally:
        close_db_connection(conn)


def get_reports_chart_data(db_path=DATABASE_PATH):
    """
    Prepares dataset dictionaries for Chart.js rendering:
    1. Category stock quantities & valuations
    2. Stock health breakdown (Available vs Low Stock vs Out of Stock)
    3. Daily sales trend
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        # 1. Category Chart Data
        cursor.execute("""
            SELECT category, COALESCE(SUM(quantity), 0) as qty, COALESCE(SUM(price * quantity), 0.0) as val
            FROM instruments
            GROUP BY category
            ORDER BY qty DESC;
        """)
        cat_rows = cursor.fetchall()
        category_labels = [r['category'] for r in cat_rows]
        category_quantities = [r['qty'] for r in cat_rows]
        category_values = [round(r['val'], 2) for r in cat_rows]

        # 2. Availability Breakdown
        cursor.execute("SELECT COUNT(*) FROM instruments WHERE quantity > 5;")
        available_cnt = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM instruments WHERE quantity BETWEEN 1 AND 5;")
        low_stock_cnt = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM instruments WHERE quantity = 0;")
        out_of_stock_cnt = cursor.fetchone()[0] or 0

        # 3. Sales Trend (by day for the last 14 days or recent days with activity)
        cursor.execute("""
            SELECT date(sale_date) as sdate, COALESCE(SUM(total_amount), 0.0) as daily_revenue, COALESCE(SUM(quantity_sold), 0) as daily_items
            FROM sales
            GROUP BY date(sale_date)
            ORDER BY sdate ASC
            LIMIT 14;
        """)
        sales_trend_rows = cursor.fetchall()
        sales_dates = [r['sdate'] for r in sales_trend_rows]
        sales_revenues = [round(r['daily_revenue'], 2) for r in sales_trend_rows]

        return {
            'category_labels': category_labels,
            'category_quantities': category_quantities,
            'category_values': category_values,
            'availability_labels': ['Available (>5)', 'Low Stock (1-5)', 'Out of Stock (0)'],
            'availability_counts': [available_cnt, low_stock_cnt, out_of_stock_cnt],
            'sales_dates': sales_dates,
            'sales_revenues': sales_revenues
        }
    finally:
        close_db_connection(conn)



def create_customer_order(user_id, items, delivery_details, db_path=DATABASE_PATH):
    """
    Executes an atomic customer order placement:
    1. Validates delivery details and stock availability for all items.
    2. Atomically decrements instrument stock in instruments table.
    3. Records corresponding transactions into sales table for Admin KPI sync.
    4. Creates order record in orders table.
    5. Inserts items into order_items table.
    6. Rolls back on any stock error.
    Returns (success_bool, message, order_id_or_none, order_number_or_none).
    """
    if not items:
        return False, "Cannot place order: No items specified.", None, None

    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        with conn:
            # 1. Validate customer exists
            cursor.execute("SELECT user_id, full_name, email FROM users WHERE user_id = ?;", (user_id,))
            customer = cursor.fetchone()
            if not customer:
                return False, "Customer account not found.", None, None

            # 2. Validate all items and stock
            total_amount = 0.0
            order_line_items = []
            for item in items:
                iid = str(item.get("instrument_id", "")).strip()
                try:
                    qty = int(item.get("quantity", 1))
                    if qty <= 0:
                        return False, "Order quantity must be at least 1.", None, None
                except (ValueError, TypeError):
                    return False, "Invalid item quantity specified.", None, None

                cursor.execute("SELECT instrument_id, name, price, quantity, image_url FROM instruments WHERE instrument_id = ?;", (iid,))
                inst = cursor.fetchone()
                if not inst:
                    return False, f"Instrument #{iid} is no longer available in the store.", None, None

                available_qty = int(inst["quantity"])
                if available_qty <= 0:
                    return False, f"Sorry, '{inst['name']}' is currently out of stock.", None, None
                if qty > available_qty:
                    return False, f"Only {available_qty} unit(s) of '{inst['name']}' available. Please adjust quantity.", None, None

                unit_price = float(inst["price"])
                subtotal = round(unit_price * qty, 2)
                total_amount += subtotal

                order_line_items.append({
                    "instrument_id": inst["instrument_id"],
                    "instrument_name": inst["name"],
                    "quantity": qty,
                    "unit_price": unit_price,
                    "subtotal": subtotal,
                    "image_url": inst["image_url"] or "/static/images/instruments/generic.jpg"
                })

            total_amount = round(total_amount, 2)

            # 3. Generate unique Order Number (e.g., ORD-20261124-9481)
            now_str = datetime.now().strftime("%Y%m%d")
            rand_code = secrets.token_hex(2).upper()
            order_number = f"ORD-{now_str}-{rand_code}"

            cust_name = delivery_details.get("customer_name") or customer["full_name"]
            cust_email = delivery_details.get("customer_email") or customer["email"]
            phone = delivery_details.get("phone_number", "").strip()
            address = delivery_details.get("shipping_address", "").strip()
            city = delivery_details.get("city", "").strip()
            pincode = delivery_details.get("pincode", "").strip()
            pay_method = delivery_details.get("payment_method", "Cash on Delivery").strip()

            if not phone or not address:
                return False, "Phone number and Delivery Address are required.", None, None

            # 4. Insert into orders table
            cursor.execute("""
                INSERT INTO orders (
                    order_number, user_id, customer_name, customer_email,
                    phone_number, shipping_address, city, pincode,
                    payment_method, total_amount, order_status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Confirmed', datetime('now', 'localtime'));
            """, (
                order_number, user_id, cust_name, cust_email,
                phone, address, city, pincode,
                pay_method, total_amount
            ))
            order_id = cursor.lastrowid

            # 5. Insert order_items, decrement inventory, and record into sales
            for line in order_line_items:
                cursor.execute("""
                    INSERT INTO order_items (
                        order_id, instrument_id, instrument_name,
                        quantity, unit_price, subtotal, image_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (
                    order_id, line["instrument_id"], line["instrument_name"],
                    line["quantity"], line["unit_price"], line["subtotal"], line["image_url"]
                ))

                # Decrement stock in instruments table
                cursor.execute("""
                    UPDATE instruments
                    SET quantity = quantity - ?
                    WHERE instrument_id = ?;
                """, (line["quantity"], line["instrument_id"]))

                # Sync into sales table for Admin KPIs & Financial Analytics
                cursor.execute("""
                    INSERT INTO sales (
                        instrument_id, instrument_name, quantity_sold,
                        unit_price, total_amount, sale_date
                    ) VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'));
                """, (
                    line["instrument_id"], line["instrument_name"], line["quantity"],
                    line["unit_price"], line["subtotal"]
                ))

            return True, "Your order has been placed successfully!", order_id, order_number
    except Exception as e:
        return False, f"Failed to place order: {str(e)}", None, None
    finally:
        close_db_connection(conn)


def get_customer_orders(user_id, db_path=DATABASE_PATH):
    """
    Fetches all orders placed by a specific customer, ordered by newest first.
    Includes item count and summary description.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT o.*, 
                   COUNT(oi.order_item_id) as item_count,
                   GROUP_CONCAT(oi.instrument_name || ' (x' || oi.quantity || ')', ', ') as items_summary
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.user_id = ?
            GROUP BY o.order_id
            ORDER BY o.order_id DESC;
        """, (user_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        close_db_connection(conn)


def get_order_details(order_id, user_id=None, db_path=DATABASE_PATH):
    """
    Fetches comprehensive order details and line items for invoice rendering.
    If user_id is provided, enforces that the order belongs to that user.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        if user_id:
            cursor.execute("SELECT * FROM orders WHERE order_id = ? AND user_id = ?;", (order_id, user_id))
        else:
            cursor.execute("SELECT * FROM orders WHERE order_id = ?;", (order_id,))
        order_row = cursor.fetchone()
        if not order_row:
            return None

        order = dict(order_row)
        cursor.execute("SELECT * FROM order_items WHERE order_id = ? ORDER BY order_item_id ASC;", (order_id,))
        items = [dict(r) for r in cursor.fetchall()]
        order["items"] = items
        order["order_items"] = items
        return order
    finally:
        close_db_connection(conn)


def get_cart_instruments(cart_dict, db_path=DATABASE_PATH):
    """
    Resolves session cart dictionary {instrument_id: quantity} into full instrument objects.
    Returns (cart_items_list, grand_total, total_item_count).
    """
    if not cart_dict:
        return [], 0.0, 0

    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cart_items = []
        grand_total = 0.0
        total_count = 0

        for iid, qty in cart_dict.items():
            cursor.execute("SELECT * FROM instruments WHERE instrument_id = ?;", (str(iid),))
            row = cursor.fetchone()
            if not row:
                continue

            item = dict(row)
            try:
                qty = max(1, int(qty))
            except (ValueError, TypeError):
                qty = 1

            avail = int(item.get("quantity", 0))
            is_out_of_stock = avail <= 0
            # Cap quantity to available stock if available > 0
            if avail > 0 and qty > avail:
                qty = avail

            unit_price = float(item["price"])
            subtotal = round(unit_price * qty, 2)
            grand_total += subtotal
            total_count += qty

            item["cart_quantity"] = qty
            item["subtotal"] = subtotal
            item["is_out_of_stock"] = is_out_of_stock
            cart_items.append(item)

        return cart_items, round(grand_total, 2), total_count
    finally:
        close_db_connection(conn)


def log_sms_notification(order_id, phone_number, message_text, gateway='WhatsApp & Push', status='Dispatched', db_path=DATABASE_PATH):
    """
    Logs an outgoing SMS / WhatsApp dispatch event for order tracking.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO sms_notifications (order_id, phone_number, message_text, gateway, status)
            VALUES (?, ?, ?, ?, ?);
        """, (order_id, phone_number, message_text, gateway, status))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error logging SMS notification: {e}")
        return False
    finally:
        close_db_connection(conn)


def get_latest_order_notification(order_id, db_path=DATABASE_PATH):
    """
    Retrieves the most recent SMS / WhatsApp notification dispatched for an order.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT * FROM sms_notifications WHERE order_id = ? ORDER BY notification_id DESC LIMIT 1;
        """, (order_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        close_db_connection(conn)


def get_all_orders_for_admin(limit=100, search=None, status_filter=None, db_path=DATABASE_PATH):
    """
    Fetches all customer orders for administrator view with item summaries,
    customer details, line items, and optional search/status filtering.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        query = """
            SELECT o.*, 
                   COUNT(oi.order_item_id) as item_count,
                   GROUP_CONCAT(oi.instrument_name || ' (x' || oi.quantity || ')', ', ') as items_summary,
                   (SELECT oi2.image_url FROM order_items oi2 WHERE oi2.order_id = o.order_id LIMIT 1) as first_item_image,
                   (SELECT oi2.instrument_name FROM order_items oi2 WHERE oi2.order_id = o.order_id LIMIT 1) as first_item_name
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            WHERE 1=1
        """
        params = []
        if status_filter and status_filter.lower() != 'all':
            query += " AND LOWER(o.order_status) = LOWER(?)"
            params.append(status_filter.strip())
        if search:
            query += " AND (o.order_number LIKE ? OR o.customer_name LIKE ? OR o.phone_number LIKE ? OR o.city LIKE ?)"
            s = f"%{search.strip()}%"
            params.extend([s, s, s, s])
        query += """
            GROUP BY o.order_id
            ORDER BY o.order_id DESC
            LIMIT ?;
        """
        params.append(limit)
        cursor.execute(query, params)
        orders = [dict(r) for r in cursor.fetchall()]

        # Attach line items to each order
        for order in orders:
            cursor.execute("SELECT * FROM order_items WHERE order_id = ? ORDER BY order_item_id ASC;", (order['order_id'],))
            items_list = [dict(item) for item in cursor.fetchall()]
            order['order_items'] = items_list
            order['items'] = items_list
            if not order.get('first_item_image'):
                order['first_item_image'] = '/static/images/instruments/generic.svg'

        return orders
    finally:
        close_db_connection(conn)


def update_order_status(order_id, new_status, db_path=DATABASE_PATH):
    """
    Updates the fulfillment status of an order (Confirmed, Processing, Out for Delivery, Delivered, Cancelled).
    """
    valid_statuses = ['Confirmed', 'Processing', 'Out for Delivery', 'Delivered', 'Cancelled']
    if new_status not in valid_statuses:
        return False, f"Invalid status '{new_status}' specified."
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE orders SET order_status = ? WHERE order_id = ?;", (new_status, order_id))
        conn.commit()
        return True, f"Order #{order_id} status updated to '{new_status}' successfully!"
    except Exception as e:
        return False, f"Error updating order status: {str(e)}"
    finally:
        close_db_connection(conn)


def get_latest_orders_feed(limit=8, db_path=DATABASE_PATH):
    """
    Fetches latest customer orders formatted for live real-time tickers and login preview.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT o.order_id, o.order_number, o.customer_name, o.phone_number,
                   o.city, o.total_amount, o.order_status, o.created_at,
                   COUNT(oi.order_item_id) as item_count,
                   GROUP_CONCAT(oi.instrument_name || ' (x' || oi.quantity || ')', ', ') as items_summary,
                   (SELECT oi2.image_url FROM order_items oi2 WHERE oi2.order_id = o.order_id LIMIT 1) as first_item_image,
                   (SELECT oi2.instrument_name FROM order_items oi2 WHERE oi2.order_id = o.order_id LIMIT 1) as first_item_name
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY o.order_id
            ORDER BY o.order_id DESC
            LIMIT ?;
        """, (limit,))
        rows = cursor.fetchall()
        orders = []
        for r in rows:
            d = dict(r)
            if not d.get('first_item_image'):
                d['first_item_image'] = '/static/images/instruments/generic.svg'
            orders.append(d)
        return orders
    finally:
        close_db_connection(conn)


def get_orders_kpi_stats(db_path=DATABASE_PATH):
    """
    Retrieves summary KPI metrics for customer orders.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM orders;")
        total_orders = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COALESCE(SUM(total_amount), 0.0) FROM orders;")
        total_revenue = cursor.fetchone()[0] or 0.0
        cursor.execute("SELECT COUNT(*) FROM orders WHERE order_status = 'Confirmed';")
        pending_orders = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM orders WHERE order_status = 'Delivered';")
        delivered_orders = cursor.fetchone()[0] or 0
        return {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'pending_orders': pending_orders,
            'delivered_orders': delivered_orders
        }
    finally:
        close_db_connection(conn)


if __name__ == '__main__':
    # Allows running database.py directly to initialize the database
    init_db()



