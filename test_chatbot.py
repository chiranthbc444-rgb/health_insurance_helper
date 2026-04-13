#!/usr/bin/env python
"""
Test script for AI chatbot functionality
"""
import os
import sys
import django

# Add the project directory to the Python path
project_dir = os.path.join(os.path.dirname(__file__), 'health_insurance_helper')
sys.path.insert(0, project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insurance_project.settings')

django.setup()

from insurance_app.ai_service import AIService

def test_chatbot():
    """Test chatbot fallback responses"""
    print("Testing AI Chatbot Fallback Functionality")
    print("=" * 50)

    ai_service = AIService()

    test_messages = [
        "Hello",
        "What is health insurance?",
        "How do I file a claim?",
        "I need help with my policy",
        "Upload document",
        "What documents do I need?",
        "Premium calculator",
        "Help me please"
    ]

    for message in test_messages:
        print(f"\nUser: {message}")
        response = ai_service.generate_chatbot_response(message)
        print(f"Bot: {response}")

    print("\n" + "=" * 50)
    print("Testing Document Analysis Fallback")

    # Test document analysis fallback
    test_document_text = """
    HEALTH INSURANCE POLICY
    Policy Number: POL123456
    Coverage Amount: ₹5,00,000
    Valid until: December 2027
    """

    analysis = ai_service.analyze_document_with_ai(test_document_text, "policy")
    print(f"\nDocument Analysis Result:")
    for key, value in analysis.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    test_chatbot()