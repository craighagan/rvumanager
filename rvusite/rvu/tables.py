import collections
import django_tables2 as tables
from django.db import connection
from .models import PatientVisit, BillingCode, Provider

TABLE_ATTRIBUTES = {"class": "paleblue"}


class PatientVisitTable(tables.Table):
    class Meta:
        model = PatientVisit
        # add class="paleblue" to <table> tag
        attrs = TABLE_ATTRIBUTES
        fields = ('provider', 'visit_date', 'code_billed')

    def render_code_billed(self, value):
        return "%s (%s)" % (value.code_name, value.nr_rvus)

    def render_provider(self, value):
        return "%s %s (%s)" % (value.user.first_name,
                               value.user.last_name,
                               value.user.email)


class ProviderTable(tables.Table):
    class Meta:
        model = Provider
        # add class="paleblue" to <table> tag
        attrs = TABLE_ATTRIBUTES
        fields = ('user', 'annual_rvu_goal')

    def render_user(self, value):
        return "%s %s (%s)" % (value.first_name, value.last_name, value.email)


class BillingCodesTable(tables.Table):
    class Meta:
        model = BillingCode
        # add class="paleblue" to <table> tag
        attrs = TABLE_ATTRIBUTES
        fields = ('code_name', 'nr_rvus')


class DailyReportTable(tables.Table):
    visit_date = tables.Column()
    provider = tables.Column()
    total_rvus = tables.Column()

    class Meta:
        attrs = TABLE_ATTRIBUTES


def getDailyReportTable(sql):
    cursor = connection.cursor()
    try:
        cursor.execute(sql)
        exptData = dictfetchall(cursor)
    except Exception as e:
        raise e

    return DailyReportTable(exptData)


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor
    ]


def getSQLTable(sql,
                bind_variables={},
                column_definitions=[]):
    cursor = connection.cursor()
    cursor.execute(sql, bind_variables)
    data = dictfetchall(cursor)

    the_attrs = collections.OrderedDict()
    cols = data[0]
    if column_definitions:
        cols = column_definitions

    for item in cols:
        the_attrs[str(item)] = tables.Column()

    # create a class with appropriate column properties
    myTable = type('myTable', (tables.Table,), the_attrs)

    # create a child of that class with the desired attributes
    class SQLTable(myTable):
        class Meta:
            attrs = TABLE_ATTRIBUTES

    table = SQLTable(data)
    return table
