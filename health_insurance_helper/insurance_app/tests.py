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
