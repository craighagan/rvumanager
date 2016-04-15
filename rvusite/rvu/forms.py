from django import forms
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from crispy_forms.bootstrap import TabHolder, Tab
from .models import PatientVisit


class NewPatientVisitForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_method = 'POST'
    helper.add_input(Submit('save', 'save', css_class='btn-primary'))

    visit_date = forms.DateTimeField(initial=timezone.now)

    class Meta:
        model = PatientVisit
        fields = ('visit_date', 'code_billed')
