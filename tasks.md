# Tasks — SAMS

Méthode : **Junior** (Gabriel code, Claude oriente). Rien n'est « Done » sans validation de Gabriel.

## Pending

### Point 1 — Hygiène du dépôt ✅ terminé le 2026-10-26 (à valider par Gabriel)
Ordre choisi : on sort d'abord les secrets du code, **puis** on les change, pour que les nouveaux ne passent jamais par Git.

1. [x] Créer un `.gitignore` (modèle Python de GitHub adapté : `staticfiles/`, `mediafiles/`). Vérifié avec `git check-ignore --no-index` le 2026-10-26.
2. [x] Retirer du suivi Git sans supprimer en local : virtualenv, `staticfiles/`, `mediafiles/`, `.vscode/`, `db.sqlite3`, `__pycache__/` (7 045 fichiers). Commit `c5d0a83`.
3. [x] Virtualenv recréé en `.venv/` (l'ancien était cassé), vrai fichier `.env` + `.env.example`, `settings.py` lit tout via `django-environ`. Commit `ba6afe5`. Migrations appliquées en local (34), MLD de `CLAUDE.md` mis à jour.
4. [x] Rotation des secrets (2026-10-26) : nouvel utilisateur `djangouser` (droits limités à `sams.*` et `test_sams.*`, sans `GRANT OPTION`), nouveau mot de passe, ancien utilisateur `gabriel` supprimé, nouvelle `SECRET_KEY` (`token_urlsafe`). Tout est dans `.env` uniquement. Hors projet, à faire : vérifier les droits de `laraveluser`.
5. [x] Nettoyage de l'historique Git (2026-10-26) : sauvegarde, `git filter-repo` (chemins + secrets), force push (`main` = `6c0c52c`), dossier local aligné et purgé (`.git` : 32 Mo → 1,5 Mo). Forks : 0.
   - Incident : le `git switch main` de l'étape 0 a écrasé les fichiers ignorés. Restaurés : `mediafiles/` (12 photos) et `.vscode/` depuis la sauvegarde, `.env` recréé, `collectstatic` refait, connexion DB OK.

**Suivi hors code (Gabriel)**
- [x] Demander à GitHub Support de purger les anciens commits encore accessibles par leur identifiant (ex. `github.com/gabrielbygas/sams/commit/f136ddd`). Liste : `git -C ~/backups/sams-avant-filter-repo.git log --all --format=%H > ~/anciens-commits.txt`.
- [x] Après la réponse de GitHub : supprimer `~/backups/sams-avant-filter-repo.git` et `~/anciens-commits.txt`.
- [x] Vérifier les droits de `laraveluser` (`SHOW GRANTS`).
- [x] Ranger les secrets de `.env` dans un gestionnaire de mots de passe.

Déplacé au point 2 : nettoyage des dépendances (`mysql`, `mysql-connector-python` inutiles avec `mysqlclient`) et passage à `uv` + `pyproject.toml`.

### Point 2 — Django 5.2 LTS + uv (branche `chore/django-5.2`)
Une étape à la fois : d'abord changer l'outil (uv) à version égale, **puis** monter les versions. Si quelque chose casse, on sait quelle étape en est la cause.

1. [ ] ⏳ **Presque fait** — Projet `uv` à version égale. Commit `76277d9` : `pyproject.toml` + `uv.lock`, 4 dépendances directes (Django 5.0.14, django-environ 0.14.0, mysqlclient 2.3.0, pillow 13.0.0), livereload retiré, `requirements.txt` supprimé, `check` OK. Expliqué dans `docs.md`. **Reste : `.python-version` toujours ignoré (ligne 84 du `.gitignore`), donc pas commité.**
2. [ ] Monter à **Django 5.2 LTS + Python 3.13** : `uv python pin 3.13`, `uv add "django>=5.2,<5.3"`, `python -Wd manage.py check`, `makemigrations --check --dry-run`, test manuel des 3 rôles.
3. [ ] Outils de dev : `uv add --dev ruff pip-audit`, config Ruff dans `pyproject.toml`, premier `pip-audit` et premier `ruff check` (lecture des résultats, pas de correction de masse).
4. [ ] Finaliser : `CLAUDE.md` (stack + commandes), `docs.md`, merge dans `main`, push.

### Plan d'amélioration (provisoire, à valider après analyse complète)
2. ⏳ Voir « Point 2 » ci-dessus.
3. Settings par environnement (`config/settings/base|dev|prod.py`), `check --deploy`.
4. Modèles : `CustomUser` sur `AbstractUser` ou rôle explicite, `TextChoices`, `related_name`, `on_delete` revus, index sur `date_appointment`, suppression du `default=1` sur `Enquiry.doctor`.
5. Logique métier : couche `services.py` (réservation atomique, anti double-réservation du créneau médecin).
6. Permissions par rôle (étudiant / médecin / réception) + tests.
7. Tests : `pytest-django` + `factory_boy`, couverture des réservations.
8. Front : template partials + HTMX pour la prise de rendez-vous.
9. Docker (web + MariaDB 10.11 + redis) et `docker compose`.
10. CI/CD GitHub Actions (ruff, migrations check, tests, déploiement).

## Done
- [x] Version cible : **Django 5.2 LTS** (décidé par Gabriel le 2026-10-26).
