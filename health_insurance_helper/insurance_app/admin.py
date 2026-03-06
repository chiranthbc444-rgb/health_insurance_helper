from django.contrib import admin
from .models import Policy, Claim


class PolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'policy_type', 'coverage_amount', 'premium']
    list_filter = ['policy_type']
    search_fields = ['name']


class ClaimAdmin(admin.ModelAdmin):
    list_display = ['user', 'policy', 'claim_amount', 'status']
    list_filter = ['status', 'policy']
    search_fields = ['user__username', 'policy__name']


admin.site.register(Policy, PolicyAdmin)
admin.site.register(Claim, ClaimAdmin)
