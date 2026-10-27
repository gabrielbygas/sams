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

### Point 2 — Django 5.2 LTS + uv ✅ terminé le 2026-10-26 (fusionné dans `main` = `5e7649c`)
Une étape à la fois : d'abord changer l'outil (uv) à version égale, **puis** monter les versions. Si quelque chose casse, on sait quelle étape en est la cause.

1. [x] Projet `uv` à version égale. Commits `76277d9` + `348abff` : `pyproject.toml`, `uv.lock`, `.python-version`, 4 dépendances directes (Django 5.0.14, django-environ 0.14.0, mysqlclient 2.3.0, pillow 13.0.0), livereload retiré, `requirements.txt` supprimé, `check` OK. Expliqué dans `docs.md`.
2. [x] Django 5.2 LTS + Python 3.13. Commit `261fd90` : Python 3.13.14, Django 5.2.18. `check -Wd` sans avertissement, `makemigrations --check` : aucun changement, `migrate` : rien à appliquer. Test manuel des 3 rôles OK (validé par Gabriel le 2026-10-26), après `changepassword` des comptes dont le mot de passe était en clair (correctif durable : point 3).
3. [x] Outils de dev. Commit `74223c7` : Ruff 0.17 + pip-audit 2.10 en groupe `dev`, config Ruff (`py313`, 100 colonnes, règles `E F I B UP DJ`). `pip-audit` : aucune vulnérabilité. `ruff check` : 119 erreurs (64 `E501`, 25 `F401`, 22 `I001`, 5 `DJ001`, 2 `DJ012`, 1 `F811`) ; `ruff format` : 30 fichiers à reformater → commit dédié au début du point 3.
4. [x] Finalisation : docs mis à jour (commit `5e7649c`), fusion fast-forward dans `main`, push, branche `chore/django-5.2` supprimée.

### Point 3 — Comptes et rôles (branche `fix/accounts-roles`) ⏳ en cours
Retours de Gabriel du 2026-10-26. Règle métier : **un utilisateur = un seul rôle** (étudiant, médecin **ou** réceptionniste) ; seul l'admin (superuser) a accès à tout.

0. [x] Commit `d9f4c44` (33 fichiers `.py`). Reste : 4 `tests.py` avec une ligne vide en trop (laissée par `--fix`) → `ruff format .` + `git commit --amend --no-edit` (branche pas encore poussée).
   **Commit de formatage seul** : `uv run ruff format .` + `uv run ruff check --fix .` (imports), vérifier `check` et le site, commit « Apply Ruff formatting » — **avant** toute modification du code. Simulation de Claude sur une copie : 30 fichiers reformatés, 47 corrections d'imports (inutilisés + triés), **11 erreurs restantes attendues** (5 `DJ001`, 4 `E501`, 2 `DJ012`) → corrigées à la main aux points 3.2 et 5, pas ici.
1. [ ] **Admin et mots de passe hachés** : `CustomUserAdmin` hérite de `django.contrib.auth.admin.UserAdmin` (hachage à la création + formulaire « changer le mot de passe » = reset par l'admin) ; `CustomUser` hérite de `PermissionsMixin` (aujourd'hui `has_perm()` renvoie `True` pour tout le monde) ; ~~re-hacher les mots de passe en clair~~ (contrôle du 2026-10-26 : 0 sur 5, déjà corrigé par `changepassword`). ✅ Commit `7522c5e` (migration `account.0007`, MLD à jour, lien « Reset password » vérifié). Reste 1 `I001` (imports de `account/models.py`) → corrigé avec le 3.2. Effet de bord : 1 compte `is_staff` non superuser perd l'accès total à l'admin (voulu).
2. [ ] **Un seul rôle par utilisateur** : champ `role` (`TextChoices`) sur `CustomUser` + data migration depuis les profils existants + validation (un profil doit correspondre au rôle) ; `is_doctor()`… s'appuient sur `role` ; superuser = accès à tout. Corriger les vérifications des vues :
   - `user_creation_error_page` : `request.user.is_superuser()` (appel d'un booléen → `TypeError`).
   - `student/views.py:27`, `doctor/views.py:32`, `receptionist/views.py:27` : `not A or B` au lieu de `not (A or B)`.
   - `doctor/views.py:27` (`not user.is_student()`) et `student/views.py:22` (`not user.is_doctor()`) : tester le rôle attendu, pas l'absence d'un autre.
   - ✅ Modèle + base (2026-10-27) : migrations `0008` (champ), `0009` (data), `0010` (CHECK) appliquées, rôles corrects, manager réécrit, `RoleProfileMixin`, admin. MLD à jour.
   - ⏳ **En cours — vues** : 8 corrections listées dans `docs.md` § 3.2 partie 4 (guide réécrit niveau junior à la demande de Gabriel) :
     1. [x] `create_student/doctor/receptionist` : arguments nommés (vérifié 2026-10-27 : 200).
     2. [x] (corrigé, vérifié 2026-10-27) URL `error-page` : ajoutées mais avec `name="doctor-error-page"` / `"receptionist-error-page"` → toujours `NoReverseMatch` (étudiant → `/doctors/…` = 500). Mettre `name="error-page"` (docs.md § 3.2 partie 4 bis, problème A).
     3. [x] `receptionist/views.py` : ancien `is_receptionist` supprimé.
     3 bis. [x] ⚠️ **Sécurité** : le `is_receptionist` restant (`receptionist/views.py:22`) teste `user.is_receptionist` sans `()` → toujours vrai → étudiant et médecin entrent dans l'espace réception. Remplacer par `user.has_role(CustomUser.Role.RECEPTIONIST)` (partie 4 bis, problème B). Ligne corrigée, mais il manque `from account.models import CustomUser` → `NameError` (500, Ruff `F821`). Import ajouté ✅ (non commité).
     4. [x] `can_access_*_space` branchées, `is_not_*` supprimées.
     5. [x] 3 pages d'erreur : message fixe.
     6. [x] `user_creation_error_page` : plus de `TypeError`.
     7. [x] Services du médecin dans `transaction.atomic()` + `.set()`.
     8. [x] `auth_login` : `ROLE_HOME`.
     Ruff : 11 erreurs attendues ✅. **Test complet du 2026-10-27** (docs.md § 3.2 partie 4 ter) : 39 URL × 7 utilisateurs, 0 erreur 500, rôles corrects, POST de création OK, contrainte + mixin OK → 3.2 fonctionnel. ✅ **Validé par Gabriel le 2026-10-27** (commit `0f4c5a0`).
     Reste : `git add receptionist/views.py` + `git commit --amend -m "Fix error-page URL names and receptionist role check"` (branche non poussée), puis commit de la doc.
   - Repéré pour le point 7 : `student/views.py` `EnquiryListView`, `EnquiryDetailView`, `EnquiryUpdateView` n'ont **aucun** test de rôle (confirmé : un médecin voit et modifie toutes les questions) ; **IDOR** : les vues détail/modifier/supprimer ne vérifient pas le propriétaire (étudiant 6 → RDV de l'étudiant 2, médecin 4 → RDV/question du médecin 3).
3. [ ] **Photo facultative** : `templates/header.html:16` (`user.photo.url` sans photo → `ValueError`, **confirmé 2026-10-27 : 500 sur toutes les pages** pour un compte sans photo) → avatar par défaut ; retirer `required: True` du widget `photo` (formulaires création/modification) ; valider taille et type du fichier.
4. [ ] **Mots de passe** : changer le sien (`PasswordChangeView` + `PasswordChangeDoneView`, lien dans l'en-tête). Création de compte par un réceptionniste/admin : **ne plus connecter** le compte créé (`authenticate_and_login`, `account/views.py:62`) — confirmé : la session de la réception passe au nouveau compte. `/accounts/create-student/` : réservé aux visiteurs non connectés (+ réception/admin).
5. [ ] **Données de démo** : `factory_boy` + `Faker` (dev), factories `CustomUser`/`Student`/`Doctor`/`Receptionist`/`Service`, commande `manage.py seed_demo` : ≥ 20 étudiants, ≥ 10 médecins, ≥ 3 réceptionnistes, ≥ 5 services, quelques comptes sans photo.

### Plan d'amélioration (provisoire, à valider après analyse complète)
2. ✅ Voir « Point 2 » ci-dessus.
3. ⏳ Voir « Point 3 » ci-dessus.
4. Settings par environnement (`config/settings/base|dev|prod.py`), `check --deploy`.
5. Modèles : `TextChoices`, `related_name`, `on_delete` revus, index sur `date_appointment`, suppression du `default=1` sur `Enquiry.doctor`.
6. Logique métier : couche `services.py` (réservation atomique, anti double-réservation du créneau médecin).
   - Bug repéré le 2026-10-27 : modifier un RDV sans changer sa date est refusé (`AppointmentForm.clean()`, `student/forms.py`, n'exclut pas `self.instance`) → `.exclude(pk=self.instance.pk)`.
7. Sécurité des vues + tests de permissions par rôle. Repéré au point 2 :
   - `account/views.py:20` — redirection vers `?next=` sans vérification (**open redirect**) → `url_has_allowed_host_and_scheme()`.
   - `account/views.py:66` — `login(request, user)` alors que `authenticate()` peut renvoyer `None` (déprécié en 5.2, erreur en 6.1).
   - Déconnexion par un lien GET (`templates/header.html:22`) → formulaire POST.
   - `sams/views.py` `back()` redirige vers `HTTP_REFERER`, une valeur envoyée par le client (même risque d'open redirect).
   - `static(...)` ajouté dans chaque `urls.py` : à ne garder qu'en dev (`if settings.DEBUG`), une seule fois dans `sams/urls.py`.
8. Tests : `pytest-django` + factories du point 3, couverture des réservations.
9. Front : template partials + HTMX pour la prise de rendez-vous.
10. **Images en production (cPanel, « Setup Python App », PlanetHoster)** : dans l'ancienne version, les photos (`/media/`) ne s'affichaient pas en prod. Cause probable, à confirmer sur le serveur : `static(...)` dans les `urls.py` ne renvoie **rien** quand `DEBUG=False` (Django refuse de servir les fichiers en prod, c'est le rôle du serveur web). À faire :
   - statiques (`/static/`) : WhiteNoise, ou dossier servi directement par Apache/LiteSpeed ;
   - photos (`/media/`) : `MEDIA_ROOT` dans un dossier servi par le serveur web (sous `public_html` ou lien symbolique), avec règle `.htaccess` ; jamais servies par Django ;
   - vérifier les droits du dossier d'upload et la taille max d'upload ;
   - documenter la procédure dans `deploiement.md`.
11. Docker (web + MariaDB 10.11 + redis), `docker compose`, CI/CD GitHub Actions (ruff, migrations check, tests, déploiement).

## Done
- [x] Version cible : **Django 5.2 LTS** (décidé par Gabriel le 2026-10-26).
