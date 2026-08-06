# Parcours de consultation OrangeHRM : connexion, référentiels et filtrage des candidats

- **Canal** : web
- **Pilotage** : Browser (Playwright), canal unique, librairie branchée dans
  `resources/common.resource` (checkpoint du 2026-07-25, pas d'hybridation
  nécessaire)
- **Système / URL** : OrangeHRM OS 5.9 (démo publique),
  `https://opensource-demo.orangehrmlive.com/web/index.php/auth/login`
- **Source vidéo** : `videos/test-video-to-rf.mp4` (durée 01:10, voix off : aucune,
  0 segment détecté ; analyse frames uniquement, 14 frames à 1/5 s)
- **Préconditions** : compte de démo `Admin` actif (identifiants affichés sur la
  page de connexion elle-même) ; jeu de données de la démo publique OrangeHRM
  (réinitialisé périodiquement par l'éditeur : toutes les volumétries ci-dessous
  sont donc volatiles).

## Données observées

- **Connexion** : la page de login affiche en clair les identifiants de démo
  « Username : Admin / Password : admin123 ». Après connexion, l'utilisateur
  affiché en haut à droite est « manda user ».
- **Dashboard** (`/dashboard/index`) : widgets « Time at Work » (Punched Out,
  16h55m Today), « My Actions » ((1) Candidate to Interview), « Quick Launch »,
  « Buzz Latest Posts », « Employees on Leave Today » (vide), « Employee
  Distribution by Sub Unit » (camembert, 94,2 % sur le segment majoritaire).
- **Admin > User Management > System Users** (`/admin/viewSystemUsers`) :
  « (4) Records Found », lignes : `Admin` (rôle Admin, employé « manda user »,
  Enabled), `FMLName`, `FMLName1`, `Jobinsam@6742` (rôle ESS, Enabled).
- **PIM > Employee List** (`/pim/viewEmployeeList`) : « (104) Records Found ».
- **Leave > Leave List** (`/leave/viewLeaveList`) : période par défaut affichée
  « 2026-01-01 » → « 2026-31-12 » (affichage année-jour-mois, voir vigilance),
  statut par défaut « Pending Approval » (chip), résultat : « No Records Found ».
- **Recruitment > Candidates** (`/recruitment/viewCandidates`) :
  « (60) Records Found » sans filtre. Filtres appliqués successivement :
  Job Title = `Account Assistant`, Vacancy = `Junior Account Assistant`,
  Hiring Manager = `Rahul Patil`, Status = `Rejected` → après Search :
  « No Records Found » (toast « Info: No Records Found »).
- **Recruitment > Add Candidate** (`/recruitment/addCandidate`) : formulaire
  avec Full Name\* (First/Middle/Last), Vacancy (liste), Email\*, Contact Number,
  Resume (Browse : .docx .doc .odt .pdf .rtf .txt ≤ 1 Mo), Keywords, Date of
  Application préremplie « 2026-25-07 », Notes, case « Consent to keep data »,
  boutons Cancel / Save. Aucune saisie observée dans le formulaire.
- Retour final sur la liste des candidats, filtres revenus à vide,
  « (60) Records Found ».

## Scénarios

### 1. Connexion au portail OrangeHRM
- **Horodatage vidéo** : [00:00 → 00:15]
- **Étapes** :
  1. Ouvrir la page de connexion du SUT.
  2. Saisir l'identifiant et le mot de passe de l'utilisateur de test et valider.
  3. Constater l'arrivée sur le tableau de bord.
- **Résultat attendu** : le tableau de bord est affiché (module « Dashboard »
  actif) et la session est ouverte (menu utilisateur présent) : aucune
  assertion sur un libellé localisé ni sur les valeurs des widgets (volatiles).
- **Keywords métier manquants** : `Open Login Page`, `Log In With`,
  `Dashboard Should Be Displayed`, `Ensure Logged In` (remise en état pour les
  scénarios suivants).

### 2. Consultation des utilisateurs système
- **Horodatage vidéo** : [00:15 → 00:28]
- **Étapes** :
  1. Depuis le menu latéral, ouvrir le module Admin (User Management > System Users).
  2. Constater la liste des utilisateurs système.
- **Résultat attendu** : la page System Users est affichée ; le compteur
  d'enregistrements annoncé est strictement positif et égal au nombre de lignes
  de la grille (assertion relationnelle mesurée dans le même run : la valeur
  « 4 » vue en vidéo n'est pas rejouée en dur).
- **Keywords métier manquants** : `Go To Module`,
  `System Users Page Should Be Displayed`, `Get Announced System Users Count`,
  `Get Displayed System Users Row Count`.

### 3. Consultation de la liste des employés (PIM)
- **Horodatage vidéo** : [00:28 → 00:33]
- **Étapes** :
  1. Depuis le menu latéral, ouvrir le module PIM (Employee List).
  2. Constater la liste des employés.
- **Résultat attendu** : la page Employee List est affichée ; le compteur
  d'employés annoncé est strictement positif et supérieur ou égal au nombre de
  lignes affichées sur la première page (la grille est paginée : 104 annoncés
  en vidéo pour une page partielle).
- **Keywords métier manquants** : `Employee List Page Should Be Displayed`,
  `Get Announced Employee Count`, `Get Displayed Employee Row Count`.

### 4. Recherche des congés en attente d'approbation
- **Horodatage vidéo** : [00:33 → 00:38]
- **Étapes** :
  1. Depuis le menu latéral, ouvrir le module Leave (Leave List).
  2. Conserver la période proposée par défaut et le statut « Pending Approval ».
  3. Lancer la recherche.
- **Résultat attendu** : la zone de résultats est affichée dans un des deux
  états valides : grille de congés ou état vide explicite (« aucun
  enregistrement ») ; en vidéo le résultat était vide. Pas d'assertion sur un
  nombre exact ni sur un libellé de message localisé.
- **Keywords métier manquants** : `Leave List Page Should Be Displayed`,
  `Search Leaves With Status`, `Leave Search Result Should Be Displayed`.

### 5. Filtrage des candidats au recrutement
- **Horodatage vidéo** : [00:38 → 00:58]
- **Étapes** :
  1. Depuis le menu latéral, ouvrir le module Recruitment (Candidates).
  2. Relever le nombre total de candidats sans filtre.
  3. Filtrer par poste, offre, responsable du recrutement et statut
     (valeurs observées : Account Assistant / Junior Account Assistant /
     Rahul Patil / Rejected) puis lancer la recherche.
  4. Relever le nombre de candidats après filtrage.
- **Résultat attendu** : nombre filtré ≤ nombre total (mesurés dans le même
  run). En vidéo : 60 sans filtre, 0 après filtrage, ces constantes ne sont
  pas rejouées en dur, le jeu de données de la démo change.
- **Keywords métier manquants** : `Candidates Page Should Be Displayed`,
  `Get Announced Candidate Count`, `Filter Candidates`,
  `Reset Candidate Filters`.

### 6. Ouverture puis abandon du formulaire d'ajout de candidat
- **Horodatage vidéo** : [00:58 → 01:10]
- **Étapes** :
  1. Depuis la liste des candidats, ouvrir le formulaire d'ajout (+ Add).
  2. Constater l'affichage du formulaire, sans rien saisir.
  3. Abandonner la création et revenir à la liste des candidats.
- **Résultat attendu** : le formulaire Add Candidate est affiché (champs
  obligatoires Full Name et Email présents), puis la liste des candidats est de
  nouveau affichée avec un compteur inchangé par rapport au relevé du
  scénario 5 (aucune création n'a eu lieu).
- **Keywords métier manquants** : `Open Add Candidate Form`,
  `Add Candidate Form Should Be Displayed`, `Cancel Candidate Creation`.

## Points de vigilance

- **Aucune voix off** : l'intention est entièrement déduite des frames ; les
  transitions entre 2 frames espacées de 5 s peuvent masquer des micro-actions.
- **Volumétries volatiles** : la démo publique OrangeHRM est réinitialisée
  régulièrement ; 4 utilisateurs, 104 employés, 60 candidats sont des valeurs
  du jour de l'enregistrement : assertions relationnelles uniquement.
- **Locale** : interface en anglais ; le navigateur (Chrome) est en français.
  Les valeurs de filtre (« Account Assistant », « Rejected »…) sont des données
  de sélection, pas des assertions sur libellés.
- **Affichage des dates ambigu** : « 2026-31-12 » (Leave) et « 2026-25-07 »
  (Add Candidate) suggèrent un format d'affichage année-jour-mois de la démo :
  ne jamais parser ces libellés dans les tests.
- **Listes déroulantes OrangeHRM** : ce sont des composants custom (div), pas
  des `<select>` natifs : les locators TODO des filtres comprennent un
  gabarit d'option paramétrable (`{value}` / `{status}` / `{module}`) à
  relever sur le SUT.
- **Rafraîchissement après Search** : la vidéo ne montre pas d'indicateur de
  chargement exploitable ; le keyword `Filter Candidates` s'appuie sur
  l'auto-attente de Browser lors de la lecture du compteur : à confirmer sur
  le SUT (risque de lecture d'un compteur périmé).
- **Hors SUT** : à [00:10] une popup Chrome « Modifiez votre mot de passe »
  (mot de passe compromis) est fermée via OK ; à [00:00] une liste
  d'autocomplétion du navigateur est visible sur le champ Username. Ces deux
  éléments appartiennent au navigateur, pas au SUT : exclus des scénarios.
- **Identifiants** : `Admin` / `admin123` sont publics (affichés par la démo),
  mais par convention le mot de passe n'est pas committé : il se passe en CLI
  (`-v APP_PASSWORD:admin123`).

## Écarts constatés à la génération

- [01:05] La souris survole l'icône de suppression d'une ligne candidat
  (« Senior QA Lead / John Doe ») en toute fin de vidéo, sans que la frame
  suivante n'existe pour confirmer un clic ou une boîte de confirmation :
  aucune suppression n'est retranscrite (jamais inventé : convention spec).
- Le retour à la liste après le formulaire Add Candidate (scénario 6) montre
  les filtres réinitialisés ; le moyen exact (bouton Cancel ou navigation) se
  produit entre deux frames : retranscrit comme un abandon via Cancel.
  **Levé au relevé du 2026-07-25** : le bouton Cancel existe et ramène bien à
  la liste des candidats (validé en live via robotmcp).

## Constats du relevé sur le SUT (/finalize-rf, 2026-07-25)

- Volumétries du jour : 7 utilisateurs système (vidéo : 4), 108 employés
  (vidéo : 104), 65 candidats (vidéo : 60), la volatilité anticipée est
  confirmée, les assertions relationnelles restent valides telles quelles.
- La période par défaut de Leave List affichait « To Date 2026-24-08 » (vidéo :
  « 2026-31-12 ») : la période par défaut varie elle aussi, le keyword
  conserve la période proposée sans la fixer, comme prévu.
- Les 26 locators ont été validés en live (unicité + action réelle) avant
  écriture ; les gabarits `{module}` / `{status}` / `{value}` avec deux
  valeurs chacun. Composants OXD sans ids : ancrages sur attributs `name`,
  classes structurelles et labels des filtres.
- Écart d'exécution corrigé (run réel n°1) : `Ensure Logged In` supposait
  qu'un navigateur au catalogue avait une page active ; or Browser ferme les
  pages en fin de test (auto-close TEST) en laissant le navigateur ouvert.
  Corps réécrit avec TRY/EXCEPT sur `Get Url` (login.resource).

## Fidélité visuelle

Contrôle du 2026-07-27 (session live robotmcp : rejeu des 6 scénarios via les
keywords des page objects, capture de l'écran de fin de chaque scénario :
`results/fidelity/` : comparée à la frame vidéo de l'horodatage
correspondant). Runs réels du jour : verts 2× (`results/test-video-to-rf_live`,
`_live2`).

| Scénario | Frame vidéo | Capture | Verdict |
| --- | --- | --- | --- |
| 1. Connexion → tableau de bord | 00:15 | s1_dashboard | **conforme**, mêmes widgets (Time at Work, My Actions, Quick Launch, Buzz) ; réagencement 2 vs 3 colonnes dû à la largeur de fenêtre, utilisateur de démo différent (données) |
| 2. Utilisateurs système | 00:25 | s2_admin_users | **conforme**, mêmes filtres/actions ; « (6) Records Found » vs « (4) » (données) |
| 3. Liste des employés | 00:30 | s3_pim_employees | **conforme**, mêmes filtres/colonnes ; 109 vs 104 enregistrements (données) |
| 4. Congés « Pending Approval » | 00:35 | s4_leave_search | **conforme**, même état : chip « Pending Approval », période par défaut, « No Records Found » |
| 5. Candidats filtrés | 00:55 | s5_candidates_filtered | **conforme**, mêmes 4 filtres appliqués, même état « No Records Found » |
| 6. Formulaire Add Candidate | 01:00 | s6_add_candidate_form | **conforme**, mêmes champs (Full Name, Vacancy, Email*, Resume…) ; date du jour différente (donnée) |

**Bilan : 6/6 conformes**, aucun écart de structure ni de flux entre la
vidéo (enregistrée le 2026-07-25) et le SUT du 2026-07-27.
