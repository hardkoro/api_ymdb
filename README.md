# API YaMDB

## Description

API allows to retrieve data from YaMDB — a service where people can share reviews of different works of art, such as movies, books etc. The service is implemented on Django Rest API.

A JWT token is used for an authentication. It can be obtained after authorization via e-mail.

Reviews can be written for each of the posts, and comments can be written for each review. You can leave a rating as for reviews, as for comments. Search and filtering are available.

Endpoints are described in the docs: http://localhost/redoc/.

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
