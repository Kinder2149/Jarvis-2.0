r"""
Tests Live — Projets de test via l'API JARVIS 2.0
Crée 3 projets de difficulté croissante dans D:\Coding\TEST,
envoie les demandes de code via Jarvis_maitre, et vérifie les résultats.

Prérequis : serveur lancé sur http://localhost:8000
"""

import os
import subprocess
import sys
import time

import requests

BASE_URL = "http://localhost:8000"
TEST_ROOT = r"D:\Coding\TEST"


# ─── Couleurs console ───
class C:
    OK = "\033[92m"
    WARN = "\033[93m"
    FAIL = "\033[91m"
    BOLD = "\033[1m"
    END = "\033[0m"
    BLUE = "\033[94m"


def header(title):
    print(f"\n{C.BOLD}{'=' * 60}{C.END}")
    print(f"{C.BOLD}{C.BLUE}  {title}{C.END}")
    print(f"{C.BOLD}{'=' * 60}{C.END}\n")


def step(msg):
    print(f"  {C.BLUE}▶{C.END} {msg}")


def ok(msg):
    print(f"  {C.OK}✅ {msg}{C.END}")


def warn(msg):
    print(f"  {C.WARN}⚠️  {msg}{C.END}")


def fail(msg):
    print(f"  {C.FAIL}❌ {msg}{C.END}")


def info(msg):
    print(f"    {msg}")


# ─── Helpers ───


def create_project(name, folder_name, description):
    """Crée un projet via l'API, retourne project_id ou None."""
    path = os.path.join(TEST_ROOT, folder_name)
    os.makedirs(path, exist_ok=True)

    resp = requests.post(
        f"{BASE_URL}/api/projects", json={"name": name, "path": path, "description": description}
    )
    if resp.status_code == 200:
        project = resp.json()
        ok(f"Projet créé : {project['name']} (id={project['id'][:8]}...)")
        return project["id"], path
    else:
        fail(f"Création projet échouée : {resp.status_code} — {resp.text}")
        return None, path


def create_conversation(project_id, agent_id="JARVIS_Maître", title="Test"):
    """Crée une conversation, retourne conversation_id ou None."""
    resp = requests.post(
        f"{BASE_URL}/api/projects/{project_id}/conversations",
        json={"agent_id": agent_id, "title": title},
    )
    if resp.status_code == 200:
        conv = resp.json()
        ok(f"Conversation créée (agent={agent_id}, id={conv['id'][:8]}...)")
        return conv["id"]
    else:
        fail(f"Création conversation échouée : {resp.status_code} — {resp.text}")
        return None


def send_message(conversation_id, content, timeout=120):
    """Envoie un message et attend la réponse. Retourne le dict résultat ou None."""
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
            ok(f"Réponse reçue ({len(response_text)} chars)")

            # Vérifier présence marqueurs de délégation
            if "[DEMANDE_CODE_CODEUR:" in response_text:
                ok("Marqueur [DEMANDE_CODE_CODEUR] détecté dans la réponse")

            delegations = result.get("delegations") or []
            if delegations:
                ok(f"Délégations exécutées : {len(delegations)}")
                for d in delegations:
                    info(f"  → {d.get('agent', '?')} : success={d.get('success', '?')}")
            else:
                warn("Aucune délégation exécutée")
                # Afficher un extrait de la réponse pour diagnostic
                preview = response_text[:300].replace("\n", " ")
                info(f"  Réponse (extrait) : {preview}...")

            return result
        else:
            fail(f"Envoi message échoué : {resp.status_code} — {resp.text[:200]}")
            return None
    except requests.exceptions.Timeout:
        fail(f"Timeout après {timeout}s")
        return None


def send_until_delegation(conv_id, initial_prompt, max_followups=3, timeout=180):
    """
    Envoie le prompt initial puis des relances jusqu'à obtenir une délégation.
    Retourne le résultat final (avec délégations) ou le dernier résultat.
    """
    followup_prompts = [
        "OK je valide ton plan. Passe directement à l'exécution : délègue au CODEUR avec [DEMANDE_CODE_CODEUR: ...] en incluant la liste complète des fichiers à produire.",
        "Produis le code maintenant. Utilise le marqueur [DEMANDE_CODE_CODEUR: instruction complète] pour déléguer au CODEUR. Inclus TOUS les fichiers dans l'instruction.",
        "EXÉCUTION IMMÉDIATE. Délègue au CODEUR avec [DEMANDE_CODE_CODEUR: ...]. Ne fais plus d'audit ni de plan.",
    ]

    step("Message 1 : demande initiale...")
    result = send_message(conv_id, initial_prompt, timeout=timeout)
    if not result:
        return None

    delegations = result.get("delegations") or []
    if delegations:
        return result

    for i in range(min(max_followups, len(followup_prompts))):
        step(f"Message {i + 2} : relance pour déclencher la délégation...")
        result = send_message(conv_id, followup_prompts[i], timeout=timeout)
        if not result:
            return None
        delegations = result.get("delegations") or []
        if delegations:
            return result

    warn(f"Aucune délégation obtenue après {max_followups + 1} messages")
    return result


def check_files_exist(project_path, expected_files):
    """Vérifie que les fichiers attendus existent sur le disque."""
    results = {}
    for f in expected_files:
        full_path = os.path.join(project_path, f)
        exists = os.path.isfile(full_path)
        results[f] = exists
        if exists:
            size = os.path.getsize(full_path)
            ok(f"Fichier trouvé : {f} ({size} bytes)")
        else:
            fail(f"Fichier MANQUANT : {f}")
    return results


def discover_project_files(project_path):
    """Découvre tous les fichiers .py et .txt écrits dans le projet (hors cache)."""
    found = []
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".pytest_cache")]
        for fname in files:
            if fname.endswith((".py", ".txt", ".json", ".yaml", ".toml")):
                rel = os.path.relpath(os.path.join(root, fname), project_path)
                rel = rel.replace("\\", "/")
                if rel == "conftest.py":
                    continue
                found.append(rel)
    return sorted(found)


def check_minimum_structure(project_path, min_src=1, min_tests=0, min_total=2):
    """Vérifie la structure minimale du projet (fichiers dans src/ et tests/)."""
    files = discover_project_files(project_path)
    src_files = [f for f in files if f.startswith("src/")]
    test_files = [f for f in files if f.startswith("tests/")]
    other_files = [f for f in files if not f.startswith("src/") and not f.startswith("tests/")]

    ok(f"Fichiers découverts : {len(files)} total")
    for f in files:
        size = os.path.getsize(os.path.join(project_path, f.replace("/", os.sep)))
        info(f"  {f} ({size} bytes)")

    structure_ok = True
    if len(src_files) >= min_src:
        ok(f"src/ : {len(src_files)} fichier(s)")
    else:
        fail(f"src/ : {len(src_files)} fichier(s) (minimum {min_src})")
        structure_ok = False
    if len(test_files) >= min_tests:
        ok(f"tests/ : {len(test_files)} fichier(s)")
    else:
        fail(f"tests/ : {len(test_files)} fichier(s) (minimum {min_tests})")
        structure_ok = False
    if len(files) >= min_total:
        ok(f"Total : {len(files)} fichier(s) (minimum {min_total})")
    else:
        fail(f"Total : {len(files)} fichier(s) (minimum {min_total})")
        structure_ok = False

    return files, src_files, test_files, structure_ok


def check_file_content(project_path, filepath, checks):
    """Vérifie le contenu d'un fichier (liste de strings à trouver)."""
    full_path = os.path.join(project_path, filepath)
    if not os.path.isfile(full_path):
        fail(f"Impossible de vérifier {filepath} — fichier absent")
        return False

    with open(full_path, encoding="utf-8") as fh:
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
        ok(f"  {filepath} — pas d'artefacts markdown")

    return all_ok


def run_tests(project_path, test_command="python -m pytest tests/ -v --tb=short"):
    """Lance les tests pytest dans le dossier projet."""
    step(f"Lancement tests dans {project_path}")
    try:
        result = subprocess.run(
            test_command, shell=True, cwd=project_path, capture_output=True, text=True, timeout=60
        )
        output = result.stdout + result.stderr

        # Chercher le résumé pytest
        for line in output.split("\n"):
            line_stripped = line.strip()
            if "passed" in line_stripped or "failed" in line_stripped or "error" in line_stripped:
                if "===" in line_stripped:
                    info(f"  {line_stripped}")

        if result.returncode == 0:
            ok("Tests passent ✅")
        else:
            fail(f"Tests échoués (code={result.returncode})")
            # Afficher les erreurs
            for line in output.split("\n"):
                if "FAILED" in line or "ERROR" in line or "assert" in line.lower():
                    info(f"  {line.strip()}")

        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        fail("Tests timeout (60s)")
        return False, ""
    except Exception as e:
        fail(f"Erreur exécution tests : {e}")
        return False, ""


def delete_project(project_id):
    """Supprime un projet via l'API."""
    resp = requests.delete(f"{BASE_URL}/api/projects/{project_id}")
    if resp.status_code == 200:
        ok(f"Projet supprimé (id={project_id[:8]}...)")
    else:
        warn(f"Suppression projet échouée : {resp.status_code}")


# ─── Tests Live ───


def test_niveau1_calculatrice():
    """Niveau 1 — Calculatrice CLI simple"""
    header("NIVEAU 1 — Calculatrice CLI")

    project_id, project_path = create_project(
        "Test Calculatrice", "test_calculatrice", "Calculatrice CLI pour test live niveau 1"
    )
    if not project_id:
        return None

    conv_id = create_conversation(project_id, title="Création calculatrice")
    if not conv_id:
        return {"project_id": project_id, "success": False}

    prompt1 = """Crée une calculatrice CLI Python avec :
- src/calculator.py : classe Calculator avec méthodes statiques add(a,b), subtract(a,b), multiply(a,b), divide(a,b). Division par zéro lève ZeroDivisionError. Entrées non numériques lèvent ValueError.
- src/main.py : interface CLI qui demande 2 nombres et une opération (+,-,*,/), appelle Calculator, affiche le résultat.
- tests/test_calculator.py : tests pytest couvrant tous les cas (succès des 4 opérations, division par zéro, entrées invalides).
- requirements.txt : pytest

Utilise des imports absolus simples. Chaque fichier doit être complet."""

    result = send_until_delegation(conv_id, prompt1)

    time.sleep(2)

    # Découvrir les fichiers réellement écrits
    step("Vérification des fichiers sur le disque...")
    all_files, src_files, test_files, structure_ok = check_minimum_structure(
        project_path, min_src=2, min_tests=1, min_total=3
    )

    # Vérifier le contenu des fichiers src
    step("Vérification du contenu...")
    for f in src_files:
        if "calculator" in f.lower() or "calc" in f.lower():
            check_file_content(
                project_path, f, ["class Calculator", "def add", "def divide", "ZeroDivisionError"]
            )
    for f in test_files:
        if f.endswith(".py"):
            check_file_content(project_path, f, ["import pytest"])

    # Lancer les tests
    step("Exécution des tests...")
    conftest_path = os.path.join(project_path, "conftest.py")
    if not os.path.isfile(conftest_path):
        with open(conftest_path, "w", encoding="utf-8") as f:
            f.write(
                "import sys, os\nsys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))\n"
            )
        info("  conftest.py créé pour les imports")

    tests_ok, _ = run_tests(project_path)

    return {
        "project_id": project_id,
        "name": "Calculatrice CLI",
        "files_expected": 3,
        "files_found": len(all_files),
        "tests_pass": tests_ok,
        "success": structure_ok and tests_ok,
    }


def test_niveau2_todo():
    """Niveau 2 — Gestionnaire de tâches TODO"""
    header("NIVEAU 2 — Gestionnaire TODO")

    project_id, project_path = create_project(
        "Test TODO", "test_todo", "Gestionnaire de tâches pour test live niveau 2"
    )
    if not project_id:
        return None

    conv_id = create_conversation(project_id, title="Création TODO")
    if not conv_id:
        return {"project_id": project_id, "success": False}

    prompt1 = """Crée un gestionnaire de tâches TODO en Python avec persistance JSON :
- src/storage.py : classe JsonStorage avec méthodes load() et save(data) qui lit/écrit un fichier JSON. Gère le cas où le fichier n'existe pas encore (retourne liste vide).
- src/todo.py : classe TodoManager qui utilise JsonStorage. Méthodes : add_task(title) retourne l'id, list_tasks() retourne la liste, complete_task(task_id) marque comme complétée, delete_task(task_id) supprime. Chaque tâche a un id (int auto-incrémenté), title, completed (bool).
- src/cli.py : interface CLI avec argparse. Commandes : add <title>, list, complete <id>, delete <id>.
- tests/test_todo.py : tests pytest pour TodoManager (add, list, complete, delete) avec fichier JSON temporaire.
- tests/test_storage.py : tests pytest pour JsonStorage (load fichier inexistant, save/load cycle).
- requirements.txt : pytest

Utilise des imports absolus simples. Chaque fichier doit être complet."""

    result = send_until_delegation(conv_id, prompt1)

    time.sleep(2)

    step("Vérification des fichiers sur le disque...")
    all_files, src_files, test_files, structure_ok = check_minimum_structure(
        project_path, min_src=2, min_tests=1, min_total=4
    )

    step("Vérification du contenu...")
    for f in src_files:
        if "storage" in f.lower():
            check_file_content(project_path, f, ["class JsonStorage", "def load", "def save"])
        if "todo" in f.lower() or "manager" in f.lower() or "task" in f.lower():
            check_file_content(project_path, f, ["def add"])

    conftest_path = os.path.join(project_path, "conftest.py")
    if not os.path.isfile(conftest_path):
        with open(conftest_path, "w", encoding="utf-8") as f:
            f.write(
                "import sys, os\nsys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))\n"
            )
        info("  conftest.py créé pour les imports")

    tests_ok, _ = run_tests(project_path)

    return {
        "project_id": project_id,
        "name": "Gestionnaire TODO",
        "files_expected": 4,
        "files_found": len(all_files),
        "tests_pass": tests_ok,
        "success": structure_ok and tests_ok,
    }


def test_niveau3_miniblog():
    """Niveau 3 — API REST mini-blog FastAPI"""
    header("NIVEAU 3 — API REST Mini-Blog")

    project_id, project_path = create_project(
        "Test MiniBlog", "test_miniblog", "API REST mini-blog pour test live niveau 3"
    )
    if not project_id:
        return None

    conv_id = create_conversation(project_id, title="Création MiniBlog")
    if not conv_id:
        return {"project_id": project_id, "success": False}

    prompt1 = """Crée une API REST mini-blog avec FastAPI et stockage en mémoire :
- src/models.py : modèles Pydantic — ArticleBase(title: str, content: str, author: str), ArticleCreate(ArticleBase), ArticleUpdate avec champs optionnels, Article(ArticleBase) avec id: str, created_at: datetime, updated_at: datetime.
- src/database.py : classe InMemoryDB avec méthodes CRUD — create(article: ArticleCreate) -> Article, get_all() -> list[Article], get_by_id(id) -> Article|None, update(id, data: ArticleUpdate) -> Article|None, delete(id) -> bool. Pagination avec skip/limit sur get_all. Recherche par mot-clé dans titre/contenu.
- src/main.py : app FastAPI avec routes POST /articles/, GET /articles/ (avec query params skip, limit, search), GET /articles/{id}, PUT /articles/{id}, DELETE /articles/{id}. Retourne 404 si article non trouvé.
- tests/test_api.py : tests pytest avec TestClient de FastAPI. Couvre : création, lecture, mise à jour, suppression, 404, pagination, recherche.
- requirements.txt : fastapi, uvicorn, pydantic, pytest, httpx

Utilise des imports absolus simples. Chaque fichier doit être complet."""

    result = send_until_delegation(conv_id, prompt1)

    time.sleep(2)

    step("Vérification des fichiers sur le disque...")
    all_files, src_files, test_files, structure_ok = check_minimum_structure(
        project_path, min_src=2, min_tests=1, min_total=4
    )

    step("Vérification du contenu...")
    for f in src_files:
        if "model" in f.lower():
            check_file_content(project_path, f, ["ArticleBase", "ArticleCreate"])
        if "main" in f.lower() or "app" in f.lower():
            check_file_content(project_path, f, ["FastAPI"])

    conftest_path = os.path.join(project_path, "conftest.py")
    if not os.path.isfile(conftest_path):
        with open(conftest_path, "w", encoding="utf-8") as f:
            f.write(
                "import sys, os\nsys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))\n"
            )
        info("  conftest.py créé pour les imports")

    # Installer les dépendances si requirements.txt existe
    req_path = os.path.join(project_path, "requirements.txt")
    if os.path.isfile(req_path):
        step("Installation dépendances...")
        subprocess.run(
            f"{sys.executable} -m pip install -r requirements.txt -q",
            shell=True,
            cwd=project_path,
            capture_output=True,
        )

    tests_ok, _ = run_tests(project_path)

    return {
        "project_id": project_id,
        "name": "API REST Mini-Blog",
        "files_expected": 4,
        "files_found": len(all_files),
        "tests_pass": tests_ok,
        "success": structure_ok and tests_ok,
    }


# ─── Main ───

if __name__ == "__main__":
    header("TESTS LIVE — JARVIS 2.0 Orchestration")
    print(f"  Dossier de test : {TEST_ROOT}")
    print(f"  Serveur : {BASE_URL}")
    print()

    # Vérifier que le serveur est accessible
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=5)
        ok(f"Serveur accessible (status={resp.status_code})")
    except Exception:
        fail("Serveur inaccessible ! Lancez-le avant de relancer ce script.")
        sys.exit(1)

    results = []

    # Test Niveau 1
    r1 = test_niveau1_calculatrice()
    if r1:
        results.append(r1)

    # Test Niveau 2
    r2 = test_niveau2_todo()
    if r2:
        results.append(r2)

    # Test Niveau 3
    r3 = test_niveau3_miniblog()
    if r3:
        results.append(r3)

    # ─── Rapport final ───
    header("RAPPORT FINAL")

    for r in results:
        status = f"{C.OK}✅ SUCCÈS{C.END}" if r.get("success") else f"{C.FAIL}❌ ÉCHEC{C.END}"
        files_status = f"{r['files_found']} fichiers (min {r['files_expected']})"
        tests_status = (
            f"{C.OK}tests OK{C.END}" if r.get("tests_pass") else f"{C.FAIL}tests KO{C.END}"
        )
        print(f"  {status}  {r['name']:25s}  {files_status:25s}  {tests_status}")

    print()

    # Analyse des points corrigés
    header("ANALYSE DES CORRECTIONS")

    all_files_ok = all(r.get("files_found", 0) == r.get("files_expected", 0) for r in results)
    all_tests_ok = all(r.get("tests_pass", False) for r in results)

    # Vérifier artefacts markdown dans tous les fichiers générés
    artifacts_found = False
    for folder in ["test_calculatrice", "test_todo", "test_miniblog"]:
        folder_path = os.path.join(TEST_ROOT, folder)
        if os.path.isdir(folder_path):
            for root, dirs, files in os.walk(folder_path):
                for fname in files:
                    if fname.endswith(".py"):
                        fpath = os.path.join(root, fname)
                        with open(fpath, encoding="utf-8", errors="ignore") as fh:
                            content = fh.read()
                        if "```python" in content or (
                            content.strip().startswith("```")
                            and not content.strip().startswith("#")
                        ):
                            fail(f"Artefact markdown trouvé dans {fpath}")
                            artifacts_found = True

    if not artifacts_found:
        ok("Problème 1 (artefacts markdown) : RÉSOLU — aucun artefact trouvé")
    else:
        fail("Problème 1 (artefacts markdown) : PERSISTE")

    if all_files_ok:
        ok("Problème 3 (max_tokens / fichiers incomplets) : RÉSOLU — tous les fichiers produits")
    else:
        warn("Problème 3 (max_tokens / fichiers incomplets) : PARTIELLEMENT résolu")

    if all_tests_ok:
        ok("Qualité du code : BONNE — tous les tests passent")
    else:
        warn("Qualité du code : À AMÉLIORER — certains tests échouent")

    print()

    # Nettoyage optionnel
    print(f"  {C.BOLD}Projets créés (non supprimés pour inspection) :{C.END}")
    for r in results:
        if r.get("project_id"):
            info(f"  ID: {r['project_id'][:8]}... — {r['name']}")

    print(
        "\n  Pour supprimer : utilisez le bouton 🗑️ dans l'interface ou l'API DELETE /api/projects/{id}"
    )
    print()
