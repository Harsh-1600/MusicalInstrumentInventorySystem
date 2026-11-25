# USER MANUAL & SYSTEM OPERATION GUIDE
## Musical Instrument Inventory System

---

### **1. GETTING STARTED**

#### **1.1 System Installation & Startup**
1. **Open your Terminal / PowerShell** and navigate to the project directory:
   ```powershell
   cd C:\Users\hp\.gemini\antigravity\scratch\MusicalInstrumentInventorySystem
   ```
2. **Install Required Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
3. **Launch the Application**:
   ```powershell
   python app.py
   ```
4. **Access the System**:
   Open any modern web browser (Google Chrome, Edge, Firefox) and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

---

### **2. SIDEBAR NAVIGATION**

The left navigation sidebar is available across all pages:
- **📊 Dashboard**: Main executive hub with cards, alerts, and category summaries.
- **➕ Add Instrument**: Form to register new musical instruments into stock.
- **🎸 Manage Inventory**: Full catalog data table with Edit and Delete options.
- **🔍 Search Instruments**: Fast search engine supporting multi-criteria filtering.
- **🛒 Sales**: Sales processing station with live stock checks and transaction logging.
- **📈 Reports**: Financial metrics, Chart.js visualizations, and CSV exports.

---

### **3. STEP-BY-STEP USER WORKFLOWS**

#### **3.1 How to Add a New Instrument**
1. Click **➕ Add Instrument** in the sidebar.
2. Enter the **Instrument ID** (e.g., `INS031` or `201`).
3. Enter the **Instrument Name** (e.g., `Fender Player Telecaster`).
4. Select a **Category** from the dropdown (`String`, `Wind`, `Percussion`, `Keyboard`, `Electronic`, `Other`).
5. Enter the **Brand / Manufacturer** (e.g., `Fender`).
6. Enter the **Price** in USD (must be &ge; 0).
7. Enter the initial **Stock Quantity** (must be an integer &ge; 0).
8. Click **➕ Save Instrument to Inventory**.
9. A green notification will confirm the addition and redirect to the Inventory list.

#### **3.2 How to Update an Existing Instrument**
1. Navigate to **🎸 Manage Inventory**.
2. Locate the instrument you wish to edit and click the **✏️ Edit** button.
3. The form will open with the instrument's current data pre-populated.
4. *Note:* The Instrument ID is fixed to maintain primary key integrity.
5. Modify the Name, Category, Brand, Price, or Quantity as needed.
6. Click **💾 Update Instrument**.

#### **3.3 How to Delete an Instrument Safely**
1. In **🎸 Manage Inventory**, click the **🗑️ Delete** button next to the desired instrument.
2. An interactive confirmation popup will appear displaying the instrument's ID and Name.
3. Confirm by clicking **Confirm Delete**.
4. The record is permanently deleted from SQLite, and any historical sales records retain their integrity with detached foreign keys.

#### **3.4 How to Search for Instruments**
1. Click **🔍 Search Instruments** in the sidebar.
2. Enter a search term in the search box (e.g., `Yamaha`, `Flute`, or `INS001`).
3. (Optional) Choose a specific search target from the **Search In** dropdown:
   - *All Fields*
   - *Instrument Name*
   - *Category*
   - *Brand / Manufacturer*
   - *Instrument ID*
4. Click **🔍 Search**.
5. Matching records are displayed immediately. To reset, click **Clear**.

#### **3.5 How to Process a Customer Sale**
1. Click **🛒 Sales** in the sidebar.
2. From the **Select Musical Instrument** dropdown, choose the item being purchased.
   - The instrument's current stock and unit price will populate automatically.
   - If the item is out of stock, a red badge appears and submission is disabled.
3. Enter the **Quantity to Sell**.
4. Observe the **Total Amount** box update automatically in real-time (`Total = Quantity × Unit Price`).
5. Click **💳 Confirm Sale**.
6. The system executes an atomic transaction: the sale is recorded, and the warehouse inventory quantity is decremented immediately.

#### **3.6 How to View Reports and Visual Analytics**
1. Click **📈 Reports** in the sidebar.
2. View the **Inventory Summary Cards** for overall asset valuation and stock counts.
3. Check the interactive **Chart.js graphs**:
   - Hover over the **Category Stock Distribution** bar chart to see unit counts and valuation.
   - Inspect the **Stock Availability Health** doughnut chart for stock ratio warnings.
   - Track daily revenue on the **Sales Revenue Timeline**.
4. Filter sales transactions by clicking the date tabs: **All Time**, **Today**, **Last 7 Days**, or **Last 30 Days**.

#### **3.7 How to Download CSV Reports**
1. On the **📈 Reports** page, look at the top-right toolbar.
2. Click **📥 Download Inventory CSV** to export the entire instrument catalog.
3. Click **📊 Download Sales CSV** to export the sales ledger matching your current date filter.
4. The CSV files can be opened in Microsoft Excel, Google Sheets, or LibreOffice Calc.

---

### **4. TROUBLESHOOTING & ERROR MESSAGES**

| Error Message | Cause | Solution |
|:---|:---|:---|
| *"Instrument ID already exists!"* | An instrument with this exact ID is already in the database. | Enter a unique alphanumeric ID (e.g. `INS032`). |
| *"Price cannot be negative"* | A negative number was entered in the price field. | Ensure price is 0 or positive (e.g. `199.99`). |
| *"Quantity cannot be negative"* | A negative quantity was entered. | Enter 0 or a positive whole integer. |
| *"Cannot sell an out-of-stock instrument"* | Selected instrument has 0 stock units in SQLite. | Restock the instrument in Manage Inventory before selling. |
| *"Insufficient stock for..."* | The quantity entered is higher than currently available in storage. | Enter a quantity less than or equal to available units. |
