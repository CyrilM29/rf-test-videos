# Guide utilisateur : de la vidéo au test Robot Framework

Ce projet transforme une **vidéo de test manuel** (capture d'écran, avec ou
sans voix off) en **suite Robot Framework** prête à être branchée sur le
système sous test. Tout se passe en local : découpage d'images par ffmpeg,
transcription de la voix par faster-whisper (aucun envoi audio à un service
externe), lecture et génération par Claude Code dans VS Code.

```text
vidéo (.mp4)  →  /video-to-rf  →  plan de test (specs/)  →  suite (tests/robot/)
                                                          →  page objects (locators TODO)
```

Ce guide s'adresse à l'utilisateur du pipeline. Le fonctionnement interne et
les conventions de génération sont documentés dans `CLAUDE.md` (lu par
l'assistant) : inutile de le connaître pour utiliser l'outil.

---

## 1. Prérequis

Sur un nouveau poste (Windows), une seule commande depuis la racine :

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
```

Elle crée l'environnement `.venv`, installe les dépendances
(`requirements.txt`), télécharge les navigateurs Playwright et vérifie
ffmpeg (`winget install ffmpeg` s'il manque : seul prérequis hors pip, avec
Python 3.10+). Ouvrir ensuite le dossier dans VS Code : les extensions
recommandées (Python, RobotCode, Copilot, Claude Code) sont proposées
automatiquement.

Côté assistant, deux options équivalentes :

- **Claude Code** (extension VS Code) : les commandes de ce guide
  fonctionnent telles quelles ;
- **GitHub Copilot** en mode **agent** : mêmes commandes `/video-to-rf` et
  `/finalize-rf` (prompt files du dépôt), avec un **modèle à vision**
  (lecture des images de la vidéo) ; pour `/finalize-rf`, démarrer le
  serveur `robotmcp` dans la vue MCP de VS Code (déclaré dans
  `.vscode/mcp.json`).

Au **premier** lancement, le modèle de transcription (`small`, ~460 Mo) se
télécharge une seule fois dans `%USERPROFILE%\.cache\huggingface`.

## 2. Enregistrer une bonne vidéo

L'outil le plus simple sous Windows : la **Game Bar** (`Win + Alt + R` pour
démarrer/arrêter, `Win + Alt + M` pour activer le micro). OBS Studio convient
aussi. Formats acceptés : tout ce que ffmpeg lit (`.mp4`, `.webm`, `.mkv`…).

Ce qui fait la qualité de la transcription :

- **1080p minimum**, fenêtre nette, pas de zoom flou : le texte à l'écran
  doit être lisible sur une image fixe ;
- **une action à la fois**, en laissant l'écran se stabiliser une seconde
  après chaque action : chaque changement d'écran devient une image analysée ;
- **une voix off qui nomme l'intention**, pas le geste : « je filtre sur le
  client Dupont » guide le plan de test, « je clique là » n'apporte rien ;
- **un scénario par vidéo courte** (2 à 10 minutes) plutôt qu'une longue
  session fourre-tout ;
- **pas de données sensibles à l'écran** : la vidéo est relue image par image.

Déposez ensuite le fichier dans `videos/` (les vidéos ne sont pas archivées
par git : les artefacts durables sont la spec et la suite générées).

## 3. Lancer la transcription

Dans VS Code : panneau Claude Code, ou chat Copilot en mode agent (la
commande est identique) :

```text
/video-to-rf videos/mon-scenario.mp4 --language fr
```

Options utiles (transmises au script de préparation) :

| Option | Effet | Défaut |
| --- | --- | --- |
| `--language fr` | force la langue de la voix off (recommandé) | détection auto |
| `--model base` \| `small` \| `medium` | précision/poids du modèle de transcription | `small` |
| `--scene 0.2` | seuil de détection des changements d'écran (plus haut = moins d'images) | `0.10` |
| `--dedup 0` | désactive l'élimination des images quasi identiques (utile si des étapes ne diffèrent que par une saisie clavier) | `2` |
| `--no-audio` | ignore la piste audio | : |
| `--force` | refait la transcription audio d'une vidéo déjà préparée | : |

Pour préparer un **lot de vidéos** d'un coup (le script seul, hors skill) :
`python scripts/prepare_video.py videos/`, puis lancer `/video-to-rf` sur
chaque vidéo.

La skill enchaîne alors :

1. découpage de la vidéo en images aux changements d'écran (les images quasi
   identiques sont écartées) + transcription horodatée de la voix off, le
   tout fusionné en un **storyboard** chronologique (`work/<nom>/`) ;
2. lecture des images dans l'ordre du storyboard, croisée avec la voix off ;
3. **checkpoint librairies** : la skill identifie les canaux en jeu dans la
   vidéo (web, desktop, SAP, mobile…) et vérifie qu'une librairie de
   pilotage couvre chacun. Si ce n'est pas le cas, **elle vous pose la
   question** avant de générer quoi que ce soit : y compris la combinaison
   de plusieurs librairies quand la vidéo mêle plusieurs canaux ;
4. écriture du **plan de test métier** `specs/<nom>.md` (scénarios, données
   observées, points de vigilance, horodatages vidéo) ;
5. génération de la **suite** `tests/robot/ui/<domaine>/<nom>.robot` : un
   test par scénario, aucun localisateur dans les tests ;
6. création des **keywords manquants** dans
   `resources/page_objects/<écran>.resource` : corps déjà implémentés avec
   la librairie retenue, localisateurs `TODO` ;
7. validation `robot --dryrun` (obligatoirement verte) et rapport final.

Comptez quelques minutes : la transcription tourne à peu près en temps réel
sur CPU, la lecture des images dépend de leur nombre (plafonné à 120).

## 4. Ce que vous obtenez

Pour `videos/demo-connexion.mp4` :

```text
specs/demo-connexion.md                        ← le plan : à relire en premier
tests/robot/ui/web/demo-connexion.robot        ← la suite générée
resources/page_objects/login_screen.resource   ← keywords + locators TODO
work/demo-connexion/                           ← images/transcription (jetable)
```

**Relisez d'abord la spec** : c'est le contrat. Si un scénario est mal
découpé ou qu'une intention a été mal comprise, corrigez la spec (ou refaites
une vidéo plus claire) et demandez une régénération : ne retouchez pas la
suite à la main.

## 5. Après la génération : brancher le système sous test

Une vidéo ne montre jamais les identifiants techniques des éléments (ids,
sélecteurs CSS…). Les keywords générés naissent donc avec des localisateurs
« à compléter » et la suite **échoue volontairement** en exécution réelle
tant que ce travail n'est pas fait : c'est le garde-fou qui empêche un test
vert par accident.

Le choix de la librairie de pilotage se fait **pendant la génération**
(checkpoint de l'étape 3) : la skill pose la question la première fois qu'un
canal apparaît, installe la dépendance et écrit directement les corps des
keywords avec cette librairie. Sur ce poste, le canal web est branché sur
**Browser (Playwright)** depuis le 2026-07-25 (`rfbrowser init` déjà fait).

Il ne reste donc, pour chaque keyword, qu'à relever le localisateur sur
l'application et remplacer le `${EMPTY}` de la variable dans
`resources/page_objects/*.resource`.

**Ce relevé est lui aussi assisté** : la skill `/finalize-rf` pilote
l'application réelle depuis VS Code (serveur MCP `robotmcp`, déclaré dans le
projet) : elle navigue écran par écran, inspecte le DOM, choisit des
localisateurs robustes, les **valide en direct** avant de les écrire, prouve
la rejouabilité par deux exécutions réelles vertes, puis compare les captures
de l'exécution aux images de la vidéo (**fidélité visuelle**) : le verdict
par scénario est consigné dans la spec et un **rapport HTML** comparant
chaque image vidéo à la capture d'exécution est généré dans
`results/fidelity/<nom>/report.html` : autonome (images embarquées), il
s'ouvre dans n'importe quel navigateur et se partage tel quel :

```text
/finalize-rf test-video-to-rf
```

Le SUT doit être accessible depuis le poste. Selon l'assistant : avec
Claude Code, le serveur `robotmcp` (déclaré dans `.mcp.json`) se charge au
démarrage de session : recharger la fenêtre après une première
installation ; avec Copilot, le démarrer dans la vue MCP de VS Code
(déclaré dans `.vscode/mcp.json`). Un relevé manuel (inspecteur du
navigateur, recorder…) reste bien sûr possible.

Avant / après :

```robotframework
*** Variables ***
${LOGIN_USER_FIELD}    ${EMPTY}    # TODO
```

```robotframework
*** Variables ***
${LOGIN_USER_FIELD}    id=username
```

Le corps du keyword, lui, est déjà écrit ; la ligne
`Require Locator    ${LOGIN_USER_FIELD}    specs/….md` cesse d'échouer dès
que la variable est renseignée. Seuls les keywords dont l'action était trop
incertaine dans la vidéo gardent un corps `Fail Missing Locator` à
implémenter à la main (ils sont signalés dans la spec).

## 6. Exécuter les tests

Toujours avec le préfixe d'encodage (bug console connu sur ce poste, voir la
FAQ) :

```powershell
# vérification à blanc (structure, imports, keywords résolus)
$env:PYTHONIOENCODING='utf-8'; robot --dryrun --outputdir results/dry tests/robot/ui/web/demo-connexion.robot

# exécution réelle
$env:PYTHONIOENCODING='utf-8'; robot --outputdir results/demo-connexion tests/robot/ui/web/demo-connexion.robot
```

Rapports dans `results/<nom>/report.html` et `log.html`. Le mot de passe ne
se met jamais dans un fichier : `-v "APP_PASSWORD: Secret:…"` en ligne de
commande.

## 7. Qualité continue et golden set

Trois garde-fous tournent en continu (localement et dans la CI GitHub
Actions à chaque push) :

- `python scripts/check_specs.py` : vérifie que chaque suite référence sa
  spec avec la bonne empreinte sha256 (une spec modifiée sans régénération
  est détectée) et que les conventions structurantes sont respectées ;
- `python -m robocop check tests resources` : lint Robot Framework (préfixer
  par `$env:PYTHONIOENCODING='utf-8';` hors des terminaux du projet) ;
- `robot --dryrun` sur toutes les suites.

**Capitalisation** : les écrans déjà couverts se réutilisent,
`python scripts/inventory_pages.py` liste les keywords existants et l'état
de leurs localisateurs (« prêt » = déjà relevés sur le SUT). Plus vous
traitez de vidéos sur la même application, moins chaque nouvelle vidéo
coûte.

**Golden set (recommandé)** : conservez hors git 3 ou 4 vidéos de référence
couvrant vos cas types (web simple, formulaire, multi-écrans, sans voix
off). Après toute évolution du pipeline, repassez-les dans `/video-to-rf`
et comparez les specs produites aux précédentes : c'est le test de
non-régression du pipeline lui-même. La section « Fidélité visuelle » des
specs (renseignée par `/finalize-rf`) sert de métrique : scénarios conformes
/ total.

## 8. FAQ / dépannage

**`robot --version` plante avec `LookupError: unknown encoding`.**
La variable d'environnement `PYTHONIOENCODING=utf-8:surrogateescape` du poste
perturbe la console de Robot Framework. Préfixer chaque commande robot par
`$env:PYTHONIOENCODING='utf-8';` (les commandes de ce guide le font déjà).

**La transcription de la voix off est approximative.**
Forcer `--language fr`, puis monter en modèle : `--model medium` (plus lent,
nettement plus précis). Refaire uniquement l'audio : ajouter `--force`.

**Trop d'images extraites (animations, vidéos dans la page).**
Monter le seuil : `--scene 0.2` voire `0.3`. Au-delà de 120 images, le script
échantillonne de lui-même et l'annonce.

**Presque aucune image extraite (application très statique).**
Le script bascule seul sur une image toutes les 5 s. Pour resserrer :
`--interval 3`.

**La vidéo n'a pas de son.**
Aucun problème : le plan est construit sur les seules images. La voix off
améliore le découpage en scénarios, elle n'est pas obligatoire.

**Le flux métier a changé depuis la vidéo.**
Refaire une capture (ou corriger la spec), puis demander la régénération de
la suite : la spec est la source de vérité, la suite référence son empreinte
(sha256) pour détecter les décalages.

**Un test passe en dry-run mais échoue en réel avec « Localisateurs à
relever… ».**
C'est le comportement attendu tant que l'étape 5 (relevé des localisateurs)
n'est pas faite pour ce keyword.

---

*Structure et conventions héritées du projet SAPFX
(`E:\QA_GenAI\SAP_library_custom`) : specs = source de vérité, tests sans
localisateurs, page objects, assertions indépendantes de la locale.*
