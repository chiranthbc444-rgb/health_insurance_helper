from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('staff/login/', views.admin_login, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('policies/', views.policy_list, name='policy_list'),
    path('policies/<int:policy_id>/', views.policy_detail, name='policy_detail'),
    path('claims/', views.claim_list, name='claim_list'),
    path('claims/<int:claim_id>/', views.claim_detail, name='claim_detail'),
    path('claims/submit/', views.submit_claim, name='submit_claim'),
    # admin/staff portals
    path('staff/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff/claims/', views.admin_claim_list, name='admin_claim_list'),
    path('staff/claims/<int:claim_id>/', views.admin_claim_detail, name='admin_claim_detail'),
    path('staff/users/', views.admin_user_list, name='admin_user_list'),
    # modern pages
    path('calculator/', views.premium_calculator, name='premium_calculator'),
    path('contact/', views.contact, name='contact'),
    # AI Chatbot and Document Upload
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('upload-document/', views.upload_document, name='upload_document'),
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    path('api/compare-documents/', views.compare_documents, name='compare_documents'),
    path('api/risk-score/', views.risk_score_api, name='risk_score_api'),
    path('api/chart-data/', views.dashboard_chart_data, name='dashboard_chart_data'),
    path('documents/', views.document_list, name='document_list'),
    path('chat-history/', views.chat_history, name='chat_history'),
    path('set-language/', views.set_language, name='set_language'),
]
