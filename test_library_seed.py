"""
Script de test pour vérifier le seed automatique de la Library
Exécuter après avoir supprimé jarvis_data.db pour tester le seed
"""

import asyncio
from backend.db.database import Database
from backend.services.function_executor import FunctionExecutor


async def test_library_seed():
    """Teste le seed automatique de la Library"""
    print("🧪 Test du seed automatique de la Library\n")
    
    db = Database()
    await db.initialize()
    
    # Test 1 : Vérifier le seed
    print("📊 Test 1 : Vérification du seed automatique")
    await db.seed_library_if_empty()
    
    # Test 2 : Compter les documents
    print("\n📊 Test 2 : Comptage des documents")
    docs = await db.list_library_documents()
    print(f"   ✅ {len(docs)} documents trouvés dans la BDD")
    
    # Test 3 : Vérifier les catégories
    print("\n📊 Test 3 : Vérification des catégories")
    categories = {}
    for doc in docs:
        cat = doc['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in categories.items():
        print(f"   - {cat}: {count} documents")
    
    # Test 4 : Tester l'accès par les agents
    print("\n📊 Test 4 : Test d'accès agents via function")
    executor = FunctionExecutor(db)
    
    # Test get_library_document
    result = await executor.get_library_document("FastAPI", "libraries")
    if result.get("success"):
        print(f"   ✅ get_library_document('FastAPI') fonctionne")
        print(f"      Contenu: {result['document']['description']}")
    else:
        print(f"   ❌ Erreur: {result.get('error')}")
    
    # Test get_library_list
    result2 = await executor.get_library_list("methodologies")
    if result2.get("success"):
        print(f"   ✅ get_library_list('methodologies') fonctionne")
        print(f"      {len(result2['documents'])} documents trouvés")
        for doc in result2['documents']:
            print(f"      - {doc['name']}")
    else:
        print(f"   ❌ Erreur: {result2.get('error')}")
    
    # Test 5 : Vérifier quelques documents clés
    print("\n📊 Test 5 : Vérification de documents clés")
    key_docs = [
        ("FastAPI", "libraries"),
        ("Pytest", "libraries"),
        ("Audit > Plan > Exécution", "methodologies"),
        ("Délégation au CODEUR", "prompts"),
        ("Conventions de code", "personal")
    ]
    
    for name, category in key_docs:
        result = await executor.get_library_document(name, category)
        if result.get("success"):
            print(f"   ✅ {name} ({category})")
        else:
            print(f"   ❌ {name} ({category}) - MANQUANT")
    
    print("\n✅ Tests terminés !")
    print(f"\n📝 Résumé : {len(docs)} documents peuplés automatiquement")
    print("   Les agents JARVIS_Maître et BASE peuvent maintenant accéder à la Library")


if __name__ == "__main__":
    asyncio.run(test_library_seed())
