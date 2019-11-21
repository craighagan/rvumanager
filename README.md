# rvumanager
tool for watching/managing rvus


## to set up python environment:

### if a virtual env has not been created:

virtualenv rvu
. rvu/bin/activate
pip install -r rvusite/requirements.txt

### if a virtual env has been created:

. rvu/bin/activate


## to run

after activating virtualenv,

### testing

to run unit tests:
RVUTEST=1 python rvusite/manage.py test

to start server:
RVUTEST=1 python rvusite/manage.py start

### production

python rvu/manage.py test
