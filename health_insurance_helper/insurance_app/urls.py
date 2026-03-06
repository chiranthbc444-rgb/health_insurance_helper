from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('policies/', views.policy_list, name='policy_list'),
    path('policies/<int:policy_id>/', views.policy_detail, name='policy_detail'),
    path('claims/', views.claim_list, name='claim_list'),
    path('claims/<int:claim_id>/', views.claim_detail, name='claim_detail'),
    path('claims/submit/', views.submit_claim, name='submit_claim'),
]
