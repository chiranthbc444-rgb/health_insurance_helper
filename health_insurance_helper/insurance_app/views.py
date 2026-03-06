from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Policy, Claim


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
    """User login view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
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


@login_required(login_url='login')
def dashboard(request):
    """User dashboard view"""
    user_policies = Policy.objects.all()
    user_claims = Claim.objects.filter(user=request.user)
    context = {
        'policies': user_policies,
        'claims': user_claims,
    }
    return render(request, 'insurance_app/dashboard.html', context)


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
