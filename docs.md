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

SECRET_KEY = env("SECRET_KEY")  # plante au démarrage si absente : voulu
DEBUG = env.bool("DEBUG", default=False)  # par défaut, la valeur sûre
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="3306"),
    }
}
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
## Point 3 — Comptes et rôles

### 3.0 — Commit de formatage seul (2026-10-26, commit `d9f4c44`)
- `ruff format .` (30 fichiers) puis `ruff check --fix .` (47 corrections sûres : imports inutilisés supprimés, imports triés). 11 erreurs restent volontairement (`DJ001`, `DJ012`, `E501`) : elles demandent une décision sur le modèle, pas du formatage.
- **Piège** : `git commit -am` aurait embarqué `docs.md` et `tasks.md`. On ajoute seulement le code : `git add -u -- '*.py'`.
- **Ordre à retenir** : `ruff check --fix` peut supprimer un import et laisser une ligne vide en trop → toujours relancer `ruff format .` **après** `--fix`. C'est ce qui est arrivé aux 4 `tests.py`.

### 3.1 — Admin et mots de passe hachés

#### Le problème, en une phrase
L'admin enregistrait `CustomUser` avec un `ModelAdmin` générique : le champ `password` était un simple champ texte, donc enregistré **en clair**, et `has_perm()` renvoyait `True` pour **tout le monde**.

#### Comment Django stocke un mot de passe
Django ne stocke jamais le mot de passe, mais une empreinte :
```
pbkdf2_sha256$1000000$sel_aleatoire$empreinte_base64
algorithme    itérations  sel        résultat
```
- `user.set_password("abc")` calcule cette chaîne ; `user.check_password("abc")` recalcule et compare.
- `authenticate()` appelle `check_password()`. Avec un mot de passe en clair dans la base, la comparaison échoue toujours → c'était la cause du « je n'arrive pas à me logger ».
- Vérifier une base : `django.contrib.auth.hashers.identify_hasher(u.password)` lève une erreur si la chaîne n'est pas une empreinte. Contrôle du 2026-10-26 : 5 comptes, **0 en clair** (les `changepassword` du point 2 ont suffi, pas de re-hachage à faire).

#### Pourquoi `UserAdmin` plutôt que `ModelAdmin`
`django.contrib.auth.admin.UserAdmin` apporte trois choses qu'on ne veut pas réécrire :

| Élément | Rôle |
|---|---|
| `add_form` (`AdminUserCreationForm`) | 2 champs mot de passe + confirmation, validateurs (`AUTH_PASSWORD_VALIDATORS`), appel de `set_password()` |
| `form` (`UserChangeForm`) | le champ `password` est affiché **en lecture seule** (algorithme + extrait de l'empreinte) avec un lien « Réinitialiser le mot de passe » |
| `change_password_form` (`AdminPasswordChangeForm`) | la page de **reset par l'admin** demandée au point 3 |

Mais `UserAdmin` est écrit pour le `User` par défaut : il référence `username`, `date_joined`… qui n'existent pas chez nous. On garde la classe et on **redéfinit** tout ce qui cite ces champs : `fieldsets`, `add_fieldsets`, `list_display`, `search_fields`, `ordering`, ainsi que les deux formulaires (leur `Meta.model` vaut `User`).

#### Pourquoi `PermissionsMixin` en même temps
`PermissionsMixin` ajoute à `CustomUser` :
- le champ `is_superuser` (on supprime le nôtre, en double) ;
- deux relations M2M : `groups` et `user_permissions` (2 nouvelles tables) ;
- les vraies méthodes `has_perm()`, `has_module_perms()`, `get_all_permissions()` : un superuser actif a tout, les autres seulement ce qu'on leur donne.

`UserAdmin` a `filter_horizontal = ("groups", "user_permissions")` : sans le mixin, ces champs n'existent pas et l'admin plante. Les deux changements vont donc ensemble.

#### Le code (à écrire par Gabriel)

`account/models.py`
```python
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ...
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    # is_superuser : supprimé, fourni par PermissionsMixin

    # has_perm() et has_module_perms() : supprimés, fournis par PermissionsMixin
```

`account/forms.py` (formulaires **réservés à l'admin**, distincts de ceux du site)
```python
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm, UserCreationForm


class CustomUserAdminCreationForm(AdminUserCreationForm):
    class Meta(AdminUserCreationForm.Meta):
        model = CustomUser
        fields = ("email", "first_name", "last_name")
        field_classes = {}  # le parent déclare un champ "username" qu'on n'a pas


class CustomUserAdminChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = "__all__"
        field_classes = {}
```
- `class Meta(Parent.Meta)` : on hérite des réglages du parent et on ne change que le modèle et les champs.
- Le `UserChangeForm` déjà importé dans ce fichier (pour `CustomUserChangeForm`) sert aux deux.

`account/admin.py`
```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserAdminChangeForm, CustomUserAdminCreationForm
from .models import CustomUser, Doctor, Receptionist, Student


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserAdminCreationForm
    form = CustomUserAdminChangeForm

    list_display = ("email", "first_name", "last_name", "is_staff", "is_active", "created_at")
    list_filter = ("is_staff", "is_superuser", "is_active", "sex")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    readonly_fields = ("last_login", "created_at")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Informations personnelles",
            {"fields": ("first_name", "last_name", "dob", "phone", "photo", "sex")},
        ),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Dates", {"fields": ("last_login", "created_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "usable_password",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
```
- `fieldsets` = page de **modification** ; `add_fieldsets` = page de **création**. Ce sont deux formulaires différents.
- `created_at` a `auto_now_add=True`, donc il n'est pas modifiable : il doit être dans `readonly_fields`, sinon l'admin lève une `FieldError`.
- `usable_password` (Django 5.1+) : case « mot de passe utilisable ou non », utile pour un compte qui ne doit pas se connecter.
- On supprime `list_editable` : modifier l'email depuis la liste, sans page de confirmation, est trop risqué pour un identifiant de connexion.

#### La migration
```bash
uv run python manage.py makemigrations account
uv run python manage.py sqlmigrate account 0007   # lire le SQL avant de l'exécuter
uv run python manage.py migrate
```
Attendu : création de `account_customuser_groups` et `account_customuser_user_permissions`, modification (texte d'aide seulement) de `is_superuser`. Aucune donnée perdue.

#### ⚠️ Effet de bord à connaître
Avant : `has_perm()` → `True`, donc tout compte `is_staff` voyait et modifiait **tout** dans l'admin. Après : un compte `is_staff` non superuser n'a plus que les permissions qu'on lui donne. Dans la base, 1 compte est dans ce cas : il verra un admin vide jusqu'à ce qu'on lui attribue un groupe. C'est le comportement voulu (moindre privilège).

#### Explication en 3 niveaux
- **Simple** : on remplace un formulaire « fait maison » par celui de Django, qui sait chiffrer les mots de passe et gérer les droits.
- **Intermédiaire** : `UserAdmin` + `PermissionsMixin` = hachage via `set_password()`, reset par l'admin via `AdminPasswordChangeForm`, permissions réelles via groupes et `user_permissions`. On adapte seulement ce qui cite `username`.
- **Expert** : `AbstractBaseUser` ne fournit que l'authentification (mot de passe, `last_login`) ; l'autorisation vient de `PermissionsMixin`, qui délègue à `AUTHENTICATION_BACKENDS` (`ModelBackend` : permissions mises en cache sur l'objet user, court-circuit `is_active and is_superuser`). Renvoyer `True` dans `has_perm()` désactivait toute la couche d'autorisation de Django, admin compris.

**Résultat** : commit `7522c5e`. Migration `account.0007` (2 tables M2M), lien « Reset password » sur la fiche d'un utilisateur (`/admin/account/customuser/<id>/change/` → bouton sous *Password* → `…/<id>/password/`).

### 3.2 — Un seul rôle par utilisateur

> **Comment lire cette section.** Elle est longue exprès. Lis d'abord la partie 1 (comment ton code est organisé), puis la partie 2 (les notions Python dont on a besoin). La partie 4 te donne les corrections **une par une**, avec le code *avant* et *après*. Ne saute pas la partie 1 : c'est elle qui rend le reste compréhensible.

---

#### Partie 1 — Comprendre ton code avant de le modifier

##### 1.1 Le trajet d'une requête
Quand un médecin ouvre `http://127.0.0.1:8000/doctors/appointment/list/`, voici ce qui se passe, dans l'ordre :

```
Navigateur : GET /doctors/appointment/list/
   │
   ▼
① sams/urls.py          path("doctors/", include("doctor.urls"))
   │                    → « tout ce qui commence par doctors/ est géré par doctor/urls.py »
   ▼
② doctor/urls.py        path("appointment/list/", AppointmentListView.as_view(), name="list-appointment")
   │                    → « cette adresse appelle la vue AppointmentListView »
   ▼
③ doctor/views.py       @method_decorator(login_required, ...)        ← connecté ?   sinon → page de login
   │                    @method_decorator(user_passes_test(...), ...) ← bon rôle ?   sinon → page d'erreur
   │                    class AppointmentListView(ListView): ...
   │                    → get_queryset() va chercher les rendez-vous en base
   ▼
④ template              doctor/templates/doctor/appointment_list.html → HTML renvoyé au navigateur
```

**À retenir** : les étapes ① et ② sont des *aiguillages* (fichiers `urls.py`), l'étape ③ est le *contrôle d'accès* puis le *travail* (fichier `views.py`), l'étape ④ est l'*affichage* (templates). Le point 3.2 touche surtout l'étape ③.

##### 1.2 Les 4 « espaces » de SAMS
| App (dossier) | Préfixe d'URL | Namespace (`app_name`) | Qui y a accès (règle voulue) |
|---|---|---|---|
| `account/` | `/accounts/` | `accounts` | login/logout : tout le monde ; créer un médecin : réception + admin ; créer un réceptionniste : admin |
| `student/` | `/students/` | `students` | étudiants + réception + admin |
| `doctor/` | `/doctors/` | `doctors` | médecins + réception + admin |
| `receptionist/` | `/receptionists/` | `receptionists` | réception + admin |

La réception voit les rendez-vous de tout le monde : c'est pour ça qu'elle a accès aux espaces étudiant et médecin. Dans `get_queryset()`, tu as déjà ce choix : `if user.is_student(): … seulement les siens … else: … tous …`.

##### 1.3 Où le rôle est vérifié
- **Dans les vues** : chaque vue protégée a un décorateur `user_passes_test(fonction_de_test, login_url="…:error-page")`.
- **Dans les templates** : `templates/sidebar.html` affiche le menu selon `{% if user.is_student %}`… (pas de sécurité ici, juste l'affichage).
- **Dans l'admin** : `account/admin.py`.

---

#### Partie 2 — Les notions Python et Django dont on a besoin

Chaque notion : une explication, un mini-exemple, et **où elle apparaît dans SAMS**.

##### 2.1 Attribut ou méthode : avec ou sans parenthèses ?
- Un **attribut** est une *valeur* stockée dans l'objet : `user.is_superuser` vaut `True` ou `False`. C'est un champ de la base.
- Une **méthode** est une *fonction* attachée à l'objet : `user.is_student` est une fonction ; `user.is_student()` l'**exécute** et renvoie `True`/`False`.

```python
user.is_superuser  # True        → attribut, pas de ()
user.is_superuser()  # TypeError: 'bool' object is not callable  → on essaie « d'appeler » True
user.is_student()  # True/False  → méthode, avec ()
user.is_student  # <bound method …>  → la fonction elle-même, toujours « vraie » dans un if !
```
**Comment savoir ?** Regarde `account/models.py` : `is_superuser` vient de `PermissionsMixin` et c'est un `models.BooleanField` → **attribut**. `is_student` est écrit `def is_student(self):` → **méthode**.

**Exception, dans les templates** : `{% if user.is_student %}` sans parenthèses est correct. Le moteur de templates de Django appelle les méthodes tout seul, et il interdit les `()`.

**Dans SAMS** : `account/views.py:173` contient `request.user.is_superuser()` → c'est l'erreur `TypeError` (vérifiée : la page `/accounts/user-creation-error-page/` plante pour tous les rôles).

##### 2.2 `not` ne s'applique qu'au terme qui le suit
```python
not A or B  # Python le lit :  (not A) or B
not (A or B)  # « ni A ni B »
```
Exemple concret avec un étudiant (A = `is_superuser` = False, B = `is_doctor()` = False) :
- `not A or B` → `(not False) or False` → `True or False` → **True** : le message d'erreur « Doctor is not allowed » s'affiche… à un étudiant.

**Dans SAMS** : `student/views.py:35`, `doctor/views.py:49`, `receptionist/views.py:34`. On va simplifier ces pages (partie 4, correction 5) : on n'aura plus besoin de ce `if`.

##### 2.3 Arguments positionnels et arguments nommés ⚠️ (bug n° 1 de ta modification)
Python associe les arguments **dans l'ordre** où la fonction les déclare, sauf si tu les nommes.

```python
def saluer(prenom, ville):
    print(f"{prenom} habite à {ville}")


saluer("Gabriel", "Kinshasa")  # Gabriel habite à Kinshasa
saluer("Kinshasa", "Gabriel")  # Kinshasa habite à Gabriel   ← aucune erreur, mais faux !
saluer(
    ville="Kinshasa", prenom="Gabriel"
)  # Gabriel habite à Kinshasa   ← nommés : l'ordre n'a plus d'importance
```

**Dans SAMS** : tu as (correctement) ajouté `role` **à la fin** de la signature :
```python
def create_user_view(request, user_form_class, custom_user_form_class, template_name, redirect_to, role):
```
mais tu l'as passé **en 4e position** dans `create_student` :
```python
create_user_view(
    request,
    CustomUserCreationForm,
    StudentForm,
    CustomUser.Role.STUDENT,  # → arrive dans template_name !
    "account/create_student.html",  # → arrive dans redirect_to !
    "students:home",
)  # → arrive dans role !
```
Résultat : Django cherche un template nommé `"student"`, trouve le **dossier** `student/templates/student/` et plante (`IsADirectoryError`, vérifié : `/accounts/create-student/` renvoie une erreur 500). Si la page avait marché, les comptes auraient été créés avec `role = "students:home"`.

**La règle à retenir** : dès qu'une fonction a plus de 3 paramètres, **nomme les arguments** à l'appel. C'est plus long à écrire, mais l'ordre ne peut plus te piéger et le code se lit tout seul.

##### 2.4 Deux fonctions du même nom : la dernière gagne
```python
def f():
    return 1


def f():  # remplace silencieusement la première
    return 2


f()  # 2
```
Python lit le fichier de haut en bas ; le 2e `def` écrase le 1er. Ruff le signale : `F811 Redefinition of unused 'is_receptionist'`.

**Dans SAMS** : `receptionist/views.py:22` (ta nouvelle version) puis `:27` (l'ancienne). C'est l'ancienne qui gagne → l'admin est refusé dans l'espace réception (vérifié).

##### 2.5 Les décorateurs et `user_passes_test`
Un **décorateur** est une fonction qui « enveloppe » une vue pour ajouter un contrôle avant elle. `@login_required` au-dessus d'une vue veut dire : « avant d'exécuter la vue, vérifie que l'utilisateur est connecté, sinon redirige vers le login ».

`user_passes_test(test, login_url=...)` est un décorateur **qu'on configure** :
```python
def can_access_doctor_space(user):  # 1. une fonction qui reçoit l'utilisateur
    return user.has_role(...)  #    et renvoie True (accès OK) ou False (refusé)


@user_passes_test(can_access_doctor_space, login_url="doctors:error-page")
#                 ▲ on passe la fonction SANS () : c'est Django qui l'appellera, avec request.user
def ma_vue(request): ...
```
- Si `can_access_doctor_space(request.user)` renvoie `True` → la vue s'exécute.
- Si `False` → redirection vers l'URL nommée `doctors:error-page`.

**Pourquoi `method_decorator`** : tes vues `ListView`, `DetailView`… sont des **classes**, pas des fonctions. `user_passes_test` ne sait décorer que des fonctions. `@method_decorator(..., name="dispatch")` l'applique à la méthode `dispatch()` de la classe, celle que Django appelle en premier pour chaque requête.

**Dans SAMS** : `doctor/views.py:55, 87, 119, 140, 148, 184` et `student/views.py:42, 79, 88, 110, 123, 181, 222` utilisent encore les anciennes fonctions `is_not_student` / `is_not_doctor`. Tu as bien **créé** `can_access_doctor_space` et `can_access_student_space`, mais tu ne les as **branchées** nulle part : elles ne servent à rien pour l'instant.

##### 2.6 Les noms d'URL : `"doctors:error-page"`
On ne met jamais d'adresse en dur (`"/doctors/error-page/"`) dans le code. On met un **nom**, que Django traduit en adresse (c'est `reverse()`).
- `doctors` = le `app_name = "doctors"` en haut de `doctor/urls.py` (le *namespace*) ;
- `error-page` = le `name="error-page"` d'un `path(...)` de ce fichier.

Si le nom n'existe pas, Django lève `NoReverseMatch: Reverse for 'error-page' not found`.

**Dans SAMS — bug ancien, pas de toi** : `doctor/views.py` et `receptionist/views.py` redirigent vers `doctors:error-page` et `receptionists:error-page`, et les vues `doctor_error_page` / `receptionist_error_page` existent avec leurs templates… mais **personne ne les a ajoutées dans les `urls.py`**. Seul `student/urls.py:47` a sa ligne. Conséquence vérifiée : un étudiant qui ouvre une page médecin obtient une **erreur 500** au lieu de la page d'erreur.

##### 2.7 `TextChoices`, `*roles` et le mixin (ce que tu as déjà écrit)
- **`TextChoices`** : une liste fermée de valeurs. `CustomUser.Role.STUDENT` vaut `"student"` en base. Équivalent d'un `enum` PHP 8.1 (`enum Role: string`). Une faute de frappe (`Role.STUDNET`) plante tout de suite, alors qu'une chaîne `"studnet"` passerait sans bruit.
- **`def has_role(self, *roles)`** : l'étoile veut dire « autant d'arguments que tu veux », regroupés dans un tuple. `user.has_role(Role.DOCTOR, Role.RECEPTIONIST)` → `roles = ("doctor", "receptionist")`, puis `self.role in roles` teste l'appartenance.
- **Le mixin `RoleProfileMixin`** : une petite classe qui n'est pas un modèle, juste un « morceau de comportement » (ici la méthode `clean()`) qu'on ajoute à `Student`, `Doctor`, `Receptionist` au lieu de l'écrire 3 fois. Il se met **avant** `models.Model` : `class Student(RoleProfileMixin, models.Model)`.

##### 2.8 `with transaction.atomic():` et l'indentation
```python
with transaction.atomic():
    a()  # ┐ dans le bloc : si b() plante, a() est annulé en base
    b()  # ┘
c()  # hors du bloc (pas indenté) : pas protégé
```
En Python, c'est **l'indentation** (les 4 espaces) qui dit ce qui est dans le bloc. Pas d'accolades comme en PHP.

**Dans SAMS** : `account/views.py`, l'ajout des services du médecin (`custom_user.service.add(...)`) est **sous** le `with`, mais pas indenté → hors de la transaction. Si l'ajout d'un service plante, le médecin reste créé sans ses services. Il faut l'indenter de 4 espaces de plus.

---

#### Partie 3 — Ce que tu as déjà réussi ✅
Vérifié par Claude le 2026-10-27 :

| Élément | Preuve |
|---|---|
| Migrations `0008` (champ), `0009` (données), `0010` (contrainte) | `showmigrations account` : `[X]` sur les trois |
| Data migration | 2 `student`, 2 `doctor`, 1 `receptionist`, le superuser à `""` → exactement les profils existants |
| Contrainte en base | MariaDB : `role_required_unless_superuser` = `` `is_superuser` = 0x01 or `role` <> '' `` |
| Manager réécrit, `TextChoices`, `has_role()`, `RoleProfileMixin` | code conforme ; `check` OK, `makemigrations --check` : rien d'oublié |
| Admin : rôle affiché, filtrable, figé après création | `get_readonly_fields` correct |
| `transaction.atomic()`, `create_user(user_form, role)` | bonne idée, à finir (correction 7) |

Les parties « modèle » et « base de données » sont **terminées**. Il reste les vues.

---

#### Partie 4 — Rapport de vérification et corrections pas à pas

##### Comment j'ai testé
J'ai simulé des visites avec le client de test de Django, connecté successivement comme anonyme, étudiant, médecin, réceptionniste et admin. Tu peux refaire ce test toi-même (voir partie 5). Résultat **actuel** :

| Page | anonyme | étudiant | médecin | réception | admin |
|---|---|---|---|---|---|
| `/accounts/create-student/` | **500** | **500** | **500** | **500** | **500** |
| `/students/appointment/list/` | → login | 200 | → page d'erreur | 200 | 200 |
| `/doctors/appointment/list/` | → login | **500** | 200 | 200 | 200 |
| `/receptionists/announcement/list/` | → login | **500** | **500** | 200 | **500** |
| `/accounts/user-creation-error-page/` | → login | **500** | **500** | **500** | **500** |

##### Les 8 corrections, de la plus grave à la plus simple

| # | Fichier | Problème | Notion |
|---|---|---|---|
| 1 | `account/views.py` `create_student/doctor/receptionist` | arguments dans le mauvais ordre → création de compte cassée | 2.3 |
| 2 | `doctor/urls.py`, `receptionist/urls.py` | URL `error-page` manquante → 500 (bug ancien) | 2.6 |
| 3 | `receptionist/views.py:27` | `is_receptionist` défini 2 fois | 2.4 |
| 4 | `doctor/views.py`, `student/views.py` | nouvelles fonctions pas branchées | 2.5 |
| 5 | 3 pages d'erreur | logique `not A or B` | 2.2 |
| 6 | `account/views.py:173` | `is_superuser()` → `TypeError` | 2.1 |
| 7 | `account/views.py` `create_user_view` | services du médecin hors transaction | 2.8 |
| 8 | `account/views.py` `auth_login` | `ROLE_HOME` créé mais pas utilisé | — |

---

**Correction 1 — `account/views.py` : nommer les arguments**

*Avant* (dans `create_student`) :
```python
    return create_user_view(
        request,
        CustomUserCreationForm,
        StudentForm,
        CustomUser.Role.STUDENT,
        "account/create_student.html",
        "students:home",
    )
```
*Après* :
```python
    return create_user_view(
        request,
        user_form_class=CustomUserCreationForm,
        custom_user_form_class=StudentForm,
        template_name="account/create_student.html",
        redirect_to="students:home",
        role=CustomUser.Role.STUDENT,
    )
```
Fais pareil dans `create_doctor` (`DoctorForm`, `"account/create_doctor.html"`, `"doctors:home"`, `CustomUser.Role.DOCTOR`) et `create_receptionist` (`ReceptionistForm`, `"account/create_receptionist.html"`, `"receptionists:home"`, `CustomUser.Role.RECEPTIONIST`).

*Pourquoi* : chaque valeur arrive dans le bon paramètre, quel que soit l'ordre (notion 2.3).

---

**Correction 2 — ajouter les URL des pages d'erreur**

`doctor/urls.py` : ajoute `doctor_error_page` dans l'import `from .views import (...)`, puis cette ligne dans la liste des `path(...)` :
```python
(path("error-page/", doctor_error_page, name="error-page"),)
```
`receptionist/urls.py` : pareil avec `receptionist_error_page`.

*Pourquoi* : `login_url="doctors:error-page"` doit pointer vers une URL qui existe (notion 2.6). Tu peux recopier la ligne déjà présente dans `student/urls.py:47`.

---

**Correction 3 — `receptionist/views.py` : supprimer l'ancien `is_receptionist`**

Supprime ces 3 lignes (vers la ligne 26) :
```python
# Only if you are receptionist
def is_receptionist(user):
    return user.is_receptionist()
```
Garde la tienne (ligne 22), qui utilise `has_role()`. Tu peux aussi remplacer son commentaire `# receptionist/views.py` (qui ne dit rien d'utile) par `# Receptionists and admin only`.

---

**Correction 4 — brancher les nouvelles fonctions de test**

Dans `doctor/views.py` :
1. Remplace **partout** `is_not_student` par `can_access_doctor_space` (6 décorateurs).
   *Astuce VS Code* : `Ctrl+H` (rechercher/remplacer dans le fichier), tape `is_not_student` puis `can_access_doctor_space`, bouton « Tout remplacer » (`Ctrl+Alt+Entrée`).
2. Supprime l'ancienne fonction :
   ```python
   # if you are not a student
   def is_not_student(user):
       return not user.is_student()
   ```

Dans `student/views.py` : même chose avec `is_not_doctor` → `can_access_student_space` (7 décorateurs), puis supprime `def is_not_doctor`.

*Pourquoi* : « tout le monde **sauf** les étudiants » (liste noire) laisse passer un compte sans rôle ou un futur rôle ; « **seulement** médecins et réception » (liste blanche) non. Et le superuser passe partout grâce à `has_role()`.

*Vérifier* : `grep -n "is_not_" doctor/views.py student/views.py` ne doit plus rien afficher.

---

**Correction 5 — simplifier les 3 pages d'erreur**

On arrive sur ces pages **uniquement** quand l'accès a été refusé. Le `if` est donc inutile (et faux, notion 2.2).

`student/views.py` *avant* :
```python
@login_required
def student_error_page(request):
    context = {}
    if not request.user.is_superuser or request.user.is_doctor():
        context["error_message"] = "Doctor is not allowed to access this page."
    return render(request, "student/student_error_page.html", context)
```
*Après* :
```python
@login_required
def student_error_page(request):
    context = {"error_message": "Only students and receptionists can access this page."}
    return render(request, "student/student_error_page.html", context)
```
- `doctor_error_page` : `"Only doctors and receptionists can access this page."`
- `receptionist_error_page` : `"Only receptionists can access this page."` (au passage, « You is » → plus de faute).

---

**Correction 6 — `account/views.py` : `user_creation_error_page`**

Deux problèmes : `is_superuser()` (notion 2.1), et le 2e message est faux. Regarde les décorateurs : `create_doctor` est ouvert à **réception + admin**, `create_receptionist` à **l'admin seul**. Donc un réceptionniste refusé est forcément sur la création d'un réceptionniste.

*Après* :
```python
@login_required
def user_creation_error_page(request):
    if request.user.has_role(CustomUser.Role.RECEPTIONIST):
        error_message = "Only an Admin can create a receptionist."
    else:
        error_message = "Only an Admin or a Receptionist can create this account."
    return render(
        request, "account/user_creation_error_page.html", {"error_message": error_message}
    )
```
Et, pour être cohérent avec le reste, plus haut dans le fichier :
```python
def is_superuser_or_receptionist(user):
    return user.has_role(CustomUser.Role.RECEPTIONIST)
```
(`has_role()` inclut déjà le superuser.)

---

**Correction 7 — `create_user_view` : tout dans la transaction**

*Avant* :
```python
                    with transaction.atomic():
                        user = create_user(user_form, role)
                        custom_user = create_custom_user(user, custom_user_form)

                    # if the custom_user is a doctor, so he has a service field
                    if custom_user_form.cleaned_data.get("service"):
                        ...
                        custom_user.save()
```
*Après* : sélectionne le bloc `# if the custom_user…` jusqu'à `custom_user.save()` et appuie sur `Tab` (VS Code ajoute 4 espaces à chaque ligne) :
```python
                    with transaction.atomic():
                        user = create_user(user_form, role)
                        custom_user = create_custom_user(user, custom_user_form)

                        # if the custom_user is a doctor, so he has a service field
                        if custom_user_form.cleaned_data.get("service"):
                            ...
                            custom_user.save()
```
Laisse `authenticate_and_login(...)` **hors** du bloc : on le supprimera au 3.4 (on ne doit plus connecter le compte qu'on vient de créer).

*Simplification possible* : les 5 lignes de la boucle `for service in services: custom_user.service.add(service)` + `custom_user.save()` peuvent devenir une seule ligne, `custom_user.service.set(services)`. `.set()` remplace toute la liste des services d'un coup, et une relation ManyToMany n'a pas besoin de `save()`.

---

**Correction 8 — `auth_login` : utiliser `ROLE_HOME`**

*Avant* :
```python
            if request.GET.get("next"):  # if @login_required
                next_url = request.GET.get("next")
            elif user.is_doctor():  # if user is doctor
                next_url = "doctors:home"
            elif user.is_receptionist():  # if user is receptionist
                next_url = "receptionists:home"
            elif user.is_student():  # if user is student
                next_url = "students:home"
            else:
                next_url = "home"
            return redirect(next_url)
```
*Après* :
```python
            next_url = request.GET.get("next") or ROLE_HOME.get(user.role, "home")
            return redirect(next_url)
```
Lecture :
- `ROLE_HOME.get(user.role, "home")` : cherche le rôle dans le dictionnaire ; s'il n'y est pas (le superuser a `""`), renvoie `"home"`.
- `A or B` : si `A` est vide (`None` ou `""`), on prend `B`.
- Tu peux aussi supprimer la ligne `next_url = ""` plus haut, devenue inutile.

La vérification de `next` (open redirect) reste au point 7.

---

**Enfin — les imports**
```bash
uv run ruff check --fix .
uv run ruff format .
uv run ruff check .
```
Ruff remet les imports dans l'ordre (Django d'abord, puis tes apps, avec une ligne vide entre les groupes). Le dernier `ruff check` doit afficher **11 erreurs**, les mêmes qu'au point 3.0 (`DJ001`, `DJ012`, `E501`), et plus aucun `I001` ni `F811`.

---

#### Partie 4 bis — Deuxième vérification (2026-10-27, après tes corrections)

**Bilan : 6 corrections sur 8 sont bonnes** ✅ : n° 1 (arguments nommés : `/accounts/create-student/` répond enfin 200), n° 3 (doublon supprimé), n° 4 (`can_access_*` branchées partout, `grep is_not_` ne trouve plus rien), n° 5 (messages fixes), n° 6 (plus de `TypeError`), n° 7 (transaction + `.set()`), n° 8 (`ROLE_HOME`). Ruff : 11 erreurs, comme prévu. 👍

**Résultat du test d'accès** (même commande qu'en partie 5, avec 6 pages) :

| | create-student | students | doctors | receptionists | user-creation-error | create-receptionist |
|---|---|---|---|---|---|---|
| anonyme | 200 | → login | → login | → login | → login | → login |
| étudiant | 200 | 200 ✅ | **500** ❌ | **200** ❌ | 200 | → page d'erreur ✅ |
| médecin | 200 | → erreur ✅ | 200 ✅ | **200** ❌ | 200 | → page d'erreur ✅ |
| réception | 200 | 200 ✅ | 200 ✅ | 200 ✅ | 200 | → page d'erreur ✅ |
| admin | 200 | 200 | 200 | 200 | 200 | 200 ✅ |

Il reste **2 problèmes**, dont un grave pour la sécurité.

##### Problème A — Le *nom* de l'URL n'est pas celui qu'attend le décorateur (encore la 500)

Tu as bien ajouté l'URL, mais avec un autre nom. Rappel de la notion 2.6 : dans `login_url="doctors:error-page"`, Django cherche **dans l'app `doctors`** une URL dont le `name=` vaut **exactement** `"error-page"`. Le texte doit être identique, lettre pour lettre.

```python
# doctor/urls.py — AVANT (ce que tu as écrit)
path("error/", doctor_error_page, name="doctor-error-page")
#                                      ▲ Django cherche "error-page" → introuvable → NoReverseMatch → 500

# doctor/urls.py — APRÈS
path("error-page/", doctor_error_page, name="error-page")
```
Même correction dans `receptionist/urls.py` :
```python
path("error-page/", receptionist_error_page, name="error-page")
```
(Dans le fichier, la ligne garde sa virgule finale, car elle est dans la liste `urlpatterns`.)
Pourquoi aussi changer `"error/"` en `"error-page/"` ? Ce n'est pas obligatoire (l'adresse visible et le nom sont deux choses indépendantes), mais `student/urls.py:47` utilise déjà `"error-page/"` : les 3 apps se ressemblent, c'est plus facile à retrouver.

**Comment le vérifier tout seul** : ce `grep` doit afficher 3 lignes, toutes avec `name="error-page"`.
```bash
grep -n 'name="error-page"' student/urls.py doctor/urls.py receptionist/urls.py
```

##### Problème B ⚠️ Sécurité — n'importe quel utilisateur connecté entre dans l'espace réception

C'est exactement le piège de la notion 2.1 (attribut ou méthode). `receptionist/views.py:22` :
```python
# AVANT
def is_receptionist(user):
    return user.is_receptionist or user.is_superuser
    #           ▲ pas de () : c'est la FONCTION elle-même, pas son résultat
```
`is_receptionist` est une **méthode** (`def is_receptionist(self):`, `account/models.py:68`). Sans parenthèses, `user.is_receptionist` vaut `<bound method …>`, et Python considère tout objet « vrai » dans un test. Donc la fonction renvoie toujours `True` → un étudiant ou un médecin peut lire, créer, modifier et **supprimer** les annonces. Le test le montre : étudiant et médecin obtiennent 200 sur `/receptionists/announcement/list/`.

```python
# APRÈS — même style que doctor/views.py:37 et student/views.py:23
def is_receptionist(user):
    return user.has_role(CustomUser.Role.RECEPTIONIST)
```
Et en haut du fichier, avec les autres imports de tes apps (avant `from receptionist.forms import ...`) :
```python
from account.models import CustomUser
```
Pourquoi `has_role` plutôt que d'ajouter les `()` ? `has_role` contient déjà le « ou superuser » (`account/models.py:75`). Les 3 apps testent alors le rôle de la même façon, et on ne peut plus oublier les parenthèses.

**Leçon à retenir** : en Python (fichiers `.py`), une méthode s'appelle **toujours** avec `()`. Sans `()`, le test est toujours vrai et Python ne signale aucune erreur. Le bug est silencieux : seul un test l'attrape. C'est pour ça qu'on écrira des tests de permissions automatiques au point 7.

##### Troisième vérification (2026-10-27)
- Problème A ✅ : étudiant → `/doctors/…` donne maintenant `302 → /doctors/error-page/`.
- Problème B : à moitié fait. La ligne 22 est corrigée, mais **l'import manque**, d'où `NameError: name 'CustomUser' is not defined` (500 pour tout le monde sur `/receptionists/…`). Python ne sait pas ce qu'est `CustomUser` tant qu'on ne lui a pas dit d'où il vient. Ajoute en ligne 9 de `receptionist/views.py`, juste avant `from receptionist.forms import AnnouncementForm` :
  ```python
  from account.models import CustomUser
  ```
- **Astuce** : Ruff l'avait vu avant toi. `uv run ruff check receptionist/views.py` affiche `F821 Undefined name 'CustomUser'`. Le code `F821` veut dire « nom utilisé mais jamais défini ni importé ». Prends l'habitude de lancer `ruff check` **avant** le test d'accès : il trouve ce genre d'oubli en 1 seconde.

##### Après ces 2 corrections
Relance `ruff check --fix .`, `ruff format .`, puis le test de la partie 5. Tu dois obtenir :
- étudiant → `doctors` : `302 → /doctors/error-page/` (au lieu de 500) ;
- étudiant et médecin → `receptionists` : `302 → /receptionists/error-page/` (au lieu de 200) ;
- tout le reste inchangé.

---

#### Partie 4 ter — Test complet et minutieux (2026-10-27, après l'ajout de l'import)

**Verdict : le point 3.2 fonctionne.** Plus aucune erreur 500, et chaque espace n'est ouvert qu'aux bons rôles. Il reste des failles plus anciennes, déjà prévues pour plus tard (3.3, 3.4, point 7). Elles sont listées plus bas pour que tu saches qu'elles existent.

##### Comment j'ai testé (pour que tu puisses refaire pareil plus tard)
- **Aucune donnée réelle modifiée** : tout tourne dans `with transaction.atomic():` terminé par `transaction.set_rollback(True)`. C'est la notion 2.8 : Django **annule** tout à la fin, comme si rien ne s'était passé. Compteurs vérifiés avant/après : 6 comptes, 1 rendez-vous, 1 annonce, 0 question.
- **7 utilisateurs** : anonyme, les 2 étudiants, les 2 médecins, la réceptionniste, l'admin.
- **39 adresses** : toutes celles des 4 apps, plus 5 pages de l'admin Django.
- Puis les **formulaires** (POST) : connexion, création des 3 types de compte, rendez-vous, question, réponse du médecin, annonce.
- Les scripts sont dans mon dossier temporaire. Au point 8, on les transformera en **vrais tests automatiques** (`pytest`) : tu n'auras plus besoin de moi pour refaire cette vérification.

##### Ce qui marche ✅
| Vérification | Résultat |
|---|---|
| `ruff check` | 11 erreurs, celles attendues (aucune nouvelle) |
| `ruff format --check` | tout est formaté |
| `manage.py check` (avec `-Wd`) | aucun problème, aucun avertissement |
| `makemigrations --check` | aucun changement oublié |
| 39 URL × 7 utilisateurs | **0 erreur 500** |
| Espace étudiant (rendez-vous) | étudiants + réception + admin ; médecins → `/students/error-page/` |
| Espace médecin | médecins + réception + admin ; étudiants → `/doctors/error-page/` |
| Espace réception | réception + admin ; étudiants et médecins → `/receptionists/error-page/` (la faille du problème B est fermée) |
| Créer un médecin | réception + admin ; les autres → page d'erreur |
| Créer un réceptionniste | admin seulement |
| Connexion (`ROLE_HOME`) | étudiant → `/students/home/`, médecin → `/doctors/`, réception → `/receptionists/`, admin → `/home` ; mauvais mot de passe → reste sur la page (200) |
| Création de compte (POST) | bon `role`, bon profil, services du médecin enregistrés, mot de passe **haché** |
| Numéro étudiant déjà pris | formulaire refusé, **aucun compte orphelin** : `transaction.atomic()` fait son travail |
| Contrainte en base | compte sans rôle refusé par MariaDB (`CONSTRAINT role_required_unless_superuser failed`) ; superuser sans rôle accepté |
| `RoleProfileMixin` | profil étudiant sur un compte médecin refusé (« This account does not have the student role. ») |
| Rendez-vous | créé par l'étudiant ; 2ᵉ le même jour refusé ; si un étudiant envoie l'identifiant d'un autre, le RDV est quand même enregistré **à son nom** ✅ ; la réception peut prendre un RDV pour un étudiant |
| Question → réponse | l'étudiant pose la question, le médecin répond, `is_answering` passe à `True` |
| Annonce | la réception crée et supprime ; un étudiant qui tente de supprimer → page d'erreur |

##### Ce qui ne marche pas encore ❌ (aucun n'a été causé par le 3.2)
| # | Problème constaté | Gravité | Prévu au |
|---|---|---|---|
| 1 | Un compte **sans photo** ne peut ouvrir aucune page : `ValueError: The 'photo' attribute has no file associated with it` (`templates/header.html:16`). Aujourd'hui les 6 comptes ont une photo, c'est pour ça que tu ne l'as jamais vu. | 🔴 500 | 3.3 |
| 2 | Quand la réception (ou l'admin) crée un compte, **elle est déconnectée et connectée à la place du nouveau compte** : la session passe au nouvel utilisateur (`authenticate_and_login`). | 🟠 | 3.4 |
| 3 | `/students/enquiry/list/`, `view/<id>/` et `update/<id>/` n'ont **aucun** contrôle de rôle : un médecin voit **toutes** les questions (la liste lui en renvoie 2 sur 2) et peut les modifier. | 🔴 sécurité | 7 |
| 4 | **IDOR** (*Insecure Direct Object Reference* : on change le numéro dans l'adresse et on accède à l'objet d'un autre). L'étudiant n° 6 ouvre, modifie et peut supprimer le RDV n° 1, qui appartient à l'étudiant n° 2. Le médecin n° 4 lit le RDV et la question du médecin n° 3. Les **listes** filtrent bien, les pages **détail / modifier / supprimer** ne vérifient pas le propriétaire. | 🔴 sécurité | 7 |
| 5 | **Modifier un rendez-vous sans changer sa date est impossible** : « You already have an appointment on this date. ». `AppointmentForm.clean()` (`student/forms.py`) cherche un RDV à la même date, et trouve… le RDV qu'on est en train de modifier. Il faut l'exclure : `.exclude(pk=self.instance.pk)`. | 🟠 bug | 6 (nouveau) |
| 6 | `/accounts/create-student/` reste ouvert quand on est déjà connecté. | 🟡 | 3.4 |
| 7 | Déconnexion par un simple lien (GET), redirection `?next=` sans vérification (*open redirect*). | 🟠 sécurité | 7 |

Note : la réceptionniste a `is_staff=True`. Elle voit donc l'accueil de `/admin/` (200), mais reçoit 403 sur les utilisateurs, car elle n'a aucune permission. C'est l'effet voulu du 3.1, pas un bug.

##### Ton historique Git, et le commit à faire
Tu as fait **2 commits avec le même message** (`2178434` et `b478577`), et l'ajout de l'import n'est pas encore commité. Comme la branche **n'est pas encore poussée** sur GitHub, on peut réécrire le dernier commit sans risque. `--amend` veut dire « remplace le dernier commit par celui-ci ». On en profite pour lui donner un message qui dit ce qu'il fait vraiment :
```bash
git add receptionist/views.py
git commit --amend -m "Fix error-page URL names and receptionist role check"
git log --oneline -4
```
Tu dois voir : ton commit corrigé, puis `2178434`, `7522c5e`, `2a9ae9f`. La règle : `--amend` uniquement sur un commit **pas encore poussé**. Après un `git push`, on ne réécrit plus l'historique.

Ensuite, je commite la doc à part : `git add CLAUDE.md docs.md tasks.md` puis `git commit -m "Document role model, view fixes and full access test"`.

---

#### Partie 5 — Tester

**1. Commandes de base**
```bash
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
```

**2. Le test des accès** (celui que j'ai utilisé). Copie tout le bloc dans le terminal :
```bash
uv run python manage.py shell -c "
from django.test import Client
from account.models import CustomUser as U

def visit(user, url):
    c = Client(HTTP_HOST='localhost', raise_request_exception=False)
    if user:
        c.force_login(user)
    r = c.get(url)
    return f'{r.status_code} {r.get(\"Location\", \"\")}'

users = [('anonyme', None)] + [(u.role or 'admin', u) for u in U.objects.order_by('role')]
urls = ['/accounts/create-student/', '/students/appointment/list/',
        '/doctors/appointment/list/', '/receptionists/announcement/list/']
for name, user in users:
    print(f'{name:13}', ' | '.join(visit(user, url) for url in urls))
"
```
- `Client` = un faux navigateur fourni par Django ; `force_login` = se connecter sans mot de passe (uniquement pour les tests) ; on ne fait que des `GET`, rien n'est modifié en base.
- Les erreurs 500 affichent leur trace (longue) au-dessus du tableau : c'est normal, c'est ce qui permet de trouver la cause. Pour ne voir que le tableau, ajoute `2>/dev/null` à la fin de la commande (`2>` = la sortie d'erreurs, `/dev/null` = la poubelle).
- Une redirection s'affiche `302 /students/error-page/?next=…` : `302` = « va voir ailleurs », suivi de l'adresse.

**Résultat attendu après les 8 corrections :**

| Page | anonyme | étudiant | médecin | réception | admin |
|---|---|---|---|---|---|
| `/accounts/create-student/` | 200 | 200 | 200 | 200 | 200 |
| `/students/appointment/list/` | → login | 200 | → `/students/error-page/` | 200 | 200 |
| `/doctors/appointment/list/` | → login | → `/doctors/error-page/` | 200 | 200 | 200 |
| `/receptionists/announcement/list/` | → login | → `/receptionists/error-page/` | → `/receptionists/error-page/` | 200 | 200 |

(`create-student` ouvert à tous, même sans connexion : c'est l'inscription libre des étudiants, à rediscuter au point 7.)

**3. À la main dans le navigateur** (`uv run python manage.py runserver`)
1. Connecte-toi avec chaque rôle : tu arrives sur **ton** accueil (`/students/`, `/doctors/`, `/receptionists/`), l'admin sur `/`.
2. Étudiant connecté : ouvre `/doctors/appointment/list/` → page d'erreur lisible, pas d'écran jaune Django.
3. Admin : crée un compte avec le rôle `doctor`, puis essaie de lui ajouter un profil **Student** (`/admin/account/student/add/`) → message « This account does not have the student role ».
4. Inscription : `/accounts/create-student/` → crée un étudiant de test, puis vérifie son rôle :
   ```bash
   uv run python manage.py shell -c "from account.models import CustomUser as U; print(U.objects.values_list('email', 'role').first())"
   ```
   (`ordering = ["-created_at"]` → `.first()` = le plus récent.)

**4. Commit** (seulement le code) :
```bash
git add account/ doctor/ receptionist/ student/
git status -s
git commit -m "Add explicit user role with DB constraint and fix role checks in views"
```
`git status -s` avant le commit : `docs.md`, `tasks.md`, `CLAUDE.md` doivent rester en rouge (non ajoutés).

---

#### Partie 6 — Explication en 3 niveaux
- **Simple** : chaque compte porte une étiquette « étudiant », « médecin » ou « réception ». Chaque page vérifie l'étiquette avant de s'afficher ; l'admin a un passe-partout.
- **Intermédiaire** : `TextChoices` pour les valeurs, data migration pour remplir l'existant, `CheckConstraint` pour que la base refuse un compte sans rôle, `clean()` pour qu'un profil corresponde à son rôle, `has_role()` comme point d'entrée unique, branché dans `user_passes_test`.
- **Expert** : on passe d'un rôle *dérivé* (présence d'une ligne dans une table liée, une requête SQL par `hasattr`) à un rôle *dénormalisé* sur `CustomUser`, garanti par une contrainte. Le prix : deux sources (`role` et la table du profil) qui pourraient diverger → rôle figé après création + validation du profil. L'alternative serait les `Group` Django avec des permissions par vue (`permission_required`) : plus souple, mais surdimensionnée pour 3 rôles fixes.
