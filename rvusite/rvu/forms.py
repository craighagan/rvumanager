from django import forms
from django.utils import timezone
from .models import PatientVisit


class NewPatientVisitForm(forms.ModelForm):
    visit_date = forms.DateTimeField(initial=timezone.now)

    class Meta:
        model = PatientVisit
        fields = ('visit_date', 'code_billed')
