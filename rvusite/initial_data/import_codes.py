import csv
from django.contrib.auth.models import User
from rvu.models import BillingCode, PatientVisit, Provider
import dateutil.parser


r = csv.reader(file("rvu_codes.csv"))

for nr_rvus, code_name in r:
    print code_name, nr_rvus
    bc = BillingCode(code_name=code_name, nr_rvus=nr_rvus)
    bc.save()


r = csv.reader(file("RVUReport.csv"))
r.next()
for visit_date, provider_email, code_name, nr_rvus in r:
    print visit_date, provider_email, code_name, nr_rvus
    user = User.objects.filter(email=provider_email)
    provider = Provider.objects.get(user=user)
    billing_code = BillingCode.objects.get(code_name=code_name)
    visit = PatientVisit(code_billed=billing_code,
                         provider=provider,
                         visit_date=dateutil.parser.parse(visit_date))
    visit.save()

