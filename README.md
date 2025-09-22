# Fintech Advisor - AI-Powered Debt Management

A MEAN stack application for personalized debt management and financial planning.

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Docker
```bash
docker-compose up -d
```

## Structure

- `backend/` - FastAPI + MongoDB
- `frontend/` - React + TypeScript
- `backend/app/core/` - Your existing business logic goes here
- `backend/kb/` - Your knowledge base files go here

## Next Steps

1. Copy your existing core files to `backend/app/core/`
2. Copy your knowledge base to `backend/kb/`
3. Set up your API keys in `.env` files
4. Start implementing components

## API Documentation

Once running: http://localhost:8000/docs
