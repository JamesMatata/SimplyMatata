# SimplyMatata

Portfolio site for James Matata — Django backend with a Tailwind + Alpine.js frontend.

## Stack

- Python 3.12 · Django 5.2 · PostgreSQL 16
- Gunicorn · WhiteNoise · Docker

## Project structure

```
SimplyMatata/
├── app/              # Core pages (home, about, contact)
├── works/            # Projects, media, comics, comments
├── config/           # Django settings
├── templates/
├── static/
├── nginx/            # Production nginx configs
├── docker/
├── data/             # Persistent media and database (not in git)
├── Dockerfile
├── docker-compose.yml
└── docker-compose.production.yml
```

## Local development

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Set DEBUG=True

python manage.py migrate
python manage.py createsuperuser
python manage.py seed_featured_projects   # optional
python manage.py runserver
```

Visit http://127.0.0.1:8000 — admin at `/admin/`.

Without `DATABASE_URL`, local dev uses SQLite.

## Production

See **[DEPLOY.md](DEPLOY.md)** for DNS, Docker deployment, nginx, and SSL.

Quick start on a dedicated server:

```bash
cp .env.production.example .env
mkdir -p data/media data/postgres
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

On a shared VPS where ports 80/443 are already taken:

```bash
docker compose -f docker-compose.yml -f docker-compose.production.yml -p simplymatata up -d --build
```

## Environment variables

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Required when `DEBUG=False` |
| `ALLOWED_HOSTS` | Include domain and `127.0.0.1` |
| `CSRF_TRUSTED_ORIGINS` | HTTPS origins with scheme |
| `POSTGRES_*` | Database credentials |
| `SITE_URL` | Canonical URL for SEO |

See `.env.example` and `.env.production.example` for the full list.

## License

Private project — all rights reserved.
