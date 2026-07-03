# terminus-data

Référentiel de la **ligne 32 TER (Bourg-en-Bresse ⇄ Lyon)** consommé par l'application
[TERMinus](https://github.com/exec-d/terminus) : `line32.json` (gares, trips, calendrier de service),
extrait du GTFS national SNCF et **mis à jour automatiquement chaque semaine** par un workflow CI.

L'app le télécharge à la volée (mise à jour OTA des horaires, sans nouvelle release APK).

## Données & licence

Données : **SNCF** via [transport.data.gouv.fr](https://transport.data.gouv.fr) — licence
**ODbL** (Open Database License). Ce dépôt redistribue un extrait de ces données avec attribution,
conformément à la licence. Application non officielle, non affiliée à la SNCF.
