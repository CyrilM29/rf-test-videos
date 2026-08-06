# Positionnement et état de l'art

Où se situe ce projet par rapport à ce qui existe (recherche académique,
outils commerciaux, open source), et ce qui le différencie. Document de
référence pour présenter le projet ; mis à jour 2026-07-27.

## Le créneau

Ce dépôt transforme une **vidéo brute** de test manuel (MP4 quelconque :
Teams, OBS, Game Bar : avec ou sans voix off) en **suite Robot Framework**
maintenable : plan de test métier (`specs/`), suite sans localisateurs,
page objects, puis relevé des localisateurs en live sur le SUT et preuve de
rejouabilité + fidélité visuelle. **Aucune instrumentation à la capture,
aucun accès au SUT pendant la génération.**

À notre connaissance, aucune solution publique ne couvre exactement ce
créneau : les approches existantes se répartissent en trois familles.

## 1. Recherche académique (vidéo → scénario rejouable)

La famille la plus proche : partir d'une vidéo non instrumentée.

- **V2S, Video2Scenario** (ICSE 2020/2021, lab SEMERU) : traduit des vidéos
  d'usage d'applications **Android** en scénarios rejouables, par vision par
  ordinateur (détection des touches → classification tap/long-tap/swipe →
  script). ~89 % des actions reproduites sur 175 vidéos.
  <https://ojcchar.github.io/publications/19-icse21-v2s-tool>
- **GIFdroid** (2022) : rejoue des bug reports visuels (GIF/vidéo) Android en
  mappant les keyframes sur un graphe de transitions d'écrans.
  <https://github.com/sidongfeng/gifdroid>

Limites par rapport à ce projet : mobile uniquement, pas de voix off, sortie
= script d'événements bruts (pas de couche métier, pas de page objects, pas
de maintenabilité).

## 2. Outils commerciaux (enregistrement live → test)

testRigor, mabl, Katalon, BugBug, Testim… convertissent un **enregistrement
instrumenté** (extension navigateur qui capture les événements DOM) ou du
texte libre en tests, avec self-healing. La tendance 2025-2026 est aux agents
qui pilotent un navigateur depuis un plan de test en langage naturel.

Limites : il faut instrumenter la session au moment de la capture, une
vidéo existante est inexploitable ; sorties propriétaires (pas de Robot
Framework) ; ciblent le web (pas SAP GUI/desktop).

## 3. Open source LLM (texte → test)

Générateurs texte → Playwright (playwright-ai, Playwright Agents, CodeceptJS
AI, Auto Browse…) : le point de départ est une description écrite, pas une
vidéo ; pas de séparation spec / suite / page objects.

## Les différenciateurs de ce projet

1. **Entrée = n'importe quelle vidéo.** Le stock de vidéos de démo, de
   formation ou de recette existant devient exploitable, sans refaire les
   sessions.
2. **Couche métier intermédiaire.** La spec (`specs/`) est la source de
   vérité relisible par le métier ; la suite est régénérable ; la
   traçabilité est outillée (empreinte sha256 vérifiée par
   `scripts/check_specs.py` et la CI).
3. **Séparation stricte tests / localisateurs** (page objects, héritée de
   SAPFX) : les localisateurs sont relevés **après coup** sur le SUT réel,
   validés en live (`/finalize-rf` + rf-mcp), jamais devinés.
4. **Preuve de fidélité** : rejouabilité (2 runs réels verts) **et**
   comparaison visuelle frames vidéo ↔ captures d'exécution, consignée dans
   la spec.
5. **Multi-canaux** : web aujourd'hui (Browser/Playwright), hybridation
   prévue par convention (SAP GUI, Fiori, desktop, mobile) : hors de portée
   des outils web-only.
6. **Capitalisation** : les page objects s'enrichissent vidéo après vidéo
   (`scripts/inventory_pages.py`) : le coût marginal d'une nouvelle vidéo
   sur un SUT déjà couvert décroît.
7. **Local et bi-assistant** : transcription et découpage en local (aucun
   envoi audio externe), pilotable par Claude Code comme par GitHub Copilot.

## Sources

- V2S : <https://ojcchar.github.io/publications/19-icse21-v2s-tool>,
  PDF <https://www.cs.wm.edu/~denys/pubs/V2S-CRC.pdf>
- GIFdroid : <https://github.com/sidongfeng/gifdroid>
- Panoramas outils IA 2026 : <https://www.testrail.com/blog/ai-testing-tools/>,
  <https://qa.tech/blog/the-13-best-ai-testing-tools-in-2026>,
  <https://bugbug.io/blog/test-automation-tools/web-test-recorders/>
- Open source LLM + Playwright :
  <https://github.com/vladikoff/playwright-ai>,
  <https://bug0.com/blog/20-underdog-open-source-projects-pushing-limits-ai-playwright>
