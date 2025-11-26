# ⏳ Time Capsule for Digital Legacy

A full-stack web application that allows users to create digital time capsules—messages, letters, and media files—that will be securely stored and delivered to loved ones at a specified future date or upon certain life events.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.12-green.svg)
![React](https://img.shields.io/badge/React-18-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey.svg)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Part 1: Authentication \& Foundation](#part-1-authentication--foundation)
- [Part 2: Capsule Creation \& Secure Storage](#part-2-capsule-creation--secure-storage)
- [Installation](#installation)
- [API Endpoints](#api-endpoints)
- [Security Features](#security-features)
- [Future Enhancements](#future-enhancements)

---

## 🎯 Overview

**Time Capsule for Digital Legacy** enables users to preserve memories and messages for their loved ones. Users can:

- Write heartfelt messages and letters
- Attach photos, videos, and documents
- Schedule delivery for specific future dates
- Set event-based triggers for delivery
- Securely encrypt all content

The application emphasizes security through encryption and provides an intuitive interface for managing digital legacies.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **Secure Authentication** | JWT-based stateless authentication with encrypted passwords |
| 📝 **Capsule Creation** | Create time capsules with encrypted messages |
| 👥 **Recipient Management** | Add and manage recipients for your capsules |
| 📎 **File Attachments** | Upload photos, videos, and documents (up to 16MB) |
| 📅 **Scheduled Delivery** | Set specific dates for capsule delivery |
| 🔒 **End-to-End Encryption** | AES-128 encryption for all capsule messages |
| 📱 **Responsive Design** | Works seamlessly on desktop and mobile |

---

## 🛠 Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Flask 3.x** | Web framework |
| **SQLAlchemy** | ORM for database operations |
| **Flask-Migrate** | Database migrations |
| **PyJWT** | JSON Web Token authentication |
| **Cryptography** | Fernet encryption for messages |
| **SQLite/PostgreSQL** | Database (SQLite for dev, PostgreSQL for prod) |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | UI framework |
| **Vite** | Build tool and dev server |
| **React Router v6** | Client-side routing |
| **Axios** | HTTP client for API calls |
| **CSS3** | Styling with CSS variables |

---

## 📁 Project Structure

```
time-capsule/
├── backend/
│   ├── app/
│   │   ├── auth/           # Authentication module
│   │   ├── main/           # Main routes (health check)
│   │   ├── recipients/     # Recipients CRUD API
│   │   ├── capsules/       # Capsules API with encryption
│   │   ├── security/       # Encryption utilities
│   │   ├── models.py       # Database models
│   │   ├── extensions.py   # Flask extensions
│   │   └── config.py       # Configuration classes
│   ├── migrations/         # Database migrations
│   ├── uploads/            # File attachments storage
│   ├── requirements.txt    # Python dependencies
│   └── run.py              # Application entry point
│
├── frontend/
│   ├── src/
│   │   ├── api/            # API client functions
│   │   ├── components/     # Reusable components
│   │   ├── context/        # React context (Auth)
│   │   ├── pages/          # Page components
│   │   ├── App.jsx         # Main app component
│   │   └── main.jsx        # Entry point
│   ├── package.json        # Node dependencies
│   └── vite.config.js      # Vite configuration
│
└── README.md               # This file
```

---

## 📦 Part 1: Authentication & Foundation

### Objective
Establish the core infrastructure including user authentication, database models, and the basic application framework.

### Backend Implementation

#### Database Models
Designed and implemented 9 comprehensive database models:

| Model | Purpose |
|-------|---------|
| **User** | Account holders who create capsules |
| **Recipient** | People who will receive capsules |
| **Guardian** | Trusted verifiers for event-based delivery |
| **Capsule** | Core entity storing encrypted messages |
| **CapsuleRecipient** | Junction table for capsule-recipient relationships |
| **CapsuleGuardian** | Junction table for capsule-guardian relationships |
| **Attachment** | Files (photos, videos) linked to capsules |
| **DeliveryLog** | Records of delivery attempts and status |
| **HeartbeatCheck** | Inactivity monitoring for event triggers |

#### Authentication System
- **Stateless authentication** using JSON Web Tokens (PyJWT)
- Secure password hashing with **Werkzeug** (PBKDF2-SHA256)
- Custom `@token_required` decorator for protecting API endpoints
- Token expiration handling (24-hour validity)

### Frontend Implementation

#### Key Features
- **AuthContext**: Global authentication state management
- **ProtectedRoute**: Route guard for authenticated pages
- **Persistent Sessions**: Auto-restoration via localStorage
- **Responsive Navbar**: Dynamic navigation based on auth state

#### Pages Implemented
| Page | Route | Description |
|------|-------|-------------|
| Home | `/` | Landing page with project introduction |
| Register | `/register` | User registration form |
| Login | `/login` | User login form |
| Dashboard | `/dashboard` | Protected user dashboard |

---

## 🔒 Part 2: Capsule Creation & Secure Storage

### Objective
Implement the core capsule functionality including recipient management, encrypted message storage, and file attachments.

### Backend Implementation

#### Encryption System
- Implemented **Fernet symmetric encryption** (AES-128-CBC)
- Capsule messages encrypted before database storage
- Decryption only when capsule owner views their capsule

```
Encryption Flow:
plain_text → Fernet.encrypt() → encrypted_blob (DB)
encrypted_blob → Fernet.decrypt() → plain_text (retrieval)
```

#### Recipients API
Full CRUD operations for managing capsule recipients:
- Create, read, update, and delete recipients
- Owner-only access control

#### Capsules API
Complete capsule management with encryption:
- Create capsules with encrypted messages
- Assign multiple recipients
- Set release dates and types (TIME/EVENT)
- Optional guardian verification

#### Attachments API
File upload system for capsule media:
- Organized storage: `uploads/<user_id>/<capsule_id>/`
- MIME type validation (images, videos, documents)
- File size limit: 16MB (configurable)
- Secure filename handling

### Frontend Implementation

#### New Pages
| Page | Route | Description |
|------|-------|-------------|
| Recipients | `/recipients` | Manage capsule recipients |
| Create Capsule | `/capsules/new` | Create new time capsule |
| Capsule Detail | `/capsules/:id` | View/edit capsule details |

#### Capsule Creation Features
- Title and message input
- Multi-select recipient picker
- Release type selection (TIME/EVENT)
- Date/time picker for scheduled delivery
- Guardian requirement option

#### Capsule Detail Features
- View decrypted message content
- Recipient list display
- File attachment upload/management
- Status indicators (Draft, Scheduled, Sent)
- Edit/delete functionality

---

## 🚀 Installation

### Prerequisites
- Python 3.12+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example)
cp .env.example .env

# Generate encryption key and update .env
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Run server
python run.py
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Run development server
npm run dev
```

### Access the Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get JWT token |
| GET | `/api/auth/me` | Get current user info |

### Recipients
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/recipients` | List all recipients |
| POST | `/api/recipients` | Create recipient |
| GET | `/api/recipients/<id>` | Get recipient details |
| PUT | `/api/recipients/<id>` | Update recipient |
| DELETE | `/api/recipients/<id>` | Delete recipient |

### Capsules
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/capsules` | List all capsules |
| POST | `/api/capsules` | Create capsule |
| GET | `/api/capsules/<id>` | Get capsule with decrypted message |
| PUT | `/api/capsules/<id>` | Update capsule |
| DELETE | `/api/capsules/<id>` | Delete capsule |

### Attachments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/capsules/<id>/attachments` | List attachments |
| POST | `/api/capsules/<id>/attachments` | Upload attachment |
| DELETE | `/api/capsules/<id>/attachments/<aid>` | Delete attachment |

---

## 🔐 Security Features

| Feature | Implementation |
|---------|----------------|
| **Password Security** | PBKDF2-SHA256 hashing with salt |
| **Message Encryption** | AES-128 symmetric encryption (Fernet) |
| **JWT Authentication** | Stateless, expiring tokens (24h) |
| **Authorization** | Owner-only access to resources |
| **CORS Configuration** | Restricted to frontend origin |
| **Input Validation** | Server-side validation for all inputs |
| **Secure File Handling** | Sanitized filenames, type validation |

---

## 🔮 Future Enhancements

### Part 3 (Planned)
- [ ] **Scheduler Implementation**: Background jobs for automated delivery
- [ ] **Email Integration**: SMTP setup for sending capsules
- [ ] **Guardian Verification**: Event-based trigger system
- [ ] **Heartbeat Monitoring**: Inactivity detection for life events

### Additional Features
- [ ] Rich text editor for messages
- [ ] Video recording within app
- [ ] Multiple delivery methods (email, SMS)
- [ ] Social login integration
- [ ] Mobile app (React Native)

---

## 👨‍💻 Author

**Rishu** - B.Tech Final Year Project

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Flask documentation and community
- React documentation
- Cryptography library maintainers