from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Count, Avg
import logging
import json
from datetime import datetime, timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)

from .models import Policy, Claim, DocumentUpload, ChatMessage, UserProfile


def staff_required(view_func):
    """Decorator ensuring the user is staff (admin)."""
    return user_passes_test(lambda u: u.is_staff, login_url='login')(view_func)


def _ensure_profile(user):
    """Ensure user has a profile, create if missing."""
    try:
        return user.profile
    except UserProfile.DoesNotExist:
        return UserProfile.objects.create(user=user)


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
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        if password != password_confirm:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('register')

        user = User.objects.create_user(
            username=username, email=email, password=password,
            first_name=first_name, last_name=last_name
        )
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
    """Login portal for administrators."""
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
        messages.success(request, 'Thank you for your message! We will get back to you soon.')
        return redirect('contact')
    return render(request, 'insurance_app/contact.html')


@login_required(login_url='login')
def dashboard(request):
    """Enhanced user dashboard with data visualization"""
    if request.user.is_staff:
        return redirect('admin_dashboard')

    user = request.user
    profile = _ensure_profile(user)

    user_claims = Claim.objects.filter(user=user)
    approved_claims_total = sum(c.claim_amount for c in user_claims if c.status == 'Approved') or 0
    pending_claims_total = sum(c.claim_amount for c in user_claims if c.status == 'Pending') or 0
    denied_claims_total = sum(c.claim_amount for c in user_claims if c.status == 'Denied') or 0
    pending_claims_count = user_claims.filter(status='Pending').count()
    total_claimed = sum(c.claim_amount for c in user_claims) or 0

    active_policy = Policy.objects.filter(name__icontains='Premium').first()
    remaining_balance = 0
    monthly_premium = 0
    coverage_utilization = 0
    if active_policy:
        monthly_premium = active_policy.premium
        remaining_balance = active_policy.coverage_amount - approved_claims_total
        coverage_utilization = round((approved_claims_total / active_policy.coverage_amount) * 100, 1) if active_policy.coverage_amount > 0 else 0

    # Update risk score
    profile.calculate_risk_score()
    profile.save()

    # Claims by status (for doughnut chart)
    claims_chart_data = {
        'labels': ['Approved', 'Pending', 'Denied'],
        'data': [approved_claims_total, pending_claims_total, denied_claims_total],
        'colors': ['#10b981', '#f59e0b', '#ef4444'],
    }

    # Monthly claims data (last 6 months)
    monthly_data = []
    monthly_labels = []
    now = timezone.now()
    for i in range(5, -1, -1):
        month_start = (now - timedelta(days=i * 30)).replace(day=1, hour=0, minute=0, second=0)
        month_end = (month_start + timedelta(days=31)).replace(day=1)
        month_total = user_claims.filter(
            submitted_at__gte=month_start,
            submitted_at__lt=month_end
        ).aggregate(total=Sum('claim_amount'))['total'] or 0
        monthly_data.append(month_total)
        monthly_labels.append(month_start.strftime('%b'))

    documents_count = DocumentUpload.objects.filter(user=user).count()

    all_policies = Policy.objects.all()

    context = {
        'profile': profile,
        'policies': all_policies,
        'active_policy': active_policy,
        'claims': user_claims[:5],
        'all_claims': user_claims,
        'pending_claims': pending_claims_count,
        'total_claimed': total_claimed,
        'approved_claims_total': approved_claims_total,
        'pending_claims_total': pending_claims_total,
        'denied_claims_total': denied_claims_total,
        'remaining_balance': remaining_balance,
        'monthly_premium': monthly_premium,
        'coverage_utilization': coverage_utilization,
        'risk_score': profile.risk_score,
        'risk_category': profile.risk_category,
        'documents_count': documents_count,
        'claims_chart_labels': json.dumps(claims_chart_data['labels']),
        'claims_chart_data': json.dumps(claims_chart_data['data']),
        'claims_chart_colors': json.dumps(claims_chart_data['colors']),
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_data': json.dumps(monthly_data),
    }
    return render(request, 'insurance_app/dashboard_modern.html', context)


@login_required(login_url='login')
def profile(request):
    """Enhanced user profile with edit functionality"""
    user = request.user
    user_profile = _ensure_profile(user)

    if request.method == 'POST':
        # Update user fields
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()

        # Update profile fields
        user_profile.phone = request.POST.get('phone', '')
        user_profile.city = request.POST.get('city', '')
        user_profile.state = request.POST.get('state', '')
        user_profile.pincode = request.POST.get('pincode', '')
        user_profile.address = request.POST.get('address', '')
        user_profile.gender = request.POST.get('gender', '')
        user_profile.blood_group = request.POST.get('blood_group', '')
        user_profile.preferred_language = request.POST.get('preferred_language', 'en')
        user_profile.is_smoker = request.POST.get('is_smoker') == 'on'
        user_profile.has_diabetes = request.POST.get('has_diabetes') == 'on'
        user_profile.has_hypertension = request.POST.get('has_hypertension') == 'on'
        user_profile.has_heart_condition = request.POST.get('has_heart_condition') == 'on'
        user_profile.exercise_frequency = request.POST.get('exercise_frequency', 'Weekly')

        dob_str = request.POST.get('date_of_birth', '')
        if dob_str:
            try:
                from datetime import date
                user_profile.date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        bmi_str = request.POST.get('bmi', '')
        if bmi_str:
            try:
                user_profile.bmi = float(bmi_str)
            except ValueError:
                pass

        user_profile.calculate_risk_score()
        user_profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    user_claims = Claim.objects.filter(user=user).count()
    total_claimed = sum(c.claim_amount for c in Claim.objects.filter(user=user)) or 0
    user_profile.calculate_risk_score()
    user_profile.save()

    context = {
        'profile': user_profile,
        'user_claims': user_claims,
        'total_claimed': total_claimed,
        'risk_score': user_profile.risk_score,
        'risk_category': user_profile.risk_category,
    }
    return render(request, 'insurance_app/profile.html', context)


@login_required(login_url='login')
def risk_score_api(request):
    """API endpoint to calculate/update risk score"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            profile = _ensure_profile(request.user)

            # Update fields from form data
            profile.is_smoker = data.get('is_smoker', False)
            profile.has_diabetes = data.get('has_diabetes', False)
            profile.has_hypertension = data.get('has_hypertension', False)
            profile.has_heart_condition = data.get('has_heart_condition', False)
            profile.exercise_frequency = data.get('exercise_frequency', 'Weekly')
            bmi = data.get('bmi')
            if bmi:
                profile.bmi = float(bmi)
            dob = data.get('date_of_birth')
            if dob:
                from datetime import date
                profile.date_of_birth = datetime.strptime(dob, '%Y-%m-%d').date()

            score = profile.calculate_risk_score()
            profile.save()

            # Build recommendations
            recs = []
            if profile.is_smoker:
                recs.append('Quit smoking to significantly reduce health risk.')
            if profile.bmi and profile.bmi > 25:
                recs.append('Maintain a healthy BMI through diet and exercise.')
            if profile.exercise_frequency in ['Never', 'Rarely']:
                recs.append('Increase physical activity to at least 3×/week.')
            if profile.has_hypertension:
                recs.append('Monitor blood pressure regularly and follow medical advice.')
            if not recs:
                recs.append('Great! Keep up your healthy lifestyle habits.')

            return JsonResponse({
                'success': True,
                'risk_score': score,
                'risk_category': profile.risk_category,
                'recommendations': recs,
            })
        except Exception as e:
            logger.error(f"Risk score API error: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'POST required'})


@login_required(login_url='login')
def dashboard_chart_data(request):
    """API for dashboard chart data"""
    user = request.user
    user_claims = Claim.objects.filter(user=user)

    approved = sum(c.claim_amount for c in user_claims if c.status == 'Approved') or 0
    pending = sum(c.claim_amount for c in user_claims if c.status == 'Pending') or 0
    denied = sum(c.claim_amount for c in user_claims if c.status == 'Denied') or 0

    now = timezone.now()
    monthly_data = []
    monthly_labels = []
    for i in range(5, -1, -1):
        month_start = (now - timedelta(days=i * 30)).replace(day=1, hour=0, minute=0, second=0)
        month_end = (month_start + timedelta(days=31)).replace(day=1)
        month_total = user_claims.filter(
            submitted_at__gte=month_start,
            submitted_at__lt=month_end
        ).aggregate(total=Sum('claim_amount'))['total'] or 0
        monthly_data.append(month_total)
        monthly_labels.append(month_start.strftime('%b %Y'))

    return JsonResponse({
        'doughnut': {'labels': ['Approved', 'Pending', 'Denied'], 'data': [approved, pending, denied]},
        'line': {'labels': monthly_labels, 'data': monthly_data},
    })


def set_language(request):
    """Set user preferred language"""
    if request.method == 'POST':
        lang = request.POST.get('language', 'en')
        if request.user.is_authenticated:
            try:
                profile = _ensure_profile(request.user)
                profile.preferred_language = lang
                profile.save()
            except Exception:
                pass
        request.session['language'] = lang
        next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
        return redirect(next_url)
    return redirect('home')


# --- admin views ---
@staff_required
def admin_dashboard(request):
    """Stats page for staff users"""
    policies_count = Policy.objects.count()
    claims_count = Claim.objects.count()
    pending_count = Claim.objects.filter(status='Pending').count()
    users_count = User.objects.count()
    approved_total = Claim.objects.filter(status='Approved').aggregate(total=Sum('claim_amount'))['total'] or 0
    context = {
        'policies_count': policies_count,
        'claims_count': claims_count,
        'pending_count': pending_count,
        'users_count': users_count,
        'approved_total': approved_total,
    }
    return render(request, 'insurance_app/admin_dashboard.html', context)


@staff_required
def admin_claim_list(request):
    claims = Claim.objects.all().order_by('-id')
    return render(request, 'insurance_app/admin_claim_list.html', {'claims': claims})


@staff_required
def admin_claim_detail(request, claim_id):
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
    users = User.objects.all().order_by('username')
    return render(request, 'insurance_app/admin_user_list.html', {'users': users})


def policy_list(request):
    policies = Policy.objects.all()
    return render(request, 'insurance_app/policy_list_modern.html', {'policies': policies})


@login_required(login_url='login')
def policy_detail(request, policy_id):
    policy = get_object_or_404(Policy, id=policy_id)
    return render(request, 'insurance_app/policy_detail.html', {'policy': policy})


@login_required(login_url='login')
def claim_list(request):
    claims = Claim.objects.filter(user=request.user)
    return render(request, 'insurance_app/claim_list.html', {'claims': claims})


@login_required(login_url='login')
def claim_detail(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id, user=request.user)
    return render(request, 'insurance_app/claim_detail.html', {'claim': claim})


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def submit_claim(request):
    if request.method == 'POST':
        policy_id = request.POST.get('policy')
        claim_amount = request.POST.get('claim_amount')
        description = request.POST.get('description', '')

        try:
            policy = Policy.objects.get(id=policy_id)
            claim = Claim.objects.create(
                user=request.user,
                policy=policy,
                claim_amount=claim_amount,
                description=description,
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


# --- AI Chatbot and Document Upload Views ---

@login_required(login_url='login')
def chatbot_view(request):
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
    if request.method == 'POST' and request.FILES.get('document'):
        document_file = request.FILES['document']
        document_type = request.POST.get('document_type', 'other')
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json'

        if document_file.size > settings.MAX_UPLOAD_SIZE:
            error_msg = 'File size too large. Maximum size is 10MB.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
            return redirect('chatbot')

        if document_file.content_type not in settings.ALLOWED_UPLOAD_TYPES:
            error_msg = 'Invalid file type. Only PDF, JPG, PNG files are allowed.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
            return redirect('chatbot')

        try:
            document = DocumentUpload.objects.create(
                user=request.user,
                document_type=document_type,
                file=document_file
            )

            from .ai_service import AIService
            ai_service = AIService()
            analysis = ai_service.process_document_upload(document)
            response_message = ai_service.create_claim_eligibility_message(analysis)

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
                analysis['document_id'] = document.id
                return JsonResponse({'success': True, 'response': response_message, 'analysis': analysis})

            messages.success(request, 'Document uploaded and analyzed successfully!')

        except Exception as e:
            logger.error(f"Document upload failed: {e}")
            error_msg = 'Failed to process document. Please try again.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)

    return redirect('chatbot')


@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            session_id = data.get('session_id', '')
            user = request.user if request.user.is_authenticated else None

            from .ai_service import AIService
            ai_service = AIService()

            context = {}
            if user:
                recent_claims = Claim.objects.filter(user=user).order_by('-id')[:3]
                context = {
                    'user_claims': len(recent_claims),
                    'pending_claims': sum(1 for c in recent_claims if c.status == 'Pending')
                }

            bot_response = ai_service.generate_chatbot_response(user_message, context)

            if user:
                ChatMessage.objects.create(user=user, message_type='user', content=user_message)
                ChatMessage.objects.create(user=user, message_type='bot', content=bot_response)
            else:
                ChatMessage.objects.create(session_id=session_id, message_type='user', content=user_message)
                ChatMessage.objects.create(session_id=session_id, message_type='bot', content=bot_response)

            return JsonResponse({'success': True, 'response': bot_response})

        except Exception as e:
            logger.error(f"Chatbot API error: {e}")
            return JsonResponse({'success': False, 'response': 'Sorry, I encountered an error. Please try again.'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required(login_url='login')
def document_list(request):
    documents = DocumentUpload.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'insurance_app/document_list.html', {'documents': documents})


@login_required(login_url='login')
def chat_history(request):
    chat_messages = ChatMessage.objects.filter(user=request.user).order_by('-timestamp')[:50]
    return render(request, 'insurance_app/chat_history.html', {'messages': chat_messages})


@login_required(login_url='login')
def compare_documents(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            bill_id = data.get('bill_id')
            policy_id = data.get('policy_id')

            bill = get_object_or_404(DocumentUpload, id=bill_id, user=request.user)
            policy = get_object_or_404(DocumentUpload, id=policy_id, user=request.user)

            from .ai_service import AIService
            ai_service = AIService()

            bill_text = ai_service.extract_document_text(bill)
            policy_text = ai_service.extract_document_text(policy)
            analysis = ai_service.analyze_document_comparison(bill_text, policy_text)
            response_message = ai_service.create_comparison_message(analysis)

            ChatMessage.objects.create(
                user=request.user,
                message_type='bot',
                content=response_message,
                ai_response=analysis
            )

            return JsonResponse({'success': True, 'response': response_message, 'analysis': analysis})

        except Exception as e:
            logger.error(f"Comparison view failed: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})
