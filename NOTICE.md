# Licences & attributions

## Ce projet
Le code de cette application (`index.html`) est original et libre d'utilisation, y compris
pour un usage public et institutionnel (événements du CoR, etc.).

## Dépendances tierces (chargées via CDN)
Toutes sous licence **Apache License 2.0** — usage libre, y compris commercial et public :

- **TensorFlow.js** — © Google LLC — Apache-2.0 — https://github.com/tensorflow/tfjs
- **@tensorflow-models/pose-detection** — © Google LLC — Apache-2.0 — https://github.com/tensorflow/tfjs-models
- **MoveNet** (modèle de détection de pose) — © Google LLC — Apache-2.0

La licence Apache 2.0 autorise l'usage, la modification et la redistribution ; en cas de
redistribution du code source, conserver les mentions de licence.

## Éléments visuels
- Aucune police externe n'est embarquée (polices système du poste).
- Les émojis sont rendus par la police système (aucune image redistribuée).
- Les étoiles et couleurs sont dessinées par le code. L'**emblème officiel européen**
  (cercle de 12 étoiles) et le **logo du CoR** ne sont PAS inclus : pour les afficher,
  suivre les règles d'usage officielles de l'UE / du CoR.

## Protection des données (RGPD)
L'application ne transmet aucune image : toute la détection s'effectue localement dans le
navigateur. Les scores et statistiques (anonymes, initiales à 3 lettres) sont stockés
uniquement dans le navigateur du poste (localStorage). Pour un usage grand public, prévoir
une **affichette** indiquant l'usage d'une caméra en temps réel sans enregistrement.
