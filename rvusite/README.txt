To deploy to elastic beanstalk:

eb deploy


To test:

source ./bin/activate

pip install -r requirements.txt

Then:

python2.7 ./manage.py makemigrations
python2.7 ./manage.py migrate


python manage.py shell
python manage.py test
python manage.py  runserver


ERROR: awsebcli 3.7.5 has requirement colorama==0.3.7, but you'll have colorama 0.3.3 which is incompatible.
ERROR: awsebcli 3.7.5 has requirement requests<=2.9.1,>=2.6.1, but you'll have requests 2.20.0 which is incompatible.
