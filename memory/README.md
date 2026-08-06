# memory/ : mémoire projet des assistants IA

Fiches de travail persistantes des assistants IA (Claude Code, GitHub Copilot,
Codex…) sur ce dépôt. **Committée et publiable**, règles non négociables :

1. **Anonymisé** : aucune donnée personnelle (nom, e-mail, compte), aucun
   chemin machine, aucune URL privée, aucun secret. Le personnel, le lié-au-
   poste et l'inter-projets vont dans la base de mémoire privée de
   l'utilisateur, jamais ici.
2. **Une fiche = un fait durable du projet** : leçon de débogage coûteuse,
   décision avec son contexte, procédure d'environnement générique. Pas de
   journal de session, pas de duplication des docs du dépôt (CLAUDE.md reste
   la référence du pipeline).
3. **Dates absolues** ; une fiche est une observation datée, pas un état
   vivant : vérifier avant d'affirmer.
4. **`MEMORY.md` est l'index** : une ligne par fiche, mis à jour dans la même
   opération que toute création/suppression. Mettre à jour plutôt que
   dupliquer ; supprimer ce qui est devenu faux.

Format d'une fiche :

```markdown
---
name: slug-kebab-case
description: résumé en une ligne, décide si on ouvre la fiche
type: projet | reference | recherche
date: AAAA-MM-JJ
---

Le fait. **Pourquoi :** le contexte. **Comment appliquer :** le geste attendu.
```
