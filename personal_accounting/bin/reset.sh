#! /bin/bash


rm db.sqlite3
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --noinput --username=alex --email=acopton@gmail.com
# prepare via `python manage.py dumpdata > initial_data.json`
python manage.py populate

PASSWORD=`pwgen -n 10 1`
echo $PASSWORD
python manage.py changepassword alex
