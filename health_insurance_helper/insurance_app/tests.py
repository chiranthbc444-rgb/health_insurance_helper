from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

# Create your tests here.

class LoginPortalTests(TestCase):
    def setUp(self):
        # create a normal user and a staff user
        self.user = User.objects.create_user(username='normal', password='pass')
        self.staff = User.objects.create_user(username='staff', password='pass', is_staff=True)

    def test_user_login_redirect(self):
        response = self.client.post(reverse('login'), {'username': 'normal', 'password': 'pass'})
        self.assertRedirects(response, reverse('dashboard'))

    def test_staff_login_from_user_portal(self):
        response = self.client.post(reverse('login'), {'username': 'staff', 'password': 'pass'}, follow=True)
        self.assertContains(response, 'Staff must login via the admin portal.')
        self.assertRedirects(response, reverse('admin_login'))

    def test_admin_login_success(self):
        response = self.client.post(reverse('admin_login'), {'username': 'staff', 'password': 'pass'})
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_nonstaff_cannot_use_admin_portal(self):
        response = self.client.post(reverse('admin_login'), {'username': 'normal', 'password': 'pass'}, follow=True)
        self.assertContains(response, 'Only staff members may use this portal.')
        self.assertRedirects(response, reverse('login'))

    def test_document_upload(self):
        # log in as normal user
        self.client.login(username='normal', password='pass')
        # create a simple in-memory file
        from django.core.files.uploadedfile import SimpleUploadedFile
        file_content = b'Test PDF content'
        uploaded_file = SimpleUploadedFile('test.pdf', file_content, content_type='application/pdf')

        response = self.client.post(reverse('upload_document'), {'document_type': 'policy', 'document': uploaded_file}, follow=True)
        self.assertContains(response, 'Document uploaded and analyzed successfully!')
        # ensure the DocumentUpload object was created
        from .models import DocumentUpload
        docs = DocumentUpload.objects.filter(user=self.user)
        self.assertEqual(docs.count(), 1)
        self.assertEqual(docs.first().document_type, 'policy')
