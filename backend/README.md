# Time Capsule Backend

Flask REST API backend for the Time Capsule Digital Legacy application.

## Tech Stack

- **Framework**: Flask 3.0
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy + Flask-Migrate
- **Authentication**: JWT (PyJWT)
- **Environment Config**: python-dotenv

## Project Structure

```
backend/
├── app/
│   ├── __init__.py        # Application factory
│   ├── config.py          # Configuration classes
│   ├── extensions.py      # Flask extensions
│   ├── models.py          # SQLAlchemy models
│   ├── auth/              # Authentication blueprint
│   │   ├── __init__.py
│   │   ├── routes.py      # Auth endpoints
│   │   ├── schemas.py     # Request validation
│   │   └── utils.py       # JWT utilities
│   └── main/              # Main blueprint
│       ├── __init__.py
│       └── routes.py      # General endpoints
├── migrations/            # Database migrations (auto-generated)
├── run.py                 # Development server entry
├── wsgi.py                # Production WSGI entry
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── .flaskenv              # Flask CLI configuration
└── README.md
```

## Setup Instructions

### 1. Prerequisites

- Python 3.10 or higher
- PostgreSQL 14 or higher
- pip (Python package manager)

### 2. Create and Activate Virtual Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings
```

Required environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | `your-secret-key` |
| `JWT_SECRET_KEY` | JWT signing key | `your-jwt-secret` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg2://user:pass@localhost:5432/timecapsule_db` |
| `FLASK_ENV` | Environment (development/production) | `development` |

### 5. Create PostgreSQL Database

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE timecapsule_db;

-- Create user (optional)
CREATE USER timecapsule_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE timecapsule_db TO timecapsule_user;
```

### 6. Run Database Migrations

```bash
# Initialize migrations (first time only)
flask db init

# Generate migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

### 7. Run Development Server

```bash
# Using Flask CLI
flask run

# Or using run.py
python run.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Check API status |

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get JWT |
| GET | `/api/auth/me` | Get current user (protected) |
| POST | `/api/auth/refresh` | Refresh JWT token (protected) |

### Protected Test

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/protected-test` | Test JWT authentication |

## API Usage Examples

### Register a New User

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword"
  }'
```

Response:
```json
{
  "message": "User registered successfully",
  "access_token": "eyJ...",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "created_at": "2025-01-01T00:00:00"
  }
}
```

### Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepassword"
  }'
```

### Get Current User (Protected)

```bash
curl http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Database Models

### User Model

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| name | String(150) | User's full name |
| email | String(150) | Unique email address |
| password_hash | String(255) | Hashed password |
| role | String(50) | User role (user/admin) |
| created_at | DateTime | Account creation time |
| updated_at | DateTime | Last update time |

### Future Models (Part 2)

- **Capsule**: Time capsule with encrypted message
- **Recipient**: People who receive capsules
- **Guardian**: Trusted verifiers for event-based releases
- **Attachment**: Files attached to capsules
- **DeliveryLog**: Capsule delivery tracking
- **HeartbeatCheck**: Inactivity verification

## Production Deployment

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

## Testing

```bash
# Run tests (when implemented)
pytest

# With coverage
pytest --cov=app tests/
```

## License

MIT License
