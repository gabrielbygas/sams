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

---

## Point 2 — Django 5.2 LTS + uv

### 2.1 — Passer à `uv` (2026-10-26)

#### Le problème que uv résout
Avant, le projet avait un `requirements.txt` de 10 lignes écrit à la main (ou par `pip freeze`) :

```
asgiref==3.7.2           ← dépendance de Django, pas du projet
Django==5.0.3            ← vraie dépendance
django-livereload-server ← outil de dev, installé en prod aussi
mysql==0.0.3             ← inutile
mysql-connector-python   ← inutile (doublon de mysqlclient)
mysqlclient==2.2.4       ← vraie dépendance
...
```

Quatre défauts :
1. **On ne sait plus ce qu'on a demandé.** Les dépendances directes (Django) et transitives (asgiref, que Django installe tout seul) sont mélangées. Impossible de savoir si `sqlparse` peut être supprimé.
2. **Rien ne fixe la version de Python.** Le virtualenv avait été créé en 3.10 ; le système est passé en 3.12 et l'a cassé.
3. **Pas de garantie d'intégrité.** Rien ne prouve que le paquet téléchargé demain est le même qu'aujourd'hui.
4. **Tout est manuel :** créer le venv, l'activer, `pip install`, `pip freeze`… et `pip` est lent.

`uv` (de la société Astral, qui fait aussi Ruff) remplace en un seul outil `pip`, `venv`, `pip-tools`, `pyenv` et en partie Poetry. Il est écrit en Rust, donc 10 à 100 fois plus rapide que pip.

#### Les 4 éléments d'un projet uv

| Élément | Rôle | Qui l'écrit | Dans Git ? | Équivalent Laravel |
|---|---|---|---|---|
| `pyproject.toml` | ce que **tu** demandes, avec des fourchettes de versions | toi, via `uv add` | ✅ | `composer.json` |
| `uv.lock` | les versions **exactes** de **tout** l'arbre + empreintes sha256 | uv, automatiquement | ✅ | `composer.lock` |
| `.python-version` | la version de Python du projet | `uv python pin` | ✅ | `"php": "^8.3"` dans `composer.json` |
| `.venv/` | l'installation réelle, reconstruite à partir de `uv.lock` | `uv sync` | ❌ | `vendor/` |

**Règle d'or :** `.venv/` est jetable. Tu peux le supprimer à tout moment, `uv sync` le recrée à l'identique à partir de `uv.lock`. C'est exactement ce qu'on a fait.

#### Lire `pyproject.toml`
```toml
[project]
name = "sams"                  # nom du projet (sert peu pour une app)
version = "0.1.0"              # version du projet (idem)
requires-python = ">=3.12"     # versions de Python acceptées
dependencies = [               # SEULEMENT les dépendances directes
    "django>=5.0,<5.1",        # fourchette écrite par toi : toute la série 5.0.x
    "django-environ>=0.14.0",  # borne basse ajoutée par uv add
    "mysqlclient>=2.3.0",
    "pillow>=13.0.0",
]
```

Les spécificateurs de version :

| Écriture | Accepte | Usage |
|---|---|---|
| `>=5.0,<5.1` | 5.0.0 → 5.0.99, pas 5.1 | rester sur une série (correctifs de sécurité uniquement) |
| `>=0.14.0` | 0.14.0 et toutes les suivantes | ce qu'écrit `uv add` par défaut |
| `~=5.2.0` | 5.2.x (équivaut à `>=5.2.0,<5.3`) | forme courte de la première ligne |
| `==5.0.3` | exactement 5.0.3 | à éviter dans `pyproject.toml` : c'est le rôle du lock |

**Pourquoi Django est passé de 5.0.3 à 5.0.14 :** la fourchette `>=5.0,<5.1` autorise toute la série, et uv a pris le dernier correctif. Ce sont 11 versions de **correctifs de sécurité et de bugs**, sans changement de fonctionnalités : c'est une bonne chose.

#### Lire `uv.lock`
```toml
[[package]]
name = "django"
version = "5.0.14"                                   # version EXACTE choisie
dependencies = [
    { name = "asgiref" },
    { name = "sqlparse" },
    { name = "tzdata", marker = "sys_platform == 'win32'" },   # seulement sous Windows
]
wheels = [{ url = "...", hash = "sha256:e762bef8…" }]  # empreinte : uv refuse un fichier modifié
```
- Le lock a **8** entrées alors que `uv pip list` montre **6** paquets : `sams` est le projet lui-même, et `tzdata` n'est installé que sous Windows (`marker`). Le lock décrit **toutes** les plateformes ; le `.venv` ne contient que ce qu'il faut pour ta machine.
- On ne modifie **jamais** `uv.lock` à la main.

#### Directes vs transitives : `uv tree`
```
sams v0.1.0
├── django v5.0.14          ← direct (dans pyproject.toml)
│   ├── asgiref v3.13.0     ← transitif : Django en a besoin, pas toi
│   └── sqlparse v0.6.0     ← transitif
├── django-environ v0.14.0
├── mysqlclient v2.3.0
└── pillow v13.0.0
```
Si un jour tu retires Django, uv retire aussi `asgiref` et `sqlparse`. Avec `requirements.txt`, ils seraient restés pour toujours.

#### Ce qu'on a fait, commande par commande
| Commande | Effet |
|---|---|
| `uv init --bare --python 3.12` | crée **seulement** `pyproject.toml` (sans fichier exemple ni README) |
| `uv python pin 3.12` | crée `.python-version` ; uv téléchargera ce Python s'il manque |
| `uv add "django>=5.0,<5.1" django-environ mysqlclient pillow` | écrit dans `pyproject.toml` → calcule `uv.lock` → installe dans `.venv` |
| `rm -rf .venv && uv sync` | repart de zéro : installe **exactement** le lock, rien d'autre |
| `uv pip list` | ce qui est réellement installé |
| `uv run python manage.py check` | lance la commande dans `.venv`, sans `source .venv/bin/activate` |
| `git rm requirements.txt` | plus de source de vérité en double |

#### Aide-mémoire du quotidien
| Je veux… | pip (avant) | uv (maintenant) |
|---|---|---|
| installer le projet après un `git clone` | `python -m venv .venv && source … && pip install -r requirements.txt` | `uv sync` |
| ajouter un paquet | `pip install X && pip freeze > requirements.txt` | `uv add X` |
| ajouter un outil de dev seulement | (pas de séparation) | `uv add --dev X` |
| retirer un paquet | `pip uninstall X` + éditer le fichier à la main | `uv remove X` |
| mettre à jour un paquet dans sa fourchette | `pip install -U X` + freeze | `uv lock --upgrade-package X && uv sync` |
| lancer une commande | activer le venv puis `python …` | `uv run python …` |
| voir l'arbre | — | `uv tree` |

#### ⚠️ Piège rencontré : `.python-version` ignoré
Le `.gitignore` copié du modèle GitHub contient `.python-version` (ligne 84). Son commentaire l'explique : c'est utile pour une **bibliothèque** (testée sur plusieurs versions de Python), mais pour une **application**, la version de Python fait partie du projet et doit être commitée. Sinon, un collègue (ou le CI, ou Docker) prendrait une autre version.

#### Explication en 3 niveaux
1. *Simple :* `pyproject.toml` est ta **liste de courses** (« du lait, n'importe quelle marque »). `uv.lock` est le **ticket de caisse** (« lait Natrel 2 %, 2 L, code-barres 123… »). Avec le ticket, n'importe qui rachète exactement les mêmes produits. `.venv` est le **frigo** : on peut le vider et le remplir de nouveau à partir du ticket.
2. *Intermédiaire :* on sépare **l'intention** (fourchettes dans `pyproject.toml`) de **la résolution** (versions exactes dans `uv.lock`). Les mises à jour deviennent des décisions explicites (`uv lock --upgrade`) et visibles dans un diff Git, au lieu d'arriver par surprise à la prochaine installation. Les dépendances de dev (`--dev`) ne sont pas installées en prod (`uv sync --no-dev`).
3. *Expert :* `pyproject.toml` suit les standards PEP 621 (métadonnées) et PEP 508 (spécificateurs et *markers*). Le lock est **universel** : il résout l'arbre pour toutes les plateformes et versions de Python couvertes par `requires-python`, puis `uv sync` n'installe que le sous-ensemble utile. Les empreintes sha256 protègent contre la substitution de paquets (attaque de la chaîne d'approvisionnement). En CI et en Docker, `uv sync --frozen` échoue si le lock n'est plus à jour par rapport à `pyproject.toml` : le build est reproductible ou il échoue, jamais entre les deux.

### 2.2 — Django 5.2 LTS + Python 3.13 (2026-10-26)

**Pourquoi en deux temps (2.1 puis 2.2) :** changer d'outil **et** de versions en même temps, c'est ne plus savoir laquelle des deux étapes a cassé le projet. Une variable à la fois.

**Pourquoi 5.2 LTS plutôt que 6.1 :** une LTS (*Long Term Support*) reçoit les correctifs de sécurité pendant environ 3 ans (5.2 : jusqu'en avril 2028), contre environ 16 mois pour une version normale. Pour une app qu'on veut stable, c'est moins de montées de version.

```bash
uv python pin 3.13                 # .python-version → 3.13 (uv télécharge Python s'il manque)
# pyproject.toml, à la main : requires-python = ">=3.13"
uv add "django>=5.2,<5.3"          # remplace la fourchette ; uv.lock recalculé
uv sync                            # .venv en 3.12 ≠ 3.13 demandé → uv le recrée tout seul
```

Vérifications d'une montée de version, **dans cet ordre** :

| Commande | Ce qu'elle prouve | Résultat SAMS |
|---|---|---|
| `uv run python -Wd manage.py check` | config valide ; `-Wd` affiche les dépréciations, cachées par défaut | 0 problème, 0 avertissement |
| `makemigrations --check --dry-run` | la nouvelle version ne demande pas de modifier les modèles | `No changes detected` |
| `migrate` | les apps de Django (`auth`, `admin`…) n'ont pas de nouvelles migrations | rien à appliquer |
| test manuel des 3 rôles avec `runserver -Wd` | les écrans marchent ; les dépréciations s'affichent quand le code concerné s'exécute | OK |

**Lire les notes de version avant :** sur https://docs.djangoproject.com/en/5.2/releases/5.2/, la section *Backwards incompatible changes*. Pour SAMS, seul point à vérifier : les connexions MySQL/MariaDB passent en `utf8mb4` (vrai UTF-8, émojis compris). La base l'était déjà :
```sql
SELECT @@character_set_database;   -- utf8mb4
```

**Pourquoi la connexion était impossible :** les comptes créés dans l'admin avaient leur mot de passe **en clair**, parce que `CustomUserAdmin` hérite de `ModelAdmin`, qui enregistre le champ tel quel. Django hache le mot de passe saisi puis compare : une valeur en clair ne correspond jamais. Contournement : `manage.py changepassword <email>`, qui hache. Correctif : point 3.1.

### 2.3 — Ruff et pip-audit (2026-10-26)

```bash
uv add --dev ruff pip-audit        # groupe "dev" : absent en prod (uv sync --no-dev)
```
```toml
[tool.ruff]
target-version = "py313"           # propose la syntaxe moderne
line-length = 100
extend-exclude = ["*/migrations/*"]  # fichiers générés par Django

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "DJ"]
```

| Famille | Détecte | Exemple dans SAMS |
|---|---|---|
| `E` | style (pycodestyle) | `E501` ligne > 100 colonnes (64) |
| `F` | bugs évidents (pyflakes) | `F401` import inutile (25), `F811` nom redéfini (1) |
| `I` | ordre des imports (isort) | `I001` (22) |
| `B` | bugs probables (bugbear) | — |
| `UP` | syntaxe dépassée (pyupgrade) | — |
| `DJ` | mauvaises pratiques Django | `DJ001` `CharField(null=True)` (5) : deux « vides » possibles, `NULL` et `""` → utiliser `blank=True` seul ; `DJ012` ordre des éléments d'un modèle (2) |

Commandes :
```bash
uv run ruff check . --statistics   # résumé par règle
uv run ruff rule DJ001             # explication d'une règle
uv run ruff check --fix .          # corrige ce qui est marqué [*] (sans risque)
uv run ruff format --check .       # montre sans modifier
uv run pip-audit                   # compare les versions installées à la base des CVE connues
```

**Linter ≠ formateur :**
- `ruff check` cherche des **problèmes** (un import inutile peut cacher une erreur).
- `ruff format` impose un **style** (guillemets doubles, coupures de lignes), sans rien changer au comportement.

**Pourquoi le formatage dans un commit séparé :** `ruff format` touche 30 fichiers. Mélangé à un correctif, ce diff noierait les 3 lignes qui comptent, et la revue deviendrait impossible. Un commit « Apply Ruff formatting » isolé se relit en un coup d'œil (« rien que du style ») et peut être ignoré par `git blame` (`.git-blame-ignore-revs`).

**3 niveaux**
1. *Simple :* Ruff est un correcteur d'orthographe pour le code ; pip-audit vérifie qu'aucune pièce du projet n'est rappelée par le fabricant.
2. *Intermédiaire :* on automatise ce qu'une revue humaine ferait mal (style, imports) pour qu'elle se concentre sur la logique ; au point 10, les deux tourneront en CI et bloqueront un merge.
3. *Expert :* Ruff réimplémente en Rust plus de 800 règles de flake8 et de ses plugins, isort, pyupgrade et black, avec un seul analyseur, d'où des temps en millisecondes. pip-audit interroge la base PyPA Advisory / OSV ; une alerte se traite en montant la version dans la fourchette (`uv lock --upgrade-package X`) ou en élargissant la fourchette.