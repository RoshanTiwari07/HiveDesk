# 🐝 HiveDesk - AI-Powered HR Onboarding Backend

**FastAPI backend with AI-powered document verification, intelligent task management, and automated employee onboarding workflows.**

Built with clean architecture, async processing, and production-ready Docker deployment.

---

## ✨ The Magic Behind HiveDesk

### 🧠 **AI-Powered Intelligence**
- **Document Verification**: Gemini AI automatically validates Aadhaar, PAN, resumes with smart data extraction
- **Intelligent Assistants**: Context-aware HR & Employee chatbots for instant onboarding guidance
- **Smart Analytics**: AI-driven performance insights and onboarding progress tracking

### 🔐 **Security & Auth**
- JWT token-based authentication with secure password hashing
- Role-based access control (HR vs Employee permissions)
- Async session management with PostgreSQL

### 📊 **Core Workflow**
```
Employee Joins → Upload Documents → AI Verification → Task Assignment 
  → Training Modules → Performance Tracking → Onboarding Complete
```

### 🏗️ **Clean Architecture**
```
Routers (API Layer) → Services (Business Logic) → Models (Database)
                    ↓
              AI Services (Gemini Integration)
```

---

## 🚀 Quick Start with Docker

### 1️⃣ **Setup Environment**

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```bash
# Required: Generate a secure secret key
SECRET_KEY=<run: python -c "import secrets; print(secrets.token_hex(32))">

# Required: Get your free API key from https://aistudio.google.com/apikey
GEMINI_API_KEY=your-gemini-api-key-here

# Database (auto-configured with Docker)
DATABASE_URL=postgresql+asyncpg://postgres:roshan@localhost:5434/hr_onboarding_system
```

### 2️⃣ **Build & Run**

```bash
# Start everything (database + backend)
docker-compose up --build -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### 3️⃣ **Access the API**

- **🌐 API Base**: http://localhost:8000
- **📖 Interactive Docs**: http://localhost:8000/scalar
- **🔧 Swagger UI**: http://localhost:8000/docs

---

## 🔐 Test Credentials

The system auto-creates demo accounts on first startup:

| Role | Email | Password |
|------|-------|----------|
| **HR** | `john.hr@company.com` | `password123` |
| **Employee** | `jane.employee@company.com` | `password123` |

---

## 📦 Environment Variables Explained

### **Required Variables**

| Variable | How to Get | Example |
|----------|-----------|---------|
| `SECRET_KEY` | Generate: `python -c "import secrets; print(secrets.token_hex(32))"` | `c2b21737f620c344...` (64 chars) |
| `GEMINI_API_KEY` | 1. Visit https://aistudio.google.com/apikey<br>2. Create free API key<br>3. Copy key | `AIzaSyC...` |
| `DATABASE_URL` | Auto-configured by Docker<br>For custom DB: `postgresql+asyncpg://user:pass@host:port/dbname` | `postgresql+asyncpg://...` |

### **Optional Variables**

| Variable | Default | Purpose |
|----------|---------|---------|
| `AI_MODE` | `live` | Set to `mock` to disable AI calls (testing) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT token expiry time |
| `UPLOAD_DIR` | `./uploads` | Document storage location |
| `MAX_FILE_SIZE` | `10485760` | Max upload size (10MB) |

### **Full .env Template**

See [.env.example](c:/Myprojects/HiveDesk/backend/.env.example) for complete configuration template.

---

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app initialization
│   ├── database.py             # Async PostgreSQL connection
│   ├── auth.py                 # JWT authentication
│   ├── routers/                # API endpoints
│   │   ├── auth.py            # Login, register, logout
│   │   ├── documents.py       # AI document verification
│   │   ├── tasks.py           # Task management
│   │   ├── training.py        # Training modules
│   │   ├── employees.py       # Employee CRUD
│   │   ├── performance.py     # Analytics
│   │   └── assistants.py      # AI chatbots
│   ├── services/               # Business logic
│   │   ├── ai_document_service.py    # Gemini AI integration
│   │   ├── hr_assistant_service.py   # HR chatbot
│   │   ├── employee_assistant_service.py  # Employee chatbot
│   │   └── ...
│   ├── models/                 # SQLModel database models
│   └── schemas/                # Pydantic request/response schemas
├── alembic/                    # Database migrations
├── uploads/                    # Document storage
├── Dockerfile                  # Multi-stage production build
├── docker-compose.yml          # Full stack orchestration
├── requirements.txt            # Python dependencies
└── .env.example               # Environment template
```

---

## 🔧 Development Commands

```bash
# Local development (without Docker)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head

# Run tests (if implemented)
pytest

# Check code quality
black app/
flake8 app/
```

---

## 🎯 Key Features & Workflows

### **1. AI Document Verification**
- Upload Aadhaar/PAN/Resume → Gemini AI extracts & validates data
- Automatic compliance checking & data standardization
- Supports PDF, images (OCR via Tesseract)

### **2. Intelligent Task System**
- Auto-assign onboarding tasks to new employees
- Track completion status with real-time updates
- Smart notifications & reminders

### **3. Training Management**
- Assign training modules with deadlines
- Track progress & completion
- Auto-generate completion certificates

### **4. AI Assistants**
- **HR Bot**: Answers policy questions, document requirements
- **Employee Bot**: Onboarding guidance, task help
- Context-aware responses using Gemini AI

### **5. Performance Analytics**
- Real-time onboarding completion rates
- Task efficiency metrics
- Training progress dashboards

---

## 📖 API Documentation

Once running, explore the interactive API documentation:

- **Scalar Docs** (Recommended): http://localhost:8000/scalar  
  *Modern, beautiful API explorer with request/response examples*

- **Swagger UI**: http://localhost:8000/docs  
  *Traditional OpenAPI interface with try-it-out functionality*

### **Quick API Flow**
```
1. POST /api/auth/login → Get JWT token
2. Use token in Authorization: Bearer <token>
3. Explore endpoints in /scalar or /docs
```

---

## 🐳 Docker Details

### **Services**
- **postgres**: PostgreSQL 15 database (port 5434)
- **backend**: FastAPI application (port 8000)

### **Volumes**
- `postgres_data`: Persistent database storage
- `./uploads`: Document uploads (bind mount)

### **Useful Commands**
```bash
# Rebuild after code changes
docker-compose up --build

# View live logs
docker-compose logs -f

# Execute commands in container
docker-compose exec backend python -c "from app.database import ..."

# Reset everything (WARNING: deletes data)
docker-compose down -v
```

---

## 🚀 Production Deployment

See [DEPLOYMENT.md](c:/Myprojects/HiveDesk/backend/DEPLOYMENT.md) for detailed production deployment guide including:
- Cloud platform setup (Render, Railway, Fly.io)
- Environment configuration
- Database migration strategy
- Security best practices

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| **Framework** | FastAPI 0.104.1 |
| **Database** | PostgreSQL 15 + SQLModel + Alembic |
| **AI/ML** | Google Gemini 1.5 Flash |
| **Auth** | JWT (python-jose) + bcrypt |
| **OCR** | Tesseract + pdf2image |
| **Deployment** | Docker + Docker Compose |
| **Python** | 3.11 (async/await) |

---

## 📄 License

MIT License - Built for hackathon showcase

---

## 🤝 Contributing

This is a hackathon project. For issues or suggestions, please open an issue.

---

