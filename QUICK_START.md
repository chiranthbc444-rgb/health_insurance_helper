# Quick Start Guide

## 🚀 Running the Application

### Option 1: Using Batch File (Windows)
Simply double-click `start_server.bat` from the project root directory.

### Option 2: Using PowerShell (Windows)
```powershell
# Run in PowerShell
.\start_server.ps1
```

### Option 3: Manual Start (All Platforms)

**Windows (PowerShell):**
```powershell
cd health_insurance_helper
..\env\Scripts\Activate.ps1
python manage.py runserver
```

**Windows (Command Prompt):**
```cmd
cd health_insurance_helper
..\env\Scripts\activate.bat
python manage.py runserver
```

**macOS/Linux:**
```bash
cd health_insurance_helper
source ../env/bin/activate
python manage.py runserver
```

## 🌐 Access Points

Once the server is running:

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:8000/ | Home page |
| http://127.0.0.1:8000/register/ | User registration |
| http://127.0.0.1:8000/login/ | User login |
| http://127.0.0.1:8000/dashboard/ | User dashboard |
| http://127.0.0.1:8000/policies/ | Browse policies |
| http://127.0.0.1:8000/claims/ | View your claims |
| http://127.0.0.1:8000/admin/ | Admin panel |

## 📋 Test Account Setup

1. **Create Admin Account:**
   ```bash
   python manage.py createsuperuser
   ```
   Follow prompts and remember your credentials

2. **Login to Admin:**
   - Go to http://127.0.0.1:8000/admin/
   - Use your superuser credentials

3. **Create Test User:**
   - Go to http://127.0.0.1:8000/register/
   - Fill in the registration form
   - Login with the new account

## 🐛 Debugging & Logs

If you encounter issues:

1. Check the terminal output for error messages
2. Run `python manage.py check` to validate setup
3. Check `db.sqlite3` exists in the project directory
4. Ensure no other application is using port 8000

## 📚 View Full Documentation

Read `PROJECT_GUIDE.md` for:
- Complete feature list
- Database model descriptions
- All available URLs
- Admin instructions
- Troubleshooting guide

## 🛑 Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

---

**Happy Insurance Managing!** 🏥
