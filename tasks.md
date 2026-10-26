# Tasks — SAMS

Méthode : **Junior** (Gabriel code, Claude oriente). Rien n'est « Done » sans validation de Gabriel.

## Pending

### Point 1 — Hygiène du dépôt (avant le 31 oct.) 🔴 sécurité
Ordre choisi : on sort d'abord les secrets du code, **puis** on les change, pour que les nouveaux ne passent jamais par Git.

1. [x] Créer un `.gitignore` (modèle Python de GitHub adapté : `staticfiles/`, `mediafiles/`). Vérifié avec `git check-ignore --no-index` le 2026-10-26.
2. [ ] ⏳ **En cours** — Retirer du suivi Git, sans les supprimer en local : le virtualenv `.env/` (6 801 fichiers), `db.sqlite3`, `staticfiles/` (177), `mediafiles/` (12), `.vscode/` (2), les `__pycache__/` des apps (52), puis commit sur `chore/repo-hygiene`.
3. [ ] Renommer le virtualenv en `.venv/`, créer un vrai fichier `.env` + `.env.example`, lire `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` et la config MySQL via `django-environ`.
4. [ ] **Rotation des secrets** : nouveau mot de passe pour l'utilisateur MySQL, nouvelle `SECRET_KEY`, écrits uniquement dans `.env`. Les anciennes valeurs restent dans l'historique GitHub : elles doivent devenir inutilisables.
5. [ ] Nettoyer les dépendances (`mysql` et `mysql-connector-python` inutiles avec `mysqlclient`) — ou passer directement à `uv` + `pyproject.toml`.

### Plan d'amélioration (provisoire, à valider après analyse complète)
2. Montée de version Django 5.0 → **5.2 LTS** (support jusqu'à avril 2028) + Python 3.13, lecture des dépréciations (`python -Wd`).
3. Settings par environnement (`config/settings/base|dev|prod.py`), `check --deploy`.
4. Modèles : `CustomUser` sur `AbstractUser` ou rôle explicite, `TextChoices`, `related_name`, `on_delete` revus, index sur `date_appointment`, suppression du `default=1` sur `Enquiry.doctor`.
5. Logique métier : couche `services.py` (réservation atomique, anti double-réservation du créneau médecin).
6. Permissions par rôle (étudiant / médecin / réception) + tests.
7. Tests : `pytest-django` + `factory_boy`, couverture des réservations.
8. Front : template partials + HTMX pour la prise de rendez-vous.
9. Docker (web + MySQL 8.4 + redis) et `docker compose`.
10. CI/CD GitHub Actions (ruff, migrations check, tests, déploiement).

## Done
- [x] Version cible : **Django 5.2 LTS** (décidé par Gabriel le 2026-10-26).
