"""
Test manuel du service de génération de documents Word.
Lancer depuis la racine du projet : python -m tests.test_docx_generator
"""

from backend.services.docx_generator_service import generer_docx


contenu = """
# Rapport sur les énergies renouvelables

## Introduction

Les énergies renouvelables sont **essentielles** pour la transition écologique.

## Les principales sources

- Solaire photovoltaïque
- Éolien terrestre et offshore
- Hydroélectricité
- Biomasse

## Avantages

1. Réduction des émissions de CO2
2. Indépendance énergétique
3. Création d'emplois locaux

## Conclusion

Le développement des renouvelables est *crucial* pour atteindre les objectifs climatiques.
"""


if __name__ == "__main__":
    nom = generer_docx(contenu, titre="Rapport sur les Énergies Renouvelables", prefix="rapport")
    print(f"✅ Document créé : {nom}")
    print(f"📁 Emplacement : backend/generated_documents/{nom}")