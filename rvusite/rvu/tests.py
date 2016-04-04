from django.test import TestCase

# Create your tests here.
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.db import transaction
from django.utils import timezone
from django.contrib.admin.sites import AlreadyRegistered
from django.contrib import admin

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
