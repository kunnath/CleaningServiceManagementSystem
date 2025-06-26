# GRK Dienstleistungen - Complete System Setup

This document explains how to run the complete GRK Dienstleistungen cleaning service system with React frontend, Node.js backend, and Streamlit admin portal.

## 🎯 System Overview

The system consists of three main components:

1. **React Frontend** (Port 3000) - Customer booking interface
2. **Node.js Backend** (Port 5000) - API server with SQLite database
3. **Streamlit Admin Portal** (Port 8502) - Admin management interface

## 🚀 Quick Start

### Option A: Start All Services at Once

```bash
cd /Users/kunnath/Projects/Bookandclean/CleaningServiceManagementSystem
./start_all_services.sh
```

### Option B: Start Services Individually

1. **Start Backend Server**
```bash
cd cleaning-service-app/backend
npm start
```

2. **Start Frontend Server**
```bash
cd cleaning-service-app/frontend
npm start
```

3. **Start Admin Portal**
```bash
source .venv/bin/activate
streamlit run admin_portal_multilingual.py --server.port 8502
```

## 🌐 Access URLs

- **Customer Portal**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Admin Portal**: http://localhost:8502

## 🔧 Admin Portal Integration

The admin portal has been configured to use the same SQLite database as the React backend:

- **Database Path**: `cleaning-service-app/backend/data/cleaning_service.db`
- **Integration**: Bookings made through the React frontend automatically appear in the admin portal
- **Real-time Updates**: Admin can manage all customer bookings in real-time

### Admin Portal Features

- **Dashboard**: Overview of bookings, customers, and revenue
- **Booking Management**: View, edit, and update booking statuses
- **Customer Management**: Manage customer profiles and history
- **Employee Management**: Assign cleaners to bookings
- **Analytics**: Revenue reports and performance metrics
- **Multilingual**: Support for English and German

## 👥 Default Admin Credentials

- **Username**: `admin`
- **Password**: `admin123`

## 🔄 Data Flow

1. Customer books service through React frontend (localhost:3000)
2. Booking data saved to SQLite database via Node.js backend (localhost:5000)
3. Admin views and manages bookings through Streamlit portal (localhost:8502)
4. All three components share the same database for real-time synchronization

## 🧪 Testing Integration

Run the integration test to verify everything is connected:

```bash
./test_integration.py
```

This will check:
- Database connectivity
- Table structure
- Data synchronization between components

## 🛑 Stopping Services

### Stop All Services
```bash
./stop_all_services.sh
```

### Stop Individual Services
- Press `Ctrl+C` in each terminal
- Or kill by port:
  ```bash
  lsof -ti:3000 | xargs kill -9  # Frontend
  lsof -ti:5000 | xargs kill -9  # Backend
  lsof -ti:8502 | xargs kill -9  # Admin Portal
  ```

## 📁 Project Structure

```
CleaningServiceManagementSystem/
├── cleaning-service-app/
│   ├── frontend/                 # React customer interface
│   ├── backend/                  # Node.js API server
│   └── backend/data/            # SQLite database
├── admin_portal_multilingual.py # Streamlit admin interface
├── translations.py              # Multi-language support
├── start_all_services.sh       # Startup script
├── stop_all_services.sh        # Shutdown script
└── test_integration.py         # Integration test
```

## 🔍 Troubleshooting

### Common Issues

1. **Module not found errors**
   ```bash
   source .venv/bin/activate
   pip install bcrypt streamlit plotly pandas
   ```

2. **Port already in use**
   ```bash
   ./stop_all_services.sh
   # Wait 5 seconds, then restart
   ./start_all_services.sh
   ```

3. **Database not found**
   - Ensure backend is started first
   - Check that `cleaning-service-app/backend/data/cleaning_service.db` exists

4. **Admin portal shows no bookings**
   - Create test bookings through React frontend first
   - Run `./test_integration.py` to verify database connectivity

## 📝 Notes

- The system uses SQLite for development (suitable for local testing)
- For production, consider upgrading to PostgreSQL or MySQL
- All services must be running for full functionality
- Bookings made in the React frontend immediately appear in the admin portal
- The admin portal provides complete management capabilities for all customer bookings

## 🎯 Company Information

- **Company Name**: GRK Dienstleistungen
- **Contact**: +49 1577 2526898
- **Address**: Glockenblumenweg 131A, 12357 Berlin, Deutschland
- **Services**: Professional cleaning services with German/English support
