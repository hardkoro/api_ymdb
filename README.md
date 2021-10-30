# API YaMDB

## Description

API allows to retrieve data from YaMDB.

Documentation is available at: redoc/

## Install

Clone the repo and change directory to the cloned repo:

```bash
git clone https://github.com/hardkoro/api_ymdb.git
```

```bash
cd api_ymdb
```

Create and activate virtual environment:

```bash
python -m venv venv
```

```bash
source venv/source/activate
```

Install requirements from file requirements.txt:

```bash
pip install -r requirements.txt
```

Migrate:

```bash
python manage.py migrate
```

Populate DB with csv-file data:

```bash
python manage.py populatedb /* PATH_TO_CSV_FILE */
```

Run project:

```bash
python manage.py runserver
```
