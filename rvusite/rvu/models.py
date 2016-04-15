from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.urlresolvers import reverse


class BillingCode(models.Model):
    nr_rvus = models.FloatField()
    creation_date = models.DateTimeField('date created', default=timezone.now)
    code_name = models.CharField(max_length=200)

    def __str__(self):
        return "%s (%0.2f)" % (self.code_name, self.nr_rvus)

    class Meta:
        ordering = ('code_name',)


class Provider(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    annual_rvu_goal = models.FloatField(default=0)

    def __str__(self):
        return "%s %s (%s)" % (self.user.first_name,
                               self.user.last_name,
                               self.user.email)

    class Meta:
        ordering = ('user',)


class PatientVisit(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    visit_date = models.DateTimeField('visit date')
    code_billed = models.ForeignKey(BillingCode)

    class Meta:
        ordering = ('visit_date',)

    def get_absolute_url(self):
        return reverse('patient-visit-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return "%s:%s:%s" % (self.visit_date, self.provider, self.code_billed)

