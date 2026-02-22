"""Script pour nettoyer les projets de test de la base de données"""
import sqlite3

conn = sqlite3.connect('jarvis_data.db')
cursor = conn.cursor()

# Supprimer projets de test
cursor.execute("""
    DELETE FROM projects 
    WHERE path LIKE '%test_%' 
       OR path LIKE '%Temp%'
       OR name LIKE 'Test%'
""")

deleted = cursor.rowcount
conn.commit()
conn.close()

print(f"✅ {deleted} projets de test supprimés de la base de données")
