# deploiement.md — SAMS

## État actuel (2026-10-26)
- Aucun déploiement : exécution locale uniquement (`python manage.py runserver`), MySQL local.
- Pas de Docker, pas de CI/CD.

## Cible (à construire aux points 9 et 10 de `tasks.md`)
- Image Docker multi-stage (`python:3.13-slim`, utilisateur non-root, Gunicorn).
- `docker compose` : web + MySQL 8.4 + redis.
- GitHub Actions : ruff, `makemigrations --check`, `check --deploy`, tests, puis déploiement.
- Hébergeur : à choisir.

## Checklist de mise en production (à compléter)
- [ ] `DEBUG=False`, `ALLOWED_HOSTS`, `SECRET_KEY` propre à la prod
- [ ] HTTPS + cookies sécurisés + HSTS
- [ ] Backup DB avant `migrate`
- [ ] `collectstatic` dans le pipeline
