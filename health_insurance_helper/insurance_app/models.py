# Create your models here.
from django.db import models
from django.contrib.auth.models import User

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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    claim_amount = models.IntegerField()
    status = models.CharField(max_length=50, default='Pending')

    def __str__(self):
        return f"{self.user.username} - {self.policy.name}"