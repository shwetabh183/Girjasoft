# **Girjasoft HRMS** 

**Girjasoft HRMS** is a comprehensive Human Resource Management System designed to streamline HR processes and enhance organizational efficiency.

---

## **Features**

- **Recruitment** - Manage job postings, candidates, and hiring pipeline
- **Onboarding** - Streamline new employee onboarding process
- **Employee Management** - Complete employee lifecycle management
- **Attendance Tracking** - Track attendance, late arrivals, early departures
- **Leave Management** - Handle leave requests, approvals, and balances
- **Asset Management** - Track company assets assigned to employees
- **Payroll** - Manage salaries, allowances, deductions, and payslips
- **Performance Management System (PMS)** - Goals, KPIs, and performance reviews
- **Offboarding** - Manage employee exits and handovers
- **Helpdesk** - Internal ticketing system for employee queries

---

## **Tech Stack**

- **Backend**: Django 4.x (Python 3.10+)
- **Frontend**: HTML, CSS, JavaScript, HTMX, Alpine.js
- **Database**: PostgreSQL (recommended) / SQLite
- **Charts**: Chart.js
- **Deployment**: Docker, Gunicorn, Azure App Service, Render

---

## **Quick Start**

### **Prerequisites**
- Python 3.10+
- PostgreSQL (recommended) or SQLite
- Git

### **Installation**

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/Girjasoft-hrms.git
   cd Girjasoft-hrms
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv girjasoftvenv
   source girjasoftvenv/bin/activate  # On Windows: .\girjasoftvenv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.dist .env
   # Edit .env with your database and settings
   ```

5. **Run migrations**
   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python3 manage.py createsuperuser
   ```

7. **Collect static files**
   ```bash
   python3 manage.py collectstatic --noinput
   ```

8. **Start the server**
   ```bash
   python3 manage.py runserver
   ```

9. **Access the application**
   Open http://localhost:8000 in your browser

---

## **Environment Variables**

Create a `.env` file based on `.env.dist`:

```env
# Development settings
DEBUG=True
SECRET_KEY=your-secret-key-here

# Allowed hosts
ALLOWED_HOSTS=localhost,127.0.0.1,*

# Database (PostgreSQL recommended)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=girjasoft_db
DB_USER=girjasoft
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# OR use DATABASE_URL format
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Database initialization password
DB_INIT_PASSWORD=your_init_password

# Timezone
TIME_ZONE=Asia/Kolkata
```

---

## **Database Setup**

### **PostgreSQL (Recommended)**

```sql
CREATE ROLE girjasoft LOGIN PASSWORD 'your_password';
CREATE DATABASE girjasoft_db OWNER girjasoft;
```

### **SQLite (Development)**
No additional setup required - SQLite database will be created automatically as `TestDB_Girjasoft.sqlite3`.

---

## **Docker Deployment**

```bash
docker-compose up -d
```

---

## **Azure Deployment**

The project includes GitHub Actions workflow for Azure App Service deployment.

### **Required Azure Environment Variables:**

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_ENGINE` | Database engine | `django.db.backends.postgresql` |
| `DB_HOST` | Azure PostgreSQL hostname | `server.postgres.database.azure.com` |
| `DB_NAME` | Database name | `girjasoft_db` |
| `DB_USER` | Database username | `girjasoft` |
| `DB_PASSWORD` | Database password | `your_secure_password` |
| `DB_PORT` | Database port | `5432` |
| `SECRET_KEY` | Django secret key | `your-secret-key` |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed domains | `yourapp.azurewebsites.net` |

### **Startup Command:**
```bash
python manage.py migrate && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 girjasoft.wsgi:application
```

---

## **Project Structure**

```
Girjasoft-hrms/
├── girjasoft/              # Main Django project settings
│   ├── settings.py         # Django settings
│   ├── urls.py             # URL configuration
│   ├── wsgi.py             # WSGI application
│   └── girjasoft_settings.py  # Custom settings
├── base/                   # Core functionality
├── employee/               # Employee management
├── recruitment/            # Recruitment module
├── attendance/             # Attendance tracking
├── leave/                  # Leave management
├── payroll/                # Payroll processing
├── asset/                  # Asset management
├── pms/                    # Performance management
├── onboarding/             # Onboarding module
├── offboarding/            # Offboarding module
├── helpdesk/               # Helpdesk ticketing
├── girjasoft_api/          # REST API
├── girjasoft_views/        # Generic class-based views
├── girjasoft_widgets/      # Custom form widgets
├── girjasoft_automations/  # Workflow automations
├── girjasoft_audit/        # Audit logging
├── static/                 # Static files (CSS, JS, images)
├── templates/              # HTML templates
├── load_data/              # Sample data fixtures
├── requirements.txt        # Python dependencies
├── entrypoint.sh           # Docker/deployment entrypoint
└── docker-compose.yaml     # Docker compose configuration
```

---

## **API Documentation**

The REST API is available at `/api/` endpoints. 

### **Authentication**
Most endpoints require authentication via session or token.

### **Available Endpoints**
- `/api/employee/` - Employee data
- `/api/attendance/` - Attendance records
- `/api/leave/` - Leave requests
- `/api/payroll/` - Payroll information

---

## **Load Sample Data**

To load sample data for testing:

```bash
python3 manage.py loaddata load_data/base_data.json
python3 manage.py loaddata load_data/employee_info_data.json
```

---

## **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## **License**

This project is licensed under the LGPL License - see the [LICENSE](LICENSE) file for details.

---

## **Support**

For support and questions, please open an issue in the repository.
