"""
Tests Live — NoteKeeper : Projet incrémental en 5 étapes
Un seul projet, 5 conversations successives, chaque étape reprend le code existant.
Teste la capacité de l'IA à construire puis reprendre et enrichir un projet.

Étape 1 : Structure de base + modèle Note + stockage JSON
Étape 2 : CRUD complet (créer, lire, modifier, supprimer)
Étape 3 : Recherche par mot-clé + tags/catégories
Étape 4 : API REST (FastAPI) exposant toutes les opérations
Étape 5 : Frontend HTML/JS simple (liste, création, recherche)

Prérequis : serveur lancé sur http://localhost:8000
"""

import os
import shutil
import subprocess
import sys
import time

import requests

BASE_URL = "http://localhost:8000"
TEST_ROOT = r"D:\Coding\TEST"
PROJECT_FOLDER = "test_notekeeper"


# ─── Couleurs console ───
class C:
    OK = "\033[92m"
    WARN = "\033[93m"
    FAIL = "\033[91m"
    BOLD = "\033[1m"
    END = "\033[0m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"


def header(title):
    print(f"\n{C.BOLD}{'=' * 60}{C.END}")
    print(f"{C.BOLD}{C.BLUE}  {title}{C.END}")
    print(f"{C.BOLD}{'=' * 60}{C.END}\n")


def step(msg):
    print(f"  {C.BLUE}>{C.END} {msg}")


def ok(msg):
    print(f"  {C.OK}  {msg}{C.END}")


def warn(msg):
    print(f"  {C.WARN}  {msg}{C.END}")


def fail(msg):
    print(f"  {C.FAIL}  {msg}{C.END}")


def info(msg):
    print(f"    {msg}")


def section(msg):
    print(f"\n  {C.CYAN}{C.BOLD}--- {msg} ---{C.END}\n")


# ─── Helpers API ───


def create_project(name, folder_name, description):
    """Crée un projet via l'API, retourne project_id ou None."""
    path = os.path.join(TEST_ROOT, folder_name)
    os.makedirs(path, exist_ok=True)

    resp = requests.post(
        f"{BASE_URL}/api/projects", json={"name": name, "path": path, "description": description}
    )
    if resp.status_code == 200:
        project = resp.json()
        ok(f"Projet cree : {project['name']} (id={project['id'][:8]}...)")
        return project["id"], path
    else:
        fail(f"Creation projet echouee : {resp.status_code} -- {resp.text}")
        return None, path


def create_conversation(project_id, agent_id="JARVIS_Maître", title="Test"):
    """Crée une conversation, retourne conversation_id ou None."""
    resp = requests.post(
        f"{BASE_URL}/api/projects/{project_id}/conversations",
        json={"agent_id": agent_id, "title": title},
    )
    if resp.status_code == 200:
        conv = resp.json()
        ok(f"Conversation creee (agent={agent_id}, id={conv['id'][:8]}...)")
        return conv["id"]
    else:
        fail(f"Creation conversation echouee : {resp.status_code} -- {resp.text}")
        return None


def send_message(conversation_id, content, timeout=900):
    """Envoie un message et attend la réponse."""
    step(f"Envoi message ({len(content)} chars)... (timeout={timeout}s)")
    try:
        resp = requests.post(
            f"{BASE_URL}/api/conversations/{conversation_id}/messages",
            json={"content": content},
            timeout=timeout,
        )
        if resp.status_code == 200:
            result = resp.json()
            response_text = result.get("response", "")
            ok(f"Reponse recue ({len(response_text)} chars)")

            if "[DEMANDE_CODE_CODEUR:" in response_text:
                ok("Marqueur [DEMANDE_CODE_CODEUR] detecte")

            delegations = result.get("delegations") or []
            if delegations:
                ok(f"Delegations executees : {len(delegations)}")
                for d in delegations:
                    info(f"  -> {d.get('agent', '?')} : success={d.get('success', '?')}")
            else:
                warn("Aucune delegation executee")
                preview = response_text[:300].replace("\n", " ")
                info(f"  Reponse (extrait) : {preview}...")

            return result
        else:
            fail(f"Envoi message echoue : {resp.status_code} -- {resp.text[:200]}")
            return None
    except requests.exceptions.Timeout:
        fail(f"Timeout apres {timeout}s")
        return None


def send_until_delegation(conv_id, initial_prompt, max_followups=3, timeout=900):
    """
    Envoie le prompt initial puis des relances jusqu'à obtenir une délégation.
    """
    followup_prompts = [
        "OK je valide ton plan. Passe directement a l'execution : delegue au CODEUR avec [DEMANDE_CODE_CODEUR: ...] en incluant la liste complete des fichiers a produire.",
        "Produis le code maintenant. Utilise le marqueur [DEMANDE_CODE_CODEUR: instruction complete] pour deleguer au CODEUR. Inclus TOUS les fichiers dans l'instruction.",
        "EXECUTION IMMEDIATE. Delegue au CODEUR avec [DEMANDE_CODE_CODEUR: ...]. Ne fais plus d'audit ni de plan.",
    ]

    step("Message 1 : demande initiale...")
    result = send_message(conv_id, initial_prompt, timeout=timeout)
    if not result:
        return None

    delegations = result.get("delegations") or []
    if delegations:
        return result

    for i in range(min(max_followups, len(followup_prompts))):
        step(f"Message {i + 2} : relance pour declencher la delegation...")
        result = send_message(conv_id, followup_prompts[i], timeout=timeout)
        if not result:
            return None
        delegations = result.get("delegations") or []
        if delegations:
            return result

    warn(f"Aucune delegation obtenue apres {max_followups + 1} messages")
    return result


# ─── Helpers vérification ───


def discover_project_files(
    project_path, extensions=(".py", ".txt", ".json", ".yaml", ".toml", ".html", ".js", ".css")
):
    """Découvre tous les fichiers du projet (hors cache)."""
    found = []
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [
            d for d in dirs if d not in ("__pycache__", ".pytest_cache", "node_modules", ".git")
        ]
        for fname in files:
            if fname.endswith(extensions):
                rel = os.path.relpath(os.path.join(root, fname), project_path)
                rel = rel.replace("\\", "/")
                if rel == "conftest.py":
                    continue
                found.append(rel)
    return sorted(found)


def check_files_exist(project_path, expected_files):
    """Vérifie que les fichiers attendus existent."""
    results = {}
    for f in expected_files:
        full_path = os.path.join(project_path, f)
        exists = os.path.isfile(full_path)
        results[f] = exists
        if exists:
            size = os.path.getsize(full_path)
            ok(f"Fichier trouve : {f} ({size} bytes)")
        else:
            fail(f"Fichier MANQUANT : {f}")
    return results


def check_file_content(project_path, filepath, checks):
    """Vérifie le contenu d'un fichier (liste de strings à trouver)."""
    full_path = os.path.join(project_path, filepath)
    if not os.path.isfile(full_path):
        fail(f"Impossible de verifier {filepath} -- fichier absent")
        return False

    with open(full_path, encoding="utf-8", errors="ignore") as fh:
        content = fh.read()

    all_ok = True
    for check in checks:
        if check in content:
            ok(f"  {filepath} contient '{check}'")
        else:
            fail(f"  {filepath} ne contient PAS '{check}'")
            all_ok = False

    # Vérifier absence d'artefacts markdown
    if "```python" in content or "```" in content:
        fail(f"  {filepath} contient des artefacts markdown !")
        all_ok = False
    else:
        ok(f"  {filepath} -- pas d'artefacts markdown")

    return all_ok


def check_minimum_files(project_path, min_py=1, min_total=2):
    """Vérifie le nombre minimum de fichiers."""
    files = discover_project_files(project_path)
    py_files = [f for f in files if f.endswith(".py")]

    ok(f"Fichiers decouverts : {len(files)} total, {len(py_files)} .py")
    for f in files:
        fpath = os.path.join(project_path, f.replace("/", os.sep))
        size = os.path.getsize(fpath) if os.path.isfile(fpath) else 0
        info(f"  {f} ({size} bytes)")

    structure_ok = True
    if len(py_files) < min_py:
        fail(f"Fichiers .py : {len(py_files)} (minimum {min_py})")
        structure_ok = False
    if len(files) < min_total:
        fail(f"Total fichiers : {len(files)} (minimum {min_total})")
        structure_ok = False

    return files, structure_ok


def ensure_conftest(project_path):
    """Crée conftest.py si absent pour les imports."""
    conftest_path = os.path.join(project_path, "conftest.py")
    if not os.path.isfile(conftest_path):
        with open(conftest_path, "w", encoding="utf-8") as f:
            f.write(
                "import sys, os\nsys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))\n"
            )
        info("  conftest.py cree pour les imports")


def install_deps(project_path):
    """Installe les dépendances si requirements.txt existe."""
    req_path = os.path.join(project_path, "requirements.txt")
    if os.path.isfile(req_path):
        step("Installation dependances...")
        subprocess.run(
            f"{sys.executable} -m pip install -r requirements.txt -q",
            shell=True,
            cwd=project_path,
            capture_output=True,
        )


def run_tests(project_path, test_command=None):
    """Lance les tests pytest."""
    if test_command is None:
        test_command = f"{sys.executable} -m pytest tests/ -v --tb=short"

    step(f"Lancement tests dans {project_path}")
    try:
        result = subprocess.run(
            test_command, shell=True, cwd=project_path, capture_output=True, text=True, timeout=60
        )
        output = result.stdout + result.stderr

        for line in output.split("\n"):
            line_stripped = line.strip()
            if "passed" in line_stripped or "failed" in line_stripped or "error" in line_stripped:
                if "===" in line_stripped:
                    info(f"  {line_stripped}")

        if result.returncode == 0:
            ok("Tests passent")
        else:
            fail(f"Tests echoues (code={result.returncode})")
            for line in output.split("\n"):
                if "FAILED" in line or "ERROR" in line or "assert" in line.lower():
                    info(f"  {line.strip()}")

        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        fail("Tests timeout (60s)")
        return False, ""
    except Exception as e:
        fail(f"Erreur execution tests : {e}")
        return False, ""


# ─── Étapes du test ───


def etape1_structure_base(project_id, project_path):
    """Étape 1 — Structure de base + modèle Note + stockage JSON"""
    section("ETAPE 1 — Structure de base + modele Note + stockage JSON")

    conv_id = create_conversation(project_id, title="Etape 1 - Structure de base")
    if not conv_id:
        return False

    prompt = """Cree un projet Python "NoteKeeper" — gestionnaire de notes personnel.

Pour cette premiere etape, cree la structure de base :
- src/models.py : classe Note avec attributs id (int), title (str), content (str), created_at (str ISO format). Methode to_dict() qui retourne un dictionnaire, et classmethod from_dict(data) qui reconstruit une Note depuis un dict.
- src/storage.py : classe JsonStorage qui gere la persistance dans un fichier JSON. Methodes : __init__(filepath), load() -> list[dict] (retourne liste vide si fichier inexistant), save(data: list[dict]) -> None. Gere les erreurs de lecture/ecriture.
- tests/test_models.py : tests pytest pour Note (creation, to_dict, from_dict, valeurs par defaut).
- tests/test_storage.py : tests pytest pour JsonStorage (load fichier inexistant retourne [], save puis load retourne les memes donnees, utiliser tmp_path).
- requirements.txt : pytest

Utilise des imports absolus simples. Chaque fichier doit etre complet et autonome."""

    result = send_until_delegation(conv_id, prompt)
    if not result:
        return False

    time.sleep(2)

    step("Verification etape 1...")
    files, structure_ok = check_minimum_files(project_path, min_py=2, min_total=3)

    # Vérifications de contenu
    content_ok = True
    py_files = [f for f in files if f.endswith(".py")]

    for f in py_files:
        if "model" in f.lower():
            if not check_file_content(project_path, f, ["class Note", "to_dict", "from_dict"]):
                content_ok = False
        if "storage" in f.lower():
            if not check_file_content(
                project_path, f, ["class JsonStorage", "def load", "def save"]
            ):
                content_ok = False

    ensure_conftest(project_path)
    tests_ok, _ = run_tests(project_path)

    success = structure_ok and tests_ok
    return {
        "etape": 1,
        "name": "Structure de base",
        "files": len(files),
        "structure_ok": structure_ok,
        "content_ok": content_ok,
        "tests_ok": tests_ok,
        "success": success,
    }


def etape2_crud(project_id, project_path):
    """Étape 2 — CRUD complet sur les notes (reprend le code existant)"""
    section("ETAPE 2 — CRUD complet (reprend le code existant)")

    conv_id = create_conversation(project_id, title="Etape 2 - CRUD complet")
    if not conv_id:
        return False

    prompt = """Le projet NoteKeeper a deja une structure de base :
- src/models.py : classe Note (id, title, content, created_at, to_dict, from_dict)
- src/storage.py : classe JsonStorage (load, save)

Ajoute maintenant le CRUD complet. IMPORTANT : ne recree PAS les fichiers existants, ajoute uniquement les nouveaux fichiers et modifie ceux qui doivent l'etre.

Fichiers a creer ou modifier :
- src/note_manager.py (NOUVEAU) : classe NoteManager qui utilise JsonStorage. Methodes :
  * __init__(storage: JsonStorage)
  * add_note(title: str, content: str) -> Note (id auto-incremente)
  * get_note(note_id: int) -> Note ou None
  * get_all_notes() -> list[Note]
  * update_note(note_id: int, title: str = None, content: str = None) -> Note ou None (met a jour uniquement les champs fournis)
  * delete_note(note_id: int) -> bool (True si supprime, False si non trouve)
- src/cli.py (NOUVEAU) : interface CLI avec argparse. Commandes : add <title> <content>, list, get <id>, update <id> [--title T] [--content C], delete <id>.
- tests/test_note_manager.py (NOUVEAU) : tests pytest pour NoteManager — add, get, get_all, update (partiel et complet), delete (existant et inexistant), avec fichier temporaire.

Utilise des imports absolus simples. Chaque fichier doit etre complet et autonome."""

    result = send_until_delegation(conv_id, prompt)
    if not result:
        return False

    time.sleep(2)

    step("Verification etape 2...")
    files, structure_ok = check_minimum_files(project_path, min_py=4, min_total=5)

    content_ok = True
    py_files = [f for f in files if f.endswith(".py")]

    for f in py_files:
        if "note_manager" in f.lower() or "manager" in f.lower():
            if not check_file_content(
                project_path, f, ["class NoteManager", "def add_note", "def delete_note"]
            ):
                content_ok = False
        if "cli" in f.lower():
            if not check_file_content(project_path, f, ["argparse"]):
                content_ok = False

    ensure_conftest(project_path)
    tests_ok, _ = run_tests(project_path)

    success = structure_ok and tests_ok
    return {
        "etape": 2,
        "name": "CRUD complet",
        "files": len(files),
        "structure_ok": structure_ok,
        "content_ok": content_ok,
        "tests_ok": tests_ok,
        "success": success,
    }


def etape3_recherche_tags(project_id, project_path):
    """Étape 3 — Recherche par mot-clé + tags/catégories"""
    section("ETAPE 3 — Recherche + tags (reprend le code existant)")

    conv_id = create_conversation(project_id, title="Etape 3 - Recherche et tags")
    if not conv_id:
        return False

    prompt = """Le projet NoteKeeper a maintenant :
- src/models.py : classe Note (id, title, content, created_at, to_dict, from_dict)
- src/storage.py : classe JsonStorage (load, save)
- src/note_manager.py : classe NoteManager (add_note, get_note, get_all_notes, update_note, delete_note)
- src/cli.py : interface CLI avec argparse

Ajoute maintenant la recherche et les tags. IMPORTANT : modifie les fichiers existants pour ajouter les fonctionnalites, ne les recree pas de zero.

Modifications et ajouts :
- src/models.py (MODIFIER) : ajouter un attribut tags: list[str] a la classe Note (defaut = liste vide). Mettre a jour to_dict et from_dict pour inclure les tags.
- src/note_manager.py (MODIFIER) : ajouter les methodes :
  * search_notes(query: str) -> list[Note] : recherche dans title ET content (insensible a la casse)
  * get_notes_by_tag(tag: str) -> list[Note] : filtre par tag (insensible a la casse)
  * add_tag(note_id: int, tag: str) -> Note ou None : ajoute un tag a une note (pas de doublon)
  * remove_tag(note_id: int, tag: str) -> Note ou None : retire un tag
  Modifier aussi add_note pour accepter un parametre optionnel tags: list[str] = None.
- tests/test_search.py (NOUVEAU) : tests pytest pour search_notes (trouve par titre, par contenu, insensible a la casse, retourne vide si rien), get_notes_by_tag, add_tag (ajout, pas de doublon), remove_tag.

Utilise des imports absolus simples. Chaque fichier doit etre complet et autonome."""

    result = send_until_delegation(conv_id, prompt)
    if not result:
        return False

    time.sleep(2)

    step("Verification etape 3...")
    files, structure_ok = check_minimum_files(project_path, min_py=5, min_total=6)

    content_ok = True
    py_files = [f for f in files if f.endswith(".py")]

    for f in py_files:
        if "model" in f.lower():
            if not check_file_content(project_path, f, ["tags"]):
                content_ok = False
        if "note_manager" in f.lower() or "manager" in f.lower():
            if not check_file_content(
                project_path, f, ["def search_notes", "def get_notes_by_tag"]
            ):
                content_ok = False

    ensure_conftest(project_path)
    tests_ok, _ = run_tests(project_path)

    success = structure_ok and tests_ok
    return {
        "etape": 3,
        "name": "Recherche + tags",
        "files": len(files),
        "structure_ok": structure_ok,
        "content_ok": content_ok,
        "tests_ok": tests_ok,
        "success": success,
    }


def etape4_api_rest(project_id, project_path):
    """Étape 4 — API REST FastAPI"""
    section("ETAPE 4 — API REST FastAPI (reprend le code existant)")

    conv_id = create_conversation(project_id, title="Etape 4 - API REST")
    if not conv_id:
        return False

    prompt = """Le projet NoteKeeper a maintenant :
- src/models.py : classe Note (id, title, content, created_at, tags, to_dict, from_dict)
- src/storage.py : classe JsonStorage (load, save)
- src/note_manager.py : classe NoteManager (add_note, get_note, get_all_notes, update_note, delete_note, search_notes, get_notes_by_tag, add_tag, remove_tag)
- src/cli.py : interface CLI

Ajoute maintenant une API REST avec FastAPI. Ne modifie PAS les fichiers existants sauf requirements.txt.

Fichiers a creer ou modifier :
- src/api.py (NOUVEAU) : app FastAPI avec les routes :
  * POST /notes/ : cree une note (body JSON : title, content, tags optionnel). Retourne la note creee.
  * GET /notes/ : liste toutes les notes. Query params optionnels : search (str), tag (str) pour filtrer.
  * GET /notes/{note_id} : retourne une note par id. 404 si non trouvee.
  * PUT /notes/{note_id} : met a jour une note (body JSON : title optionnel, content optionnel). 404 si non trouvee.
  * DELETE /notes/{note_id} : supprime une note. 404 si non trouvee.
  * POST /notes/{note_id}/tags : ajoute un tag (body JSON : tag). 404 si note non trouvee.
  * DELETE /notes/{note_id}/tags/{tag} : retire un tag. 404 si note non trouvee.
  L'app utilise NoteManager avec JsonStorage("notes.json").
  Definir des modeles Pydantic pour les requetes : NoteCreate(title, content, tags optionnel), NoteUpdate(title optionnel, content optionnel), TagAdd(tag).
- tests/test_api.py (NOUVEAU) : tests pytest avec TestClient de FastAPI. Couvre : creation, liste, get par id, update, delete, 404, recherche par query, filtre par tag, ajout/suppression tag.
- requirements.txt (MODIFIER) : ajouter fastapi, uvicorn, httpx

Utilise des imports absolus simples. Chaque fichier doit etre complet et autonome."""

    result = send_until_delegation(conv_id, prompt)
    if not result:
        return False

    time.sleep(2)

    step("Verification etape 4...")
    files, structure_ok = check_minimum_files(project_path, min_py=6, min_total=7)

    content_ok = True
    py_files = [f for f in files if f.endswith(".py")]

    for f in py_files:
        if "api" in f.lower() and "test" not in f.lower():
            if not check_file_content(project_path, f, ["FastAPI", "NoteManager", "/notes/"]):
                content_ok = False

    ensure_conftest(project_path)
    install_deps(project_path)
    tests_ok, _ = run_tests(project_path)

    success = structure_ok and tests_ok
    return {
        "etape": 4,
        "name": "API REST FastAPI",
        "files": len(files),
        "structure_ok": structure_ok,
        "content_ok": content_ok,
        "tests_ok": tests_ok,
        "success": success,
    }


def etape5_frontend(project_id, project_path):
    """Étape 5 — Frontend HTML/JS"""
    section("ETAPE 5 — Frontend HTML/JS (reprend le code existant)")

    conv_id = create_conversation(project_id, title="Etape 5 - Frontend")
    if not conv_id:
        return False

    prompt = """Le projet NoteKeeper a maintenant un backend complet :
- src/models.py : classe Note (id, title, content, created_at, tags)
- src/storage.py : classe JsonStorage
- src/note_manager.py : classe NoteManager (CRUD + recherche + tags)
- src/api.py : API REST FastAPI (POST/GET/PUT/DELETE /notes/, tags)

Ajoute maintenant un frontend simple. Ne modifie PAS les fichiers Python existants sauf src/api.py pour ajouter le CORS et servir les fichiers statiques.

Fichiers a creer ou modifier :
- src/api.py (MODIFIER) : ajouter CORSMiddleware (allow_origins=["*"]) et StaticFiles pour servir le dossier static/. Ajouter une route GET / qui retourne le fichier index.html.
- static/index.html (NOUVEAU) : page HTML complete avec :
  * Un formulaire pour creer une note (titre, contenu, tags separes par virgule)
  * Un champ de recherche (texte) et un filtre par tag (select ou input)
  * Une liste des notes affichees sous forme de cartes (titre, extrait du contenu, tags, date)
  * Boutons modifier et supprimer sur chaque carte
  * Modal ou section pour modifier une note
  * Style CSS integre : design moderne, responsive, couleurs agreables
  * JavaScript integre : appels fetch vers l'API, pas de framework
- tests/test_frontend.py (NOUVEAU) : tests basiques — verifier que GET / retourne 200 et contient "NoteKeeper", verifier que le fichier static/index.html existe et contient les elements attendus (form, input, button).

Utilise des imports absolus simples. Chaque fichier doit etre complet et autonome."""

    result = send_until_delegation(conv_id, prompt)
    if not result:
        return False

    time.sleep(2)

    step("Verification etape 5...")
    files, structure_ok = check_minimum_files(project_path, min_py=6, min_total=8)

    content_ok = True

    # Vérifier que index.html existe
    html_files = [f for f in files if f.endswith(".html")]
    if html_files:
        for f in html_files:
            full_path = os.path.join(project_path, f.replace("/", os.sep))
            if os.path.isfile(full_path):
                with open(full_path, encoding="utf-8", errors="ignore") as fh:
                    html_content = fh.read()
                checks = ["<form", "<input", "fetch(", "NoteKeeper"]
                for check in checks:
                    if check.lower() in html_content.lower():
                        ok(f"  {f} contient '{check}'")
                    else:
                        fail(f"  {f} ne contient PAS '{check}'")
                        content_ok = False
    else:
        fail("Aucun fichier HTML trouve")
        content_ok = False

    # Vérifier CORS dans api.py
    py_files = [f for f in files if f.endswith(".py")]
    for f in py_files:
        if "api" in f.lower() and "test" not in f.lower():
            check_file_content(project_path, f, ["CORSMiddleware"])

    ensure_conftest(project_path)
    install_deps(project_path)
    tests_ok, _ = run_tests(project_path)

    success = structure_ok and tests_ok
    return {
        "etape": 5,
        "name": "Frontend HTML/JS",
        "files": len(files),
        "structure_ok": structure_ok,
        "content_ok": content_ok,
        "tests_ok": tests_ok,
        "success": success,
    }


# ─── Main ───

if __name__ == "__main__":
    header("TEST LIVE INCREMENTAL — NoteKeeper")
    print(f"  Dossier de test : {os.path.join(TEST_ROOT, PROJECT_FOLDER)}")
    print(f"  Serveur : {BASE_URL}")
    print("  5 etapes incrementales sur un seul projet")
    print()

    # Vérifier que le serveur est accessible
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=10)
        ok(f"Serveur accessible (status={resp.status_code})")
    except Exception as e:
        fail(f"Serveur inaccessible ! Erreur: {e}")
        fail("Lancez le serveur avec: uvicorn backend.app:app --reload --port 8000")
        sys.exit(1)

    # Nettoyer le dossier de test si existant
    project_path = os.path.join(TEST_ROOT, PROJECT_FOLDER)
    if os.path.isdir(project_path):
        step("Nettoyage du dossier de test existant...")
        shutil.rmtree(project_path, ignore_errors=True)
        ok("Dossier nettoye")

    # Créer le projet
    project_id, project_path = create_project(
        "NoteKeeper", PROJECT_FOLDER, "Gestionnaire de notes personnel — test incremental 5 etapes"
    )
    if not project_id:
        fail("Impossible de creer le projet. Arret.")
        sys.exit(1)

    # Exécuter les 5 étapes
    results = []
    etapes = [
        etape1_structure_base,
        etape2_crud,
        etape3_recherche_tags,
        etape4_api_rest,
        etape5_frontend,
    ]

    for etape_fn in etapes:
        result = etape_fn(project_id, project_path)
        if result and isinstance(result, dict):
            results.append(result)
            if not result["success"]:
                warn(f"Etape {result['etape']} echouee — on continue quand meme")
        else:
            fail(f"Etape {etape_fn.__name__} a retourne un resultat invalide")
            results.append(
                {
                    "etape": len(results) + 1,
                    "name": etape_fn.__name__,
                    "files": 0,
                    "structure_ok": False,
                    "content_ok": False,
                    "tests_ok": False,
                    "success": False,
                }
            )

    # ─── Rapport final ───
    header("RAPPORT FINAL — NoteKeeper (5 etapes)")

    total_success = 0
    for r in results:
        status = f"{C.OK}SUCCES{C.END}" if r["success"] else f"{C.FAIL}ECHEC{C.END}"
        struct = f"{C.OK}struct OK{C.END}" if r.get("structure_ok") else f"{C.FAIL}struct KO{C.END}"
        content = (
            f"{C.OK}contenu OK{C.END}" if r.get("content_ok") else f"{C.FAIL}contenu KO{C.END}"
        )
        tests = f"{C.OK}tests OK{C.END}" if r.get("tests_ok") else f"{C.FAIL}tests KO{C.END}"

        print(
            f"  {status}  Etape {r['etape']}: {r['name']:25s}  {r['files']:2d} fichiers  {struct}  {content}  {tests}"
        )
        if r["success"]:
            total_success += 1

    print()
    print(f"  {C.BOLD}Score : {total_success}/{len(results)} etapes reussies{C.END}")

    # Analyse de la reprise de projet
    section("ANALYSE — Reprise de projet")

    # Vérifier que les fichiers de l'étape 1 n'ont pas été écrasés par l'étape 2
    all_files = discover_project_files(project_path)
    print(f"  Fichiers finaux dans le projet : {len(all_files)}")
    for f in all_files:
        fpath = os.path.join(project_path, f.replace("/", os.sep))
        size = os.path.getsize(fpath) if os.path.isfile(fpath) else 0
        info(f"  {f} ({size} bytes)")

    # Vérifier artefacts markdown
    artifacts_found = False
    for f in all_files:
        if f.endswith(".py"):
            fpath = os.path.join(project_path, f.replace("/", os.sep))
            with open(fpath, encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
            if "```python" in content or (
                content.strip().startswith("```") and not content.strip().startswith("#")
            ):
                fail(f"Artefact markdown dans {f}")
                artifacts_found = True

    if not artifacts_found:
        ok("Aucun artefact markdown dans les fichiers Python")

    # Lancer tous les tests une dernière fois
    section("TESTS FINAUX — Tous les tests du projet")
    ensure_conftest(project_path)
    install_deps(project_path)
    final_tests_ok, final_output = run_tests(project_path)

    print()
    print(f"  {C.BOLD}Projet : {os.path.join(TEST_ROOT, PROJECT_FOLDER)}{C.END}")
    print(f"  {C.BOLD}Project ID : {project_id}{C.END}")
    print(f"\n  Pour supprimer : DELETE {BASE_URL}/api/projects/{project_id}")
    print()
