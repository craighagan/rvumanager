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

class AdminTest(TestCase):
    def test_registered(self):
        with self.assertRaises(AlreadyRegistered):
            admin.site.register(Provider)
        with self.assertRaises(AlreadyRegistered):
            admin.site.register(BillingCode)
        with self.assertRaises(AlreadyRegistered):
            admin.site.register(PatientVisit)


class RvuConfigTest(TestCase):
    def test_rvu_config(self):
        self.assertEquals(RvuConfig.name, "rvu")


class ProviderTest(TestCase):
    fixtures = ['rvu']

    def test_simple(self):
        p = Provider.objects.get(pk=1)
        self.assertEquals(p.user.email, 'someemail@somewhere.org')
        p = Provider.objects.get(pk=2)
        self.assertEquals(p.user.email, 'anotheremail@somewhere.else.com')
        self.assertEqual(len(Provider.objects.all()), 2)

    def test_create(self):
        u = User.objects.create(email="bob@somewhereelse.com", first_name="bob", last_name="dobbs")
        p=Provider.objects.create(user=u, annual_rvu_goal=600)
        self.assertEquals(str(p), "bob dobbs (bob@somewhereelse.com)")
        pp=Provider.objects.get(user=u)
        self.assertEquals(p, pp)
        p.delete()

        with self.assertRaises(ObjectDoesNotExist):
            pp=Provider.objects.get(user=u)

class BillingCodeTest(TestCase):
    fixtures = ['rvu']

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

class PatientVisitTest(TestCase):
    fixtures = ['rvu']


    def test_simple(self):
        billingcodes = BillingCode.objects.all()
        self.assertEquals(len(billingcodes), 23)


    def test_create(self):
        p=Provider.objects.get(pk=1)
        code = BillingCode.objects.get(pk=1)
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                pv = PatientVisit.objects.create(provider=p, code_billed=code)
        visit_date = "2016-04-01 01:01:01Z"
        pv = PatientVisit.objects.create(provider=p, code_billed=code, visit_date=visit_date)
        self.assertEquals(str(pv), "%s:%s:%s" % (visit_date, p, code))



# todo: test / this only tests /rvu
class TestViewIndex(TestCase):
    fixtures = ['rvu']

    def setUp(self):
        self.user = User.objects.get(email="someemail@somewhere.org")
        self.user.set_password('testpassword')
        self.user.save()
        self.client = Client()

    def test_unauthenticated_base_redirect(self):
        response = self.client.get('/rvu')
        self.assertRedirects(response, '/rvu/',
                             status_code=301,
                             target_status_code=302)

    def test_authenticated_base_redirect(self):
        logged_in = self.client.login(username="AUserName", password="testpassword")
        response = self.client.get('/rvu')
        self.assertRedirects(response, '/rvu/',
                             status_code=301,
                             target_status_code=200)

    def test_unauthenticated_redirect(self):
        response = self.client.get('/rvu/')
        self.assertRedirects(response, '/admin/login/?next=/rvu/',
                             status_code=302)

    def test_authenticated_get(self):
        logged_in = self.client.login(username="AUserName", password="testpassword")
        self.assertTrue(logged_in)
        response = self.client.get('/rvu/')
        self.assertEquals(response.status_code, 200)
        self.assertNotEquals(response.content, "")


class TestViewAllVisits(TestCase):
    fixtures = ['rvu']

    def setUp(self):
        self.user = User.objects.get(email="someemail@somewhere.org")
        self.user.set_password('testpassword')
        self.user.save()
        self.client = Client()

    def test_unauthenticated_redirect(self):
        response = self.client.get('/rvu/visit/all')
        self.assertRedirects(response, '/admin/login/?next=/rvu/visit/all', status_code=302)

    def test_authenticated_get(self):
        logged_in = self.client.login(username="AUserName", password="testpassword")
        self.assertTrue(logged_in)
        response = self.client.get('/rvu/visit/all')
        self.assertEquals(response.status_code, 200)
        self.assertNotEquals(response.content, "")


class TestPatientVisitDetail(TestCase):
    fixtures = ['rvu']

    def setUp(self):
        self.user = User.objects.get(email="someemail@somewhere.org")
        self.user.set_password('testpassword')
        self.user.save()
        self.client = Client()

        self.provider = Provider.objects.get(user=self.user)
        self.pv = PatientVisit.objects.filter(provider=self.provider).first()

    def test_unauthenticated_base_redirect(self):
        response = self.client.get('/rvu/visit/%d' % self.pv.pk)
        self.assertRedirects(response, '/rvu/visit/%d/' % self.pv.pk,
                             status_code=301,
                             target_status_code=302)

    def test_authenticated_base_redirect(self):
        logged_in = self.client.login(username="AUserName", password="testpassword")
        response = self.client.get('/rvu/visit/%d' % self.pv.pk)
        self.assertRedirects(response, '/rvu/visit/%d/' % self.pv.pk,
                             status_code=301,
                             target_status_code=200)

    def test_user_not_provider(self):
        new_user = User.objects.create(username='test', email="test@somewhere.org")
        new_user.set_password('test123')
        new_user.save()
        logged_in = self.client.login(username="test", password="test123")
        self.assertTrue(logged_in)
        response = self.client.get('/rvu/visit/%d/' % self.pv.pk)
        self.assertEquals(response.status_code, 404)
        self.assertNotEquals(response.content, "")
        new_user.delete()

    def test_unauthenticated_redirect(self):
        response = self.client.get('/rvu/visit/%d/' % self.pv.pk)
        self.assertRedirects(response, '/admin/login/?next=/rvu/visit/%d/' % self.pv.pk, status_code=302)

    def test_authenticated_get(self):
        logged_in = self.client.login(username="AUserName", password="testpassword")
        self.assertTrue(logged_in)
        response = self.client.get('/rvu/visit/%d/' % self.pv.pk)
        self.assertEquals(response.status_code, 200)
        self.assertNotEquals(response.content, "")

