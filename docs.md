# docs.md — SAMS

Journal d'apprentissage de la refonte (méthode Junior). Chaque point du plan ajoute une section : **quoi**, **comment** (code), **pourquoi**, explication en 3 niveaux (simple → expert).

## Ce qui a changé dans Django depuis 5.0 (rappel après 2 ans)

- **5.1** : `LoginRequiredMiddleware`, tag `{% querystring %}`, `STORAGES` obligatoire (anciens settings de stockage supprimés).
- **5.2 (LTS)** : clés primaires composites (`CompositePrimaryKey`), `shell` qui importe les modèles automatiquement.
- **6.0** : Python 3.12+ requis, `BigAutoField` par défaut, **CSP natif**, **template partials**, **framework de tâches `django.tasks`**, API email moderne.
- **6.1** : `QuerySet.fetch_mode()` (anti N+1), `on_delete=DB_CASCADE`, setting `MAILERS`, passage annoncé au calendar versioning (« Django 2028 »).

Détails et règles : skill `bp-django`.