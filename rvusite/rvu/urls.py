from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # ex: /patient_visit/5/
    url(r'(?P<patient_visit_id>[0-9]+)/$', views.patient_visit_detail, name='patient_visit_detail'),
    url(r'visits/$', views.patient_visits, name='patient_visits'),
    url(r'billing_codes/$', views.billing_codes, name='billing_codes'),
    url(r'providers/$', views.providers, name='providers'),
    url(r'new_patient_visit/$', views.new_patient_visit, name='new_patient_visit'),
    url(r'reports/daily/$', views.daily_report, name="daily_report"),
    url(r'reports/weekly/$', views.weekly_report, name="weekly_report"),
    url(r'reports/monthly/$', views.monthly_report, name="monthly_report"),

]
