from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django_tables2 import RequestConfig
from django.contrib.auth.models import User
from .models import PatientVisit, BillingCode, Provider
from .tables import PatientVisitTable, BillingCodesTable, ProviderTable, getSQLTable
from .forms import NewPatientVisitForm


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def patient_visit_detail(request, patient_visit_id):
    user = request.user
    provider_email = request.GET.get('provider_email', '')
    if provider_email:
        user = get_object_or_404(User, email=provider_email)

    provider = get_object_or_404(Provider, user=user)
    table = PatientVisitTable(PatientVisit.objects.filter(pk=patient_visit_id,
                                                          provider=provider))
    return render(request, "rvu/render_table.html", {"table": table})


def patient_visits(request):
    user = request.user
    provider_email = request.GET.get('provider_email', '')
    if provider_email:
        user = get_object_or_404(User, email=provider_email)

    provider = get_object_or_404(Provider, user=user)
    table = PatientVisitTable(PatientVisit.objects.filter(provider=provider))
    RequestConfig(request).configure(table)
    return render(request, "rvu/render_table.html", {"table": table})


def billing_codes(request):
    table = BillingCodesTable(BillingCode.objects.all())
    RequestConfig(request).configure(table)
    return render(request, "rvu/render_table.html", {"table": table})


def providers(request):
    table = ProviderTable(Provider.objects.all())
    RequestConfig(request).configure(table)
    return render(request, "rvu/render_table.html", {"table": table})


def monthly_report(request):
    sql = """
    select strftime("%%Y %%m", rvu_patientvisit.visit_date) as visit_date, auth_user.email as provider,
    sum(rvu_billingcode.nr_rvus) as total_rvus,
    sum(rvu_billingcode.nr_rvus)/(rvu_provider.annual_rvu_goal/12)*100||'%%' as pct_rvu_goal
    from
    rvu_patientvisit, auth_user, rvu_billingcode, rvu_provider
    where
    rvu_patientvisit.provider_id = rvu_provider.id and
    rvu_patientvisit.code_billed_id = rvu_billingcode.id and
    rvu_provider.user_id = auth_user.id and
    auth_user.id = :user_id
    group by strftime("%%Y %%m", rvu_patientvisit.visit_date), auth_user.email
    """
    user = request.user
    provider_email = request.GET.get('provider_email', '')
    if provider_email:
        user = get_object_or_404(User, email=provider_email)

    table = getSQLTable(sql,
                        bind_variables={"user_id": user.id},
                        column_definitions=["provider", "visit_date", "total_rvus", "pct_rvu_goal"])
    RequestConfig(request).configure(table)
    return render(request, "rvu/render_table.html", {"table": table})


def weekly_report(request):
    sql = """
    select strftime("%%Y Wk:%%W", rvu_patientvisit.visit_date) as visit_date, auth_user.email as provider,
    sum(rvu_billingcode.nr_rvus) as total_rvus,
    sum(rvu_billingcode.nr_rvus)/(rvu_provider.annual_rvu_goal/52)*100||'%%' as pct_rvu_goal
    from
    rvu_patientvisit, auth_user, rvu_billingcode, rvu_provider
    where
    rvu_patientvisit.provider_id = rvu_provider.id and
    rvu_patientvisit.code_billed_id = rvu_billingcode.id and
    rvu_provider.user_id = auth_user.id and
    auth_user.id = :user_id
    group by strftime("%%Y Wk:%%W", rvu_patientvisit.visit_date), auth_user.email
    """
    user = request.user
    provider_email = request.GET.get('provider_email', '')
    if provider_email:
        user = get_object_or_404(User, email=provider_email)

    table = getSQLTable(sql,
                        bind_variables={"user_id": user.id},
                        column_definitions=["provider", "visit_date", "total_rvus", "pct_rvu_goal"])
    RequestConfig(request).configure(table)
    return render(request, "rvu/render_table.html", {"table": table})


def daily_report(request):
    sql = """
    select date(rvu_patientvisit.visit_date) as visit_date, auth_user.email as provider,
    sum(rvu_billingcode.nr_rvus) as total_rvus,
    sum(rvu_billingcode.nr_rvus)/(rvu_provider.annual_rvu_goal/314)*100||'%%' as pct_rvu_goal
    from
    rvu_patientvisit, auth_user, rvu_billingcode, rvu_provider
    where
    rvu_patientvisit.provider_id = rvu_provider.id and
    rvu_patientvisit.code_billed_id = rvu_billingcode.id and
    rvu_provider.user_id = auth_user.id and
    auth_user.id = :user_id
    group by date(rvu_patientvisit.visit_date), auth_user.email
    """
    user = request.user
    provider_email = request.GET.get('provider_email', '')
    if provider_email:
        user = get_object_or_404(User, email=provider_email)
    table = getSQLTable(sql,
                        bind_variables={"user_id": user.id},
                        column_definitions=["provider", "visit_date", "total_rvus", "pct_rvu_goal"])
    RequestConfig(request).configure(table)
    return render(request, "rvu/render_table.html", {"table": table})


def new_patient_visit(request):
    if request.method == "POST":
        form = NewPatientVisitForm(request.POST)
        if form.is_valid():
            patient_visit = form.save(commit=False)
            patient_visit.provider = Provider.objects.get(user=request.user)
            patient_visit.save()
            return redirect('patient_visit_detail', patient_visit_id=patient_visit.pk)
    else:
        form = NewPatientVisitForm()
    return render(request, 'rvu/new_patient_visit.html', {'form': form})
