from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # ex: /patient_visit/5/
    url(r'visit/(?P<patient_visit_id>[0-9]+)/$', views.patient_visit_detail, name='patient_visit_detail'),
    url(r'visit/all$', views.patient_visits, name='patient_visits'),
    url(r'billing_codes/$', views.billing_codes, name='billing_codes'),
    url(r'providers/$', views.providers, name='providers'),
    url(r'visit/new/$', views.new_patient_visit, name='new_patient_visit'),
    url(r'report/daily/$', views.daily_report, name="daily_report"),
    url(r'report/weekly/$', views.weekly_report, name="weekly_report"),
    url(r'report/monthly/$', views.monthly_report, name="monthly_report"),

]
