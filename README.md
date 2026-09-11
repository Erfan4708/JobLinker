# JobLinker

JobLinker is a job listing aggregator for the Iranian job market. It scrapes IT and software job ads from three
Iranian job boards ([Jobinja](https://jobinja.ir), [JobVision](https://jobvision.ir) and
[e-estekhdam](https://www.e-estekhdam.com)), stores them in one database and shows them on a single Persian (RTL)
website, so you don't have to check each site separately.

I built it in 2023 as a personal project to practice Django, web scraping with Selenium and background jobs with
Celery. It was deployed on Liara at the time; that deployment is no longer online.

## Features

- **Scrapers for three job boards** – Selenium (Firefox via Selenium Grid) opens each ad and saves the title,
  company, location, description and a link to the original ad.
- **Scheduled updates** – Celery Beat runs every scraper every 30 minutes. A nightly task updates the
  "published N days ago" counter of the stored ads.
- **Job list** – the home page has two tabs: urgent ads and the latest ads, 20 per page.
- **Search** – keyword search over title, company and description, with an optional city filter (the city
  box suggests matching cities as you type).
- **Job detail page** – the full ad with a button that opens the original ad to apply.
- **Accounts and bookmarks** – users can sign up, log in and bookmark ads, and see their bookmarks on a
  separate page.
- **Django admin** for managing posts and bookmarks.

## Tech Stack

- **Python 3.9**, **Django 4.2**
- **Celery 5.3** with **Redis** as broker and result backend, **Celery Beat** for scheduling
- **Selenium 4** with a **Selenium Grid** hub and a Firefox node
- **PostgreSQL 14** (SQLite for quick local runs)
- **django-crispy-forms** (Bootstrap 4) for the login/sign-up forms
- Front end based on a free [Colorlib](https://colorlib.com) job board template (Bootstrap 4, jQuery)
- **Docker** / **Docker Compose** for the full local stack

## Project Structure

```
config/                Django project: settings, root URLs, Celery app and beat schedule (celery.py)
post/                  Main app
  models.py            Post (a scraped job ad), FavoritePost (a user's bookmark)
  views.py             List, detail, search and bookmark views
  tasks.py             Celery tasks: one Selenium scraper per site + the nightly update task
  tests.py             Tests for the views and task helpers
account/               Sign-up view (login/logout use Django's built-in auth views)
templates/             Django templates (_base.html is the layout, _*.html are shared partials)
static/                CSS, JS, fonts and images from the front-end template
Dockerfile
docker-compose.yml     web, Celery worker, Celery Beat, Redis, PostgreSQL, pgAdmin, Selenium Grid
```

## Getting Started

### Option 1: Docker Compose (full stack)

Prerequisites: Docker with Docker Compose.

```bash
git clone https://github.com/Erfan4708/JobLinker.git
cd JobLinker
docker compose up --build
```

In a second terminal, create the database tables and an admin user:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Then open:

| Service           | URL                          |
|-------------------|------------------------------|
| JobLinker         | http://localhost:6060        |
| Django admin      | http://localhost:6060/admin/ |
| pgAdmin           | http://localhost:5050        |
| Selenium Grid UI  | http://localhost:4444        |

> **Note:** `docker compose up` also starts Celery Beat, which schedules the scrapers right away. The scrapers
> visit the real job sites. To only run the website, start just the web part:
> `docker compose up --build web`

The database username/password in `docker-compose.yml` are local development defaults only.

### Option 2: Run the website locally without Docker

Prerequisites: Python 3.9+ (tested with 3.9 and 3.11).

```bash
git clone https://github.com/Erfan4708/JobLinker.git
cd JobLinker
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Without `POSTGRES_DB` set, the project uses a local `db.sqlite3` file, so no database server is needed. The site is
then available at http://localhost:8000. The database will be empty until the scrapers run (or you add posts in the
admin).

> `psycopg2` is built from source on Linux/macOS, so you may need the PostgreSQL client headers
> (e.g. `libpq-dev` on Debian/Ubuntu).

To run the scrapers outside Docker you also need a Redis server and a Selenium Grid (hub + Firefox node). Point the
project to them with environment variables and start a worker and the scheduler:

```bash
export CELERY_BROKER=redis://localhost:6379/0
export CELERY_BACKEND=redis://localhost:6379/0
export SELENIUM_REMOTE_HOST=localhost
celery -A config worker -l info       # on Windows add: -P solo
celery -A config beat -l info
```

## Configuration

All settings have defaults that work for local development. They are read from environment variables in
`config/settings.py` and `post/tasks.py`.

| Variable               | Default                                | Description                                                   |
|------------------------|----------------------------------------|---------------------------------------------------------------|
| `DJANGO_SECRET_KEY`    | a development-only key                 | Set your own value anywhere outside local development.        |
| `DEBUG`                | `1`                                    | `1` to enable debug mode, `0` to disable it.                  |
| `DJANGO_ALLOWED_HOSTS` | `localhost 127.0.0.1`                  | Space-separated list of allowed host names.                   |
| `POSTGRES_DB`          | *(unset)*                              | Database name. If unset, SQLite is used instead of PostgreSQL. |
| `POSTGRES_USER`        | *(empty)*                              | PostgreSQL user.                                              |
| `POSTGRES_PASSWORD`    | *(empty)*                              | PostgreSQL password.                                          |
| `POSTGRES_HOST`        | `localhost`                            | PostgreSQL host (`db` in Docker Compose).                     |
| `POSTGRES_PORT`        | `5432`                                 | PostgreSQL port.                                              |
| `CELERY_BROKER`        | `redis://redis:6379/0`                 | Celery broker URL.                                            |
| `CELERY_BACKEND`       | `redis://redis:6379/0`                 | Celery result backend URL.                                    |
| `SELENIUM_REMOTE_HOST` | `selenium-hub`                         | Host of the Selenium Grid hub (port 4444).                    |

Example for a non-development environment:

```bash
DJANGO_SECRET_KEY=replace-with-a-long-random-string
DEBUG=0
DJANGO_ALLOWED_HOSTS=joblinker.example.com
POSTGRES_DB=job_linker
POSTGRES_USER=joblinker
POSTGRES_PASSWORD=replace-me
POSTGRES_HOST=db.example.com
```

## Usage

- The home page lists the urgent ads; the second tab shows the latest ads, newest first.
- Use the search box at the top to search by job title / skill / company, and optionally pick a city.
- Open an ad to see its details; the apply button takes you to the original ad on the source site.
- Sign up or log in to bookmark ads; bookmarked ads are listed under "نشان شده ها" (Bookmarks).

To run a scraper once without waiting for the schedule (with the Docker stack running):

```bash
docker compose exec web python manage.py shell -c "from post.tasks import jobinja_scrap; jobinja_scrap.delay()"
```

The available tasks are `jobinja_scrap`, `jobvision_scrap`, `e_estekhdam_scrap` and `update_database`.

## Testing

```bash
python manage.py test
# or, with Docker Compose running:
docker compose exec web python manage.py test
```

The tests cover the list, detail and search views, bookmarking (including the login requirement) and the database
side of the tasks (`save_to_postgres` and `update_database`). The Selenium scrapers are not covered by tests,
since they need a Selenium Grid and the live job sites.

## Technical Notes

How the data flows:

1. Celery Beat (schedule in `config/celery.py`) queues the scraper tasks every 30 minutes.
2. A Celery worker runs a task, which opens a remote Firefox session on the Selenium Grid.
3. The scraper goes through the listing pages of the site, opens each ad and saves it as a `Post`. Ads are
   identified by their link, so an ad that is already stored is skipped (urgent ads are updated in place).
4. The Django views read the `Post` table; bookmarks are stored in `FavoritePost`.

`Post.date_modified` is not a date: it stores how many days ago the ad was published, as shown on the source site.
`0` means today and `-1` marks an urgent ("فوری") ad. The nightly `update_database` task adds one to every
non-urgent ad.

## Limitations

- The scrapers rely on the HTML structure (class names and some absolute XPaths) of the three sites as it was in
  2023. These sites have most likely changed since then, so the scrapers would need to be updated to work again.
- The scraped categories are hardcoded to IT/software jobs.
- Old ads are never removed, and publish dates are tracked with a day counter instead of a real date.
  e-estekhdam ads don't have their publish date parsed and are stored as "2 days ago".
- Search results are not paginated.
- Docker Compose runs Django's development server; there is no production setup (e.g. Gunicorn, `collectstatic`).
- The `City` model is not used yet.
