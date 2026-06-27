# 🚀 Smart Attendance System - Setup Guide

Complete step-by-step installation and configuration guide.

## Prerequisites

### System Requirements
- **OS**: Windows 10+, macOS 10.14+, or Linux
- **Python**: 3.8 or higher
- **MySQL**: 5.7 or higher
- **RAM**: 2GB minimum
- **Disk Space**: 500MB

### Required Software
- Git
- MySQL Server
- Python pip

## Installation Steps

### 1. Download and Setup Python

**Windows:**
```bash
# Download from python.org
# Run installer with "Add Python to PATH" checked
python --version
```

**macOS:**
```bash
brew install python3
python3 --version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
python3 --version
```

### 2. Install and Configure MySQL

**Windows:**
- Download from mysql.com
- Run installer
- Remember the root password
- Start MySQL Server

**macOS:**
```bash
brew install mysql
brew services start mysql
mysql_secure_installation
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install mysql-server
sudo mysql_secure_installation
sudo systemctl start mysql
```

### 3. Clone Repository

```bash
cd Documents  # or your preferred directory
git clone https://github.com/yourusername/smart-attendance.git
cd Smart-Attendance
```

### 4. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal.

### 5. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Create MySQL Database

```bash
# Connect to MySQL
mysql -u root -p
# Enter your MySQL root password

# In MySQL console, execute:
CREATE DATABASE smart_attendance 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

# Verify creation
SHOW DATABASES;

# Exit MySQL
EXIT;
```

### 7. Configure Environment Variables

**Copy the example file:**
```bash
cp .env.example .env
```

**Edit .env file:**
```env
# Flask Configuration
SECRET_KEY=your-very-secure-random-string-here
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=smart_attendance

# Admin Account
ADMIN_EMAIL=admin@school.edu
ADMIN_PASSWORD=Admin@1234

# Paths
QR_CODES_DIR=qr_codes
EXPORTS_DIR=exports
```

**Generate secure SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and paste as `SECRET_KEY` in .env

### 8. Run the Application

**First run (initializes database):**
```bash
python app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

### 9. Access the Application

Open your web browser and go to:
```
http://localhost:5000
```

## ✅ Verification Checklist

- [ ] Python installed and version 3.8+
- [ ] MySQL running and accessible
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip list | grep Flask`)
- [ ] `.env` file configured with correct credentials
- [ ] `smart_attendance` database created
- [ ] Application starts without errors
- [ ] Can access login page at localhost:5000
- [ ] Admin login works with default credentials

## 🔑 Default Login Credentials

After setup, you can login with:

**Admin Account:**
- Email: `admin@school.edu`
- Password: `Admin@1234`

⚠️ **IMPORTANT**: Change these credentials immediately in production!

## 📁 Project Folder Structure

```
Smart-Attendance/
├── app.py                 # Main application
├── config.py             # Configuration
├── requirements.txt      # Dependencies
├── .env                  # Environment (create this)
├── .env.example         # Template
├── models/              # Database models
├── routes/              # URL routes
├── services/            # Business logic
├── middleware/          # Access control
├── templates/           # HTML files
├── static/              # CSS, JS
├── qr_codes/           # Generated QRs
├── exports/            # PDF/Excel files
├── docs/               # Documentation
└── database/           # SQL scripts
```

## 🔧 Common Issues & Solutions

### Issue: "No module named flask"

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install requirements again
pip install -r requirements.txt
```

### Issue: "Access denied for user 'root'@'localhost'"

**Solution:**
1. Check MySQL is running: `mysql --version`
2. Verify credentials in `.env`
3. Test MySQL connection:
   ```bash
   mysql -u root -p
   # Enter your password
   EXIT;
   ```

### Issue: "No such file or directory: 'qr_codes'"

**Solution:**
```bash
# Create required directories
mkdir -p qr_codes exports
# Should be created automatically on first run
```

### Issue: Port 5000 already in use

**Solution:**
```bash
# Change port in app.py
# Find the last line and change:
app.run(debug=True, host="0.0.0.0", port=5001)
```

## 🚀 Running in Production

### Using Gunicorn (Recommended)

```bash
# Install Gunicorn
pip install gunicorn

# Run application
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### Using Docker

```bash
# Build image
docker build -t smart-attendance .

# Run container
docker run -p 5000:5000 \
  -e DB_HOST=host.docker.internal \
  -e DB_USER=root \
  -e DB_PASSWORD=your_password \
  smart-attendance
```

### Configure Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔒 Security Best Practices

1. **Change Default Credentials**
   ```bash
   # Login as admin and change password
   ```

2. **Use Strong SECRET_KEY**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Enable HTTPS in Production**
   - Use Let's Encrypt for free SSL
   - Configure with Nginx/Apache

4. **Database Backups**
   ```bash
   mysqldump -u root -p smart_attendance > backup.sql
   ```

5. **Regular Updates**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --upgrade
   ```

## 📊 Database Backup & Restore

### Backup

```bash
mysqldump -u root -p smart_attendance > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore

```bash
mysql -u root -p smart_attendance < backup.sql
```

## 🆘 Getting Help

If you encounter issues:

1. **Check logs**: Look at terminal output for error messages
2. **Verify database**: `mysql> SELECT * FROM users;`
3. **Test imports**: `python -c "import flask; print(flask.__version__)"`
4. **Check ports**: `netstat -tulpn | grep 5000` (Linux/Mac)
5. **Create issue** on GitHub with error message

## 📞 Support

- **Documentation**: See `/docs` folder
- **GitHub Issues**: Create an issue for bugs
- **Email**: support@smartattendance.dev

---

**Happy Installing! 🎓**
