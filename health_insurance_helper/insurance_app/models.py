from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import os


class Policy(models.Model):
    POLICY_TYPES = [
        ('Basic', 'Basic'),
        ('Premium', 'Premium'),
        ('Family', 'Family'),
    ]

    name = models.CharField(max_length=100)
    policy_type = models.CharField(max_length=50, choices=POLICY_TYPES)
    coverage_amount = models.IntegerField()
    premium = models.IntegerField()

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """Extended user profile with health risk score and preferences"""
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]
    LANGUAGE_CHOICES = [
        ('en', 'English'), ('hi', 'Hindi'), ('kn', 'Kannada'),
        ('ta', 'Tamil'), ('te', 'Telugu'), ('mr', 'Marathi'),
        ('es', 'Spanish'), ('fr', 'French'), ('de', 'German'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    avatar_color = models.CharField(max_length=7, default='#3b82f6')
    preferred_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')

    # Health risk factors
    is_smoker = models.BooleanField(default=False)
    has_diabetes = models.BooleanField(default=False)
    has_hypertension = models.BooleanField(default=False)
    has_heart_condition = models.BooleanField(default=False)
    bmi = models.FloatField(null=True, blank=True)
    exercise_frequency = models.CharField(
        max_length=20,
        choices=[('Never', 'Never'), ('Rarely', 'Rarely'), ('Weekly', 'Weekly'), ('Daily', 'Daily')],
        default='Weekly'
    )

    # Risk score cached value (0-100)
    risk_score = models.FloatField(default=0)
    risk_category = models.CharField(max_length=20, default='Low')  # Low, Medium, High, Critical

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_risk_score(self):
        score = 0

        # Age factor
        if self.date_of_birth:
            from datetime import date
            age = (date.today() - self.date_of_birth).days // 365
            if age < 25:
                score += 5
            elif age < 35:
                score += 10
            elif age < 45:
                score += 20
            elif age < 55:
                score += 35
            elif age < 65:
                score += 50
            else:
                score += 65

        # Smoking
        if self.is_smoker:
            score += 20

        # Chronic conditions
        if self.has_diabetes:
            score += 15
        if self.has_hypertension:
            score += 12
        if self.has_heart_condition:
            score += 18

        # BMI
        if self.bmi:
            if self.bmi < 18.5:
                score += 8
            elif self.bmi > 30:
                score += 15
            elif self.bmi > 25:
                score += 8

        # Exercise
        exercise_bonus = {'Never': 10, 'Rarely': 5, 'Weekly': 0, 'Daily': -5}
        score += exercise_bonus.get(self.exercise_frequency, 0)

        # Claim history factor
        from .models import Claim
        claim_count = Claim.objects.filter(user=self.user).count()
        score += min(claim_count * 3, 20)

        # Normalize to 0-100
        score = max(0, min(100, score))
        self.risk_score = round(score, 1)

        if score < 25:
            self.risk_category = 'Low'
        elif score < 50:
            self.risk_category = 'Medium'
        elif score < 75:
            self.risk_category = 'High'
        else:
            self.risk_category = 'Critical'

        return self.risk_score

    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)


class Claim(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Denied', 'Denied'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    claim_amount = models.IntegerField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    description = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.policy.name} ({self.status})"

    class Meta:
        ordering = ['-id']


def document_upload_path(instance, filename):
    """Generate upload path for documents"""
    return f'documents/{instance.user.username}/{filename}'


class DocumentUpload(models.Model):
    DOCUMENT_TYPES = [
        ('policy', 'Insurance Policy'),
        ('claim_form', 'Claim Form'),
        ('medical_bill', 'Medical Bill'),
        ('prescription', 'Prescription'),
        ('id_proof', 'ID Proof'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to=document_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.PositiveIntegerField(blank=True, null=True)
    content_type = models.CharField(max_length=100, blank=True)
    extracted_text = models.TextField(blank=True, null=True)
    ai_analysis = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.document_type} - {self.file.name}"

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            if hasattr(self.file, 'file') and hasattr(self.file.file, 'content_type'):
                self.content_type = self.file.file.content_type
            elif hasattr(self.file, 'content_type'):
                self.content_type = self.file.content_type
            else:
                self.content_type = ''
        super().save(*args, **kwargs)

    def get_file_extension(self):
        return os.path.splitext(self.file.name)[1].lower()

    class Meta:
        ordering = ['-uploaded_at']


class ChatMessage(models.Model):
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('bot', 'Bot Response'),
        ('system', 'System Message'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    document = models.ForeignKey(DocumentUpload, on_delete=models.SET_NULL, null=True, blank=True)
    ai_response = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."

    class Meta:
        ordering = ['timestamp']