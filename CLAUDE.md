# CLAUDE.md — SAMS (Student Appointment Management System)

## Méthode : Junior
- Claude : **lecture seule** sur le code. Écriture autorisée uniquement sur `CLAUDE.md`, `tasks.md`, `docs.md`, `deploiement.md`.
- Gabriel code à la main selon les orientations ; Claude explique, relit, propose les tests et commandes.
- `docs.md` riche (code, comment, pourquoi), mis à jour après chaque point du plan.
- Cycle : Plan → Gabriel développe → Tester → Gabriel valide.
- Skills à charger : `bp-django`, `bp-database`, `bp-git-security`.

## Projet
Gestion des rendez-vous d'un service de santé étudiant : les étudiants prennent rendez-vous (service, médecin, créneau), les médecins gèrent leurs rendez-vous, la réception publie des annonces.

- Dépôt : https://github.com/gabrielbygas/sams (branche `main`)
- Stack : **Python 3.13 + Django 5.2 LTS** (support jusqu'à avril 2028), **MariaDB 10.11** (driver `mysqlclient`, `ENGINE = django.db.backends.mysql`), Pillow, templates Django.
- Dépendances : **uv** (`pyproject.toml` + `uv.lock` + `.python-version`). Dev : Ruff, pip-audit.
- Config : variables d'environnement dans `.env` (jamais commité), lues par `django-environ` ; modèle dans `.env.example`.
- Utilisateur DB : `djangouser`, droits limités aux bases `sams` et `test_sams`.
- Suite de la refonte : comptes et rôles (point 3), Docker, CI/CD GitHub Actions (voir `tasks.md`).
- Règle métier : **un utilisateur = un seul rôle** (étudiant, médecin ou réceptionniste) ; le superuser a accès à tout.

## Commandes
```bash
uv sync                                          # installer / recréer .venv à partir de uv.lock
uv run python manage.py runserver
uv run python -Wd manage.py check                # avec les avertissements de dépréciation
uv run python manage.py makemigrations --check --dry-run
uv run python manage.py migrate
uv run ruff check . --statistics                 # lint
uv run ruff format --check .                     # formatage (pas encore appliqué : début du point 3)
uv run pip-audit                                 # vulnérabilités connues des dépendances
uv add <paquet> / uv add --dev <outil> / uv remove <paquet>
```

## Structure actuelle
| Dossier | Rôle |
|---|---|
| `sams/` | projet (settings unique, urls, vues home) |
| `account/` | `CustomUser` (login par email) + profils `Student`, `Doctor`, `Receptionist` |
| `student/` | `Appointment`, `Enquiry` |
| `doctor/` | `Service` |
| `receptionist/` | `Announcement` |
| `templates/` | gabarits communs (`header.html`, `sidebar.html`…) |
| `sams/static/` | sources des fichiers statiques (suivies par Git) |
| `staticfiles/`, `mediafiles/` | statiques collectés (`collectstatic`), uploads — ignorés par Git |
| `.venv/` | virtualenv géré par uv — ignoré par Git |
| `.env` | secrets et config locale — ignoré par Git |

## MLD (schéma réel MariaDB après `migrate`, 2026-10-26 — 34 migrations appliquées)

```mermaid
erDiagram
    account_customuser ||--o| account_student : "user_id (1-1, CASCADE)"
    account_customuser ||--o| account_doctor : "user_id (1-1, CASCADE)"
    account_customuser ||--o| account_receptionist : "user_id (1-1, CASCADE)"
    account_doctor ||--o{ account_doctor_service : "doctor_id"
    doctor_service ||--o{ account_doctor_service : "service_id"
    account_student ||--o{ student_appointment : "student_id (CASCADE)"
    doctor_service |o--o{ student_appointment : "service_id (SET NULL)"
    account_doctor |o--o{ student_appointment : "doctor_id (SET NULL)"
    account_student ||--o{ student_enquiry : "student_id (CASCADE)"
    account_doctor ||--o{ student_enquiry : "doctor_id (CASCADE)"
    account_receptionist ||--o{ receptionist_announcement : "posted_by_id (CASCADE)"

    account_customuser {
        int id PK
        string email UK
        string password
        string first_name
        string last_name
        date dob
        string phone
        string photo
        string sex
        bool is_active
        bool is_staff
        bool is_superuser
        datetime last_login
        datetime created_at
    }
    account_student {
        int id PK
        int user_id FK,UK
        string studentNumber UK
    }
    account_doctor {
        int id PK
        int user_id FK,UK
        string doctorNumber UK
    }
    account_receptionist {
        int id PK
        int user_id FK,UK
        string receptionistNumber UK
    }
    doctor_service {
        int id PK
        string name UK
    }
    account_doctor_service {
        int id PK
        int doctor_id FK
        int service_id FK
    }
    student_appointment {
        int id PK
        date date_appointment
        string time_schedule
        int student_id FK
        int service_id FK
        int doctor_id FK
        datetime created_at
    }
    student_enquiry {
        int id PK
        string question
        string answer
        bool is_answering
        int student_id FK
        int doctor_id FK
        datetime created_at
    }
    receptionist_announcement {
        int id PK
        date date_announcement
        string subject
        string message
        int posted_by_id FK
    }
```
Contraintes uniques : `unique_appointment_per_student_per_day` (`date_appointment`, `student_id`) ; (`doctor_id`, `service_id`) sur la table M2M.

## Contact
Gabriel KALALA 🇨🇩 — gabrielkalala@protonmail.com — https://gabrielkalala.com — https://github.com/gabrielbygas
