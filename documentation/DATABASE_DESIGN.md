# DATABASE DESIGN AND ARCHITECTURE SPECIFICATION
## Musical Instrument Inventory System

---

### **1. OVERVIEW**
The system uses **SQLite 3** as its database management system, stored in a local database file named `musical_inventory.db`. SQLite provides a lightweight, zero-configuration, serverless, and transactional relational database engine that ensures ACID (Atomicity, Consistency, Isolation, Durability) compliance.

---

### **2. ENTITY-RELATIONSHIP (ER) DIAGRAM**

```
+-------------------------------------------------+
|                   instruments                   |
+-------------------------------------------------+
| PK | instrument_id : TEXT                       |
|    | name          : TEXT                       |
|    | category      : TEXT                       |
|    | brand         : TEXT                       |
|    | price         : REAL (CHECK >= 0)          |
|    | quantity      : INTEGER (CHECK >= 0)       |
+-------------------------------------------------+
                         |
                         | 1
                         |
                         | has many
                         |
                         | N
                         v
+-------------------------------------------------+
|                      sales                      |
+-------------------------------------------------+
| PK | sale_id         : INTEGER AUTOINCREMENT    |
| FK | instrument_id   : TEXT (NULLABLE)          |
|    | instrument_name : TEXT                     |
|    | quantity_sold   : INTEGER (CHECK >= 0)     |
|    | unit_price      : REAL (CHECK >= 0)        |
|    | total_amount    : REAL (CHECK >= 0)        |
|    | sale_date       : TIMESTAMP                |
+-------------------------------------------------+
```

---

### **3. DATA DICTIONARY**

#### **3.1 Table: `instruments`**
Contains the master catalog and inventory levels of all musical instruments.

| Column | Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| `instrument_id` | `TEXT` | PRIMARY KEY | None | Unique instrument code (e.g., `INS001`, `101`) |
| `name` | `TEXT` | NOT NULL | None | Instrument product model name |
| `category` | `TEXT` | NOT NULL | None | Instrument category (String, Wind, Percussion, Keyboard, Electronic, Other) |
| `brand` | `TEXT` | NOT NULL | None | Brand manufacturer name (Yamaha, Fender, Roland, etc.) |
| `price` | `REAL` | NOT NULL, CHECK (price >= 0) | None | Retail unit price in USD ($) |
| `quantity` | `INTEGER` | NOT NULL, CHECK (quantity >= 0) | None | Available warehouse stock quantity |

#### **3.2 Table: `sales`**
Maintains the transactional sales ledger for sold instruments.

| Column | Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| `sale_id` | `INTEGER` | PRIMARY KEY AUTOINCREMENT | Auto | Auto-incrementing transaction receipt number |
| `instrument_id` | `TEXT` | FOREIGN KEY REFERENCES `instruments(instrument_id)` ON DELETE SET NULL | NULL | Reference to the sold instrument (decoupled if item is deleted) |
| `instrument_name` | `TEXT` | NOT NULL | None | Static snapshot of instrument name at time of sale |
| `quantity_sold` | `INTEGER` | NOT NULL, CHECK (quantity_sold >= 0) | None | Number of units purchased |
| `unit_price` | `REAL` | NOT NULL, CHECK (unit_price >= 0) | None | Unit price at the time of sale |
| `total_amount` | `REAL` | NOT NULL, CHECK (total_amount >= 0) | None | Total transaction value (`quantity_sold * unit_price`) |
| `sale_date` | `TIMESTAMP` | NOT NULL | `CURRENT_TIMESTAMP` | Date and time the transaction was processed |

---

### **4. DATABASE SCHEMA DDL SCRIPT**

```sql
-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- Instruments Catalog Table
CREATE TABLE IF NOT EXISTS instruments (
    instrument_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    brand TEXT NOT NULL,
    price REAL NOT NULL CHECK (price >= 0),
    quantity INTEGER NOT NULL CHECK (quantity >= 0)
);

-- Sales Transaction Ledger Table
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
```

---

### **5. TRANSACTION MANAGEMENT & ATOMICITY**

When a customer sale is recorded, the database must execute two related operations:
1. Insert a new record into `sales`.
2. Decrement the `quantity` of the matching instrument in `instruments`.

To prevent inconsistencies (e.g. money recorded without deducting stock, or stock deducted without logging the sale), these operations execute inside an **atomic transaction context**:

```python
with conn:  # Context manager starts transaction; commits on success, rolls back on exception
    cursor.execute("""
        INSERT INTO sales (instrument_id, instrument_name, quantity_sold, unit_price, total_amount, sale_date)
        VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'));
    """, (instrument_id, name, qty, price, total))
    
    cursor.execute("""
        UPDATE instruments
        SET quantity = quantity - ?
        WHERE instrument_id = ?;
    """, (qty, instrument_id))
```

If an error occurs (such as a database lock or integrity failure), Python rolls back both operations, leaving the database state pristine.

---

### **6. SEED DATA: 30 DEFAULT MUSICAL INSTRUMENTS**

The database is pre-configured with exactly 30 standard musical instruments across 5 classifications:

| ID | Name | Category | Brand | Price ($) | Quantity |
|:---|:---|:---|:---|:---:|:---:|
| `INS001` | Guitar | String Instruments | Yamaha | 8,500.00 | 10 |
| `INS002` | Piano | Keyboard Instruments | Casio | 45,000.00 | 5 |
| `INS003` | Violin | String Instruments | Stentor | 12,000.00 | 8 |
| `INS004` | Drum Kit | Percussion Instruments | Pearl | 35,000.00 | 4 |
| `INS005` | Flute | Wind Instruments | Yamaha | 2,500.00 | 15 |
| `INS006` | Keyboard | Keyboard Instruments | Roland | 18,000.00 | 7 |
| `INS007` | Ukulele | String Instruments | Kadence | 3,500.00 | 12 |
| `INS008` | Saxophone | Wind Instruments | Jupiter | 28,000.00 | 3 |
| `INS009` | Trumpet | Wind Instruments | Bach | 22,000.00 | 6 |
| `INS010` | Cello | String Instruments | Yamaha | 65,000.00 | 2 |
| `INS011` | Tabla | Percussion Instruments | Radhe | 4,500.00 | 10 |
| `INS012` | Mridangam | Percussion Instruments | Handmade | 7,000.00 | 5 |
| `INS013` | Clarinet | Wind Instruments | Yamaha | 15,000.00 | 4 |
| `INS014` | Harmonica | Wind Instruments | Hohner | 1,200.00 | 20 |
| `INS015` | Banjo | String Instruments | Deering | 18,000.00 | 3 |
| `INS016` | Mandolin | String Instruments | Ibanez | 9,500.00 | 6 |
| `INS017` | Electric Guitar | String Instruments | Fender | 25,000.00 | 5 |
| `INS018` | Bass Guitar | String Instruments | Ibanez | 22,000.00 | 4 |
| `INS019` | Djembe | Percussion Instruments | Meinl | 6,000.00 | 7 |
| `INS020` | Conga | Percussion Instruments | LP | 14,000.00 | 3 |
| `INS021` | Xylophone | Percussion Instruments | Yamaha | 8,500.00 | 5 |
| `INS022` | Accordion | Keyboard Instruments | Hohner | 32,000.00 | 2 |
| `INS023` | Organ | Keyboard Instruments | Yamaha | 55,000.00 | 2 |
| `INS024` | Oboe | Wind Instruments | Yamaha | 38,000.00 | 2 |
| `INS025` | Trombone | Wind Instruments | Bach | 26,000.00 | 3 |
| `INS026` | Tuba | Wind Instruments | Jupiter | 48,000.00 | 2 |
| `INS027` | Sitar | String Instruments | Handmade | 18,000.00 | 4 |
| `INS028` | Veena | String Instruments | Saraswati | 15,000.00 | 5 |
| `INS029` | Tambourine | Percussion Instruments | Meinl | 1,800.00 | 12 |
| `INS030` | Triangle | Percussion Instruments | Stagg | 900.00 | 15 |

---

### **7. SAMPLE PARAMETERIZED QUERIES**

#### Multi-Criteria Search:
```sql
SELECT * FROM instruments
WHERE name LIKE ? OR category LIKE ? OR brand LIKE ? OR CAST(instrument_id AS TEXT) LIKE ?
ORDER BY instrument_id ASC;
```

#### Category Valuation Summary:
```sql
SELECT 
    category,
    COUNT(*) as instrument_count,
    COALESCE(SUM(quantity), 0) as total_quantity,
    COALESCE(SUM(price * quantity), 0.0) as total_value
FROM instruments
GROUP BY category
ORDER BY total_value DESC;
```

#### Date-Filtered Sales Query (e.g. Last 7 Days):
```sql
SELECT * FROM sales
WHERE date(sale_date) >= date('now', '-7 days', 'localtime')
ORDER BY sale_id DESC;
```
