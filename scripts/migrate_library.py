import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.db.migrations import migrate_library_data


async def main():
    print("🚀 Démarrage de la migration des données de la Knowledge Base...")
    try:
        await migrate_library_data()
        print("✅ Migration terminée avec succès!")
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
