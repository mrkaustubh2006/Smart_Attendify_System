# 🎓 Smart Attendance System

A modern, production-ready QR-based attendance management system for colleges and schools built with Flask, MySQL, and Bootstrap 5.

## ✨ Features

### Admin Panel
- 📊 Dashboard with real-time analytics
- 👥 Complete student management (CRUD)
- 🏫 Teacher management
- 📚 Subject and class management
- 📋 View all attendance records
- 📊 Export reports (Excel & PDF)
- 🔍 Comprehensive audit logs
- 🔐 Role-based access control

### Teacher Portal
- ✅ Mark attendance via QR scanning
- 📷 Live webcam QR scanner
- 📊 View attendance history
- 📈 Generate attendance reports
- 📥 Export reports to Excel/PDF
- 📝 Per-subject attendance statistics

### Student Dashboard
- 👤 View personal profile
- 🎫 Generate and download QR code
- 📊 Track attendance percentage
- 📈 Subject-wise attendance breakdown
- 📋 View attendance history
- 🔐 Secure login

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask 3.0.3
- **Database**: MySQL
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login + Bcrypt
- **QR Generation**: qrcode library
- **Rate Limiting**: Flask-Limiter

### Frontend
- **HTML5** + **CSS3**
- **Bootstrap 5.3**
- **JavaScript (Vanilla)**
- **QR Scanner**: html5-qrcode library
- **Charts**: Chart.js

### Database
- Students
- Teachers
- Subjects
- Classes
- Attendance Records
- Audit Logs
- User Accounts

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL Server
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/smart-attendance.git
cd Smart-Attendance
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Create MySQL database**
```bash
mysql -u root -p
CREATE DATABASE smart_attendance CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

6. **Initialize database** (runs automatically on first run)
```bash
python app.py
```

7. **Run the application**
```bash
python app.py
```

Access the application at `http://localhost:5000`

## 📝 Default Admin Credentials

| Email | Password |
|-------|----------|
| admin@school.edu | Admin@1234 |

⚠️ **Change these immediately in production!**

## 📁 Project Structure

```
Smart-Attendance/
├── app.py                 # Main application entry point
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
│
├── models/              # SQLAlchemy ORM models
│   ├── user.py
│   ├── student.py
│   ├── teacher.py
│   ├── subject.py
│   ├── attendance.py
│   └── audit_log.py
│
├── routes/              # Flask blueprints
│   ├── auth.py         # Login/Register
│   ├── admin.py        # Admin panel
│   ├── teacher.py      # Teacher portal
│   └── student.py      # Student dashboard
│
├── services/            # Business logic
│   ├── auth_service.py
│   ├── qr_service.py
│   ├── attendance_service.py
│   └── export_service.py
│
├── middleware/          # Access control
│   └── access.py
│
├── templates/           # HTML templates
│   ├── shared/
│   ├── auth/
│   ├── admin/
│   ├── teacher/
│   ├── student/
│   └── errors/
│
├── static/              # CSS, JS, Images
│   ├── css/style.css
│   ├── js/main.js
│   └── images/
│
├── qr_codes/           # Generated QR codes
├── exports/            # PDF/Excel exports
├── database/           # Database scripts
└── docs/               # Documentation
```

## 🔐 Security Features

- **Password Hashing**: Bcrypt with salt
- **CSRF Protection**: Flask-WTF
- **SQL Injection Prevention**: SQLAlchemy ORM
- **Rate Limiting**: Brute-force protection
- **Session Management**: Secure cookies
- **QR Security**: Opaque tokens (no PII in QR)
- **Audit Logging**: Track all admin actions
- **Environment Variables**: Sensitive data isolation

## 📊 API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - Student registration
- `GET /logout` - User logout

### Admin Routes
- `GET /admin/dashboard` - Admin dashboard
- `GET/POST /admin/students` - Student management
- `GET/POST /admin/teachers` - Teacher management
- `GET/POST /admin/subjects` - Subject management
- `GET /admin/attendance` - View all attendance
- `GET /admin/export/excel` - Export to Excel
- `GET /admin/export/pdf` - Export to PDF
- `GET /admin/audit-logs` - View audit logs

### Teacher Routes
- `GET /teacher/dashboard` - Teacher dashboard
- `GET /teacher/attendance` - Attendance marking
- `POST /teacher/api/mark-attendance` - Mark attendance (AJAX)
- `GET /teacher/history` - Attendance history
- `GET /teacher/reports` - Generate reports
- `GET /teacher/export/excel` - Export reports

### Student Routes
- `GET /student/dashboard` - Student dashboard
- `GET /student/profile` - View profile
- `GET /student/qr` - View QR code
- `GET /student/attendance` - View attendance
- `GET /student/qr/download` - Download QR

## 🛠️ Configuration

### Environment Variables (.env)

```env
# Flask
SECRET_KEY=your-secret-key
FLASK_ENV=development
FLASK_DEBUG=True

# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=smart_attendance

# JWT (optional)
JWT_SECRET_KEY=your-jwt-secret

# Admin seed
ADMIN_EMAIL=admin@school.edu
ADMIN_PASSWORD=Admin@1234
```

## 📚 Database Schema

### Users Table
```sql
- id (Primary Key)
- email (Unique)
- password_hash
- role (admin, teacher, student)
- is_active (Boolean)
- created_at
```

### Students Table
```sql
- id
- user_id (Foreign Key)
- student_id (Unique)
- name
- email
- class_name
- roll_no
- qr_token (Secure token for QR)
- qr_image_path
```

### Attendance Table
```sql
- id
- student_id
- subject_id
- teacher_id
- date
- time
- status (present, absent, late)
- method (qr_scan, manual)
- Unique Constraint: (student_id, subject_id, date)
```

## 🚢 Deployment

### Docker Setup

```bash
# Build image
docker build -t smart-attendance .

# Run container
docker run -p 5000:8000 --env-file .env smart-attendance
```

### Render Deployment

1. Push to GitHub
2. Connect repository to Render
3. Set environment variables in Render dashboard
4. Deploy

### Manual Server Deployment

```bash
# Install Python and MySQL
# Clone repository
# Setup virtual environment
# Install dependencies
# Configure .env
# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
```

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=.
```

## 📖 Documentation

- [API Documentation](docs/API.md)
- [Database Schema](docs/DATABASE.md)
- [Security Guide](docs/SECURITY.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 🐛 Troubleshooting

### QR Code Not Generating
- Check write permissions in `qr_codes/` directory
- Verify Pillow library is installed

### Database Connection Error
- Verify MySQL is running
- Check credentials in `.env`
- Ensure database exists

### Login Issues
- Clear browser cookies/cache
- Verify user email in database
- Check password hash

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 👨‍💼 Support

For issues, questions, or suggestions:
- Create an Issue on GitHub
- Contact: support@smartattendance.dev

## 🎯 Roadmap

- [ ] Mobile app (iOS/Android)
- [ ] Biometric attendance
- [ ] SMS/Email notifications
- [ ] Calendar integration
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Dark mode UI
- [ ] WhatsApp integration

---

**Made with ❤️ for educational institutions**
