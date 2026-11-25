import io
import csv
from datetime import timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, Response, session, jsonify
from database import (
    init_db,
    get_dashboard_stats,
    get_instrument_by_id,
    insert_instrument,
    get_all_instruments,
    update_instrument,
    delete_instrument,
    search_instruments,
    record_sale,
    get_sales_history,
    get_next_sale_id,
    get_all_instruments_for_sales,
    get_inventory_report_summary,
    get_category_report,
    get_low_stock_and_out_of_stock,
    get_sales_report,
    get_reports_chart_data,
    verify_user,
    get_user_by_username,
    create_user,
    get_admin_profile,
    get_user_profile,
    update_admin_profile,
    update_admin_password,
    update_customer_profile,
    update_customer_password,
    create_password_reset_token,
    validate_reset_token,
    reset_password_with_token,
    register_customer,
    get_store_instruments,
    get_instrument_with_details,
    create_customer_order,
    get_customer_orders,
    get_order_details,
    get_cart_instruments,
    log_sms_notification,
    get_latest_order_notification,
    get_all_orders_for_admin,
    update_order_status,
    get_latest_orders_feed,
    get_orders_kpi_stats
)
from services.sms_service import (
    send_order_notification,
    send_custom_admin_message,
    clean_phone_number,
    format_display_phone
)

# Initialize Flask application
app = Flask(__name__)

# Secret key for session management and flash messages
app.config['SECRET_KEY'] = 'musical-instrument-secret-key-12345'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Context processor: Injects active cart item count for customer header navigation
@app.context_processor
def inject_cart_info():
    cart = session.get('cart', {})
    cart_count = sum(cart.values()) if isinstance(cart, dict) else 0
    return dict(cart_count=cart_count)

# Initialize SQLite database and ensure tables exist on startup
init_db()

# Allowed musical instrument categories
CATEGORIES = [
    "String Instruments",
    "Wind Instruments",
    "Percussion Instruments",
    "Keyboard Instruments",
    "Electronic Instruments",
    "Other"
]


# Authentication Decorator: Protects admin routes against unauthenticated or non-admin access
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in as an administrator to access this page.", "warning")
            return redirect(url_for('login', next=request.path))
        if session.get('role') != 'Admin':
            flash("Access Denied: You do not have administrator permissions to access this page.", "danger")
            return redirect(url_for('customer_store'))
        return f(*args, **kwargs)
    return decorated_function


# Customer Authentication Decorator: Protects customer account routes
def customer_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access your customer account.", "warning")
            return redirect(url_for('customer_login', next=request.full_path if request.query_string else request.path))
        return f(*args, **kwargs)
    return decorated_function


# Root Route (/) - Entry point when users open the application
# Redirects customers/guests directly to Customer Storefront (/store), and admins to /dashboard
@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'Admin':
            return redirect(url_for('dashboard'))
        elif session.get('role') == 'Customer':
            return redirect(url_for('customer_store'))
    return redirect(url_for('customer_store'))


# STEP 2: Dedicated Administrator Login Page Route
@app.route('/login', methods=['GET', 'POST'])
@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    # If user is already authenticated as Admin, redirect to Dashboard
    if 'user_id' in session and session.get('role') == 'Admin':
        return redirect(url_for('dashboard'))

    recent_orders = get_latest_orders_feed(limit=6)

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        remember_me = request.form.get('remember_me')

        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return render_template('login.html', username=username, recent_orders=recent_orders)

        user = verify_user(username, password)
        if user:
            session.clear()
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['full_name'] = user.get('full_name') or 'Store Administrator'
            session['role'] = user.get('role', 'Admin')

            if remember_me:
                session.permanent = True
            else:
                session.permanent = False

            flash(f"Welcome back, {user.get('full_name') or user['username']}! Logged into Admin Portal.", "success")
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid administrator username or password. Please try again.", "danger")
            return render_template('login.html', username=username, recent_orders=recent_orders)

    return render_template('login.html', recent_orders=recent_orders)


# STEP 2: Logout Route
@app.route('/logout')
@app.route('/admin/logout')
def logout():
    session.clear()
    flash("You have been signed out of the Administrator Portal.", "info")
    return redirect(url_for('login'))


# =========================================================
# MODULE 1 & 11: ADMIN PROFILE & PASSWORD MANAGEMENT ROUTES
# =========================================================

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    Admin Profile Management:
    - GET: Displays administrator details (Name, Email, Username, Role, Created Date).
    - POST: Updates administrator profile with uniqueness checks.
    """
    user_id = session.get('user_id')
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()

        if not full_name or not email or not username:
            flash("All fields (Full Name, Email, Username) are required.", "danger")
            admin_data = get_admin_profile(user_id)
            return render_template('profile.html', admin=admin_data)

        success, message = update_admin_profile(user_id, full_name, email, username)
        if success:
            session['username'] = username
            session['full_name'] = full_name
            flash(message, "success")
            return redirect(url_for('profile'))
        else:
            flash(message, "danger")
            admin_data = get_admin_profile(user_id)
            return render_template('profile.html', admin=admin_data)

    admin_data = get_admin_profile(user_id)
    if not admin_data:
        flash("Administrator profile record could not be found.", "danger")
        return redirect(url_for('dashboard'))
    return render_template('profile.html', admin=admin_data)


@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Admin Password Change:
    - Verifies current PBKDF2-SHA256 password before applying changes.
    - Enforces minimum length and confirmation matching.
    """
    if request.method == 'POST':
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not current_password or not new_password or not confirm_password:
            flash("All password fields are required.", "danger")
            return render_template('change_password.html')

        if len(new_password) < 6:
            flash("New password must be at least 6 characters long.", "danger")
            return render_template('change_password.html')

        if new_password != confirm_password:
            flash("New password and confirmation password do not match.", "danger")
            return render_template('change_password.html')

        user_id = session.get('user_id')
        success, message = update_admin_password(user_id, current_password, new_password)
        if success:
            flash(message, "success")
            return redirect(url_for('dashboard'))
        else:
            flash(message, "danger")
            return render_template('change_password.html')

    return render_template('change_password.html')


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Admin Forgot Password Request:
    - Generates cryptographically secure one-time reset token with 30-minute validity.
    - Provides demo quick-link in flash alert for instant local testing.
    """
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if not email:
            flash("Please enter your registered email address.", "warning")
            return render_template('forgot_password.html')

        raw_token, user = create_password_reset_token(email)
        if raw_token:
            reset_url = url_for('reset_password', token=raw_token, _external=True)
            flash(
                f"Password reset link generated! Demo link: {reset_url}",
                "info"
            )
            return render_template('forgot_password.html', email_sent=True, reset_url=reset_url)
        else:
            flash(
                "If the entered email is registered with an administrator account, a reset link has been dispatched.",
                "info"
            )
            return render_template('forgot_password.html', email_sent=True)

    return render_template('forgot_password.html')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Admin Password Reset via Token:
    - Validates token authenticity, expiration (30 mins), and single-use status.
    - Resets password using PBKDF2-SHA256 and invalidates token.
    """
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    is_valid, user_id, message = validate_reset_token(token)
    if not is_valid:
        flash(message, "danger")
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not new_password or not confirm_password:
            flash("Both password fields are required.", "danger")
            return render_template('reset_password.html', token=token)

        if len(new_password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template('reset_password.html', token=token)

        if new_password != confirm_password:
            flash("New password and confirmation password do not match.", "danger")
            return render_template('reset_password.html', token=token)

        success, result_message = reset_password_with_token(token, new_password)
        if success:
            flash(result_message, "success")
            return redirect(url_for('login'))
        else:
            flash(result_message, "danger")
            return render_template('reset_password.html', token=token)

    return render_template('reset_password.html', token=token)


# STEP 2 & 3: Main Dashboard Route (Protected)
@app.route('/dashboard')
@login_required
def dashboard():
    stats = get_dashboard_stats()
    return render_template('index.html', stats=stats)

# Alias 'home' endpoint for backward compatibility with existing templates
home = dashboard
app.add_url_rule('/dashboard', endpoint='home', view_func=dashboard)


# Task 1 & 4: Add Instrument Route
@app.route('/add-instrument', methods=['GET', 'POST'])
@login_required
def add_instrument():
    if request.method == 'POST':
        instrument_id_raw = request.form.get('instrument_id', '').strip()
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        brand = request.form.get('brand', '').strip()
        price_raw = request.form.get('price', '').strip()
        quantity_raw = request.form.get('quantity', '').strip()

        errors = []

        # 1. Required fields check
        if not (instrument_id_raw and name and category and brand and price_raw and quantity_raw):
            errors.append("All fields are required. Please fill in all fields.")

        # 2. Instrument ID validation
        instrument_id = instrument_id_raw
        if instrument_id:
            if get_instrument_by_id(instrument_id):
                errors.append(f"Instrument ID '{instrument_id}' already exists! Please choose a unique ID.")

        # 3. Category validation
        if category and category not in CATEGORIES:
            errors.append("Please select a valid instrument category from the options.")

        # 4. Price validation
        price = None
        if price_raw:
            try:
                price = float(price_raw)
                if price < 0:
                    errors.append("Price cannot be negative. It must be greater than or equal to 0.")
            except ValueError:
                errors.append("Price must be a valid number (e.g., 149.99).")

        # 5. Quantity validation
        quantity = None
        if quantity_raw:
            try:
                quantity = int(quantity_raw)
                if quantity < 0:
                    errors.append("Quantity cannot be negative. It must be a non-negative integer (0 or more).")
            except ValueError:
                errors.append("Quantity must be a valid whole number (e.g., 10).")

        # If validation errors exist, show messages and re-render form with entered data
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('add_instrument.html', categories=CATEGORIES, form_data=request.form)

        # Database Insertion
        success, message = insert_instrument(instrument_id, name, category, brand, price, quantity)
        if success:
            flash(f"Instrument '{name}' (ID: #{instrument_id}) added to inventory successfully!", "success")
            return redirect(url_for('manage_inventory'))
        else:
            flash(message, 'danger')
            return render_template('add_instrument.html', categories=CATEGORIES, form_data=request.form)

    return render_template('add_instrument.html', categories=CATEGORIES, form_data={})


# Step 5: Manage Inventory Route
@app.route('/inventory')
@app.route('/manage-inventory')
@login_required
def manage_inventory():
    search_query = request.args.get('search', '').strip()
    instruments = get_all_instruments(search_query=search_query)
    total_count = len(instruments)
    return render_template(
        'manage_inventory.html',
        instruments=instruments,
        total_count=total_count,
        search_query=search_query
    )


# Step 6: Update Instrument Route
@app.route('/edit-instrument/<instrument_id>', methods=['GET', 'POST'])
@app.route('/update-instrument/<instrument_id>', methods=['GET', 'POST'])
@login_required
def edit_instrument(instrument_id):
    # Verify instrument exists
    instrument = get_instrument_by_id(instrument_id)
    if not instrument:
        flash(f"Instrument #{instrument_id} does not exist in inventory.", "danger")
        return redirect(url_for('manage_inventory'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        brand = request.form.get('brand', '').strip()
        price_raw = request.form.get('price', '').strip()
        quantity_raw = request.form.get('quantity', '').strip()

        errors = []

        # 1. Required fields
        if not (name and category and brand and price_raw and quantity_raw):
            errors.append("All fields are required. Please fill in all fields.")

        # 2. Category validation
        if category and category not in CATEGORIES:
            errors.append("Please select a valid instrument category from the options.")

        # 3. Price validation
        price = None
        if price_raw:
            try:
                price = float(price_raw)
                if price < 0:
                    errors.append("Price cannot be negative. It must be greater than or equal to 0.")
            except ValueError:
                errors.append("Price must be a valid number (e.g., 299.99).")

        # 4. Quantity validation
        quantity = None
        if quantity_raw:
            try:
                quantity = int(quantity_raw)
                if quantity < 0:
                    errors.append("Quantity cannot be negative. It must be a non-negative integer (0 or more).")
            except ValueError:
                errors.append("Quantity must be a valid whole number (e.g., 10).")

        if errors:
            for err in errors:
                flash(err, 'danger')
            form_data = {
                'instrument_id': instrument_id,
                'name': name,
                'category': category,
                'brand': brand,
                'price': price_raw,
                'quantity': quantity_raw
            }
            return render_template('update_instrument.html', instrument=form_data, categories=CATEGORIES)

        # Database update
        success, message = update_instrument(instrument_id, name, category, brand, price, quantity)
        if success:
            flash(f"Instrument '{name}' (ID: #{instrument_id}) updated successfully!", "success")
            return redirect(url_for('manage_inventory'))
        else:
            flash(message, 'danger')
            form_data = {
                'instrument_id': instrument_id,
                'name': name,
                'category': category,
                'brand': brand,
                'price': price_raw,
                'quantity': quantity_raw
            }
            return render_template('update_instrument.html', instrument=form_data, categories=CATEGORIES)

    return render_template('update_instrument.html', instrument=instrument, categories=CATEGORIES)


# Step 7: Delete Instrument Route
@app.route('/delete-instrument/<instrument_id>', methods=['GET', 'POST'])
@login_required
def delete_instrument_route(instrument_id):
    instrument = get_instrument_by_id(instrument_id)
    if not instrument:
        flash(f"Instrument #{instrument_id} does not exist in inventory.", "danger")
        return redirect(url_for('manage_inventory'))

    # Deletion requires POST method for safety
    if request.method == 'POST':
        success, message = delete_instrument(instrument_id)
        if success:
            flash(message, "success")
        else:
            flash(message, "danger")
        return redirect(url_for('manage_inventory'))

    # If accessed directly via GET, render a dedicated confirmation page (safe fallback)
    return render_template('confirm_delete.html', instrument=instrument)


# Step 8: Search Instruments Route
@app.route('/search')
@app.route('/search-instruments')
@login_required
def search_instruments_route():
    query = request.args.get('q', '').strip()
    criteria = request.args.get('criteria', 'all').strip()
    valid_criteria = ['all', 'name', 'category', 'brand', 'id']
    if criteria not in valid_criteria:
        criteria = 'all'

    results = search_instruments(query=query, criteria=criteria)
    total_results = len(results)
    is_search_performed = bool(query)

    return render_template(
        'search.html',
        results=results,
        query=query,
        criteria=criteria,
        total_results=total_results,
        is_search_performed=is_search_performed
    )


# =========================================================
# Step 10: Sales and Stock Management Route
# =========================================================
@app.route('/sales', methods=['GET', 'POST'])
@login_required
def sales_route():
    if request.method == 'POST':
        instrument_id = request.form.get('instrument_id', '').strip()
        quantity_raw = request.form.get('quantity', '').strip()

        if not instrument_id:
            flash("Please select an instrument to sell.", "danger")
            return redirect(url_for('sales_route'))

        if not quantity_raw:
            flash("Please enter the quantity to sell.", "danger")
            return redirect(url_for('sales_route'))

        try:
            quantity = int(quantity_raw)
            if quantity <= 0:
                flash("Quantity to sell must be greater than zero.", "danger")
                return redirect(url_for('sales_route'))
        except ValueError:
            flash("Quantity must be a valid whole number.", "danger")
            return redirect(url_for('sales_route'))

        # Process the transactional sale
        success, message, sale_id = record_sale(instrument_id, quantity)
        if success:
            flash(message, "success")
        else:
            flash(message, "danger")

        return redirect(url_for('sales_route'))

    # GET request
    instruments = get_all_instruments_for_sales()
    sales_history = get_sales_history()
    next_sale_id = get_next_sale_id()

    return render_template(
        'sales.html',
        instruments=instruments,
        sales_history=sales_history,
        next_sale_id=next_sale_id
    )


# =========================================================
# Step 11: Reports and Analytics Route
# =========================================================
@app.route('/reports')
@login_required
def reports_route():
    date_filter = request.args.get('range', 'all').strip().lower()
    valid_filters = ['all', 'today', '7days', '30days']
    if date_filter not in valid_filters:
        date_filter = 'all'

    inventory_summary = get_inventory_report_summary()
    category_report = get_category_report()
    low_stock, out_of_stock = get_low_stock_and_out_of_stock()
    sales_report = get_sales_report(date_filter=date_filter)
    chart_data = get_reports_chart_data()

    return render_template(
        'reports.html',
        inventory_summary=inventory_summary,
        category_report=category_report,
        low_stock=low_stock,
        out_of_stock=out_of_stock,
        sales_report=sales_report,
        chart_data=chart_data,
        active_filter=date_filter
    )


# Step 11: CSV Exports
@app.route('/reports/export/inventory')
@app.route('/export-inventory-csv')
@login_required
def export_inventory_csv():
    instruments = get_all_instruments()
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        'Instrument ID',
        'Instrument Name',
        'Category',
        'Brand',
        'Price ($)',
        'Stock Quantity',
        'Stock Status',
        'Total Valuation ($)'
    ])

    for inst in instruments:
        qty = inst['quantity']
        status = 'Out of Stock' if qty == 0 else ('Low Stock' if qty <= 5 else 'Available')
        val = round(inst['price'] * qty, 2)
        writer.writerow([
            inst['instrument_id'],
            inst['name'],
            inst['category'],
            inst['brand'],
            f"{inst['price']:.2f}",
            qty,
            status,
            f"{val:.2f}"
        ])

    csv_data = output.getvalue()
    output.close()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=inventory_report.csv"}
    )


@app.route('/reports/export/sales')
@app.route('/export-sales-csv')
@login_required
def export_sales_csv():
    date_filter = request.args.get('range', 'all').strip().lower()
    sales_data = get_sales_report(date_filter=date_filter)
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        'Sale ID',
        'Instrument ID',
        'Instrument Name',
        'Quantity Sold',
        'Unit Price ($)',
        'Total Amount ($)',
        'Sale Date'
    ])

    for sale in sales_data['sales_records']:
        writer.writerow([
            sale['sale_id'],
            sale['instrument_id'] or 'N/A',
            sale['instrument_name'],
            sale['quantity_sold'],
            f"{sale['unit_price']:.2f}",
            f"{sale['total_amount']:.2f}",
            sale['sale_date']
        ])

    csv_data = output.getvalue()
    output.close()

    filename = f"sales_report_{date_filter}.csv"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# =========================================================
# CUSTOMER PORTAL, STOREFRONT & INSTRUMENT USAGE ROUTES
# =========================================================

@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    """
    Customer Self-Registration:
    - Enforces unique username and email
    - Hashes password using PBKDF2-SHA256
    - Assigns role='Customer'
    """
    if 'user_id' in session and session.get('role') == 'Customer':
        return redirect(url_for('customer_store'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not full_name or not username or not email or not password or not confirm_password:
            flash("All registration fields are required.", "danger")
            return render_template('customer/register.html', full_name=full_name, username=username, email=email)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template('customer/register.html', full_name=full_name, username=username, email=email)

        if password != confirm_password:
            flash("Passwords do not match. Please verify.", "danger")
            return render_template('customer/register.html', full_name=full_name, username=username, email=email)

        success, msg = register_customer(full_name, username, email, password)
        if success:
            flash(msg, "success")
            return redirect(url_for('customer_login'))
        else:
            flash(msg, "danger")
            return render_template('customer/register.html', full_name=full_name, username=username, email=email)

    return render_template('customer/register.html')


@app.route('/customer/login', methods=['GET', 'POST'])
def customer_login():
    """
    Dedicated Customer Login Screen:
    - Authenticates customer or store staff credentials
    - Sets authenticated session and immediately redirects to destination URL (e.g. checkout)
    """
    next_url = request.args.get('next') or request.form.get('next')
    if 'user_id' in session:
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        return redirect(url_for('customer_store'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        remember_me = request.form.get('remember_me')
        next_page = request.form.get('next') or request.args.get('next')

        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return render_template('customer/login.html', username=username, next=next_page)

        user = verify_user(username, password)
        if user:
            session.clear()
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['full_name'] = user.get('full_name') or user['username']
            session['role'] = user.get('role', 'Customer')

            if remember_me:
                session.permanent = True
            else:
                session.permanent = False

            flash(f"Welcome to SoundCraft, {session['full_name']}! You are signed in.", "success")
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('customer_store'))
        else:
            flash("Invalid customer username or password. Please try again.", "danger")
            return render_template('customer/login.html', username=username, next=next_page)

    return render_template('customer/login.html', next=next_url)


@app.route('/customer/logout')
def customer_logout():
    """
    Terminates Customer session and returns to customer login.
    """
    session.clear()
    flash("You have been signed out of your customer account.", "info")
    return redirect(url_for('customer_login'))


@app.route('/customer/profile', methods=['GET', 'POST'])
@customer_login_required
def customer_profile():
    """
    Customer Profile Management:
    - Displays customer account details (Name, Email, Username, Role, Created Date)
    - Allows updating full name and email address
    """
    user_id = session.get('user_id')
    user = get_user_profile(user_id)
    if not user:
        flash("Customer account not found.", "danger")
        return redirect(url_for('customer_logout'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()

        if not full_name or not email:
            flash("Full Name and Email are required.", "danger")
            return render_template('customer/profile.html', user=user)

        success, message = update_customer_profile(user_id, full_name, email)
        if success:
            session['full_name'] = full_name
            flash("Your customer profile has been updated successfully!", "success")
            user = get_user_profile(user_id)
            return render_template('customer/profile.html', user=user)
        else:
            flash(message, "danger")
            return render_template('customer/profile.html', user=user)

    return render_template('customer/profile.html', user=user)


@app.route('/customer/change-password', methods=['GET', 'POST'])
@customer_login_required
def customer_change_password():
    """
    Customer Password Update:
    - Enforces current password re-verification
    - Requires new password length >= 6 and matching confirmation
    """
    user_id = session.get('user_id')
    user = get_user_profile(user_id)

    if request.method == 'POST':
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not current_password or not new_password or not confirm_password:
            flash("All password fields are required.", "danger")
            return render_template('customer/change_password.html', user=user)

        if len(new_password) < 6:
            flash("New password must be at least 6 characters long.", "danger")
            return render_template('customer/change_password.html', user=user)

        if new_password != confirm_password:
            flash("New passwords do not match. Please verify.", "danger")
            return render_template('customer/change_password.html', user=user)

        success, message = update_customer_password(user_id, current_password, new_password)
        if success:
            flash(message, "success")
            return redirect(url_for('customer_profile'))
        else:
            flash(message, "danger")
            return render_template('customer/change_password.html', user=user)

    return render_template('customer/change_password.html', user=user)


@app.route('/customer/forgot-password', methods=['GET', 'POST'])
def customer_forgot_password():
    """
    Customer Password Recovery:
    - Accepts customer's registered email
    - Generates one-time password reset token with 30-min expiry
    """
    if 'user_id' in session and session.get('role') == 'Customer':
        return redirect(url_for('customer_store'))

    demo_reset_link = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if not email:
            flash("Please enter your registered email address.", "danger")
            return render_template('customer/forgot_password.html')

        raw_token, user = create_password_reset_token(email)
        if raw_token and user:
            demo_reset_link = url_for('customer_reset_password', token=raw_token, _external=True)
            flash(f"Password reset link generated for {email}.", "success")
        else:
            flash("If that email address is registered, password reset instructions have been generated.", "info")

    return render_template('customer/forgot_password.html', demo_reset_link=demo_reset_link)


@app.route('/customer/reset-password/<token>', methods=['GET', 'POST'])
def customer_reset_password(token):
    """
    Customer Password Reset Token Verification & Update:
    - Validates token hash and expiration
    - Sets new password and marks token consumed
    """
    is_valid, user_id, msg = validate_reset_token(token)
    if not is_valid:
        flash(msg, "danger")
        return redirect(url_for('customer_forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not new_password or not confirm_password:
            flash("Please fill in both password fields.", "danger")
            return render_template('customer/reset_password.html', token=token)

        if len(new_password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template('customer/reset_password.html', token=token)

        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('customer/reset_password.html', token=token)

        success, reset_msg = reset_password_with_token(token, new_password)
        if success:
            flash("Your password has been successfully reset! You can now log in with your new password.", "success")
            return redirect(url_for('customer_login'))
        else:
            flash(reset_msg, "danger")
            return render_template('customer/reset_password.html', token=token)

    return render_template('customer/reset_password.html', token=token)


@app.route('/catalog')
@app.route('/store')
def customer_store():
    """
    Customer Storefront & Catalog View:
    - Lists instruments with high-resolution real photographs
    - Shows real-time stock status (In Stock / Low Stock / Out of Stock)
    - Supports live multi-dimensional filtering by Category, Stock Status, and Search Query
    """
    category = request.args.get('category', 'All').strip()
    search = request.args.get('search', '').strip()
    stock_filter = request.args.get('stock', 'all').strip().lower()

    # Fetch all instruments matching category and search (for baseline counts)
    all_matching = get_store_instruments(category=category, search=search)

    total_count = len(all_matching)
    in_stock_count = sum(1 for i in all_matching if i['stock_status'] == 'in_stock')
    low_stock_count = sum(1 for i in all_matching if i['stock_status'] == 'low_stock')
    out_of_stock_count = sum(1 for i in all_matching if i['stock_status'] == 'out_of_stock')

    # Apply stock filter if selected
    if stock_filter in ['in_stock', 'low_stock', 'out_of_stock']:
        instruments = [i for i in all_matching if i['stock_status'] == stock_filter]
    else:
        stock_filter = 'all'
        instruments = all_matching

    # Categories list for quick filtering pills
    store_categories = ['All', 'String Instruments', 'Wind Instruments', 'Percussion Instruments', 'Keyboard Instruments', 'Electronic Instruments', 'Other']

    return render_template(
        'customer/store.html',
        instruments=instruments,
        categories=store_categories,
        current_category=category,
        current_stock=stock_filter,
        search_query=search,
        total_count=total_count,
        in_stock_count=in_stock_count,
        low_stock_count=low_stock_count,
        out_of_stock_count=out_of_stock_count
    )


@app.route('/customer/instrument/<instrument_id>')
@app.route('/instrument/<instrument_id>')
def customer_instrument_detail(instrument_id):
    """
    Detailed Instrument View ("Ethuku Use Pannalam"):
    - Displays large instrument image and price
    - Displays live stock availability status
    - Explains what the instrument is used for (musical genres, playing context, sound characteristics, and tips)
    """
    instrument = get_instrument_with_details(instrument_id)
    if not instrument:
        flash(f"Instrument '{instrument_id}' could not be found.", "warning")
        return redirect(url_for('customer_store'))

    # Fetch related instruments in the same category
    related_instruments = get_store_instruments(category=instrument['category'])
    # Filter out current instrument and limit to 4
    related_instruments = [i for i in related_instruments if str(i['instrument_id']) != str(instrument_id)][:4]

    return render_template(
        'customer/instrument_detail.html',
        instrument=instrument,
        related_instruments=related_instruments
    )


@app.route('/customer/inquire/<instrument_id>', methods=['POST'])
def customer_inquire(instrument_id):
    """
    Handles customer inquiry / reservation request for an instrument.
    """
    instrument = get_instrument_with_details(instrument_id)
    name = instrument['name'] if instrument else "the instrument"
    flash(f"Thank you! Your inquiry for '{name}' has been received. Our store specialist will contact you shortly.", "success")
    return redirect(url_for('customer_instrument_detail', instrument_id=instrument_id))


# =========================================================
# CUSTOMER ORDERING & CHECKOUT SYSTEM ROUTES
# =========================================================

@app.route('/customer/checkout/<instrument_id>', methods=['GET', 'POST'])
def customer_checkout_single(instrument_id):
    """
    Direct 1-Click Checkout for a single instrument:
    - Enforces customer login (redirects with destination URL preserved)
    - Validates live stock
    - Renders delivery address & payment review form
    - Places order, updates inventory, and redirects to digital receipt
    """
    if 'user_id' not in session:
        flash("Please sign in to place an order.", "warning")
        return redirect(url_for('customer_login', next=request.full_path if request.query_string else request.path))

    user_id = session.get('user_id')
    user = get_user_profile(user_id)
    instrument = get_instrument_with_details(instrument_id)
    if not instrument:
        flash(f"Instrument '{instrument_id}' could not be found.", "warning")
        return redirect(url_for('customer_store'))

    available_qty = int(instrument.get('quantity', 0))
    if available_qty <= 0:
        flash(f"Sorry, '{instrument['name']}' is currently out of stock.", "danger")
        return redirect(url_for('customer_instrument_detail', instrument_id=instrument_id))

    try:
        qty = int(request.args.get('quantity', 1))
        qty = max(1, min(qty, available_qty))
    except (ValueError, TypeError):
        qty = 1

    unit_price = float(instrument['price'])
    subtotal = round(unit_price * qty, 2)
    grand_total = subtotal

    if request.method == 'POST':
        try:
            qty = int(request.form.get('quantity', qty))
            qty = max(1, min(qty, available_qty))
        except (ValueError, TypeError):
            qty = 1

        subtotal = round(unit_price * qty, 2)
        grand_total = subtotal

        delivery_details = {
            'customer_name': request.form.get('customer_name', '').strip() or user.get('full_name'),
            'customer_email': request.form.get('customer_email', '').strip() or user.get('email'),
            'phone_number': request.form.get('phone_number', '').strip(),
            'shipping_address': request.form.get('shipping_address', '').strip(),
            'city': request.form.get('city', '').strip(),
            'pincode': request.form.get('pincode', '').strip(),
            'payment_method': request.form.get('payment_method', 'Cash on Delivery').strip()
        }

        if not delivery_details['phone_number'] or not delivery_details['shipping_address']:
            flash("Please provide your delivery phone number and shipping address.", "danger")
            return render_template(
                'customer/checkout.html',
                instrument=instrument,
                quantity=qty,
                subtotal=subtotal,
                grand_total=grand_total,
                user=user,
                is_cart_checkout=False
            )

        items = [{'instrument_id': instrument['instrument_id'], 'quantity': qty}]
        success, msg, order_id, order_number = create_customer_order(user_id, items, delivery_details)

        if success:
            session['customer_phone'] = delivery_details.get('phone_number')
            session.modified = True
            order_full = get_order_details(order_id)
            notif = send_order_notification(order_full or delivery_details, delivery_details.get('phone_number'))
            log_sms_notification(order_id, notif['clean_phone'], notif['message_text'], notif['gateway'])
            flash(f"Order #{order_number} confirmed! SMS & WhatsApp notification sent to {notif['formatted_phone']}.", "success")
            return redirect(url_for('customer_order_receipt', order_id=order_id))
        else:
            flash(msg, "danger")
            return render_template(
                'customer/checkout.html',
                instrument=instrument,
                quantity=qty,
                subtotal=subtotal,
                grand_total=grand_total,
                user=user,
                is_cart_checkout=False
            )

    return render_template(
        'customer/checkout.html',
        instrument=instrument,
        quantity=qty,
        subtotal=subtotal,
        grand_total=grand_total,
        user=user,
        is_cart_checkout=False
    )


@app.route('/customer/cart')
def customer_cart():
    """
    Displays current customer shopping cart with live quantities, subtotals, and checkout button.
    """
    cart = session.get('cart', {})
    cart_items, grand_total, total_count = get_cart_instruments(cart)
    return render_template(
        'customer/cart.html',
        cart_items=cart_items,
        grand_total=grand_total,
        total_count=total_count
    )


@app.route('/customer/cart/add/<instrument_id>', methods=['POST'])
def customer_cart_add(instrument_id):
    """
    Adds an instrument to the session cart or increments existing quantity.
    """
    cart = session.get('cart', {})
    if not isinstance(cart, dict):
        cart = {}

    try:
        qty = int(request.form.get('quantity', 1))
        qty = max(1, qty)
    except (ValueError, TypeError):
        qty = 1

    instrument = get_instrument_with_details(instrument_id)
    if not instrument:
        flash("Instrument not found.", "danger")
        return redirect(url_for('customer_store'))

    avail = int(instrument.get('quantity', 0))
    if avail <= 0:
        flash(f"Sorry, '{instrument['name']}' is out of stock.", "danger")
        return redirect(url_for('customer_instrument_detail', instrument_id=instrument_id))

    current_qty = cart.get(str(instrument_id), 0)
    new_qty = min(current_qty + qty, avail)
    cart[str(instrument_id)] = new_qty
    session['cart'] = cart
    session.modified = True

    flash(f"Added '{instrument['name']}' (x{qty}) to your cart!", "success")
    return redirect(url_for('customer_cart'))


@app.route('/customer/cart/update', methods=['POST'])
def customer_cart_update():
    """
    Updates quantities for items in session cart.
    """
    cart = session.get('cart', {})
    if not isinstance(cart, dict):
        cart = {}

    instrument_id = str(request.form.get('instrument_id', '')).strip()
    action = request.form.get('action')

    if instrument_id in cart:
        if action == 'increase':
            inst = get_instrument_with_details(instrument_id)
            avail = int(inst.get('quantity', 0)) if inst else 1
            if cart[instrument_id] < avail:
                cart[instrument_id] += 1
            else:
                flash(f"Maximum available stock ({avail}) reached for this item.", "warning")
        elif action == 'decrease':
            cart[instrument_id] -= 1
            if cart[instrument_id] <= 0:
                del cart[instrument_id]
        elif action == 'remove':
            del cart[instrument_id]

    session['cart'] = cart
    session.modified = True
    return redirect(url_for('customer_cart'))


@app.route('/customer/cart/clear', methods=['POST'])
def customer_cart_clear():
    """
    Empties all items from the customer cart.
    """
    session['cart'] = {}
    session.modified = True
    flash("Your shopping cart has been cleared.", "info")
    return redirect(url_for('customer_cart'))


@app.route('/customer/cart/checkout', methods=['GET', 'POST'])
def customer_cart_checkout():
    """
    Multi-item checkout for all items currently in customer cart:
    - Enforces customer login
    - Validates cart is not empty
    - Processes order and clears cart upon success
    """
    if 'user_id' not in session:
        flash("Please sign in to complete your checkout.", "warning")
        return redirect(url_for('customer_login', next=url_for('customer_cart_checkout')))

    cart = session.get('cart', {})
    cart_items, grand_total, total_count = get_cart_instruments(cart)
    if not cart_items:
        flash("Your cart is empty. Please add items to proceed with checkout.", "warning")
        return redirect(url_for('customer_store'))

    # Check for any out-of-stock items
    for item in cart_items:
        if item['is_out_of_stock']:
            flash(f"'{item['name']}' in your cart is currently out of stock. Please remove it to proceed.", "danger")
            return redirect(url_for('customer_cart'))

    user_id = session.get('user_id')
    user = get_user_profile(user_id)

    if request.method == 'POST':
        delivery_details = {
            'customer_name': request.form.get('customer_name', '').strip() or user.get('full_name'),
            'customer_email': request.form.get('customer_email', '').strip() or user.get('email'),
            'phone_number': request.form.get('phone_number', '').strip(),
            'shipping_address': request.form.get('shipping_address', '').strip(),
            'city': request.form.get('city', '').strip(),
            'pincode': request.form.get('pincode', '').strip(),
            'payment_method': request.form.get('payment_method', 'Cash on Delivery').strip()
        }

        if not delivery_details['phone_number'] or not delivery_details['shipping_address']:
            flash("Please provide your delivery phone number and shipping address.", "danger")
            return render_template(
                'customer/checkout.html',
                cart_items=cart_items,
                grand_total=grand_total,
                total_count=total_count,
                user=user,
                is_cart_checkout=True
            )

        items = [{'instrument_id': item['instrument_id'], 'quantity': item['cart_quantity']} for item in cart_items]
        success, msg, order_id, order_number = create_customer_order(user_id, items, delivery_details)

        if success:
            session['cart'] = {}
            session['customer_phone'] = delivery_details.get('phone_number')
            session.modified = True
            order_full = get_order_details(order_id)
            notif = send_order_notification(order_full or delivery_details, delivery_details.get('phone_number'))
            log_sms_notification(order_id, notif['clean_phone'], notif['message_text'], notif['gateway'])
            flash(f"Order #{order_number} confirmed! SMS & WhatsApp notification sent to {notif['formatted_phone']}.", "success")
            return redirect(url_for('customer_order_receipt', order_id=order_id))
        else:
            flash(msg, "danger")
            return render_template(
                'customer/checkout.html',
                cart_items=cart_items,
                grand_total=grand_total,
                total_count=total_count,
                user=user,
                is_cart_checkout=True
            )

    return render_template(
        'customer/checkout.html',
        cart_items=cart_items,
        grand_total=grand_total,
        total_count=total_count,
        user=user,
        is_cart_checkout=True
    )


@app.route('/customer/order/<int:order_id>')
def customer_order_receipt(order_id):
    """
    Renders detailed customer digital receipt / invoice with printable view
    and interactive Smartphone SMS & WhatsApp notification alerts.
    """
    if 'user_id' not in session:
        flash("Please sign in to view your order receipt.", "warning")
        return redirect(url_for('customer_login'))

    user_id = session.get('user_id') if session.get('role') != 'Admin' else None
    order = get_order_details(order_id, user_id=user_id)
    if not order:
        flash(f"Order #{order_id} could not be found or you do not have permission to view it.", "danger")
        return redirect(url_for('customer_store'))

    # Prepare real-time notification data for on-screen SMS card and WhatsApp delivery
    notification = send_order_notification(order)
    return render_template('customer/order_receipt.html', order=order, notification=notification)


@app.route('/api/order/<int:order_id>/send-sms', methods=['POST'])
def api_send_order_sms(order_id):
    """
    Interactive API endpoint to re-dispatch or test sending SMS to any mobile number.
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401

    user_id = session.get('user_id') if session.get('role') != 'Admin' else None
    order = get_order_details(order_id, user_id=user_id)
    if not order:
        return jsonify({'success': False, 'message': 'Order not found'}), 404

    custom_phone = request.form.get('phone_number', '').strip() or order.get('phone_number', '')
    notif = send_order_notification(order, custom_phone)
    log_sms_notification(order_id, notif['clean_phone'], notif['message_text'], notif['gateway'])
    return jsonify({
        'success': True,
        'message': f"Order confirmation notification dispatched to {notif['formatted_phone']}",
        'notification': notif
    })


@app.route('/customer/orders')
@customer_login_required
def customer_orders():
    """
    Customer 'My Orders' History View:
    - Lists all previous purchases made by the customer with status and date.
    """
    user_id = session.get('user_id')
    orders = get_customer_orders(user_id)
    return render_template('customer/orders.html', orders=orders)


# =========================================================
# ADMIN CUSTOMER ORDERS MANAGEMENT & DIRECT MESSAGING
# =========================================================

@app.route('/api/admin/live-orders')
def api_admin_live_orders():
    """
    Real-time Live Customer Orders Feed:
    - Strictly checks administrator privileges.
    - Non-admins and unauthenticated requests receive empty orders array with zero leaked customer details.
    """
    is_admin = ('user_id' in session and session.get('role') == 'Admin')
    limit = request.args.get('limit', 8, type=int)

    if not is_admin:
        # Do not expose customer phone numbers or order data to unauthorized visitors
        return jsonify({
            'success': True,
            'count': 0,
            'orders': [],
            'authenticated': False,
            'message': 'Administrator permissions required to access customer orders feed.'
        })

    orders = get_latest_orders_feed(limit=limit)
    return jsonify({
        'success': True,
        'count': len(orders),
        'orders': orders,
        'authenticated': True
    })


@app.route('/admin/orders')
@login_required
def admin_orders():
    """
    Admin Customer Orders Hub:
    - Lists all orders placed through the customer storefront
    - Supports status filtering (All, Confirmed, Processing, Out for Delivery, Delivered, Cancelled)
    - Supports search by order number, customer name, phone, or city
    - Provides 1-click Direct WhatsApp & SMS messaging straight to customer's phone
    """
    status_filter = request.args.get('status', 'all').strip()
    search = request.args.get('search', '').strip()

    orders = get_all_orders_for_admin(status_filter=status_filter, search=search)
    kpis = get_orders_kpi_stats()

    return render_template(
        'admin/orders.html',
        orders=orders,
        kpis=kpis,
        current_status=status_filter,
        search_query=search
    )


@app.route('/admin/orders/status/<int:order_id>', methods=['POST'])
@login_required
def admin_update_order_status(order_id):
    """
    Updates customer order fulfillment status directly from Admin portal.
    """
    new_status = request.form.get('order_status', '').strip()
    success, msg = update_order_status(order_id, new_status)
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')
    return redirect(url_for('admin_orders'))


@app.route('/api/admin/send-customer-message', methods=['POST'])
@login_required
def api_admin_send_customer_message():
    """
    Dispatches a direct SMS / WhatsApp message to a customer's phone number.
    RESTRICTED: Strictly only authenticated store administrators can send messages.
    """
    if 'user_id' not in session or session.get('role') != 'Admin':
        return jsonify({
            'success': False,
            'message': 'Access restricted: Only store administrators can send messages to customers.'
        }), 403

    order_id = request.form.get('order_id')
    raw_phone = request.form.get('phone_number', '').strip()
    customer_name = request.form.get('customer_name', '').strip()
    message_text = request.form.get('message_text', '').strip()
    order_number = request.form.get('order_number', '').strip()

    if not raw_phone or not message_text:
        return jsonify({'success': False, 'message': 'Phone number and message text are required.'}), 400

    notif = send_custom_admin_message(raw_phone, customer_name, message_text, order_number)

    # Log dispatch event to sms_notifications audit table
    valid_order_id = int(order_id) if order_id and str(order_id).isdigit() else None
    log_sms_notification(
        order_id=valid_order_id,
        phone_number=notif['clean_phone'],
        message_text=notif['message_text'],
        gateway=notif['gateway'],
        status='Dispatched'
    )

    return jsonify({
        'success': True,
        'message': f"Direct message prepared and dispatched to {notif['formatted_phone']}!",
        'notification': notif
    })


if __name__ == '__main__':
    # Run the Flask development server in debug mode
    app.run(debug=True, port=5000)



