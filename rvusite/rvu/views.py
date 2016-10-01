import logging
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django_tables2 import RequestConfig
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.db.models import Count, Min, Sum, Avg
from django.utils.timezone import get_current_timezone
from django.utils.dateparse import parse_date
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, FormView, ListView
from django_tables2 import RequestConfig, SingleTableView, SingleTableMixin
from django.contrib.messages.views import SuccessMessageMixin
from braces.views import LoginRequiredMixin, RecentLoginRequiredMixin
from django.conf import settings
from .models import PatientVisit, BillingCode, Provider
from .tables import PatientVisitTable, BillingCodesTable, ProviderTable, getSQLTable
from .forms import NewPatientVisitForm
from .utils import get_fiscal_year_start

#database = "mysql"
database = settings.DATABASES['default']['ENGINE'].split('.')[-1]

MAX_SESSION_TIME = 4 * 60 * 60 # four hours

@login_required(login_url='/admin/login/')
def index(request):
    return render(request, "rvu/index.html")
    #return HttpResponse("Hello, world. You're at the rvu index.")

@login_required(login_url='/admin/login/')
def monthly_report(request):
    fiscal_year_start = get_fiscal_year_start()
    if database == "sqlite3":
        sql = """
        select strftime("%%Y-%%m", rvu_patientvisit.visit_date) as visit_date, auth_user.email as provider,
        sum(rvu_billingcode.nr_rvus) as total_rvus,
        sum(rvu_billingcode.nr_rvus)/(rvu_provider.annual_rvu_goal/12)*100 as pct_rvu_goal
        from
        rvu_patientvisit, auth_user, rvu_billingcode, rvu_provider
        where
        rvu_patientvisit.provider_id = rvu_provider.id and
        rvu_patientvisit.code_billed_id = rvu_billingcode.id and
        rvu_provider.user_id = auth_user.id and
        auth_user.id = :user_id and
        visit_date >= DATETIME(:fy_start)
        group by strftime("%%Y-%%m", rvu_patientvisit.visit_date), auth_user.email
        """
    elif database == "mysql":
        fiscal_year_start = fiscal_year_start.strftime("%Y-%m-%d")
        sql = """
        select DATE_FORMAT(rvu_patientvisit.visit_date, "%%Y-%%m") as visit_date, auth_user.email as provider,
        sum(rvu_billingcode.nr_rvus) as total_rvus,
        sum(rvu_billingcode.nr_rvus)/(rvu_provider.annual_rvu_goal/12)*100 as pct_rvu_goal
        from
        rvu_patientvisit, auth_user, rvu_billingcode, rvu_provider
        where
        rvu_patientvisit.provider_id = rvu_provider.id and
        rvu_patientvisit.code_billed_id = rvu_billingcode.id and
        rvu_provider.user_id = auth_user.id and
        auth_user.id = %(user_id)s and
        visit_date >= %(fy_start)s
        group by DATE_FORMAT(rvu_patientvisit.visit_date, "%%Y-%%m"), auth_user.email
        """
    user = request.user
    provider_email = request.GET.get('provider_email', '')
    if provider_email:
        user = get_object_or_404(User, email=provider_email)

    table = getSQLTable(sql,
                        bind_variables={"user_id": user.id, "fy_start": fiscal_year_start},
                        column_definitions=["provider", "visit_date", "total_rvus", "pct_rvu_goal"])
    RequestConfig(request).configure(table)
    return render(request, "rvu/render_table.html", {"table": table})

@login_required(login_url='/admin/login/')
def weekly_report(request):
    fiscal_year_start = get_fiscal_year_start()
    if database == "sqlite3":
        sql = """
        select strftime("%%Y Wk:%%W", rvu_patientvisit.visit_date) as visit_date, auth_user.email as provider,
        sum(rvu_billingcode.nr_rvus) as total_rvus,
        sum(rvu_billingcode.nr_rvus)/(rvu_provider.annual_rvu_goal/52)*100 as pct_rvu_goal
        from
        rvu_patientvisit, auth_user, rvu_billingcode, rvu_provider
        where
        rvu_patientvisit.provider_id = rvu_provider.id and
        rvu_patientvisit.code_billed_id = rvu_billingcode.id and
        rvu_provider.user_id = auth_user.id and
        auth_user.id = :user_id and
        visit_date >= DATETIME(:fy_start)
        group by strftime("%%Y Wk:%%W", rvu_patientvisit.visit_date), auth_user.email
        """
    elif database == "mysql":
        fiscal_year_start = fiscal_year_start.strftime("%Y-%m-%d")
        sql = """
        select DATE_FORMAT(rvu_patientvisit.visit_date, "%%Y Wk:%%U") as visit_date, auth_user.email as provider,
        sum(rvu_billingcode.nr_rvus) as total_rvus,
        sum(rvu_billingcode.nr_rvus)/(rvu_provider.annual_rvu_goal/52)*100 as pct_rvu_goal
        from
        rvu_patientvisit, auth_user, rvu_billingcode, rvu_provider
        where
        rvu_patientvisit.provider_id = rvu_provider.id and
        rvu_patientvisit.code_billed_id = rvu_billingcode.id and
        rvu_provider.user_id = auth_user.id and
        auth_user.id = %(user_id)s and
        visit_date >= %(fy_start)s
        group by DATE_FORMAT(rvu_patientvisit.visit_date, "%%Y Wk:%%U"), auth_user.email
        """
    user = request.user
    provider_email = request.GET.get('provider_email', '')
    if provider_email:
        user = get_object_or_404(User, email=provider_email)

    table = getSQLTable(sql,
                        bind_variables={"user_id": user.id, "fy_start": fiscal_year_start},
                        column_definitions=["provider", "visit_date", "total_rvus", "pct_rvu_goal"])
    RequestConfig(request).configure(table)
    return render(request, "rvu/render_table.html", {"table": table})

@login_required(login_url='/admin/login/')
def daily_report(request):
    fiscal_year_start = get_fiscal_year_start()
    if database == "sqlite3":
        sql = """
        select date(rvu_patientvisit.visit_date) as visit_date, auth_user.email as provider,
        sum(rvu_billingcode.nr_rvus) as total_rvus,
        sum(rvu_billingcode.nr_rvus)/(rvu_provider.annual_rvu_goal/314)*100 as pct_rvu_goal
        from
        rvu_patientvisit, auth_user, rvu_billingcode, rvu_provider
        where
        rvu_patientvisit.provider_id = rvu_provider.id and
        rvu_patientvisit.code_billed_id = rvu_billingcode.id and
        rvu_provider.user_id = auth_user.id and
        auth_user.id = :user_id and
        visit_date >= DATETIME(:fy_start)
        group by date(rvu_patientvisit.visit_date), auth_user.email
        """
    elif database == "mysql":
        fiscal_year_start = fiscal_year_start.strftime("%Y-%m-%d")
        sql = """
        select DATE_FORMAT(rvu_patientvisit.visit_date, "%%Y-%%m-%%d") as visit_date,
        auth_user.email as provider,
        sum(rvu_billingcode.nr_rvus) as total_rvus,
        sum(rvu_billingcode.nr_rvus)/(rvu_provider.annual_rvu_goal/314.0)*100 as pct_rvu_goal
        from
        rvu_patientvisit, auth_user, rvu_billingcode, rvu_provider
        where
        rvu_patientvisit.provider_id = rvu_provider.id and
        rvu_patientvisit.code_billed_id = rvu_billingcode.id and
        rvu_provider.user_id = auth_user.id and
        auth_user.id = %(user_id)s and
        visit_date >= %(fy_start)s
        group by DATE_FORMAT(rvu_patientvisit.visit_date, "%%Y-%%m-%%d"), auth_user.email
        """
    user = request.user
    provider_email = request.GET.get('provider_email', '')
    if provider_email:
        user = get_object_or_404(User, email=provider_email)

    table = getSQLTable(sql,
                        bind_variables={"user_id": user.id, "fy_start": fiscal_year_start},
                        column_definitions=["provider", "visit_date", "total_rvus", "pct_rvu_goal"])

    RequestConfig(request).configure(table)
    return render(request, "rvu/render_table.html", {"table": table})


class BillingCodeListView(RecentLoginRequiredMixin, SingleTableMixin, ListView):
    model = BillingCode
    table_class = BillingCodesTable
    login_url = '/admin/login/'
    template_name = "rvu/render_table.html"
    max_last_login_delta = MAX_SESSION_TIME

    def get(self, request, *args, **kwargs):
        provider = get_object_or_404(Provider, user=self.request.user)
        return super(BillingCodeListView, self).get(request, *args, **kwargs)


class ProviderListView(RecentLoginRequiredMixin, SingleTableMixin, ListView):
    model = Provider
    table_class = ProviderTable
    login_url = '/admin/login/'
    template_name = "rvu/render_table.html"
    max_last_login_delta = MAX_SESSION_TIME

    def get(self, request, *args, **kwargs):
        provider = get_object_or_404(Provider, user=self.request.user)
        return super(ProviderListView, self).get(request, *args, **kwargs)


class CreatePatientVisitView(RecentLoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = PatientVisit
    form_class = NewPatientVisitForm
    login_url = '/admin/login/'
    success_url = "/rvu"
    success_message = "Patient visit saved"
    max_last_login_delta = MAX_SESSION_TIME

    def form_valid(self, form):
        form.instance.provider = get_object_or_404(Provider, user=self.request.user)
        return super(CreatePatientVisitView, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        provider = get_object_or_404(Provider, user=self.request.user)
        return super(CreatePatientVisitView, self).get(request, *args, **kwargs)


class PatientVisitDeleteView(RecentLoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = PatientVisit
    form_class = NewPatientVisitForm
    login_url = '/admin/login/'
    success_url = "/rvu"
    success_message = "Patient visit deleted"
    max_last_login_delta = MAX_SESSION_TIME

    def form_valid(self, form):
        form.instance.provider = get_object_or_404(Provider, user=self.request.user)
        return super(PatientVisitDeleteView, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        provider = get_object_or_404(Provider, user=self.request.user)
        return super(PatientVisitDeleteView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            self.success_message = "cancelled delete"
            return HttpResponseRedirect(self.success_url)

        return super(PatientVisitDeleteView, self).post(request, *args, **kwargs)


class PatientVisitListView(RecentLoginRequiredMixin, SingleTableMixin, ListView):
    model = PatientVisit
    table_class = PatientVisitTable
    login_url = '/admin/login/'
    template_name = "rvu/render_table.html"
    max_last_login_delta = MAX_SESSION_TIME

    def get(self, request, *args, **kwargs):
        provider = get_object_or_404(Provider, user=self.request.user)
        self.order = self.request.GET.get('orderby', '-visit_date')
        return super(PatientVisitListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        fiscal_year_start = get_fiscal_year_start()
        visit_date = self.kwargs.get("visit_date", None)
        logging.warn("visit_date = %s", visit_date)
        provider = get_object_or_404(Provider, user=self.request.user)
        if not visit_date:
            return PatientVisit.objects.filter(provider=provider).order_by(self.order)
        else:
            parsed_visit_date = parse_date(visit_date)
            return PatientVisit.objects.filter(visit_date__year=parsed_visit_date.year,
                                               visit_date__month=parsed_visit_date.month,
                                               visit_date__day=parsed_visit_date.day,
                                               provider=provider).order_by(self.order)

class PatientVisitListThisFiscalYearView(PatientVisitListView):
    def get_queryset(self):
        fiscal_year_start = get_fiscal_year_start()
        visit_date = self.kwargs.get("visit_date", None)
        logging.warn("visit_date = %s", visit_date)
        provider = get_object_or_404(Provider, user=self.request.user)
        if not visit_date:
            return PatientVisit.objects.filter(provider=provider,
                                               visit_date__gte=fiscal_year_start).order_by(self.order)
        else:
            parsed_visit_date = parse_date(visit_date)
            return PatientVisit.objects.filter(visit_date__year=parsed_visit_date.year,
                                               visit_date__month=parsed_visit_date.month,
                                               visit_date__day=parsed_visit_date.day,
                                               provider=provider).order_by(self.order)

class PatientVisitDetailView(PatientVisitListView):
    def get_queryset(self):
        return [get_object_or_404(PatientVisit, pk=self.kwargs['pk'])]


class oldPatientVisitDetailView(RecentLoginRequiredMixin, SingleTableMixin, DetailView):
    model = PatientVisit
    table_class = PatientVisitTable
    login_url = '/admin/login/'
    max_last_login_delta = MAX_SESSION_TIME

    def get_context_data(self, **kwargs):
        context = kwargs
        context_object_name = self.get_context_object_name(self.object)
        if context_object_name:
            context[context_object_name] = [self.object]
        return context

    def get(self, request, *args, **kwargs):
        provider = get_object_or_404(Provider, user=self.request.user)
        return super(PatientVisitDetailView, self).get(request, *args, **kwargs)


class PatientVisitUpdateView(RecentLoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = PatientVisit
    form_class = NewPatientVisitForm
    login_url = '/admin/login/'
    success_url = "/rvu"
    success_message = "Patient visit updated"
    max_last_login_delta = MAX_SESSION_TIME

    def form_valid(self, form):
        if form.instance.provider != get_object_or_404(Provider, user=self.request.user):
            raise ValidationError(_("only change visits belonging to you"))
        return super(PatientVisitUpdateView, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        provider = get_object_or_404(Provider, user=self.request.user)
        return super(PatientVisitUpdateView, self).get(request, *args, **kwargs)


