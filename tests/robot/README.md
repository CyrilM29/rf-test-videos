# tests/robot/ — suites générées depuis les specs

- `ui/<domaine>/<slug>.robot` : une suite par vidéo transcrite ;
  domaine ∈ `web` | `fiori` | `ecc` | `desktop` | `mobile`.
- L'en-tête de chaque suite référence sa spec et son empreinte
  (`Spec: specs/<slug>.md (sha256:…, date)`) : quand le flux change, on met à
  jour la spec et on **régénère** — on n'édite pas les localisateurs à la
  main ici (ils n'y sont d'ailleurs pas : convention 1).

Exécution (le préfixe `PYTHONIOENCODING` contourne un bug console de robot
sur ce poste — voir CLAUDE.md « Pièges connus ») :

```powershell
$env:PYTHONIOENCODING='utf-8'; robot --dryrun --outputdir results/dry_x tests/robot/ui/web/x.robot
$env:PYTHONIOENCODING='utf-8'; robot --outputdir results/x tests/robot/ui/web/x.robot
```

Le `--dryrun` est la porte de sortie obligatoire de toute génération ;
l'exécution réelle reste rouge tant que les locators TODO des page objects
n'ont pas été relevés sur le SUT (convention 5) — c'est voulu.
