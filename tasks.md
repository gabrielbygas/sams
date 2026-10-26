# Tasks — SAMS

Méthode : **Junior** (Gabriel code, Claude oriente). Rien n'est « Done » sans validation de Gabriel.

## Pending

### Point 1 — Hygiène du dépôt (avant le 31 oct.) 🔴 sécurité
Ordre choisi : on sort d'abord les secrets du code, **puis** on les change, pour que les nouveaux ne passent jamais par Git.

1. [x] Créer un `.gitignore` (modèle Python de GitHub adapté : `staticfiles/`, `mediafiles/`). Vérifié avec `git check-ignore --no-index` le 2026-10-26.
2. [ ] ⏳ **Presque fait** — Retirer du suivi Git sans supprimer en local. Commit `c897d8e` : `.env/`, `staticfiles/`, `mediafiles/`, `.vscode/`, `db.sqlite3` retirés (6 993 fichiers). Les 52 `__pycache__/` sont retirés de l'index (staged) : **reste `git commit --amend --no-edit`.**
3. [ ] ⏳ **Presque fait** (relu le 2026-10-26) — `.venv/` créé, ancien `.env/` supprimé, `settings.py` lit tout via `django-environ`, `check` OK. **Reste : corriger le format de `.env.example`, réactiver le bon virtualenv, commit.** — **Recréer** le virtualenv en `.venv/` (l'ancien `.env/` est cassé : créé pour Python 3.10 dans un autre projet, `shis`, alors que le système est en 3.12 — un virtualenv ne se déplace pas), supprimer `.env/`, créer un vrai fichier `.env` + `.env.example`, lire `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` et la config MySQL via `django-environ`.
4. [ ] **Rotation des secrets** : nouveau mot de passe pour l'utilisateur MySQL, nouvelle `SECRET_KEY`, écrits uniquement dans `.env`.
5. [ ] **Nettoyage de l'historique Git** (décidé par Gabriel le 2026-10-26, priorité sécurité) : avec `git filter-repo`, effacer de tous les commits les anciens secrets de `sams/settings.py`, les photos de `mediafiles/`, `db.sqlite3`, le virtualenv et `staticfiles/`. Puis force-push vers GitHub (par Gabriel). Se fait **après** 1.4 et sur un clone de sauvegarde.

Déplacé au point 2 : nettoyage des dépendances (`mysql`, `mysql-connector-python` inutiles avec `mysqlclient`) et passage à `uv` + `pyproject.toml`.

### Plan d'amélioration (provisoire, à valider après analyse complète)
2. Montée de version Django 5.0 → **5.2 LTS** (support jusqu'à avril 2028) + Python 3.13, passage à `uv` + `pyproject.toml`, nettoyage des dépendances, `pip-audit`, lecture des dépréciations (`python -Wd`).
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
