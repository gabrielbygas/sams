# deploiement.md — SAMS

## État actuel (2026-10-26)
- Aucun déploiement : exécution locale uniquement (`uv run python manage.py runserver`), MariaDB 10.11 local.
- Installation locale après un `git clone` :
  1. `cp .env.example .env`, puis remplir les valeurs.
  2. `uv sync` (installe Python 3.13 si besoin, crée `.venv`).
  3. `uv run python manage.py migrate`, puis `createsuperuser`.
- Prérequis système pour compiler `mysqlclient` : `pkg-config`, `libmariadb-dev`.
- Pas de Docker, pas de CI/CD.

## Cible (à construire aux points 9 et 10 de `tasks.md`)
- Image Docker multi-stage (`python:3.13-slim`, `uv sync --frozen --no-dev`, utilisateur non-root, Gunicorn).
- `docker compose` : web + MariaDB 10.11 (même version qu'en local) + redis.
- GitHub Actions : ruff, `makemigrations --check`, `check --deploy`, tests, puis déploiement.
- Hébergeur : à choisir.

## Checklist de mise en production (à compléter)
- [ ] `DEBUG=False`, `ALLOWED_HOSTS`, `SECRET_KEY` propre à la prod
- [ ] HTTPS + cookies sécurisés + HSTS
- [ ] Backup DB avant `migrate`
- [ ] `collectstatic` dans le pipeline
- [ ] Hébergement actuel visé : cPanel « Setup Python App » (PlanetHoster). Problème connu de l'ancienne version : images non affichées en prod. Avec `DEBUG=False`, `static()` des `urls.py` ne sert plus rien ; `/static/` et `/media/` doivent être servis par le serveur web (ou WhiteNoise pour `/static/` uniquement). Voir `tasks.md` point 10.
