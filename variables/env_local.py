"""Données d'environnement du poste local.

Ce que ce fichier porte : les adresses et identifiants techniques d'un
environnement — pas des localisateurs (ils vivent dans
``resources/page_objects/``) ni des données métier (elles vivent dans la
suite ou dans ``resources/``).

Format Python et non YAML, volontairement : un fichier de variables ``.py``
n'ajoute aucune dépendance au projet.

Aucun secret ici — un mot de passe ne se met JAMAIS dans un fichier de
variables : il se passe en ligne de commande, typé Secret
(``-v "APP_PASSWORD: Secret:…"``), pour rester masqué jusqu'au niveau TRACE.

Surcharge possible sans toucher au fichier ::

    robot -v SUT_BASE_URL:http://autre-hote:8080 …
"""

# URL de base du système sous test — observée dans la barre d'adresse de
# videos/test-video-to-rf.mp4 (specs/test-video-to-rf.md) : démo publique
# OrangeHRM OS 5.9.
SUT_BASE_URL = "https://opensource-demo.orangehrmlive.com"

# Navigateur piloté par la librairie Browser (choix poste, surchargeables en
# CLI : -v SUT_HEADLESS:True pour un run CI).
SUT_BROWSER = "chromium"
SUT_HEADLESS = False
