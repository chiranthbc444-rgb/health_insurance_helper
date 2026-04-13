import os
import sys

# Add the project directory to sys.path
sys.path.append(r'c:\U01MI23S0020\health_insurance_helper\health_insurance_helper')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insurance_project.settings')

import django
django.setup()

from django.core.files import File
from django.contrib.auth.models import User

from insurance_app.models import DocumentUpload

def seed_samples():
    # Get the first user
    user = User.objects.first()
    if not user:
        print("No user found in database. Please create a user first.")
        return

    print(f"Seeding samples for user: {user.username}")

    samples = [
        {
            'type': 'medical_bill',
            'path': r'C:\Users\chiranth\.gemini\antigravity\brain\5d9b4b20-3d85-4ebb-a8ad-4c82b6ea3a58\sample_medical_bill_1773376113804.png',
            'filename': 'sample_medical_bill.png'
        },
        {
            'type': 'policy',
            'path': r'C:\Users\chiranth\.gemini\antigravity\brain\5d9b4b20-3d85-4ebb-a8ad-4c82b6ea3a58\sample_policy_document_1773376133051.png',
            'filename': 'sample_premium_policy.png'
        }
    ]

    for sample in samples:
        if not os.path.exists(sample['path']):
            print(f"File not found: {sample['path']}")
            continue

        with open(sample['path'], 'rb') as f:
            doc = DocumentUpload.objects.create(
                user=user,
                document_type=sample['type'],
                file=File(f, name=sample['filename'])
            )
            print(f"Created DocumentUpload ID: {doc.id} for {sample['filename']}")

if __name__ == "__main__":
    seed_samples()
