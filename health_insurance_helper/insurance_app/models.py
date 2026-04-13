# Create your models here.
from django.db import models
from django.contrib.auth.models import User
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

    def __str__(self):
        return f"{self.user.username} - {self.policy.name} ({self.status})"


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
    ai_analysis = models.JSONField(blank=True, null=True)  # Store AI analysis results

    def __str__(self):
        return f"{self.user.username} - {self.document_type} - {self.file.name}"

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            # some UploadedFile objects may not expose content_type through file attribute
            if hasattr(self.file, 'file') and hasattr(self.file.file, 'content_type'):
                self.content_type = self.file.file.content_type
            elif hasattr(self.file, 'content_type'):
                self.content_type = self.file.content_type
            else:
                self.content_type = ''
        super().save(*args, **kwargs)

    def get_file_extension(self):
        """Get file extension"""
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
    session_id = models.CharField(max_length=100, blank=True)  # For anonymous users
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    document = models.ForeignKey(DocumentUpload, on_delete=models.SET_NULL, null=True, blank=True)
    ai_response = models.JSONField(blank=True, null=True)  # Store AI analysis if applicable

    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."

    class Meta:
        ordering = ['timestamp']