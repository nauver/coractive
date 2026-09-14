# Mur interactif — Comité européen des régions

Mur interactif trilingue (**EN / FR / DE**) pour la gamification du CoR : on joue avec son corps
devant une webcam, sans manette. Pensé pour être projeté sur un mur lors d'événements.

Détection de pose 100 % dans le navigateur via **TensorFlow.js MoveNet** (jusqu'à 6 personnes
suivies simultanément). Aucune donnée n'est envoyée : tout tourne côté client.

## Modes

- 🧠 **Quiz corporel** — on répond en gardant une main dans la zone de gauche ou de droite
  (questions sur l'UE, le CoR, le drapeau…).
- ⭐ **Attrape les étoiles** — des étoiles tombent, on les attrape avec les mains (score sur 45 s).
- ✨ **Miroir de particules** — le corps génère des traînées de particules aux couleurs de l'Europe.

## Fonctionnement

- Sélecteur de **langue** (EN/FR/DE) sur l'écran d'accueil — interface et questions traduites, choix mémorisé.
- Sélecteur de **caméra** (choix mémorisé).
- **Plein écran** : bouton ou touche `F`. **Retour menu** : bouton ou touche `Échap`.

## Structure

```
.
├── index.html                 # l'application (fichier unique, autonome)
├── README.md
├── .gitignore
└── .github/workflows/deploy.yml   # déploiement automatique GitHub Pages
```

Les bibliothèques (TensorFlow.js, pose-detection) sont chargées via CDN : aucun build,
aucune dépendance à installer.

## Lancer en local

Ouvrir `index.html` dans **Chrome** et autoriser l'accès à la caméra.
> Sur `file://`, l'accès caméra peut être capricieux selon la machine. En cas de souci,
> servir le dossier en local :
> ```bash
> python -m http.server 8000
> # puis ouvrir http://localhost:8000
> ```

## Déployer sur GitHub Pages

### Option A — automatique (recommandé, workflow inclus)
1. Créer un dépôt GitHub et y pousser ce dossier :
   ```bash
   git init
   git add .
   git commit -m "Initial commit — mur interactif CoR"
   git branch -M main
   git remote add origin https://github.com/<utilisateur>/<depot>.git
   git push -u origin main
   ```
2. Sur GitHub : **Settings → Pages → Build and deployment → Source : GitHub Actions**.
3. À chaque `push` sur `main`, le site est publié. L'URL s'affiche dans l'onglet **Actions**
   et sous **Settings → Pages** (`https://<utilisateur>.github.io/<depot>/`).

### Option B — sans workflow
**Settings → Pages → Source : Deploy from a branch → `main` / `/root`**.
(Dans ce cas, le fichier `.github/workflows/deploy.yml` est inutile ; on peut le supprimer.)

## Déployer sur Netlify

Glisser-déposer le dossier sur https://app.netlify.com, ou connecter le dépôt GitHub.
Aucune commande de build ; répertoire de publication : la racine (`.`).

## Note caméra

L'accès à la webcam nécessite un **contexte sécurisé** : `https://` (GitHub Pages et Netlify
le fournissent) ou `localhost`. Une caméra affichée en noir vient généralement d'une
caméra virtuelle (VPN, OBS, outil de sécurité) qui tient le matériel — la sélectionner ne
suffit pas, il faut libérer/désactiver cet outil.

## Personnalisation rapide

- **Questions du quiz** : objet `QUIZ` dans `index.html` (une liste par langue).
- **Traductions d'interface** : objet `I18N`.
- **Couleurs** : variables CSS `--eu-blue`, `--eu-gold`… en haut du fichier.

## Technologies

TensorFlow.js · @tensorflow-models/pose-detection (MoveNet MultiPose Lightning) · Canvas 2D · HTML/CSS/JS vanilla.
