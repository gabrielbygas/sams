# docs.md — SAMS

Journal d'apprentissage de la refonte (méthode Junior). Chaque point du plan ajoute une section : **quoi**, **comment** (code), **pourquoi**, explication en 3 niveaux (simple → expert).

## Ce qui a changé dans Django depuis 5.0 (rappel après 2 ans)

- **5.1** : `LoginRequiredMiddleware`, tag `{% querystring %}`, `STORAGES` obligatoire (anciens settings de stockage supprimés).
- **5.2 (LTS)** : clés primaires composites (`CompositePrimaryKey`), `shell` qui importe les modèles automatiquement.
- **6.0** : Python 3.12+ requis, `BigAutoField` par défaut, **CSP natif**, **template partials**, **framework de tâches `django.tasks`**, API email moderne.
- **6.1** : `QuerySet.fetch_mode()` (anti N+1), `on_delete=DB_CASCADE`, setting `MAILERS`, passage annoncé au calendar versioning (« Django 2028 »).

Détails et règles : skill `bp-django`. Version retenue pour SAMS : **5.2 LTS** (support jusqu'à avril 2028).

---

## Point 1 — Hygiène du dépôt (2026-10-26)

**Quoi :** le dépôt public contenait la `SECRET_KEY`, le mot de passe MySQL, le virtualenv (6 801 fichiers), des photos d'utilisateurs, `db.sqlite3` et des fichiers générés. Résultat : secrets changés, plus rien de sensible ni dans le code ni dans l'historique, dépôt passé de 32 Mo à 1,5 Mo.

### 1.1 — `.gitignore`
**Comment :** modèle Python de GitHub, adapté au projet (`staticfiles/`, `mediafiles/`).

| Syntaxe | Effet |
|---|---|
| `nom/` | dossiers seulement |
| `nom` | fichier **ou** dossier (`.env` couvre les deux) |
| `*.pyc` | ce motif dans tous les sous-dossiers |
| `!motif` | ré-autorise ce qu'une règle a exclu |

Vérifier :
```bash
git check-ignore -v --no-index .env staticfiles/x
```
**Piège :** sans `--no-index`, `check-ignore` n'affiche **rien** pour les fichiers déjà suivis.

**Pourquoi :** un modèle trouvé en ligne est un point de départ ; il faut le lire et l'adapter aux noms réels du projet (ici `mediafiles/`, pas `media/`).

### 1.2 — Retirer du suivi sans supprimer
```bash
git rm -r --cached .env staticfiles mediafiles .vscode db.sqlite3
git rm -r --cached --quiet -- '*/__pycache__/*'
git commit --amend --no-edit     # OK tant que la branche n'est pas poussée
```
- `--cached` agit sur l'**index** (la liste des fichiers suivis), pas sur le disque.
- Un `.gitignore` n'a **aucun effet** sur un fichier déjà suivi : il faut d'abord le retirer de l'index.

### 1.3 — Secrets dans les variables d'environnement
```python
# sams/settings.py
import environ

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")                 # plante au démarrage si absente : voulu
DEBUG = env.bool("DEBUG", default=False)       # par défaut, la valeur sûre
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])
DATABASES = {"default": {
    "ENGINE": "django.db.backends.mysql",
    "NAME": env("DB_NAME"), "USER": env("DB_USER"), "PASSWORD": env("DB_PASSWORD"),
    "HOST": env("DB_HOST", default="localhost"), "PORT": env("DB_PORT", default="3306"),
}}
```
- `.env` (ignoré, valeurs réelles) et `.env.example` (commité, mêmes clés, valeurs factices, format `CLE=valeur`).
- Un virtualenv **ne se déplace pas** : il contient des chemins absolus. L'ancien, créé pour Python 3.10 dans le projet `shis`, a été recréé avec `uv venv .venv --python 3.12`.

**3 niveaux**
1. *Simple :* le code dit « va chercher la clé dans le tiroir » au lieu d'écrire la clé dans le code. Le tiroir (`.env`) ne quitte jamais ta machine.
2. *Intermédiaire :* c'est le facteur III des *12-Factor Apps* : la config varie selon l'environnement (dev, prod), le code non. Le même code tourne partout, avec un `.env` différent.
3. *Expert :* en prod, les variables viennent de l'orchestrateur (Docker secrets, variables de la plateforme) plutôt que d'un fichier. `django-environ` lit `os.environ` en priorité, donc le code ne change pas.

### 1.4 — Rotation des secrets et moindre privilège
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```
- Préférer `token_urlsafe` à `get_random_secret_key()` : une valeur qui commence par `$` est interprétée par `django-environ` comme une référence à une autre variable.

```sql
-- utilisateur dédié au projet, droits sur SA base uniquement
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'djangouser'@'localhost';
GRANT ALL PRIVILEGES ON `sams`.*      TO 'djangouser'@'localhost';
GRANT ALL PRIVILEGES ON `test_sams`.* TO 'djangouser'@'localhost';  -- base des tests Django
```
**Pourquoi :** un secret publié doit être **changé** ; l'effacer ne suffit pas (copies, forks, caches). Le moindre privilège limite les dégâts : si SAMS est compromis, l'attaquant n'obtient que la base `sams`, pas `FILE`/`SUPER` sur tout le serveur.

### 1.5 — Réécrire l'historique avec `git filter-repo`
Chaque commit est une photo complète du projet. Retirer un fichier aujourd'hui ne l'efface pas des anciennes photos. `filter-repo` repasse sur **toutes** les photos.

```bash
git clone --mirror /var/www/html/sams ~/backups/sams-avant-filter-repo.git   # 1. sauvegarde
git clone --no-local /var/www/html/sams ~/sams-clean                         # 2. clone neuf
cd ~/sams-clean
# 3. ~/secrets-a-effacer.txt : décrire la forme du secret, sans le recopier
#    regex:SECRET_KEY = 'django-insecure-[^']*'==>SECRET_KEY = 'REMOVED'
#    regex:'PASSWORD': '[^']*'==>'PASSWORD': 'REMOVED'
git filter-repo --invert-paths --path .env --path staticfiles --path mediafiles \
  --path .vscode --path db.sqlite3 --path-glob '*/__pycache__/*' \
  --replace-text ~/secrets-a-effacer.txt                                      # 4. nettoyage
git log --all -p | grep -c "django-insecure"                                 # 5. doit afficher 0
git remote add origin https://github.com/gabrielbygas/sams.git
git push --force-with-lease=main:<SHA complet de 40 caractères> origin main  # 6. remplace GitHub
```
Puis, dans le dossier de travail :
```bash
git fetch origin && git reset --hard origin/main
git reflog expire --expire=now --all && git gc --prune=now
```

| Notion | À retenir |
|---|---|
| Nouveaux SHA | une photo modifiée est une nouvelle photo, d'où le force push |
| `--force-with-lease=main:<sha>` | écrase **seulement si** GitHub est encore à `<sha>` ; demande le SHA **complet** quand l'ancien commit n'existe plus en local |
| `reflog` + `gc` | sans ces commandes, les anciens commits restent sur le disque |
| Preuve | même empreinte `HEAD^{tree}` avant et après : le présent n'a pas changé, seul le passé a été réécrit |
| Limite | GitHub garde en cache les commits orphelins (accessibles par leur SHA) : seul GitHub Support peut les purger |

**3 niveaux**
1. *Simple :* on réimprime tout l'album photo en gommant les secrets, puis on remplace l'album de GitHub.
2. *Intermédiaire :* un commit = un hash de son contenu et de son parent. Changer un vieux commit change son hash et celui de tous ses descendants : l'historique devient incompatible, donc force push, et tout clone existant doit être réaligné (`reset --hard`).
3. *Expert :* `filter-repo` réécrit le flux `fast-export`/`fast-import`. Les objets d'origine survivent dans les reflogs, les clones, les forks et les caches de l'hébergeur. La rotation reste donc la vraie mesure de sécurité ; la réécriture réduit l'exposition.

### ⚠️ Incident : Git a écrasé des fichiers ignorés
Le `git switch main` de l'étape 0 a sorti l'ancien commit `f136ddd`, qui **suivait** un dossier `.env/`. Git considère les fichiers ignorés comme **jetables** : il a remplacé le vrai fichier `.env` sans prévenir. Le retour au nouveau commit a ensuite supprimé `mediafiles/`, `staticfiles/` et `.vscode/`.

**Récupération :** depuis la sauvegarde, avec
```bash
git -C ~/backups/sams-avant-filter-repo.git archive f136ddd mediafiles .vscode | tar -x -C .
```
puis `.env` recréé et `collectstatic`.

**Leçons :**
- Pour déplacer une branche sans toucher aux fichiers : `git branch -f main <autre-branche>`.
- Avant toute manip d'historique, copier les fichiers ignorés précieux (`.env`, médias) **hors** du dépôt.
- Toujours avoir une copie des secrets dans un gestionnaire de mots de passe.