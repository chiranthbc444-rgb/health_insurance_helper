import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insurance_project.settings')
django.setup()

from insurance_app.models import Policy, Claim
from django.contrib.auth.models import User

def execute_balance():
    user = User.objects.filter(is_superuser=False).first()
    if not user:
        print("No user found.")
        return

    policy = Policy.objects.filter(name__icontains='Premium').first()
    if not policy:
        print("No Premium policy found.")
        return

    # Reset claims to just the one from the demo for a clean balance report
    Claim.objects.filter(user=user).delete()
    
    claim = Claim.objects.create(
        user=user,
        policy=policy,
        claim_amount=75000,
        status='Approved'
    )

    monthly_premium = policy.premium
    initial_coverage = policy.coverage_amount
    total_approved_claims = claim.claim_amount
    
    remaining_balance = initial_coverage - total_approved_claims - monthly_premium

    print("--- Financial Summary ---")
    print(f"User: {user.username}")
    print(f"Plan: {policy.name}")
    print(f"Status: Monthly Withdrawal Executed")
    print(f"Initial Coverage: Rs. {initial_coverage:,}")
    print(f"Monthly Premium Deducted: Rs. {monthly_premium:,}")
    print(f"Approved Claim (City Hospital): Rs. {total_approved_claims:,}")
    print(f"-------------------------")
    print(f"Final Remaining Balance: Rs. {remaining_balance:,}")
    print("-------------------------")

if __name__ == "__main__":
    execute_balance()
