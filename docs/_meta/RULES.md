# Règles de Gouvernance Documentaire - JARVIS 2.0

**Statut** : REFERENCE  
**Version** : 1.0  
**Date** : 2026-02-10

---

## 🎯 Principe Fondamental

**1 sujet = 1 document de référence** (éviter les redondances)

Tout le reste est `work` ou `history`.

---

## 📂 Arborescence et Séparation Stricte

### `docs/reference/`
- **Nature** : Documents contractuels validés (source de vérité)
- **Modification** : Gelés - toute modification = nouvelle version
- **Nommage** : `NOM_SPECIFICATION.md`
- **En-tête requis** :
  ```markdown
  **Statut** : REFERENCE
  **Version** : X.Y
  **Date** : YYYY-MM-DD
  **Remplace** : [document précédent si applicable]
  ```

### `docs/work/`
- **Nature** : Documents en cours (audits, analyses, brouillons)
- **Durée de vie** : Limitée, revue périodique
- **Nommage** : `YYYYMMDD_NOM.md`
- **En-tête requis** :
  ```markdown
  **Statut** : WORK
  **Date** : YYYY-MM-DD
  **Objectif** : [description courte]
  ```

### `docs/history/`
- **Nature** : Archive lecture seule (traçabilité)
- **Contenu** : Documents obsolètes/remplacés/terminés
- **Nommage** : Conserver nom original
- **Modification** : **INTERDITE**
- **Preuve d'archivage** : Ajouter `_ARCHIVED_YYYY-MM-DD.txt` précisant raison + référence de remplacement

### `docs/_meta/`
- **Nature** : Index, règles, templates, changelog
- **Contenu** :
  - `INDEX.md` - Point d'entrée unique
  - `RULES.md` - Ce document
  - `CHANGELOG.md` - Historique des modifications
  - `IA_CONTEXT.md` - Contexte pour IA externe

---

## 🔄 Règles d'Entrée/Sortie

### `work` → `reference`
**Conditions** :
- Document complet et validé
- Revue technique effectuée
- Versioning appliqué
- INDEX.md mis à jour

### `reference` → `history`
**Conditions** :
- Ancienne version remplacée par nouvelle
- Document obsolète
- Indication claire du remplaçant dans l'archive

### `work` → `history`
**Conditions** :
- Mission terminée
- Document périmé
- Analyse ponctuelle archivée

### `history`
**Règle absolue** : Aucune modification autorisée

---

## 🔍 Gouvernance

### Revue Mensuelle de `docs/work/`
- Archiver les documents terminés
- Promouvoir les documents validés vers `reference`
- Nettoyer les brouillons obsolètes

### Maintien de `docs/_meta/INDEX.md`
- Point d'entrée unique à jour
- Cartographie complète des documents
- Liens vers documents clés

### Audit Documentaire (sans réécriture)
1. Identifier toutes les sources/documents liés à un sujet
2. Classer chaque document :
   - (a) TEMPORAIRE/WIP
   - (b) OBSOLÈTE
   - (c) VALIDE MAIS INCOMPLET
   - (d) VALIDE ET RÉFÉRENCE
3. Pour chaque doc : statut, apport réel, chevauchements, décision (conserver/archiver/supprimer) avec justification
4. Produire une cartographie + liste des documents qui font foi + liste à exclure

---

## ✅ Checklist de Création de Document

### Document `reference`
- [ ] Nommage : `NOM_SPECIFICATION.md`
- [ ] En-tête complet (statut, version, date)
- [ ] Contenu validé et complet
- [ ] Ajout dans `INDEX.md`
- [ ] Ajout dans `CHANGELOG.md`

### Document `work`
- [ ] Nommage : `YYYYMMDD_NOM.md`
- [ ] En-tête avec statut et objectif
- [ ] Durée de vie estimée
- [ ] Revue planifiée

### Archivage vers `history`
- [ ] Fichier `_ARCHIVED_YYYY-MM-DD.txt` créé
- [ ] Raison d'archivage documentée
- [ ] Référence de remplacement indiquée
- [ ] Retrait de `INDEX.md` (si applicable)
- [ ] Ajout dans `CHANGELOG.md`
