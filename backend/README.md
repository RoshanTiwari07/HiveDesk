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
3. Explore endpoints in /docs
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

## 🚀 Deploy to Render (Production)

### **Step 1: Create Render Account**
Sign up at [render.com](https://render.com) (free tier available)

### **Step 2: Create PostgreSQL Database**
1. Go to Render Dashboard → New → PostgreSQL
2. Name: `hivedesk-db`
3. Copy the **Internal Database URL** (starts with `postgresql://`)

### **Step 3: Create Web Service**
1. New → Web Service
2. Connect your GitHub repo
3. Configure:
   - **Name**: `hivedesk-backend`
   - **Region**: Choose closest to you
   - **Branch**: `main` or `master`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run.py`

### **Step 4: Set Environment Variables**
Add these in Render Dashboard → Environment:

```env
DATABASE_URL=<paste-internal-database-url-from-step-2>
SECRET_KEY=<generate-with: python -c "import secrets; print(secrets.token_hex(32))">
GEMINI_API_KEY=<your-gemini-api-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
PYTHON_VERSION=3.11.0
```

### **Step 5: Deploy**
Click "Create Web Service" → Render auto-deploys!

### **Step 6: Update Frontend CORS**
Once deployed, add your Render URL to [main.py](c:/Myprojects/HiveDesk/backend/app/main.py#L28):
```python
allow_origins=[
    "http://localhost:5173",
    "https://your-render-app.onrender.com"  # Add this
]
```

### **Your API will be live at:**
`https://hivedesk-backend.onrender.com`

---

### **Alternative: Deploy with Docker on Render**
If you prefer Docker:
- **Dockerfile Path**: `backend/Dockerfile`
- No build/start commands needed
- Render auto-detects and uses Dockerfile

---

## 🎯 **Quick Render Troubleshooting**

| Issue | Solution |
|-------|----------|
| Port error | Render auto-sets `PORT` env var (already handled in code) |
| Database connection fails | Use **Internal Database URL**, not External |
| Build fails | Check `requirements.txt` is in `backend/` folder |
| Health check fails | Render pings `/` - add health endpoint if needed |

---

## � Common Issues & Solutions

### **🔴 CRITICAL: Database Schema Mismatch**
**Error:** `column users.onboarding_status does not exist`

**Cause:** Old database doesn't have new columns from code updates

**Solution:**
```bash
# Reset database (deletes all data!)
docker-compose down -v
docker-compose up --build -d
```

---

### **🟡 Backend Won't Start**

#### **Issue: Port 8000 already in use**
```
Error: bind: address already in use
```
**Solution:**
```bash
# Find and kill process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -i :8000
kill -9 <PID>
```

#### **Issue: Port 5434 already in use (PostgreSQL)**
**Solution:**
```bash
# Change port in docker-compose.yml
ports:
  - "5435:5432"  # Use different port

# Update DATABASE_URL in .env
DATABASE_URL=postgresql+asyncpg://postgres:roshan@localhost:5435/hr_onboarding_system
```

---

### **🟡 Database Connection Failed**

#### **Error:** `could not connect to server`
**Cause:** PostgreSQL container not running or wrong credentials

**Solution:**
```bash
# Check if postgres is running
docker-compose ps

# View postgres logs
docker-compose logs postgres

# Restart postgres
docker-compose restart postgres

# Verify DATABASE_URL matches docker-compose.yml credentials
```

---

### **🟡 Environment Variables Not Loading**

#### **Error:** `GEMINI_API_KEY not found in environment`
**Cause:** .env file missing or not in correct location

**Solution:**
```bash
# Check .env exists in backend/ folder
ls backend/.env

# Verify .env format (no quotes around values)
# ✅ Correct:
GEMINI_API_KEY=AIzaSyC...

# ❌ Wrong:
GEMINI_API_KEY="AIzaSyC..."

# Restart containers to reload .env
docker-compose down
docker-compose up -d
```

---

### **🟡 AI Features Not Working**

#### **Error:** API calls failing or returning mock data
**Possible causes:**

1. **Invalid API Key**
   - Get new key: https://aistudio.google.com/apikey
   - Update in `.env`

2. **API Quota Exceeded**
   - Check quota: https://aistudio.google.com/
   - Wait for reset or upgrade plan
   - Or use mock mode: `AI_MODE=mock` in `.env`

3. **Network Issues**
   - Check internet connection
   - Fallback to mock mode automatically (already configured)

---

### **🟡 Docker Build Failures**

#### **Error:** `failed to solve with frontend dockerfile.v0`
**Solution:**
```bash
# Clear Docker cache
docker system prune -a
docker-compose build --no-cache
```

#### **Error:** `requirements.txt not found`
**Solution:**
```bash
# Ensure you're in correct directory
cd backend
docker-compose up --build
```

---

### **🟡 CORS Errors (Frontend Can't Connect)**

#### **Error:** `Access to fetch blocked by CORS policy`
**Cause:** Frontend URL not in allowed origins

**Solution:**
Edit [app/main.py](c:/Myprojects/HiveDesk/backend/app/main.py#L28):
```python
allow_origins=[
    "http://localhost:5173",
    "http://localhost:3000",
    "https://your-frontend-url.com"  # Add your URL
]
```

---

### **🟡 File Upload Errors**

#### **Error:** `File size exceeds maximum`
**Solution:**
Increase limit in `.env`:
```env
MAX_FILE_SIZE=20971520  # 20MB
```

#### **Error:** `uploads directory not found`
**Solution:**
```bash
# Create uploads directory
mkdir uploads
chmod 755 uploads

# Or rebuild Docker
docker-compose up --build
```

---

### **🟡 Migration Issues**

#### **Error:** `Target database is not up to date`
**Solution:**
```bash
# Run migrations manually
docker-compose exec backend alembic upgrade head

# Or reset database completely
docker-compose down -v
docker-compose up --build -d
```

---

### **🔧 Debugging Commands**

```bash
# View all container logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f postgres

# Access backend container shell
docker-compose exec backend bash

# Access database
docker-compose exec postgres psql -U postgres -d hr_onboarding_system

# Check database tables
docker-compose exec postgres psql -U postgres -d hr_onboarding_system -c "\dt"

# Restart specific service
docker-compose restart backend

# Check container status
docker-compose ps

# View resource usage
docker stats

# Complete cleanup (removes everything)
docker-compose down -v
docker system prune -a
```

---

### **🚨 Emergency Reset (Nuclear Option)**

If nothing works, complete fresh start:
```bash
# 1. Stop everything
docker-compose down -v

# 2. Remove all Docker resources
docker system prune -a -f
docker volume prune -f

# 3. Delete uploads
rm -rf uploads/*

# 4. Rebuild from scratch
docker-compose up --build -d

# 5. Check logs
docker-compose logs -f
```

---

### **💡 Quick Health Check**

```bash
# Test if backend is running
curl http://localhost:8000/scalar

# Test database connection
docker-compose exec backend python -c "from app.database import AsyncSessionLocal; import asyncio; asyncio.run(AsyncSessionLocal().__aenter__())"

# Test environment variables
docker-compose exec backend python -c "import os; print('SECRET_KEY:', bool(os.getenv('SECRET_KEY'))); print('GEMINI_API_KEY:', bool(os.getenv('GEMINI_API_KEY')))"
```

---

## �🛠️ Tech Stack

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

