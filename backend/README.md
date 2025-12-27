# HR Onboarding System - Async FastAPI Backend

A comprehensive HR onboarding system built with FastAPI, SQLModel, and PostgreSQL using async/await patterns.

## Features

- **Async/Await Architecture**: Fully asynchronous for better performance
- **Role-based Authentication**: JWT-based auth with HR and Employee roles
- **Task Management**: Create, assign, and track onboarding tasks
- **Document Management**: Upload and verify employee documents
- **Training Modules**: Manage training content and track progress
- **RESTful API**: Clean API endpoints following REST conventions
- **Type Safety**: Pydantic schemas for request/response validation
- **Organized Structure**: Separated models, schemas, and core enums

## Project Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   └── enums.py          # Core enumerations
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py           # User database model
│   │   ├── task.py           # Task database models
│   │   ├── document.py       # Document database model
│   │   └── training.py       # Training database models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py           # User Pydantic schemas
│   │   ├── task.py           # Task Pydantic schemas
│   │   ├── document.py       # Document Pydantic schemas
│   │   └── training.py       # Training Pydantic schemas
│   ├── __init__.py
│   ├── main.py               # FastAPI application
│   ├── database.py           # Async database configuration
│   └── auth.py               # Async authentication utilities
├── uploads/                  # File upload directory
├── requirements.txt          # Python dependencies
├── run.py                   # Application entry point
├── create_sample_data.py    # Sample data creation
├── .env                     # Environment variables
└── README.md                # This file
```

## Database Schema

### Tables
- **users**: HR and Employee users with role-based access
- **tasks**: Onboarding tasks (READ, UPLOAD, SIGN types)
- **employee_tasks**: Task assignments and completion tracking
- **documents**: File metadata and verification status
- **training_modules**: Training content and modules
- **employee_training**: Training progress tracking

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - Register new user (HR only)

### Dashboard & Management
- `GET /{name}/{role}/dashboard` - Get dashboard data
- `GET /{name}/{role}/employees` - Manage all employees (HR only)
- `GET /{name}/{role}/manage/{employee_name}` - Manage specific employee (HR only)
- `POST /{name}/{role}/assign-task` - Assign task to employee (HR only)

### Tasks
- `GET /{name}/{role}/tasks` - Get tasks (all for HR, assigned for Employee)
- `POST /{name}/{role}/tasks/complete` - Mark task as completed

### Documents
- `GET /{name}/{role}/documents` - Get documents (all for HR, own for Employee)
- `POST /{name}/{role}/documents/upload` - Upload document

### Training
- `GET /{name}/{role}/training` - Get training modules

## Setup Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip or poetry

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Database Setup
Create a PostgreSQL database:
```sql
CREATE DATABASE hr_onboarding_system;
CREATE USER hr_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE hr_onboarding_system TO hr_user;
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and update the values:
```bash
cp .env.example .env
```

Update the `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql+asyncpg://hr_user:your_password@localhost:5432/hr_onboarding_system
```

### 4. Run the Application
```bash
python run.py
```

The API will be available at `http://localhost:8000`

### 5. Create Sample Data (Optional)
```bash
python create_sample_data.py
```

This creates sample users, tasks, and training modules for testing.

## Key Changes in Async Version

### Database
- Uses `asyncpg` instead of `psycopg2-binary`
- `AsyncSession` instead of `Session`
- `create_async_engine` for async database operations
- All database operations use `await`

### Models & Schemas
- **Models**: Database models with proper naming (`UserModel`, `TaskModel`, etc.)
- **Schemas**: Pydantic schemas for request/response validation
- **Enums**: Centralized enumerations in `core/enums.py`
- **Organization**: Separated into logical modules

### API Endpoints
- All endpoints are `async def`
- Database queries use `await session.exec()`
- File uploads use `aiofiles` for async file operations
- Proper response models with Pydantic schemas

### Performance Benefits
- Non-blocking I/O operations
- Better concurrency handling
- Improved scalability
- Async file operations

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Sample Login Credentials

After running `create_sample_data.py`:

**HR User:**
- Email: `john.hr@company.com`
- Password: `password123`

**Employee Users:**
- Email: `jane.employee@company.com` / Password: `password123`
- Email: `bob.employee@company.com` / Password: `password123`
- Email: `alice.employee@company.com` / Password: `password123`

## Usage Examples

### 1. Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=john.hr@company.com&password=password123"
```

### 2. Get HR Dashboard
```bash
curl -X GET "http://localhost:8000/john/hr/dashboard" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Upload Document (Employee)
```bash
curl -X POST "http://localhost:8000/jane/employee/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf" \
  -F "document_type=resume"
```

## Security Features

- JWT-based authentication
- Role-based access control
- Password hashing with bcrypt
- File upload validation
- SQL injection protection via SQLModel
- Async-safe operations

## Development

### Adding New Endpoints
1. Define new models in appropriate `models/` files
2. Create Pydantic schemas in `schemas/` files
3. Add endpoints in `main.py`
4. Update authentication/authorization as needed

### Database Migrations
The application uses SQLModel which automatically creates tables. For production, consider using Alembic for proper migrations.

## Production Deployment

1. Set strong `SECRET_KEY` in environment
2. Use production PostgreSQL instance
3. Configure proper file storage (AWS S3, etc.)
4. Set up HTTPS
5. Configure logging and monitoring
6. Use production ASGI server (Gunicorn with Uvicorn workers)

## License

This project is for educational/hackathon purposes.