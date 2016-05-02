from django.conf.urls import url
from django.utils import timezone
from django.views.generic import RedirectView
from . import views

def get_current_date_str():
    now = timezone.now()
    return timezone.template_localtime(now).strftime("%Y-%m-%d")

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # ex: /patient_visit/5/
    url(r'visit/edit/(?P<pk>[0-9]+)/$', views.PatientVisitUpdateView.as_view(), name='patient-visit-edit'),
    url(r'visit/delete/(?P<pk>[0-9]+)/$', views.PatientVisitDeleteView.as_view(), name='patient-visit-delete'),
    url(r'visit/(?P<pk>[0-9]+)/$', views.PatientVisitDetailView.as_view(), name='patient-visit-detail'),
    url(r'visit/all/$', views.PatientVisitListView.as_view(), name='patient_visits'),
    url(r'visit/(?P<visit_date>\d\d\d\d-\d\d-\d\d)/$', views.PatientVisitListView.as_view(), name='patient_visits_day'),
    url(r'visit/today/$', RedirectView.as_view(url='/rvu/visit/%s' % get_current_date_str()), name='patient_visits_today'),
    url(r'billing_codes/$', views.BillingCodeListView.as_view(), name='billing_codes'),
    url(r'providers/$', views.ProviderListView.as_view(), name='providers'),
    url(r'visit/new/$', views.CreatePatientVisitView.as_view(), name='patient-visit-create'),
    url(r'report/daily/$', views.daily_report, name="daily_report"),
    url(r'report/weekly/$', views.weekly_report, name="weekly_report"),
    url(r'report/monthly/$', views.monthly_report, name="monthly_report"),
]
