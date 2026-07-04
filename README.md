# terminus-data

Données de la **ligne 32 TER (Bourg-en-Bresse ⇄ Lyon)** consommées par l'application
[TERMinus](https://github.com/exec-d/terminus) :

- **`line32.json`** — référentiel (gares, trips, calendrier de service), extrait du GTFS
  national SNCF et **mis à jour automatiquement chaque semaine** par la CI du repo app.
- **`stats/line32.json`** — statistiques de ponctualité par train (% à l'heure, retard médian,
  % suppression) sur fenêtre glissante de 60 jours, recalculées **3 fois par jour** par le
  workflow `collect-stats.yml` de ce dépôt (`tools/collect.py` échantillonne le flux GTFS-RT).
- **`history/AAAA-MM-JJ.json`** — observations brutes par journée de service (retard final,
  retard max, arrêts sautés, suppression), auditables dans l'historique git.

L'app télécharge ces fichiers à la volée (mise à jour OTA, sans nouvelle release APK).

## Données & licence

Données : **SNCF** via [transport.data.gouv.fr](https://transport.data.gouv.fr) — licence
**ODbL** (Open Database License). Ce dépôt redistribue un extrait de ces données avec attribution,
conformément à la licence. Application non officielle, non affiliée à la SNCF.
