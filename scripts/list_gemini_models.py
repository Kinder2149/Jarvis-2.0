"""
Script pour lister les modèles Gemini disponibles
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ GEMINI_API_KEY non configurée")
    exit(1)

genai.configure(api_key=api_key)

print("📋 Modèles Gemini disponibles :\n")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")
        print(f"   Description: {model.description}")
        print(f"   Méthodes: {', '.join(model.supported_generation_methods)}")
        print()
