# Time Capsule - Deployment Guide

This guide covers deploying the Time Capsule application with:
- **Frontend**: Vercel (React/Vite)
- **Backend**: PythonAnywhere (Flask)
- **Database**: Azure PostgreSQL

---

## Prerequisites

Before starting, ensure you have:
- [ ] GitHub account (for code deployment)
- [ ] Vercel account (free tier works)
- [ ] PythonAnywhere account (free tier works, but paid recommended)
- [ ] Azure PostgreSQL database (already set up)
- [ ] Gmail account with App Password configured

---

## Step 1: Set Up Azure PostgreSQL Database

### 1.1 Run the DDL Script

1. Connect to your Azure PostgreSQL database using a client like pgAdmin, DBeaver, or Azure Data Studio:

```
Host: prodtest-db.postgres.database.azure.com
Database: postgres
Username: prodtestdb
Password: ORX5YU1n2VRsMU
Port: 5432
SSL Mode: Require
```

2. Open the file `database/schema.sql` from this project
3. Run the entire script to create all tables and indexes

### 1.2 Verify Tables Created

Run this query to verify:
```sql
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
```

You should see these tables:
- users
- recipients
- guardians
- capsules
- capsule_recipients
- capsule_guardians
- attachments
- delivery_logs
- heartbeat_checks

---

## Step 2: Deploy Backend to PythonAnywhere

### 2.1 Create PythonAnywhere Account

1. Go to [PythonAnywhere](https://www.pythonanywhere.com)
2. Sign up for a free account (or upgrade for custom domain)
3. Note your username - it will be used in URLs

### 2.2 Upload Code to PythonAnywhere

**Option A: Using Git (Recommended)**

1. Go to **Consoles** tab and open a **Bash console**
2. Clone your repository:
```bash
git clone https://github.com/YOUR_USERNAME/time-capsule.git
cd time-capsule
```

**Option B: Manual Upload**

1. Go to **Files** tab
2. Create a folder called `time-capsule`
3. Upload all backend files to `time-capsule/backend/`

### 2.3 Set Up Virtual Environment

In the Bash console:
```bash
cd ~/time-capsule/backend
mkvirtualenv --python=/usr/bin/python3.10 timecapsule-env
pip install -r requirements.txt
```

### 2.4 Configure Environment Variables

1. Go to **Files** tab
2. Navigate to `/home/YOUR_USERNAME/time-capsule/backend/`
3. Create a new file called `.env.production` with:

```env
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Security Keys (GENERATE NEW ONES!)
SECRET_KEY=your-production-secret-key-at-least-32-chars
JWT_SECRET_KEY=your-jwt-secret-key-at-least-32-chars

# Azure PostgreSQL Database
DATABASE_URL=postgresql+psycopg2://prodtestdb:ORX5YU1n2VRsMU@prodtest-db.postgres.database.azure.com:5432/postgres?sslmode=require

# Encryption Key (use the same key as development!)
ENCRYPTION_KEY=8OCMTDLKTz6V1ffCYSO3iQSAZNbUjirzzXSFCxLPXyU=

# File Uploads
UPLOAD_FOLDER=/home/YOUR_USERNAME/time-capsule/backend/uploads
MAX_CONTENT_LENGTH=16777216

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=rishankj749@gmail.com
MAIL_PASSWORD=uqzatynzlhqnjptr
MAIL_DEFAULT_SENDER=rishankj749@gmail.com
MAIL_SENDER_NAME=Time Capsule

# CORS - Add your Vercel URL after frontend deployment
FRONTEND_URLS=https://your-app.vercel.app,http://localhost:5173
```

**⚠️ IMPORTANT**: Replace `YOUR_USERNAME` with your actual PythonAnywhere username!

### 2.5 Configure Web App

1. Go to **Web** tab
2. Click **Add a new web app**
3. Choose **Manual configuration** (not Flask!)
4. Select **Python 3.10**

### 2.6 Configure WSGI File

1. In the **Web** tab, click on the WSGI configuration file link
2. Replace the entire content with:

```python
import sys
import os

# Add project directory to sys.path
project_home = '/home/YOUR_USERNAME/time-capsule/backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables
from dotenv import load_dotenv
dotenv_path = os.path.join(project_home, '.env.production')
load_dotenv(dotenv_path)

# Create the Flask app
from app import create_app
from app.config import ProductionConfig

application = create_app(ProductionConfig)
```

**⚠️ Replace `YOUR_USERNAME` with your actual username!**

### 2.7 Configure Virtual Environment Path

1. In the **Web** tab, find **Virtualenv** section
2. Enter: `/home/YOUR_USERNAME/.virtualenvs/timecapsule-env`

### 2.8 Configure Static Files (Optional)

In the **Static files** section:
```
URL: /static/
Directory: /home/YOUR_USERNAME/time-capsule/backend/app/static
```

### 2.9 Reload Web App

1. Click the green **Reload** button
2. Visit `https://YOUR_USERNAME.pythonanywhere.com/api/health`
3. You should see: `{"message": "Time Capsule API is running", "status": "ok"}`

### 2.10 Troubleshooting

If you see errors:
1. Go to **Web** tab → **Log files** → **Error log**
2. Common issues:
   - Missing dependencies: Run `pip install -r requirements.txt` again
   - Wrong paths: Check WSGI file paths match your username
   - Database connection: Verify DATABASE_URL in .env.production

---

## Step 3: Deploy Frontend to Vercel

### 3.1 Update API URL

1. Open `frontend/.env.production`
2. Update the API URL:
```env
VITE_API_URL=https://YOUR_PYTHONANYWHERE_USERNAME.pythonanywhere.com
```

### 3.2 Push to GitHub

```bash
git add .
git commit -m "Configure for production deployment"
git push origin main
```

### 3.3 Deploy to Vercel

1. Go to [Vercel](https://vercel.com)
2. Sign in with GitHub
3. Click **Add New** → **Project**
4. Import your `time-capsule` repository
5. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

6. Add Environment Variable:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://YOUR_USERNAME.pythonanywhere.com`

7. Click **Deploy**

### 3.4 Get Your Frontend URL

After deployment, Vercel will give you a URL like:
- `https://your-app.vercel.app`

### 3.5 Update Backend CORS

1. Go back to PythonAnywhere
2. Edit `.env.production`
3. Update `FRONTEND_URLS` with your Vercel URL:
```env
FRONTEND_URLS=https://your-app.vercel.app,http://localhost:5173
```
4. Reload the web app

---

## Step 4: Test the Deployment

### 4.1 Test Backend API

```bash
# Health check
curl https://YOUR_USERNAME.pythonanywhere.com/api/health

# Should return:
# {"message": "Time Capsule API is running", "status": "ok"}
```

### 4.2 Test Frontend

1. Open your Vercel URL in a browser
2. Register a new account
3. Log in
4. Create a recipient
5. Create a time capsule

### 4.3 Test Email

1. Log in to the app
2. Create a capsule with your email as recipient
3. Check if you receive confirmation email

---

## Step 5: Set Up Scheduled Tasks (PythonAnywhere)

For automatic capsule delivery, set up scheduled tasks.

### 5.1 Create Task Script

Create `/home/YOUR_USERNAME/time-capsule/backend/tasks.py`:

```python
#!/usr/bin/env python
"""
Scheduled tasks for Time Capsule.
Run this via PythonAnywhere's scheduled tasks.
"""
import os
import sys

# Add project to path
project_home = '/home/YOUR_USERNAME/time-capsule/backend'
sys.path.insert(0, project_home)

# Load environment
from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env.production'))

# Import and run
from app import create_app
from app.config import ProductionConfig
from app.services.scheduler_service import process_scheduled_capsules, send_delivery_reminders

app = create_app(ProductionConfig)

with app.app_context():
    print("Processing scheduled capsules...")
    result = process_scheduled_capsules()
    print(f"Result: {result}")
    
    print("Sending delivery reminders...")
    reminders = send_delivery_reminders()
    print(f"Reminders: {reminders}")
```

### 5.2 Configure Scheduled Task

1. Go to PythonAnywhere **Tasks** tab
2. Add a new scheduled task:
   - **Time**: Choose your preferred time (e.g., daily at 00:00 UTC)
   - **Command**: 
   ```
   /home/YOUR_USERNAME/.virtualenvs/timecapsule-env/bin/python /home/YOUR_USERNAME/time-capsule/backend/tasks.py
   ```
3. Enable the task

---

## Configuration Summary

### Backend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | Random 32+ char string |
| `JWT_SECRET_KEY` | JWT signing key | Random 32+ char string |
| `DATABASE_URL` | PostgreSQL connection | `postgresql+psycopg2://...` |
| `ENCRYPTION_KEY` | Fernet encryption key | Base64 encoded key |
| `MAIL_SERVER` | SMTP server | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP port | `587` |
| `MAIL_USERNAME` | Email address | `your@gmail.com` |
| `MAIL_PASSWORD` | App password | Gmail app password |
| `FRONTEND_URLS` | Allowed CORS origins | Comma-separated URLs |

### Frontend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `https://username.pythonanywhere.com` |

---

## Security Checklist

Before going live:

- [ ] Generate new `SECRET_KEY` and `JWT_SECRET_KEY` for production
- [ ] Ensure `ENCRYPTION_KEY` is backed up securely
- [ ] Remove any test accounts from database
- [ ] Enable HTTPS on all endpoints (automatic on Vercel & PythonAnywhere)
- [ ] Review CORS settings to only allow your frontend domain
- [ ] Set up database backups on Azure

---

## Troubleshooting

### Backend Issues

**500 Internal Server Error**
- Check PythonAnywhere error logs
- Verify all environment variables are set
- Check database connection

**CORS Errors**
- Ensure `FRONTEND_URLS` includes your Vercel domain
- Reload the PythonAnywhere web app after changes

**Email Not Sending**
- Verify Gmail App Password is correct (no spaces)
- Check if Gmail has blocked access
- Test with `/api/test-email` endpoint

### Frontend Issues

**API Connection Failed**
- Verify `VITE_API_URL` is correct in Vercel
- Check browser console for errors
- Ensure backend is running

**After Deploy, Old Version Shows**
- Clear browser cache
- Trigger a new deployment on Vercel

### Database Issues

**Connection Refused**
- Verify Azure PostgreSQL firewall allows PythonAnywhere IPs
- Check SSL mode is set to `require`
- Verify credentials are correct

---

## Maintenance

### Regular Tasks

1. **Monitor Logs**: Check PythonAnywhere error logs weekly
2. **Database Backups**: Set up Azure automated backups
3. **Update Dependencies**: Periodically update Python packages
4. **Review Scheduled Tasks**: Ensure delivery tasks are running

### Scaling

For higher traffic:
1. Upgrade to PythonAnywhere paid plan
2. Consider migrating backend to Azure App Service
3. Add Redis for caching
4. Use a CDN for static assets

---

## Support

If you encounter issues:
1. Check the error logs
2. Review this documentation
3. Search for similar issues in the framework documentation
4. Contact support@pythonanywhere.com for hosting issues
