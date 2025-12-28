# Production Deployment Guide - HiveDesk Backend

## 🚀 Quick Deploy Checklist

### 1. Environment Setup
```bash
# Copy .env.example and fill in production values
cp .env.example .env

# Generate secure SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
# Add the output to .env as SECRET_KEY
```

### 2. Database Setup
- Set up PostgreSQL database (recommend: Supabase, Railway, or AWS RDS)
- Update `DATABASE_URL` in `.env` with production credentials
- Run migrations: `alembic upgrade head`

### 3. API Key Configuration
- Get Gemini API key from Google AI Studio
- Add to `.env` as `GEMINI_API_KEY`

### 4. Deploy Options

#### Option A: Docker (Recommended)
```bash
docker-compose up -d
```

#### Option B: Cloud Platform (Render, Railway, Fly.io)
1. Connect your GitHub repo
2. Set environment variables from `.env`
3. Deploy with auto-build

### 5. Frontend CORS
Update `allow_origins` in `app/main.py` with your frontend URL:
```python
allow_origins=["https://your-frontend-url.com"]
```

### 6. Health Check
After deployment, verify:
- `/scalar` - API documentation accessible
- `/api/auth/test` - Health endpoint returns 200

## 🔒 Security Notes
- Never commit `.env` file (already in .gitignore)
- Use strong passwords for database
- Keep `SECRET_KEY` secret and unique per environment
- Enable HTTPS in production

## 📝 Environment Variables Required
```
DATABASE_URL=postgresql+asyncpg://...
SECRET_KEY=<generated-secret>
GEMINI_API_KEY=<your-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🎯 Hackathon Demo Tips
- Use `.env.example` as template
- Test locally with docker-compose first
- Provide demo credentials in README
- Include deployment URL in project submission
