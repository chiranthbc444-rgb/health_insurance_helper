import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insurance_project.settings')
django.setup()

from insurance_app.models import Policy, Claim, DocumentUpload
from django.contrib.auth.models import User

def check_data():
    user = User.objects.filter(is_superuser=False).first()
    if not user:
        print("No regular user found.")
        return

    print(f"Checking data for user: {user.username}")
    
    policies = Policy.objects.all()
    print("\nAvailable Policies:")
    for p in policies:
        print(f"- {p.name}: Coverage={p.coverage_amount}, Premium={p.premium}")

    claims = Claim.objects.filter(user=user)
    print(f"\nClaims for {user.username}:")
    for c in claims:
        print(f"- Policy: {c.policy.name}, Amount: {c.claim_amount}, Status: {c.status}")

    uploads = DocumentUpload.objects.filter(user=user)
    print(f"\nDocument Uploads for {user.username}:")
    for u in uploads:
        print(f"- {u.document_type}: {u.file.name}")

if __name__ == "__main__":
    check_data()
