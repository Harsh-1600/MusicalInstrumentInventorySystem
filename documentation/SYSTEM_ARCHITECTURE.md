# SYSTEM ARCHITECTURE & DATA FLOW SPECIFICATION
## Musical Instrument Inventory System

---

### **1. ARCHITECTURE OVERVIEW**

The Musical Instrument Inventory System is designed using the **Model-View-Controller (MVC) pattern adapted for web microframeworks**:

```
+---------------------------------------------------------------------------------+
|                                 PRESENTATION TIER                               |
|                                                                                 |
|   +-----------------------+   +-----------------------+   +------------------+  |
|   |   HTML5 / CSS3 Grid   |   |   Vanilla JavaScript  |   |    Chart.js      |  |
|   |   (base.html & views) |   |  (Live calculations)  |   | (Visualizations) |  |
|   +-----------------------+   +-----------------------+   +------------------+  |
+----------------------------------------+----------------------------------------+
                                         |
                                         | HTTP GET / POST Requests
                                         v
+---------------------------------------------------------------------------------+
|                                APPLICATION TIER                                 |
|                                                                                 |
|   +-------------------------------------------------------------------------+   |
|   |                       Flask Application (app.py)                        |   |
|   |                                                                         |   |
|   |   - Dashboard Controller         - Sales Manager (Atomicity)            |   |
|   |   - Inventory CRUD Controller    - Reports & Filter Engine              |   |
|   |   - Search Engine Handler        - CSV Export Generator                 |   |
|   +-------------------------------------------------------------------------+   |
+----------------------------------------+----------------------------------------+
                                         |
                                         | Python DB-API 2.0 (sqlite3)
                                         v
+---------------------------------------------------------------------------------+
|                                  DATA TIER                                      |
|                                                                                 |
|   +-------------------------------------------------------------------------+   |
|   |                   Database Abstraction (database.py)                    |   |
|   |                                                                         |   |
|   |   - Connection pooling & Foreign Keys (`PRAGMA foreign_keys = ON`)      |   |
|   |   - Transaction management (`with conn:`)                               |   |
|   |   - Default Seeding Engine (30 Default Instruments)                     |   |
|   +-------------------------------------------------------------------------+   |
|                                        |                                        |
|                                        v                                        |
|   +-------------------------------------------------------------------------+   |
|   |                 SQLite File Database (musical_inventory.db)             |   |
|   |                                                                         |   |
|   |                 [ instruments Table ] <---> [ sales Table ]             |   |
|   +-------------------------------------------------------------------------+   |
+---------------------------------------------------------------------------------+
```

---

### **2. DATA FLOW DIAGRAMS (DFD)**

#### **2.1 DFD Level 0: Context Diagram**
Represents the system boundary and external entity interaction.

```
                   +--------------------------------------------+
                   | 1. Form Submission (Add/Edit/Delete/Sale)   |
                   | 2. Search Queries & Filter Parameters      |
                   | 3. CSV Download Requests                   |
                   v                                            |
         +-------------------+                        +---------------------+
         |                   |=======================>|  Musical Instrument |
         |   Store Manager / |                        |   Inventory System  |
         |      Cashier      |<=======================|                     |
         |                   |                        +---------------------+
         +-------------------+                                  |
                   ^                                            |
                   | 1. Live Stock Status & Alerts              |
                   | 2. Real-Time Transaction Receipts          |
                   | 3. Rendered Charts & Data Tables           |
                   | 4. Downloaded Inventory/Sales CSV Files    |
                   +--------------------------------------------+
```

#### **2.2 DFD Level 1: Functional Decomposition**
Decomposes the system into its core processing units:

```
                  [ Store Manager / Cashier ]
                         |   |   |   |
           +-------------+   |   |   +-------------+
           |                 |   |                 |
           v                 v   v                 v
   +---------------+ +---------------+     +---------------+ +---------------+
   | 1.0 Inventory | |  2.0 Search   |     |   3.0 Sales   | |  4.0 Reports  |
   |   Operations  | |    Engine     |     |   Processing  | |  & Analytics  |
   +---------------+ +---------------+     +---------------+ +---------------+
          |                  |                    | |                |
          | Write/Read       | Read-only          | | Deduct/Log     | Read-only
          v                  v                    v v                v
   [  instruments Table  ] <----------------------+ |     [   sales Table   ]
          |                                         +---> [                 ]
          +---------------------------------------------> [                 ]
```

#### **2.3 DFD Level 2: Sales Processing Subsystem**
Shows the internal logic of recording a sale:

```
[ User selects instrument & enters qty ]
                   |
                   v
        ( 3.1 Validate Input )
          - Check qty > 0
          - Check stock >= qty
                   |
        +----------+----------+
        |                     |
     [Valid]               [Invalid]
        |                     |
        v                     v
( 3.2 Compute Total )     ( 3.3 Emit Flash Error Alert )
  Total = Qty * Price         |
        |                     v
        v                 [ User ]
( 3.4 Begin Transaction )
  |
  +---> [ Insert row into sales table ]
  |
  +---> [ Decrement stock in instruments table ]
  |
  v
( 3.5 Commit Transaction )
  |
  v
( 3.6 Redirect & Flash Success Receipt ) ---> [ User ]
```

---

### **3. SYSTEM FLOWCHARTS**

#### **3.1 Instrument CRUD Operations Flowchart**
```
                    +--------------------+
                    |  Open Manage Page  |
                    +--------------------+
                               |
              +----------------+----------------+
              |                                 |
              v                                 v
     [ Click Add Instrument ]          [ Click Edit / Delete ]
              |                                 |
              v                                 v
     +--------------------+            +--------------------+
     | Fill In Form:      |            | Edit: Pre-fill Form|
     | - ID, Name, Brand  |            | Delete: Open Modal |
     | - Category, Price  |            +--------------------+
     | - Quantity         |                     |
     +--------------------+                     v
              |                        +--------------------+
              v                        | Confirm Operation  |
     +--------------------+            +--------------------+
     | Validate Fields:   |                     |
     | - Price >= 0       |                     |
     | - Quantity >= 0    |                     |
     | - ID is unique     |                     |
     +--------------------+                     |
              |                                 |
         /         \                            |
    [Valid]     [Invalid]                       |
       |            |                           |
       v            v                           v
  +----------+ +-----------+              +--------------------+
  | Commit   | | Flash Err |              | Execute Update or  |
  | to DB    | | & Retry   |              | Parameterized Del  |
  +----------+ +-----------+              +--------------------+
       |                                        |
       +-------------------+--------------------+
                           |
                           v
              +-------------------------+
              | Redirect to /inventory  |
              | with Flash Alert        |
              +-------------------------+
```

---

### **4. COMPONENT INTERACTION & THE PRG PATTERN**

To prevent duplicate form submissions caused by users clicking the browser reload button, the application enforces the **Post/Redirect/Get (PRG)** design pattern:

```
Browser                       Flask Server                       SQLite DB
   |                               |                                |
   |--- 1. POST /sales ----------->|                                |
   |    (Form payload)             |--- 2. Execute Transaction ---->|
   |                               |<-- 3. Success / Commit --------|
   |                               |                                |
   |<-- 4. HTTP 302 Redirect ------|                                |
   |    (Location: /sales)         |                                |
   |                               |                                |
   |--- 5. GET /sales ------------>|                                |
   |                               |--- 6. Query updated records -->|
   |<-- 7. HTTP 200 (HTML View) ---|<-- 8. Return datasets ---------|
```
