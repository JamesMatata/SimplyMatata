# Production deployment

Deploy **simplymatata.com** with Docker on a Linux server. Two layouts are supported:

| Layout | When to use | Public entry |
|--------|-------------|--------------|
| **Standalone** | Dedicated server | Host nginx on :80/:443 → app :8000 |
| **Shared VPS** | Another service already owns :80/:443 | Host reverse proxy → app on :8081 |

## Stack

- Django 5.2 + Gunicorn
- PostgreSQL 16
- WhiteNoise (static files)
- Media on `./data/media/`

---

## DNS (Namecheap)

1. Domain List → **Manage** → **Advanced DNS**
2. Add A records:

| Type | Host | Value |
|------|------|-------|
| A | `@` | Your server IP |
| A | `www` | Your server IP |

3. Verify:

```bash
nslookup simplymatata.com 8.8.8.8
nslookup www.simplymatata.com 8.8.8.8
```

---

## First deploy

```bash
sudo mkdir -p /opt/simplymatata
sudo chown $USER:$USER /opt/simplymatata
cd /opt/simplymatata

git clone <YOUR_REPO_URL> .
cp .env.production.example .env
nano .env
mkdir -p data/media data/postgres
```

Generate secrets:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
openssl rand -base64 32
```

Set `SECRET_KEY` and `POSTGRES_PASSWORD` in `.env`.

### Standalone server

```bash
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

Configure host nginx using `nginx/host.conf.example`, then:

```bash
sudo certbot --nginx -d simplymatata.com -d www.simplymatata.com
```

### Shared VPS (port 8081)

Use when ports 80 and 443 are already in use by another reverse proxy.

```bash
docker compose -f docker-compose.yml -f docker-compose.production.yml -p simplymatata up -d --build
curl -I http://127.0.0.1:8081
docker compose -p simplymatata exec web python manage.py createsuperuser
```

Add `nginx/simplymatata.com.conf` to your host reverse proxy, obtain TLS certificates for `simplymatata.com`, and reload nginx. The config proxies to `172.17.0.1:8081` (Docker host gateway).

---

## Routine updates

**Standalone:**

```bash
cd /opt/simplymatata
git pull
docker compose up -d --build
```

**Shared VPS:**

```bash
cd /opt/simplymatata
git pull
docker compose -f docker-compose.yml -f docker-compose.production.yml -p simplymatata up -d --build
```

Migrations run automatically on container start.

---

## Operations

| Task | Command |
|------|---------|
| Logs | `docker compose -p simplymatata logs -f web` |
| Restart | `docker compose -p simplymatata restart web nginx` |
| Shell | `docker compose -p simplymatata exec web python manage.py shell` |
| Backup DB | `docker compose -p simplymatata exec db pg_dump -U simplymatata simplymatata > backup.sql` |
| Backup media | `tar -czf media-backup.tar.gz -C /opt/simplymatata data/media` |

---

## Verify

- https://simplymatata.com
- https://simplymatata.com/admin/
- https://simplymatata.com/sitemap.xml
- Media uploads appear in `data/media/`

---

## Troubleshooting

**502 from reverse proxy**

```bash
docker compose -p simplymatata ps
docker compose -p simplymatata logs web --tail 50
curl -I http://127.0.0.1:8081
```

**CSRF or redirect loop**

Confirm in `.env`:

```
USE_SECURE_PROXY=True
CSRF_TRUSTED_ORIGINS=https://simplymatata.com,https://www.simplymatata.com
```

**Media 404**

```bash
ls -la /opt/simplymatata/data/media/
```

---

## Local development

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Set DEBUG=True in .env
python manage.py migrate
python manage.py runserver
```

Or with Docker:

```bash
docker compose up -d --build
```
