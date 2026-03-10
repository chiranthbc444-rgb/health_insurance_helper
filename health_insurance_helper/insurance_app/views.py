from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Policy, Claim


def staff_required(view_func):
    """Decorator ensuring the user is staff (admin)."""
    return user_passes_test(lambda u: u.is_staff, login_url='login')(view_func)


def home(request):
    """Home page view"""
    policies_count = Policy.objects.count()
    claims_count = Claim.objects.count()
    users_count = User.objects.count()
    context = {
        'policies_count': policies_count,
        'claims_count': claims_count,
        'users_count': users_count,
    }
    return render(request, 'insurance_app/home.html', context)


def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('register')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login')
    
    return render(request, 'insurance_app/register.html')


def login_view(request):
    """Login view for regular users only"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_staff:
                # staff must use the admin portal
                messages.error(request, 'Staff must login via the admin portal.')
                return redirect('admin_login')
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password!')
    
    return render(request, 'insurance_app/login.html')


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('home')


def admin_login(request):
    """Login portal for administrators (staff users)."""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_staff:
                messages.error(request, 'Only staff members may use this portal.')
                return redirect('login')
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid username or password!')
    
    return render(request, 'insurance_app/admin_login.html')


@login_required(login_url='login')
def dashboard(request):
    """User dashboard view"""
    # if a staff member stumbles here, send them to admin dashboard
    if request.user.is_staff:
        return redirect('admin_dashboard')

    user_policies = Policy.objects.all()
    user_claims = Claim.objects.filter(user=request.user)
    context = {
        'policies': user_policies,
        'claims': user_claims,
    }
    return render(request, 'insurance_app/dashboard.html', context)


# --- admin views ---
@staff_required
def admin_dashboard(request):
    """Simple stats page for staff users"""
    policies_count = Policy.objects.count()
    claims_count = Claim.objects.count()
    pending_count = Claim.objects.filter(status='Pending').count()
    users_count = User.objects.count()
    context = {
        'policies_count': policies_count,
        'claims_count': claims_count,
        'pending_count': pending_count,
        'users_count': users_count,
    }
    return render(request, 'insurance_app/admin_dashboard.html', context)


@staff_required
def admin_claim_list(request):
    """List all claims for admin"""
    claims = Claim.objects.all().order_by('-id')
    return render(request, 'insurance_app/admin_claim_list.html', {'claims': claims})


@staff_required
def admin_claim_detail(request, claim_id):
    """View and update a claim as admin"""
    claim = get_object_or_404(Claim, id=claim_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            claim.status = 'Approved'
            messages.success(request, 'Claim approved.')
        elif action == 'deny':
            claim.status = 'Denied'
            messages.success(request, 'Claim denied.')
        claim.save()
        return redirect('admin_claim_detail', claim_id=claim.id)
    return render(request, 'insurance_app/admin_claim_detail.html', {'claim': claim})


@staff_required
def admin_user_list(request):
    """List all users for admin"""
    users = User.objects.all().order_by('username')
    return render(request, 'insurance_app/admin_user_list.html', {'users': users})


@login_required(login_url='login')
def policy_list(request):
    """List all available policies"""
    policies = Policy.objects.all()
    return render(request, 'insurance_app/policy_list.html', {'policies': policies})


@login_required(login_url='login')
def policy_detail(request, policy_id):
    """Display policy details"""
    policy = get_object_or_404(Policy, id=policy_id)
    return render(request, 'insurance_app/policy_detail.html', {'policy': policy})


@login_required(login_url='login')
def claim_list(request):
    """List user's claims"""
    claims = Claim.objects.filter(user=request.user)
    return render(request, 'insurance_app/claim_list.html', {'claims': claims})


@login_required(login_url='login')
def claim_detail(request, claim_id):
    """Display claim details"""
    claim = get_object_or_404(Claim, id=claim_id, user=request.user)
    return render(request, 'insurance_app/claim_detail.html', {'claim': claim})


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def submit_claim(request):
    """Submit a new claim"""
    if request.method == 'POST':
        policy_id = request.POST.get('policy')
        claim_amount = request.POST.get('claim_amount')
        
        try:
            policy = Policy.objects.get(id=policy_id)
            claim = Claim.objects.create(
                user=request.user,
                policy=policy,
                claim_amount=claim_amount,
                status='Pending'
            )
            messages.success(request, 'Claim submitted successfully!')
            return redirect('claim_detail', claim_id=claim.id)
        except Policy.DoesNotExist:
            messages.error(request, 'Invalid policy selected!')
        except Exception as e:
            messages.error(request, f'Error submitting claim: {str(e)}')
    
    policies = Policy.objects.all()
    return render(request, 'insurance_app/submit_claim.html', {'policies': policies})


@login_required(login_url='login')
def profile(request):
    """User profile view"""
    user_claims = Claim.objects.filter(user=request.user).count()
    total_claimed = sum([claim.claim_amount for claim in Claim.objects.filter(user=request.user)])
    
    context = {
        'user_claims': user_claims,
        'total_claimed': total_claimed,
    }
    return render(request, 'insurance_app/profile.html', context)
