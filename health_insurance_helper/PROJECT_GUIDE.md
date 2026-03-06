# Health Insurance Helper - Complete Project Guide

## Project Overview
This is a full-featured Django web application for managing health insurance policies and claims. Users can register, browse policies, and submit claims with a clean, modern interface.

---

## Project Structure

```
health_insurance_helper/
├── manage.py                 # Django management script
├── db.sqlite3               # SQLite database
├── insurance_project/       # Project configuration
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py              # URL routing
│   ├── asgi.py
│   └── wsgi.py
├── insurance_app/           # Main application
│   ├── models.py            # Data models (Policy, Claim)
│   ├── views.py             # View functions
│   ├── admin.py             # Admin configuration
│   ├── urls.py              # App URL patterns
│   ├── apps.py
│   ├── tests.py
│   ├── migrations/          # Database migrations
│   └── templates/           # HTML templates
│       └── insurance_app/
│           ├── base.html
│           ├── home.html
│           ├── register.html
│           ├── login.html
│           ├── dashboard.html
│           ├── policy_list.html
│           ├── policy_detail.html
│           ├── claim_list.html
│           ├── claim_detail.html
│           ├── submit_claim.html
│           └── profile.html
└── env/                     # Virtual environment
```

---

## Features Implemented

### ✅ User Management
- User registration with validation
- Login/Logout functionality
- User profile page
- Authentication decorators on protected views

### ✅ Policy Management
- View all available insurance policies
- Display policy details with coverage information
- Policy types: Basic, Premium, Family
- Admin interface to manage policies

### ✅ Claim Management
- Submit insurance claims
- View claim history
- Track claim status (Pending, Approved, Rejected)
- View detailed claim information
- Admin interface to manage and update claims

### ✅ Frontend
- Responsive modern UI with gradient design
- Beautiful card-based layouts
- Status badges for claims
- Navigation system
- Message alerts for user feedback

---

## Getting Started

### 1. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
cd C:\U01MI23S0020\health_insurance_helper\health_insurance_helper
..\env\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
..\env\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source ../env/bin/activate
```

### 2. Run Database Migrations (if needed)

```bash
python manage.py migrate
```

### 3. Create Superuser for Admin Access

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account. We recommend:
- Username: `admin`
- Email: `admin@example.com`
- Password: (your choice)

### 4. Add Sample Data (Optional)

Sample policies have already been added:
- **Basic Health Plan**: $100,000 coverage, $150/month
- **Premium Health Plan**: $500,000 coverage, $300/month
- **Family Health Plan**: $1,000,000 coverage, $500/month

To add more policies through the admin panel:
1. Go to `http://127.0.0.1:8000/admin/`
2. Login with your superuser credentials
3. Click "Policies" and add new policies

### 5. Start Development Server

```bash
python manage.py runserver
```

The application will be available at: **http://127.0.0.1:8000/**

---

## Using the Application

### For Regular Users

1. **Register**: Click "Register" on the home page
   - Enter username, email, and password
   - Password confirmation is required

2. **Login**: Click "Login" and enter your credentials

3. **View Dashboard**: After login, you'll see an overview of:
   - Available policies
   - Your submitted claims
   - Quick action buttons

4. **Browse Policies**: Click "View All Policies" to:
   - See all available insurance plans
   - Click on a policy for detailed information
   - Understand coverage and premium costs

5. **Submit a Claim**:
   - Click "Submit New Claim" from dashboard
   - Select a policy from the dropdown
   - Enter the claim amount
   - Submit the form
   - Your claim will appear in "My Claims" with "Pending" status

6. **Track Claims**: 
   - View your claim history
   - Click on a claim to see detailed information
   - Check the status (Pending, Approved, or Rejected)

7. **View Profile**: See your account information and claim statistics

### For Administrators

1. **Access Admin Panel**: Go to `http://127.0.0.1:8000/admin/`

2. **Manage Policies**:
   - Add new insurance policies
   - Edit existing policies
   - Delete policies
   - View all policies at a glance

3. **Manage Claims**:
   - View all submitted claims
   - Update claim status (Pending → Approved/Rejected)
   - Filter claims by status or policy
   - Search for specific claims

4. **Manage Users**:
   - View registered users
   - Manage user accounts
   - Assign admin privileges

---

## Database Models

### Policy Model
```python
- name: CharField (Policy name)
- policy_type: CharField (Basic, Premium, Family)
- coverage_amount: IntegerField (Coverage limit in dollars)
- premium: IntegerField (Monthly premium in dollars)
```

### Claim Model
```python
- user: ForeignKey (Link to User)
- policy: ForeignKey (Link to Policy)
- claim_amount: IntegerField (Claimed amount in dollars)
- status: CharField (Pending, Approved, Rejected)
```

---

## URLs and Routes

| URL | View | Purpose |
|-----|------|---------|
| `/` | home | Home page |
| `/register/` | register | User registration |
| `/login/` | login_view | User login |
| `/logout/` | logout_view | User logout |
| `/dashboard/` | dashboard | User dashboard (protected) |
| `/profile/` | profile | User profile (protected) |
| `/policies/` | policy_list | List all policies (protected) |
| `/policies/<id>/` | policy_detail | Policy details (protected) |
| `/claims/` | claim_list | List user claims (protected) |
| `/claims/<id>/` | claim_detail | Claim details (protected) |
| `/claims/submit/` | submit_claim | Submit claim form (protected) |
| `/admin/` | Django admin | Admin panel |

---

## Common Issues & Solutions

### Issue: Server won't start
**Solution**: 
- Ensure virtual environment is activated
- Check if port 8000 is available
- Try running with a different port: `python manage.py runserver 8001`

### Issue: Templates not found
**Solution**: 
- Templates are automatically discovered in `insurance_app/templates/`
- Ensure folder structure is: `insurance_app/templates/insurance_app/`

### Issue: Database errors
**Solution**:
- Run migrations: `python manage.py migrate`
- Delete `db.sqlite3` and re-run migrations if corrupted

### Issue: Admin login fails
**Solution**:
- Create a new superuser: `python manage.py createsuperuser`
- Ensure you're using the correct credentials

---

## Development Commands

```bash
# Activate virtual environment
cd health_insurance_helper && ..\env\Scripts\activate.ps1

# Run migrations
python manage.py migrate

# Create new migrations
python manage.py makemigrations

# Start development server
python manage.py runserver

# Open Django shell for testing
python manage.py shell

# Run tests
python manage.py test

# Collect static files (for production)
python manage.py collectstatic

# Check for errors
python manage.py check

# Create superuser
python manage.py createsuperuser
```

---

## Sample Test Data

When first setting up, test with these credentials:

**Admin Account:**
- Username: `admin`
- Password: (whatever you set during `createsuperuser`)

**Test Flow:**
1. Create a new user account via registration
2. Login with the new account
3. Go to "Policies" to view available policies
4. Submit a claim for one of the policies
5. Visit "My Claims" to see your submitted claim
6. Logout and login as admin to approve/reject the claim

---

## Features You Can Add

- Payment integration
- Email notifications for claim status
- Policy recommendations based on user profile
- Claim tracking with timeline
- Document upload for claims
- Premium calculator
- Policy comparison tool
- Live chat support
- Mobile app

---

## Security Notes

⚠️ **Important for Production:**
- Change `SECRET_KEY` in `settings.py`
- Set `DEBUG = False` in production
- Configure `ALLOWED_HOSTS` properly
- Use environment variables for sensitive data
- Set up HTTPS
- Use PostgreSQL instead of SQLite
- Implement proper authentication (JWT, OAuth)
- Add CSRF protection
- Implement rate limiting

---

## Support & Resources

- Django Documentation: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- Python Documentation: https://docs.python.org/

---

## Project Status

✅ **Completed**
- User authentication system
- Policy management
- Claim submission and tracking
- Admin interface
- Responsive UI
- Form validation
- Message notifications
- Database design

🎯 **Next Steps (Optional)**
- Add more claim statuses
- Implement claim history timeline
- Add policy filters/search
- Create API endpoints
- Add more sophisticated validation
- Implement payment processing

---

## License

This project is created for educational purposes.

---

**Last Updated**: March 6, 2026  
**Version**: 1.0
