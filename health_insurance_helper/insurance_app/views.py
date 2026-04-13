from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

from .models import Policy, Claim, DocumentUpload, ChatMessage


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
    return render(request, 'insurance_app/home_modern.html', context)


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
    
    return render(request, 'insurance_app/register_modern.html')


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
    
    return render(request, 'insurance_app/login_modern.html')


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


def premium_calculator(request):
    """Premium calculator page"""
    return render(request, 'insurance_app/premium_calculator.html')


def contact(request):
    """Contact page"""
    if request.method == 'POST':
        # Handle contact form submission
        messages.success(request, 'Thank you for your message! We will get back to you soon.')
        return redirect('contact')
    return render(request, 'insurance_app/contact.html')


@login_required(login_url='login')
def dashboard(request):
    """User dashboard view"""
    # if a staff member stumbles here, send them to admin dashboard
    if request.user.is_staff:
        return redirect('admin_dashboard')

    user_policies = Policy.objects.all()
    # For this demo, we assume the user has the 'Premium Health Plan' 
    # In a real app, this would be linked via a UserPolicy model
    active_policy = Policy.objects.filter(name__icontains='Premium').first()
    
    user_claims = Claim.objects.filter(user=request.user)
    approved_claims_total = sum([claim.claim_amount for claim in user_claims if claim.status == 'Approved']) or 0
    pending_claims = Claim.objects.filter(user=request.user, status='Pending').count()
    total_claimed = sum([claim.claim_amount for claim in user_claims]) or 0
    
    # Calculate Remaining Balance
    remaining_balance = 0
    monthly_premium = 0
    if active_policy:
        monthly_premium = active_policy.premium
        remaining_balance = active_policy.coverage_amount - approved_claims_total - monthly_premium

    context = {
        'policies': user_policies,
        'active_policy': active_policy,
        'claims': user_claims,
        'pending_claims': pending_claims,
        'total_claimed': total_claimed,
        'approved_claims_total': approved_claims_total,
        'remaining_balance': remaining_balance,
        'monthly_premium': monthly_premium,
    }
    return render(request, 'insurance_app/dashboard_modern.html', context)


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



def policy_list(request):
    """List all available policies"""
    policies = Policy.objects.all()
    return render(request, 'insurance_app/policy_list_modern.html', {'policies': policies})


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


# --- AI Chatbot and Document Upload Views ---

@login_required(login_url='login')
def chatbot_view(request):
    """Main chatbot interface"""
    all_docs = DocumentUpload.objects.filter(user=request.user).order_by('-uploaded_at')
    bills = [d for d in all_docs if d.document_type in ['medical_bill', 'prescription']]
    policies = [d for d in all_docs if d.document_type == 'policy']
    return render(request, 'insurance_app/chatbot.html', {
        'user_documents': all_docs,
        'bills': bills,
        'policies': policies
    })


@login_required(login_url='login')
def upload_document(request):
    """Handle document upload"""
    if request.method == 'POST' and request.FILES.get('document'):
        document_file = request.FILES['document']
        document_type = request.POST.get('document_type', 'other')
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json'

        # Validate file size
        if document_file.size > settings.MAX_UPLOAD_SIZE:
            error_msg = 'File size too large. Maximum size is 10MB.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
            return redirect('chatbot')

        # Validate file type
        if document_file.content_type not in settings.ALLOWED_UPLOAD_TYPES:
            error_msg = 'Invalid file type. Only PDF, JPG, PNG files are allowed.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
            return redirect('chatbot')

        try:
            # Create document upload record
            document = DocumentUpload.objects.create(
                user=request.user,
                document_type=document_type,
                file=document_file
            )

            # Process document with AI
            from .ai_service import AIService
            ai_service = AIService()
            analysis = ai_service.process_document_upload(document)

            # Create AI response message
            response_message = ai_service.create_claim_eligibility_message(analysis)

            # Save chat messages
            ChatMessage.objects.create(
                user=request.user,
                message_type='user',
                content=f"Uploaded {document_type} document: {document_file.name}",
                document=document
            )

            ChatMessage.objects.create(
                user=request.user,
                message_type='bot',
                content=response_message,
                ai_response=analysis
            )

            if is_ajax:
                # Add document ID to analysis for frontend update
                analysis['document_id'] = document.id
                return JsonResponse({
                    'success': True,
                    'response': response_message,
                    'analysis': analysis
                })

            messages.success(request, 'Document uploaded and analyzed successfully!')

        except Exception as e:
            logger.error(f"Document upload failed: {e}")
            error_msg = 'Failed to process document. Please try again.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)

    return redirect('chatbot')


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def chatbot_api(request):
    """API endpoint for chatbot interactions"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            session_id = data.get('session_id', '')
            user = request.user if request.user.is_authenticated else None

            # Get AI service
            from .ai_service import AIService
            ai_service = AIService()

            # Generate response
            context = {}
            if user:
                # Add user context for personalized responses
                recent_claims = Claim.objects.filter(user=user).order_by('-id')[:3]
                context = {
                    'user_claims': len(recent_claims),
                    'pending_claims': sum(1 for c in recent_claims if c.status == 'Pending')
                }

            bot_response = ai_service.generate_chatbot_response(user_message, context)

            # Save chat messages
            if user:
                ChatMessage.objects.create(
                    user=user,
                    message_type='user',
                    content=user_message
                )
                ChatMessage.objects.create(
                    user=user,
                    message_type='bot',
                    content=bot_response
                )
            else:
                # Handle anonymous users with session_id
                ChatMessage.objects.create(
                    session_id=session_id,
                    message_type='user',
                    content=user_message
                )
                ChatMessage.objects.create(
                    session_id=session_id,
                    message_type='bot',
                    content=bot_response
                )

            return JsonResponse({
                'success': True,
                'response': bot_response
            })

        except Exception as e:
            logger.error(f"Chatbot API error: {e}")
            return JsonResponse({
                'success': False,
                'response': 'Sorry, I encountered an error. Please try again.'
            })

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required(login_url='login')
def document_list(request):
    """List user's uploaded documents"""
    documents = DocumentUpload.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'insurance_app/document_list.html', {'documents': documents})


@login_required(login_url='login')
def chat_history(request):
    """View chat history"""
    messages = ChatMessage.objects.filter(user=request.user).order_by('-timestamp')[:50]
    return render(request, 'insurance_app/chat_history.html', {'messages': messages})
@login_required(login_url='login')
def compare_documents(request):
    """Handle comparison of two documents (typically a bill and a policy)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            bill_id = data.get('bill_id')
            policy_id = data.get('policy_id')
            
            bill = get_object_or_404(DocumentUpload, id=bill_id, user=request.user)
            policy = get_object_or_404(DocumentUpload, id=policy_id, user=request.user)
            
            # Extract text
            from .ai_service import AIService
            ai_service = AIService()
            
            bill_text = ai_service.extract_document_text(bill)
            policy_text = ai_service.extract_document_text(policy)
            
            # Run comparison
            analysis = ai_service.analyze_document_comparison(bill_text, policy_text)
            
            # Create AI response message
            response_message = ai_service.create_comparison_message(analysis)
            
            # Save to chat history
            ChatMessage.objects.create(
                user=request.user,
                message_type='bot',
                content=response_message,
                ai_response=analysis
            )
            
            return JsonResponse({
                'success': True,
                'response': response_message,
                'analysis': analysis
            })
            
        except Exception as e:
            logger.error(f"Comparison view failed: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
            
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
