# TUNGA SHOPPING LIST API

This is a project for Tunga TIA

## run this project
Clone this project

create virtual environment
```bash
python -m venv venv
```

activate virtual environment 
```bash
# for windows 
venv\scripts\activate

# for mac 
venv/bin/activate
```

install dependencies
```bash
pip install -r requirements.txt
```
#
create .env file and add the content of .env.example to it
#
Database used is postgresql
#

make migrations
```bash
python manage.py makemigrations main
```

migrate models
```bash
python manage.py migrate
```

create super admin
```bash
python manage.py createsuperuser
```

run server
```bash
python manage.py runserver
```
docs
<a href="https://documenter.getpostman.com/view/11580677/2s9YJXZjvA"> https://documenter.getpostman.com/view/11580677/2s9YJXZjvA </a>
