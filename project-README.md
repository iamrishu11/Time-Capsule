# Time Capsule for Digital Legacy

A full-stack web application that allows users to create "time capsules" — messages, letters, photos, and memories — that will be delivered to loved ones at a future date or on certain life events.

## 🎯 Project Overview

This B.Tech final year project implements a digital legacy platform where users can:

- **Create Time Capsules**: Write heartfelt messages and letters for loved ones
- **Schedule Delivery**: Set specific dates or event-based triggers
- **Manage Recipients**: Add family members and friends who will receive capsules
- **Secure Content**: All messages are encrypted for privacy
- **Verify Events**: Use guardians for event-based releases (e.g., passing)

## 📁 Project Structure

```
time-capsule/
├── backend/                 # Flask REST API
│   ├── app/                 # Application package
│   │   ├── auth/            # Authentication module
│   │   ├── main/            # Main routes module
│   │   ├── models.py        # Database models
│   │   └── ...
│   ├── migrations/          # Database migrations
│   ├── requirements.txt     # Python dependencies
│   └── README.md            # Backend documentation
│
├── frontend/                # React SPA
│   ├── src/
│   │   ├── api/             # API client
│   │   ├── components/      # Reusable components
│   │   ├── context/         # React Context
│   │   ├── pages/           # Page components
│   │   └── ...
│   ├── package.json         # Node dependencies
│   └── README.md            # Frontend documentation
│
└── README.md                # This file
```

## 🛠️ Tech Stack

### Backend
- **Python 3.10+**
- **Flask** - Web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **Flask-Migrate** - Database migrations
- **PyJWT** - JWT authentication
- **Flask-CORS** - Cross-origin support

### Frontend
- **React 18** - UI library
- **Vite** - Build tool
- **React Router DOM** - Client-side routing
- **Axios** - HTTP client
- **Context API** - State management

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/time-capsule.git
cd time-capsule
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your database credentials

# Create database
# (First create the database in PostgreSQL)

# Run migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Start server
flask run
```

Backend runs at: `http://localhost:5000`

### 3. Frontend Setup

```bash
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

Frontend runs at: `http://localhost:5173`

## 📋 Current Features (Part 1)

### ✅ Implemented

- [x] User registration with validation
- [x] User login with JWT tokens
- [x] Protected routes with authentication
- [x] Session persistence (localStorage)
- [x] User dashboard
- [x] Responsive design
- [x] PostgreSQL database with all models

### 🔜 Coming in Part 2

- [ ] Create and manage time capsules
- [ ] Add and manage recipients
- [ ] Add and manage guardians
- [ ] Message encryption (AES)
- [ ] File attachments
- [ ] Scheduled delivery system
- [ ] Event-based triggers
- [ ] Heartbeat checks

## 🗄️ Database Models

| Model | Description |
|-------|-------------|
| User | Account owners who create capsules |
| Recipient | People who receive capsules |
| Guardian | Trusted verifiers for event releases |
| Capsule | Core entity with encrypted messages |
| CapsuleRecipient | Junction table for capsule-recipient |
| CapsuleGuardian | Junction table for capsule-guardian |
| Attachment | Files linked to capsules |
| DeliveryLog | Capsule delivery tracking |
| HeartbeatCheck | Inactivity verification pings |

## 🔑 API Endpoints

### Public
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Login user |

### Protected (Requires JWT)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/refresh` | Refresh token |
| GET | `/api/protected-test` | Test auth |

## 🧪 Testing

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
npm run lint
```

## 📝 Environment Variables

### Backend (.env)
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/timecapsule_db
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:5000
```

## 👥 Team

- **Student Name** - Developer
- **Guide Name** - Project Guide

## 📄 License

This project is part of a B.Tech final year project.

---

*Time Capsule for Digital Legacy - Preserving memories for future generations.*
