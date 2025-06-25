"""
Multilingual Customer Portal for Aufraumenbee Cleaning Service
Production-ready version with internationalization support
"""

import streamlit as st
import sqlite3
import bcrypt
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import re
import random
import string
import hashlib
import time
import random
import string
import hashlib

# Import translation system
from translations import t, init_language_selector, get_current_language, format_currency, format_date, format_time

# Page configuration
st.set_page_config(
    page_title="Aufraumenbee - Book Cleaning Services",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for multilingual support
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #FF6B6B;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .service-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #f0f0f0;
        margin: 1rem 0;
        transition: border-color 0.3s, transform 0.2s;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .service-card:hover {
        border-color: #FF6B6B;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .price-tag {
        color: #FF6B6B;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .language-switcher {
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 999;
        background: white;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-message {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        color: #155724;
    }
</style>
""", unsafe_allow_html=True)

def init_database():
    """Initialize the database"""
    conn = sqlite3.connect('aufraumenbee.db', check_same_thread=False)
    
    # Customer users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS customer_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            verified BOOLEAN DEFAULT FALSE
        )
    ''')
    
    # Customers table (for admin compatibility)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            address TEXT,
            preferences TEXT,
            rating REAL DEFAULT 0,
            total_jobs INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Service types with multilingual support
    conn.execute('''
        CREATE TABLE IF NOT EXISTS service_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_en TEXT NOT NULL,
            name_de TEXT NOT NULL,
            description_en TEXT,
            description_de TEXT,
            base_price REAL,
            duration_hours INTEGER DEFAULT 2
        )
    ''')
    
    # Customer bookings
    conn.execute('''
        CREATE TABLE IF NOT EXISTS customer_bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_user_id INTEGER,
            service_type TEXT NOT NULL,
            service_date DATE NOT NULL,
            service_time TEXT NOT NULL,
            address TEXT NOT NULL,
            special_instructions TEXT,
            status TEXT DEFAULT 'pending',
            total_price REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_user_id) REFERENCES customer_users (id)
        )
    ''')
    
    # Password reset codes table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            reset_code TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN DEFAULT FALSE
        )
    ''')
    
    # Insert default service types if they don't exist
    default_services = [
        ('Basic Cleaning', 'Grundreinigung', 'Standard home cleaning service', 'Standard-Hausreinigungsservice', 45.0, 2),
        ('Deep Cleaning', 'Tiefenreinigung', 'Thorough deep cleaning service', 'Gründlicher Tiefenreinigungsservice', 75.0, 4),
        ('Office Cleaning', 'Büroreinigung', 'Professional office cleaning', 'Professionelle Büroreinigung', 55.0, 3),
        ('Window Cleaning', 'Fensterreinigung', 'Interior and exterior window cleaning', 'Innen- und Außenfensterreinigung', 35.0, 1),
        ('Carpet Cleaning', 'Teppichreinigung', 'Professional carpet and upholstery cleaning', 'Professionelle Teppich- und Polsterreinigung', 65.0, 2),
        ('Move-in/Move-out', 'Ein-/Auszugsreinigung', 'Complete cleaning for moving', 'Komplette Reinigung für Umzug', 95.0, 5)
    ]
    
    for service in default_services:
        try:
            conn.execute('''INSERT OR IGNORE INTO service_types 
                           (name_en, name_de, description_en, description_de, base_price, duration_hours) 
                           VALUES (?, ?, ?, ?, ?, ?)''', service)
        except:
            pass
    
    conn.commit()
    return conn

def hash_password(password: str) -> bytes:
    """Hash a password"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password: str, password_hash: bytes) -> bool:
    """Verify a password"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash)

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def register_customer(email: str, password: str, first_name: str, last_name: str, phone: str, address: str) -> bool:
    """Register new customer with multilingual support"""
    try:
        conn = init_database()
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute('SELECT email FROM customer_users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return False
        
        # Hash password and insert new user
        password_hash = hash_password(password)
        
        # Insert into customer_users table (for portal login)
        cursor.execute('''
            INSERT INTO customer_users (email, password_hash, first_name, last_name, phone, address)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (email, password_hash, first_name, last_name, phone, address))
        
        # Also insert into customers table (for admin management)
        full_name = f"{first_name} {last_name}".strip()
        cursor.execute('''
            INSERT INTO customers (name, email, phone, address, preferences)
            VALUES (?, ?, ?, ?, ?)
        ''', (full_name, email, phone, address, "Registered via customer portal"))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception:
        if 'conn' in locals():
            conn.close()
        return False

def authenticate_customer(email: str, password: str) -> Optional[Dict]:
    """Authenticate customer login"""
    try:
        conn = init_database()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customer_users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and verify_password(password, user[2]):  # user[2] is password_hash
            return {
                'id': user[0],
                'email': user[1],
                'first_name': user[3],
                'last_name': user[4],
                'phone': user[5],
                'address': user[6]
            }
        return None
    except Exception:
        return None

def get_available_services(language: str = 'en') -> List[Dict]:
    """Get available services in the specified language"""
    conn = init_database()
    services = pd.read_sql_query('SELECT * FROM service_types WHERE active = 1', conn)
    conn.close()
    
    service_list = []
    for _, service in services.iterrows():
        # Handle multilingual names with fallback
        name_col = f'name_{language}'
        desc_col = f'description_{language}'
        
        # Get name with fallback logic
        if name_col in service.index and service[name_col] and pd.notna(service[name_col]):
            name = service[name_col]
        elif 'name_en' in service.index and service['name_en'] and pd.notna(service['name_en']):
            name = service['name_en']
        elif 'name' in service.index and service['name'] and pd.notna(service['name']):
            name = service['name']
        else:
            name = f"Service {service['id']}"
        
        # Get description with fallback logic
        if desc_col in service.index and service[desc_col] and pd.notna(service[desc_col]):
            description = service[desc_col]
        elif 'description_en' in service.index and service['description_en'] and pd.notna(service['description_en']):
            description = service['description_en']
        elif 'description' in service.index and service['description'] and pd.notna(service['description']):
            description = service['description']
        else:
            description = "Service description"
        
        # Get duration with fallback
        duration = service.get('duration_hours', service.get('duration_minutes', 120) // 60 if 'duration_minutes' in service else 2)
        
        service_list.append({
            'id': service['id'],
            'name': name,
            'description': description,
            'price': service['base_price'],
            'duration': duration
        })
    
    return service_list

def show_language_selector():
    """Show language selector at the top"""
    current_lang = init_language_selector()
    return current_lang

def show_registration_form():
    """Show customer registration form with multilingual support"""
    current_lang = get_current_language()
    
    st.markdown(f"### 📝 {t('create_account', current_lang)}")
    
    with st.form("customer_registration", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input(
                f"👤 {t('first_name', current_lang)}*",
                placeholder=t('first_name', current_lang)
            )
            email = st.text_input(
                f"📧 {t('email', current_lang)}*",
                placeholder="your@email.com"
            )
            password = st.text_input(
                f"🔒 {t('password', current_lang)}*",
                type="password",
                placeholder=t('password', current_lang)
            )
        
        with col2:
            last_name = st.text_input(
                f"👤 {t('last_name', current_lang)}*",
                placeholder=t('last_name', current_lang)
            )
            phone = st.text_input(
                f"📱 {t('phone', current_lang)}",
                placeholder="+49 123 456 7890"
            )
            confirm_password = st.text_input(
                f"🔒 {t('confirm_password', current_lang)}*",
                type="password",
                placeholder=t('confirm_password', current_lang)
            )
        
        address = st.text_area(
            f"🏠 {t('address', current_lang)}",
            placeholder=t('address', current_lang)
        )
        
        terms_accepted = st.checkbox(t('accept_terms', current_lang) if 'accept_terms' in st.session_state.get('translations', {}) else "I accept the terms and conditions*")
        
        if st.form_submit_button(f"🎉 {t('register', current_lang)}", use_container_width=True):
            # Validation
            if not all([first_name, last_name, email, password, confirm_password, terms_accepted]):
                st.error(t('required_fields_missing', current_lang))
                return False
            
            if not validate_email(email):
                st.error(t('invalid_email', current_lang))
                return False
            
            if len(password) < 6:
                st.error(t('password_too_short', current_lang))
                return False
            
            if password != confirm_password:
                st.error(t('password_mismatch', current_lang))
                return False
            
            # Register customer
            if register_customer(email, password, first_name, last_name, phone, address):
                st.success(t('registration_success', current_lang))
                st.balloons()
                st.session_state.registration_success = True
                st.session_state.new_customer_name = first_name
                st.rerun()
            else:
                st.error(t('registration_failed', current_lang))
    
    return False

def show_login_form():
    """Show customer login form with multilingual support"""
    current_lang = get_current_language()
    
    # Check if we should show password reset form
    if 'show_password_reset' in st.session_state and st.session_state.show_password_reset:
        show_password_reset_form()
        return
    
    st.markdown(f"### 🔐 {t('login', current_lang)}")
    
    with st.form("customer_login"):
        email = st.text_input(
            f"📧 {t('email', current_lang)}",
            placeholder="your@email.com"
        )
        password = st.text_input(
            f"🔒 {t('password', current_lang)}",
            type="password"
        )
        
        col1, col2 = st.columns([2, 1])
        with col1:
            if st.form_submit_button(t('login', current_lang), use_container_width=True):
                user = authenticate_customer(email, password)
                if user:
                    st.session_state.customer_logged_in = True
                    st.session_state.customer_data = user
                    st.success(t('login_success', current_lang))
                    st.rerun()
                else:
                    st.error(t('login_failed', current_lang))
    
    # Forgot password link
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(f"🔑 {t('forgot_password', current_lang)}", use_container_width=True):
            st.session_state.show_password_reset = True
            st.session_state.reset_step = 1
            st.rerun()

def show_services_booking():
    """Show services and booking interface with multilingual support"""
    current_lang = get_current_language()
    
    st.title(f"🧹 {t('book_cleaning', current_lang)}")
    
    # Get available services
    services = get_available_services(current_lang)
    
    if not services:
        st.error(t('no_services_available', current_lang) if 'no_services_available' in st.session_state.get('translations', {}) else "No services available")
        return
    
    # Service selection
    st.subheader(t('service_type', current_lang))
    
    selected_service = None
    for service in services:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{service['name']}**")
                st.markdown(service['description'])
            
            with col2:
                st.markdown(f"<span class='price-tag'>{format_currency(service['price'], current_lang)}</span>", unsafe_allow_html=True)
                st.markdown(f"⏱️ {service['duration']}h")
            
            with col3:
                if st.button(t('select', current_lang) if 'select' in st.session_state.get('translations', {}) else "Select", key=f"select_{service['id']}"):
                    selected_service = service
                    st.session_state.selected_service = service
    
    # Booking form
    if 'selected_service' in st.session_state:
        service = st.session_state.selected_service
        
        st.markdown("---")
        st.subheader(f"📅 {t('booking_details', current_lang) if 'booking_details' in st.session_state.get('translations', {}) else 'Booking Details'}")
        
        with st.form("booking_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                service_date = st.date_input(
                    t('choose_date', current_lang),
                    min_value=date.today(),
                    max_value=date.today() + timedelta(days=30)
                )
            
            with col2:
                time_slots = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
                service_time = st.selectbox(t('choose_time', current_lang), time_slots)
            
            booking_address = st.text_area(
                f"🏠 {t('address', current_lang)}*",
                value=st.session_state.customer_data.get('address', ''),
                placeholder=t('address', current_lang)
            )
            
            special_instructions = st.text_area(
                t('special_instructions', current_lang),
                placeholder=t('special_instructions_placeholder', current_lang) if 'special_instructions_placeholder' in st.session_state.get('translations', {}) else "Any special requirements or instructions..."
            )
            
            # Booking summary
            st.markdown("---")
            st.subheader(t('booking_summary', current_lang))
            st.write(f"**{t('service', current_lang) if 'service' in st.session_state.get('translations', {}) else 'Service'}:** {service['name']}")
            st.write(f"**{t('date', current_lang) if 'date' in st.session_state.get('translations', {}) else 'Date'}:** {format_date(service_date, current_lang)}")
            st.write(f"**{t('time', current_lang) if 'time' in st.session_state.get('translations', {}) else 'Time'}:** {service_time}")
            st.write(f"**{t('duration', current_lang) if 'duration' in st.session_state.get('translations', {}) else 'Duration'}:** {service['duration']} {t('hours', current_lang) if 'hours' in st.session_state.get('translations', {}) else 'hours'}")
            st.write(f"**{t('total', current_lang)}:** {format_currency(service['price'], current_lang)}")
            
            if st.form_submit_button(f"✨ {t('book_now', current_lang) if 'book_now' in st.session_state.get('translations', {}) else 'Book Now'}", use_container_width=True):
                if not booking_address:
                    st.error(t('address_required', current_lang) if 'address_required' in st.session_state.get('translations', {}) else "Address is required")
                    return
                
                # Save booking
                try:
                    conn = init_database()
                    cursor = conn.cursor()
                    
                    # Calculate end time based on service duration
                    start_dt = datetime.strptime(service_time, '%H:%M')
                    duration_hours = service.get('duration', 2)  # Default 2 hours
                    end_dt = start_dt + timedelta(hours=duration_hours)
                    end_time = end_dt.strftime('%H:%M')
                    
                    cursor.execute('''
                        INSERT INTO customer_bookings 
                        (customer_user_id, service_type_id, date, start_time, end_time, address, special_instructions, total_price, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        st.session_state.customer_data['id'],
                        service['id'],  # Use service ID instead of name
                        service_date.isoformat(),
                        service_time,
                        end_time,
                        booking_address,
                        special_instructions,
                        service['price'],
                        'pending'  # Set initial status
                    ))
                    
                    conn.commit()
                    conn.close()
                    
                    st.success(t('booking_success', current_lang))
                    st.balloons()
                    
                    # Clear selected service
                    if 'selected_service' in st.session_state:
                        del st.session_state.selected_service
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(t('booking_failed', current_lang))

def show_customer_dashboard():
    """Show customer dashboard with multilingual support"""
    current_lang = get_current_language()
    customer = st.session_state.customer_data
    
    st.title(f"👋 {t('welcome', current_lang)}, {customer['first_name']}!")
    
    # Navigation tabs
    tab1, tab2, tab3 = st.tabs([
        t('book_cleaning', current_lang),
        t('my_bookings', current_lang),
        t('account_settings', current_lang)
    ])
    
    with tab1:
        show_services_booking()
    
    with tab2:
        st.subheader(t('my_bookings', current_lang))
        
        # Get customer bookings with service details
        conn = init_database()
        bookings = pd.read_sql_query('''
            SELECT cb.*, st.name_en, st.name_de, st.name as service_name
            FROM customer_bookings cb
            LEFT JOIN service_types st ON cb.service_type_id = st.id
            WHERE cb.customer_user_id = ? 
            ORDER BY cb.created_at DESC
        ''', conn, params=(customer['id'],))
        conn.close()
        
        if not bookings.empty:
            for _, booking in bookings.iterrows():
                # Get service name in current language
                if current_lang == 'de' and booking.get('name_de'):
                    service_name = booking['name_de']
                elif booking.get('name_en'):
                    service_name = booking['name_en']
                else:
                    service_name = booking.get('service_name', f"Service {booking['service_type_id']}")
                
                with st.expander(f"{service_name} - {format_date(datetime.strptime(booking['date'], '%Y-%m-%d').date(), current_lang)}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**{t('date', current_lang)}:** {format_date(datetime.strptime(booking['date'], '%Y-%m-%d').date(), current_lang)}")
                        st.write(f"**{t('time', current_lang)}:** {booking['start_time']}")
                        st.write(f"**{t('address', current_lang)}:** {booking['address']}")
                    
                    with col2:
                        status_color = {"pending": "🟡", "confirmed": "🟢", "completed": "🔵", "cancelled": "🔴"}
                        status = booking.get('status', 'pending')
                        st.write(f"**Status:** {status_color.get(status, '⚪')} {t(status, current_lang)}")
                        st.write(f"**{t('total', current_lang)}:** {format_currency(booking['total_price'], current_lang)}")
                        if booking.get('created_at'):
                            st.write(f"**{t('booked_on', current_lang)}:** {format_date(datetime.strptime(booking['created_at'], '%Y-%m-%d %H:%M:%S').date(), current_lang)}")
                    
                    if booking.get('special_instructions'):
                        st.write(f"**{t('special_instructions', current_lang)}:** {booking['special_instructions']}")
        else:
            st.info(t('no_bookings_yet', current_lang) if 'no_bookings_yet' in st.session_state.get('translations', {}) else "No bookings yet. Book your first cleaning service!")
    
    with tab3:
        st.subheader(t('account_settings', current_lang))
        
        with st.form("update_profile"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_first_name = st.text_input(t('first_name', current_lang), value=customer['first_name'])
                new_email = st.text_input(t('email', current_lang), value=customer['email'])
            
            with col2:
                new_last_name = st.text_input(t('last_name', current_lang), value=customer['last_name'])
                new_phone = st.text_input(t('phone', current_lang), value=customer.get('phone', ''))
            
            new_address = st.text_area(t('address', current_lang), value=customer.get('address', ''))
            
            if st.form_submit_button(t('save', current_lang)):
                # Update customer information
                try:
                    conn = init_database()
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        UPDATE customer_users 
                        SET first_name = ?, last_name = ?, email = ?, phone = ?, address = ?
                        WHERE id = ?
                    ''', (new_first_name, new_last_name, new_email, new_phone, new_address, customer['id']))
                    
                    # Also update in customers table
                    full_name = f"{new_first_name} {new_last_name}".strip()
                    cursor.execute('''
                        UPDATE customers 
                        SET name = ?, email = ?, phone = ?, address = ?
                        WHERE email = ?
                    ''', (full_name, new_email, new_phone, new_address, customer['email']))
                    
                    conn.commit()
                    conn.close()
                    
                    # Update session data
                    st.session_state.customer_data.update({
                        'first_name': new_first_name,
                        'last_name': new_last_name,
                        'email': new_email,
                        'phone': new_phone,
                        'address': new_address
                    })
                    
                    st.success(t('profile_updated', current_lang) if 'profile_updated' in st.session_state.get('translations', {}) else "Profile updated successfully!")
                    st.rerun()
                    
                except Exception:
                    st.error(t('update_failed', current_lang) if 'update_failed' in st.session_state.get('translations', {}) else "Update failed. Please try again.")

def generate_reset_code() -> str:
    """Generate a 6-digit reset code"""
    return ''.join(random.choices(string.digits, k=6))

def send_reset_code(email: str) -> bool:
    """Generate and store reset code for email (simulated email sending)"""
    try:
        conn = init_database()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT id FROM customer_users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return False
        
        # Generate reset code
        reset_code = generate_reset_code()
        
        # Set expiration time (15 minutes from now)
        expires_at = (datetime.now() + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Clean up old codes for this email
        cursor.execute('DELETE FROM password_reset_codes WHERE email = ? OR expires_at < datetime("now")', (email,))
        
        # Insert new reset code
        cursor.execute('''
            INSERT INTO password_reset_codes (email, reset_code, expires_at)
            VALUES (?, ?, ?)
        ''', (email, reset_code, expires_at))
        
        conn.commit()
        conn.close()
        
        # In a real application, you would send the code via email
        # For demo purposes, we'll store it in session state
        st.session_state.demo_reset_code = reset_code
        st.session_state.demo_reset_email = email
        
        return True
        
    except Exception as e:
        return False

def verify_reset_code(email: str, reset_code: str) -> bool:
    """Verify if the reset code is valid and not expired"""
    try:
        conn = init_database()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM password_reset_codes 
            WHERE email = ? AND reset_code = ? AND expires_at > datetime("now") AND used = FALSE
        ''', (email, reset_code))
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
        
    except Exception:
        return False

def reset_customer_password(email: str, reset_code: str, new_password: str) -> bool:
    """Reset customer password using valid reset code"""
    try:
        conn = init_database()
        cursor = conn.cursor()
        
        # Verify reset code is valid
        cursor.execute('''
            SELECT id FROM password_reset_codes 
            WHERE email = ? AND reset_code = ? AND expires_at > datetime("now") AND used = FALSE
        ''', (email, reset_code))
        
        reset_record = cursor.fetchone()
        
        if not reset_record:
            conn.close()
            return False
        
        # Hash new password
        password_hash = hash_password(new_password)
        
        # Update customer password
        cursor.execute('''
            UPDATE customer_users SET password_hash = ? WHERE email = ?
        ''', (password_hash, email))
        
        # Mark reset code as used
        cursor.execute('''
            UPDATE password_reset_codes SET used = TRUE WHERE id = ?
        ''', (reset_record[0],))
        
        conn.commit()
        conn.close()
        
        # Clear demo session state
        if 'demo_reset_code' in st.session_state:
            del st.session_state.demo_reset_code
        if 'demo_reset_email' in st.session_state:
            del st.session_state.demo_reset_email
        
        return True
        
    except Exception:
        return False

def show_password_reset_form():
    """Show password reset form"""
    current_lang = get_current_language()
    
    st.markdown(f"### 🔐 {t('reset_password_title', current_lang)}")
    
    # Step 1: Request reset code
    if 'reset_step' not in st.session_state:
        st.session_state.reset_step = 1
    
    if st.session_state.reset_step == 1:
        st.info(t('reset_instructions', current_lang))
        
        with st.form("request_reset_code"):
            email = st.text_input(
                f"📧 {t('email', current_lang)}",
                placeholder="your@email.com"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button(t('send_reset_code', current_lang), use_container_width=True):
                    if email and '@' in email:
                        if send_reset_code(email):
                            st.session_state.reset_email = email
                            st.session_state.reset_step = 2
                            st.success(t('reset_code_sent', current_lang))
                            st.rerun()
                        else:
                            st.error(t('invalid_email', current_lang))
                    else:
                        st.error(t('invalid_email', current_lang))
            
            with col2:
                if st.form_submit_button(t('back_to_login', current_lang), use_container_width=True):
                    st.session_state.show_password_reset = False
                    st.session_state.reset_step = 1
                    if 'reset_email' in st.session_state:
                        del st.session_state.reset_email
                    st.rerun()
    
    # Step 2: Enter reset code and new password
    elif st.session_state.reset_step == 2:
        st.success(t('reset_code_sent', current_lang))
        st.info(t('reset_code_instructions', current_lang))
        
        # Show demo code for testing
        if 'demo_reset_code' in st.session_state:
            st.info(f"🔧 **Demo Code**: {st.session_state.demo_reset_code}")
        
        with st.form("reset_password"):
            reset_code = st.text_input(
                f"🔐 {t('reset_code', current_lang)}",
                placeholder="000000",
                help=t('enter_reset_code', current_lang)
            )
            
            new_password = st.text_input(
                f"🔒 {t('new_password', current_lang)}",
                type="password"
            )
            
            confirm_password = st.text_input(
                f"🔒 {t('confirm_new_password', current_lang)}",
                type="password"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button(t('reset_password', current_lang), use_container_width=True):
                    if not all([reset_code, new_password, confirm_password]):
                        st.error(t('required_fields_missing', current_lang))
                    elif len(new_password) < 6:
                        st.error(t('password_too_short', current_lang))
                    elif new_password != confirm_password:
                        st.error(t('password_mismatch', current_lang))
                    elif not verify_reset_code(st.session_state.reset_email, reset_code):
                        st.error(t('invalid_reset_code', current_lang))
                    else:
                        if reset_customer_password(st.session_state.reset_email, reset_code, new_password):
                            st.success(t('password_reset_success', current_lang))
                            st.session_state.show_password_reset = False
                            st.session_state.reset_step = 1
                            if 'reset_email' in st.session_state:
                                del st.session_state.reset_email
                            st.balloons()
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error(t('password_reset_failed', current_lang))
            
            with col2:
                if st.form_submit_button(t('back_to_login', current_lang), use_container_width=True):
                    st.session_state.show_password_reset = False
                    st.session_state.reset_step = 1
                    if 'reset_email' in st.session_state:
                        del st.session_state.reset_email
                    st.rerun()

def main():
    """Main application with multilingual support"""
    # Initialize session state
    if 'customer_logged_in' not in st.session_state:
        st.session_state.customer_logged_in = False
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    
    # Language selector
    current_lang = show_language_selector()
    
    # Main header
    st.markdown(f'<h1 class="main-header">🧹 {t("app_name", current_lang)}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;">{t("tagline", current_lang)}</p>', unsafe_allow_html=True)
    
    if not st.session_state.customer_logged_in:
        # Show registration success message
        if st.session_state.get('registration_success', False):
            st.success(f"🎉 {t('registration_success', current_lang)} {t('welcome', current_lang)}, {st.session_state.get('new_customer_name', '')}!")
            st.info(f"ℹ️ {t('login_to_continue', current_lang) if 'login_to_continue' in st.session_state.get('translations', {}) else 'Please login below to continue.'}")
            
            if st.button(t('continue_to_login', current_lang) if 'continue_to_login' in st.session_state.get('translations', {}) else "Continue to Login"):
                st.session_state.registration_success = False
                st.rerun()
        
        # Login/Registration tabs
        tab1, tab2 = st.tabs([t('login', current_lang), t('register', current_lang)])
        
        with tab1:
            show_login_form()
            st.markdown(f"---\n<p style='text-align: center;'>{t('dont_have_account', current_lang)} <strong>{t('sign_up_here', current_lang)}</strong> ➡️</p>", unsafe_allow_html=True)
        
        with tab2:
            show_registration_form()
            st.markdown(f"---\n<p style='text-align: center;'>{t('already_have_account', current_lang)} <strong>{t('login_here', current_lang)}</strong> ⬅️</p>", unsafe_allow_html=True)
    
    else:
        # Show customer dashboard
        with st.sidebar:
            customer = st.session_state.customer_data
            st.markdown(f"### 👋 {t('welcome', current_lang)}")
            st.markdown(f"**{customer['first_name']} {customer['last_name']}**")
            st.markdown(f"📧 {customer['email']}")
            
            if st.button(f"🚪 {t('logout', current_lang)}", use_container_width=True):
                st.session_state.customer_logged_in = False
                st.session_state.customer_data = None
                st.rerun()
        
        show_customer_dashboard()

if __name__ == "__main__":
    main()
