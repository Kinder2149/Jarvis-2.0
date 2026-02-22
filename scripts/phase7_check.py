import os
import sys
from pathlib import Path


def main() -> int:
    repo_root = str(Path(__file__).resolve().parents[1])
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from backend.agents.agent_factory import clear_cache, get_agent
    from backend.agents.base_agent import InvalidRuntimeMessageError

    # Force environment for the test run (no dependency on user .env state)
    os.environ["MISTRAL_API_KEY"] = os.environ.get("MISTRAL_API_KEY", "test_key")
    os.environ["USE_MISTRAL_AGENT_API"] = os.environ.get("USE_MISTRAL_AGENT_API", "1")
    os.environ["JARVIS_BASE_AGENT_ID"] = os.environ.get("JARVIS_BASE_AGENT_ID", "ag_test_base_123")
    os.environ["JARVIS_MAITRE_AGENT_ID"] = os.environ.get(
        "JARVIS_MAITRE_AGENT_ID", "ag_test_maitre_456"
    )

    clear_cache()

    base = get_agent("BASE")
    maitre = get_agent("JARVIS_Maître")

    # 1) BASE -> log agent_id
    base.log(
        "phase7_test",
        {"case": "BASE", "agent_id": base.id},
        session_id="PHASE7",
    )

    # 2) JARVIS_Maître -> log agent_id
    maitre.log(
        "phase7_test",
        {"case": "JARVIS_Maître", "agent_id": maitre.id},
        session_id="PHASE7",
    )

    # 3) Comparaison des deux
    ids_distinct = base.id != maitre.id

    # 4) Test isolation mémoire (instances + client.agent_id)
    instances_distinct = base is not maitre
    client_ids_distinct = base.client.agent_id != maitre.client.agent_id

    # 5) Test rejet message system (doit échouer avant tout appel réseau)
    system_role_rejected = False
    system_role_error = None
    try:
        base.handle([{"role": "system", "content": "x"}], session_id="PHASE7")
    except InvalidRuntimeMessageError as e:
        system_role_rejected = True
        system_role_error = str(e)

    print("BASE_ID", base.id)
    print("MAITRE_ID", maitre.id)
    print("IDS_DISTINCT", ids_distinct)
    print("INSTANCES_DISTINCT", instances_distinct)
    print("BASE_CLIENT_AGENT_ID", base.client.agent_id)
    print("MAITRE_CLIENT_AGENT_ID", maitre.client.agent_id)
    print("CLIENT_IDS_DISTINCT", client_ids_distinct)
    print("SYSTEM_ROLE_REJECTED", system_role_rejected)
    if system_role_error:
        print("SYSTEM_ROLE_ERROR", system_role_error)

    all_ok = all(
        [
            ids_distinct,
            instances_distinct,
            client_ids_distinct,
            system_role_rejected,
        ]
    )
    return 0 if all_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
