# AGENTS.md

Guide condensé pour les assistants IA. **`CLAUDE.md` à la racine est la
référence canonique** (pipeline vidéo → spec → suite, layout, conventions,
pièges connus) : la lire et l'appliquer, quel que soit l'assistant. Répondre
en français.

## Mémoire (trois couches qui coexistent)

1. **Mémoire du projet (ce dépôt, publiable)** : `memory/` à la racine —
   faits durables du projet, **anonymisés** (aucune donnée personnelle, aucun
   chemin machine, aucune URL privée) ; index `memory/MEMORY.md`, règles dans
   `memory/README.md`.
2. **Base privée inter-projets** : `E:\QA_GenAI\agent-memory\` — profil et
   préférences de l'utilisateur, spécificités du poste, faits transverses,
   recherches web ; contrat dans son `PROTOCOLE.md`. Jamais publiée.
3. **Mémoire automatique de Claude Code** (Claude seulement) — pointeurs
   internes, sans dupliquer les deux autres couches.

Lire les deux index en début de session. Fait nouveau : publiable et propre
au projet → couche 1 ; personnel, lié au poste ou inter-projets → couche 2.
Une fiche par fait, index mis à jour dans la même opération, jamais de
secrets — nulle part.
