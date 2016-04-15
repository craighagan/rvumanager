from django.test import TestCase

# Create your tests here.
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.db import transaction
from django.utils import timezone
from django.contrib.admin.sites import AlreadyRegistered
from django.contrib import admin
from django.test.client import Client

from rvu.models import PatientVisit, BillingCode, Provider
from rvu.apps import RvuConfig
from rvu.forms import NewPatientVisitForm
import rvu.views


class ViewTestCase(TestCase):
    fixtures = ['rvu']
    _url = ''

    @property
    def url(self):
        return self._url

    @property
    def terminated_url(self):
        return self._url + '/'

    def setUp(self):
        self.user = User.objects.get(email="someemail@somewhere.org")
        self.user.set_password('testpassword')
        self.user.save()
        self.client = Client()

# todo: test / this only tests /rvu
class TestView(ViewTestCase):
    _url = '/rvu'

    def test_unauthenticated_base_redirect(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, self.terminated_url,
                             status_code=301,
                             target_status_code=302)

    def test_authenticated_base_redirect(self):
        logged_in = self.client.login(username="AUserName", password="testpassword")
        response = self.client.get(self.url)
        self.assertRedirects(response, self.terminated_url,
                             status_code=301,
                             target_status_code=200)

    def test_unauthenticated_redirect(self):
        response = self.client.get(self.terminated_url)
        self.assertRedirects(response, '/admin/login/?next=%s' % self.terminated_url,
                             status_code=302)

    def test_authenticated_get(self):
        logged_in = self.client.login(username="AUserName", password="testpassword")
        self.assertTrue(logged_in)
        response = self.client.get(self.terminated_url)
        self.assertEquals(response.status_code, 200)
        self.assertNotEquals(response.content, "")


class TestBillingCode(TestView):
    _url = '/rvu/billing_codes'

    def test_simple(self):
        billingcodes = BillingCode.objects.all()
        self.assertEquals(len(billingcodes), 23)

    def test_create(self):
        instance = BillingCode.objects.create(code_name="test item", nr_rvus=0.5)
        self.assertTrue(BillingCode(instance))
        self.assertEquals(str(instance), "test item (0.50)")

        instance2 = BillingCode.objects.get(code_name="test item")
        self.assertEquals(instance, instance2)
        instance.delete()
        with self.assertRaises(ObjectDoesNotExist):
            BillingCode.objects.get(code_name="test item")


class ProviderViewTest(TestView):
    _url = '/rvu/providers'


class TestViewAllVisits(TestView):
    _url = '/rvu/visit/all'

    def test_user_not_provider(self):
        new_user = User.objects.create(username='test', email="test@somewhere.org")
        new_user.set_password('test123')
        new_user.save()
        logged_in = self.client.login(username="test", password="test123")
        self.assertTrue(logged_in)
        response = self.client.get(self.terminated_url, {"provider_email": "notfound@nowhere.com"})
        self.assertEquals(response.status_code, 404)
        self.assertNotEquals(response.content, "")
        new_user.delete()


class TestPatientVisitDetail(TestView):
    def setUp(self):
        super(TestPatientVisitDetail, self).setUp()

        self.provider = Provider.objects.get(user=self.user)
        self.pv = PatientVisit.objects.filter(provider=self.provider).first()
        self._url = '/rvu/visit/%d' % self.pv.pk

    def test_invalid_provider_email(self):
        logged_in = self.client.login(username="AUserName", password="testpassword")
        self.assertTrue(logged_in)
        response = self.client.get(self.terminated_url)
        self.assertEquals(response.status_code, 200)
        self.assertNotEquals(response.content, "")

    def test_user_not_provider(self):
        new_user = User.objects.create(username='test', email="test@somewhere.org")
        new_user.set_password('test123')
        new_user.save()
        logged_in = self.client.login(username="test", password="test123")
        self.assertTrue(logged_in)
        response = self.client.get(self.terminated_url, {"provider_email": "notfound@nowhere.com"})
        self.assertEquals(response.status_code, 404)
        self.assertNotEquals(response.content, "")
        new_user.delete()


class TestPatientVisitUpdate(TestView):
    def setUp(self):
        super(TestPatientVisitUpdate, self).setUp()

        self.provider = Provider.objects.get(user=self.user)
        self.pv = PatientVisit.objects.filter(provider=self.provider).first()
        self._url = '/rvu/visit/edit/%d' % self.pv.pk

    def test_invalid_provider_email(self):
        logged_in = self.client.login(username="AUserName", password="testpassword")
        self.assertTrue(logged_in)
        response = self.client.get(self.terminated_url)
        self.assertEquals(response.status_code, 200)
        self.assertNotEquals(response.content, "")

    def test_user_not_provider(self):
        new_user = User.objects.create(username='test', email="test@somewhere.org")
        new_user.set_password('test123')
        new_user.save()
        logged_in = self.client.login(username="test", password="test123")
        self.assertTrue(logged_in)
        response = self.client.get(self.terminated_url, {"provider_email": "notfound@nowhere.com"})
        self.assertEquals(response.status_code, 404)
        self.assertNotEquals(response.content, "")
        new_user.delete()

