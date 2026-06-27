# Smart Attendance System - API Documentation

Complete API reference for the Smart Attendance System.

## Base URL
```
http://localhost:5000
http://yourdomain.com
```

## Authentication

All protected endpoints require the user to be logged in. Authentication is handled via Flask-Login with session cookies.

**Required Headers:**
```
Cookie: session=<session_id>
```

## Response Format

All responses are in JSON format with standard HTTP status codes.

**Success Response:**
```json
{
    "success": true,
    "message": "Operation successful",
    "data": {}
}
```

**Error Response:**
```json
{
    "success": false,
    "message": "Error description",
    "error": "error_code"
}
```

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Not authenticated |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Server Error - Internal error |

---

## Authentication Endpoints

### Login
```
POST /login
Content-Type: application/x-www-form-urlencoded
```

**Request:**
```
email=user@example.com&password=password123&remember=on
```

**Response (200):**
```json
{
    "success": true,
    "message": "Welcome back!",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "role": "student"
    }
}
```

**Response (401):**
```json
{
    "success": false,
    "message": "Invalid email or password"
}
```

---

### Register (Student)
```
POST /register
Content-Type: application/x-www-form-urlencoded
```

**Request:**
```
name=John Doe&email=john@example.com&password=secure123&student_id=STU001&
class_name=B.Tech 2nd Year&roll_no=42&department=Computer Science
```

**Response (201):**
```json
{
    "success": true,
    "message": "Registration successful! Please log in."
}
```

**Response (400):**
```json
{
    "success": false,
    "message": "Email already registered"
}
```

---

### Logout
```
GET /logout
```

**Response (200):**
```json
{
    "success": true,
    "message": "You have been logged out."
}
```

---

## Admin Endpoints

All admin endpoints require `role="admin"`.

### Get Students
```
GET /admin/students?q=search&page=1
```

**Response (200):**
```json
{
    "students": [
        {
            "id": 1,
            "student_id": "STU001",
            "name": "John Doe",
            "email": "john@example.com",
            "class_name": "B.Tech 2nd",
            "roll_no": "42",
            "department": "Computer Science"
        }
    ],
    "total": 100,
    "page": 1,
    "pages": 5
}
```

### Add Student
```
POST /admin/students/add
Content-Type: application/x-www-form-urlencoded
```

**Request:**
```
name=Jane&email=jane@example.com&student_id=STU002&class_name=B.Tech 2nd&
roll_no=43&department=Computer Science&password=secure123
```

**Response (201):**
```json
{
    "success": true,
    "message": "Student added successfully",
    "student": {
        "id": 2,
        "student_id": "STU002",
        "name": "Jane"
    }
}
```

### Edit Student
```
POST /admin/students/<id>/edit
```

**Request:**
```
name=Jane Doe&class_name=B.Tech 3rd&roll_no=44
```

**Response (200):**
```json
{
    "success": true,
    "message": "Student updated"
}
```

### Delete Student
```
POST /admin/students/<id>/delete
```

**Response (200):**
```json
{
    "success": true,
    "message": "Student deleted"
}
```

### Regenerate Student QR
```
POST /admin/students/<id>/regenerate_qr
```

**Response (200):**
```json
{
    "success": true,
    "message": "QR code regenerated"
}
```

### Get All Attendance
```
GET /admin/attendance?date=2024-01-15&subject_id=1&page=1
```

**Query Parameters:**
- `date` (optional): Filter by date (YYYY-MM-DD)
- `subject_id` (optional): Filter by subject
- `page` (optional): Page number

**Response (200):**
```json
{
    "attendance": [
        {
            "id": 1,
            "student": {
                "id": 1,
                "name": "John Doe",
                "student_id": "STU001"
            },
            "subject": {
                "id": 1,
                "subject_name": "Mathematics",
                "subject_code": "MATH101"
            },
            "date": "2024-01-15",
            "time": "10:30:00",
            "status": "present",
            "method": "qr_scan"
        }
    ],
    "total": 50
}
```

### Export Attendance to Excel
```
GET /admin/export/excel
```

**Response (200):**
- File download: `attendance_YYYYMMDD_HHMMSS.xlsx`

### Export Attendance to PDF
```
GET /admin/export/pdf
```

**Response (200):**
- File download: `attendance_YYYYMMDD_HHMMSS.pdf`

---

## Teacher Endpoints

All teacher endpoints require `role="teacher"` or `role="admin"`.

### Get Dashboard Stats
```
GET /teacher/dashboard
```

**Response (200):**
```json
{
    "teacher": {
        "id": 1,
        "teacher_id": "TEA001",
        "name": "Prof. Smith",
        "email": "smith@example.com"
    },
    "today_count": 45,
    "subjects": [
        {
            "id": 1,
            "subject_name": "Mathematics",
            "subject_code": "MATH101"
        }
    ]
}
```

### Mark Attendance (via QR)
```
POST /teacher/api/mark-attendance
Content-Type: application/json
```

**Request:**
```json
{
    "qr_token": "a1b2c3d4e5f6...",
    "subject_id": 1
}
```

**Response (200):**
```json
{
    "success": true,
    "message": "✓ John Doe marked present",
    "student_name": "John Doe",
    "student_id": "STU001",
    "time": "10:30:45"
}
```

**Response (400) - Duplicate:**
```json
{
    "success": false,
    "message": "Attendance for John Doe in Mathematics already recorded today"
}
```

**Response (400) - Invalid QR:**
```json
{
    "success": false,
    "message": "Invalid QR code — student not found"
}
```

### Get Attendance History
```
GET /teacher/history?subject_id=1&page=1
```

**Response (200):**
```json
{
    "records": [
        {
            "id": 1,
            "student": {
                "id": 1,
                "name": "John Doe"
            },
            "subject": {
                "id": 1,
                "subject_name": "Mathematics"
            },
            "date": "2024-01-15",
            "time": "10:30:00",
            "status": "present"
        }
    ],
    "total": 45,
    "page": 1
}
```

### Get Reports
```
GET /teacher/reports?subject_id=1
```

**Response (200):**
```json
{
    "subject": "Mathematics",
    "stats": [
        {
            "student_id": "STU001",
            "student_name": "John Doe",
            "total": 20,
            "present": 18,
            "percentage": 90.0
        }
    ]
}
```

### Export Teacher's Attendance (Excel)
```
GET /teacher/export/excel
```

**Response (200):**
- File download: `attendance_TEA001_YYYYMMDD_HHMMSS.xlsx`

### Export Teacher's Attendance (PDF)
```
GET /teacher/export/pdf
```

**Response (200):**
- File download: `attendance_TEA001_YYYYMMDD_HHMMSS.pdf`

---

## Student Endpoints

All student endpoints require `role="student"`.

### Get Dashboard
```
GET /student/dashboard
```

**Response (200):**
```json
{
    "student": {
        "id": 1,
        "student_id": "STU001",
        "name": "John Doe",
        "class_name": "B.Tech 2nd",
        "roll_no": "42"
    },
    "overall_percentage": 85.5,
    "subject_stats": [
        {
            "subject": {
                "id": 1,
                "subject_name": "Mathematics",
                "subject_code": "MATH101"
            },
            "total": 20,
            "present": 17,
            "percentage": 85.0
        }
    ]
}
```

### Get Profile
```
GET /student/profile
```

**Response (200):**
```json
{
    "student": {
        "id": 1,
        "student_id": "STU001",
        "name": "John Doe",
        "email": "john@example.com",
        "class_name": "B.Tech 2nd",
        "roll_no": "42",
        "department": "Computer Science",
        "qr_image_path": "qr_codes/qr_STU001.png"
    }
}
```

### Get QR Code
```
GET /student/qr
```

**Response (200):**
```json
{
    "student": {
        "id": 1,
        "student_id": "STU001",
        "name": "John Doe",
        "qr_image_path": "qr_codes/qr_STU001.png",
        "qr_token": "a1b2c3d4e5f6..."
    }
}
```

### Download QR Code
```
GET /student/qr/download
```

**Response (200):**
- File download: `QR_STU001.png`

### Get Attendance History
```
GET /student/attendance?subject_id=1&page=1
```

**Response (200):**
```json
{
    "records": [
        {
            "id": 1,
            "subject": {
                "subject_name": "Mathematics",
                "subject_code": "MATH101"
            },
            "date": "2024-01-15",
            "time": "10:30:00",
            "status": "present",
            "method": "qr_scan"
        }
    ],
    "total": 20,
    "page": 1
}
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| AUTH_REQUIRED | User not authenticated |
| PERMISSION_DENIED | Insufficient permissions |
| INVALID_CREDENTIALS | Wrong email/password |
| INVALID_QR | QR token not found |
| DUPLICATE_ATTENDANCE | Attendance already marked |
| SUBJECT_NOT_FOUND | Subject doesn't exist |
| STUDENT_NOT_FOUND | Student doesn't exist |
| TEACHER_NOT_FOUND | Teacher doesn't exist |
| DATABASE_ERROR | Database operation failed |
| RATE_LIMIT | Too many requests |
| VALIDATION_ERROR | Invalid input data |

---

## Rate Limiting

- **Default**: 50 requests per hour, 200 per day
- **Login Route**: 10 requests per hour
- **QR Marking**: 100 requests per hour

**Rate Limit Headers:**
```
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1674000000
```

---

## Example Workflows

### Student Self-Registration
1. `POST /register` - Create account
2. System generates unique QR code
3. Student can login and download QR

### Teacher Mark Attendance
1. `GET /teacher/attendance` - Select subject
2. `POST /teacher/api/mark-attendance` - Scan QR codes
3. `GET /teacher/reports` - View statistics

### Admin Export Report
1. `GET /admin/attendance` - Filter by date/subject
2. `GET /admin/export/excel` or `GET /admin/export/pdf`
3. Download generated file

---

## Testing with cURL

### Login
```bash
curl -X POST http://localhost:5000/login \
  -d "email=admin@school.edu&password=Admin@1234" \
  -c cookies.txt
```

### Mark Attendance
```bash
curl -X POST http://localhost:5000/teacher/api/mark-attendance \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"qr_token": "a1b2c3d4", "subject_id": 1}'
```

### Get Attendance Report
```bash
curl -X GET http://localhost:5000/admin/attendance \
  -b cookies.txt
```

---

## Pagination

Endpoints that return lists support pagination:

**Query Parameters:**
- `page` (default: 1) - Page number
- `per_page` (default: varies) - Items per page

**Response:**
```json
{
    "items": [...],
    "total": 100,
    "page": 1,
    "pages": 5,
    "has_prev": false,
    "has_next": true,
    "prev_num": null,
    "next_num": 2
}
```

---

## Changelog

### v1.0.0 (Initial Release)
- Admin panel with full CRUD
- Teacher QR attendance marking
- Student dashboard with analytics
- Excel/PDF report export
- Audit logging
- Security features (Bcrypt, CSRF, rate limiting)

---

For more information, see the [README.md](README.md) and [SETUP.md](SETUP.md).
