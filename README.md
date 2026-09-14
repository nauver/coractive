# Mur interactif — Comité européen des régions (Europe Day)

Mur interactif trilingue (**EN / FR / DE**) pour la gamification du CoR : on joue avec son
corps devant une webcam, sans manette. Conçu pour être projeté sur un mur lors d'événements
grand public (Europe Day, EuroPCom…).

Détection de pose 100 % dans le navigateur via **TensorFlow.js MoveNet** (jusqu'à 6 personnes
suivies simultanément). **Aucune image n'est envoyée** : tout tourne côté client.

## Modes

- 🧠 **Quiz corporel** — 5 questions par manche (UE, CoR, EuroPCom…), réponse en gardant une
  main dans la bonne zone. Réponses mélangées à chaque partie.
- ⭐ **Attrape les étoiles** — attraper les étoiles qui tombent, 45 s.
- ⚔️ **Duel (2 joueurs)** — Équipe A (gauche) vs Équipe B (droite), qui en attrape le plus.
- ✨ **Miroir de particules** — le corps génère des traînées aux couleurs de l'Europe.
- 📸 **Photo souvenir** — compte à rebours, cadre CoR/EuroPCom, enregistrement en PNG (offline).

## Fonctionnalités événementielles

- 🏆 **Leaderboard local** : Top 10 du jour + meilleur score de l'événement (Quiz et Attrape).
  Saisie des **initiales par gestes** (façon borne d'arcade) quand on entre dans le classement.
- 🎯 **Record à battre** affiché pendant les parties Quiz/Attrape.
- 📊 **Statistiques anonymes** : parties jouées, mode le plus joué, score moyen, pic de
  personnes simultanées, photos prises. Accès par la touche **`S`**, export **CSV**, remise à zéro.
- Sélecteur de **langue** et de **caméra** (choix mémorisés), **plein écran** (`F`), **menu** (`Échap`).

Toutes les données (scores, stats) sont stockées **uniquement dans le navigateur du poste**
(localStorage) — rien n'est envoyé à l'extérieur.

## Structure

```
.
├── index.html                     # l'application (fichier unique, autonome)
├── README.md
├── NOTICE.md                      # licences & RGPD
├── .gitignore
└── .github/workflows/deploy.yml   # déploiement automatique GitHub Pages
```

Bibliothèques chargées via CDN : aucun build, aucune dépendance à installer.

## Lancer en local

Ouvrir `index.html` dans **Chrome** et autoriser la caméra. Sur `file://` l'accès caméra peut
être capricieux ; sinon servir le dossier :
```bash
python -m http.server 8000    # puis http://localhost:8000
```

## Déployer sur GitHub Pages

1. Pousser ce dossier sur un dépôt GitHub :
   ```bash
   git init && git add . && git commit -m "Mur interactif CoR — Europe Day"
   git branch -M main
   git remote add origin https://github.com/<utilisateur>/<depot>.git
   git push -u origin main
   ```
2. **Settings → Pages → Source : GitHub Actions**. À chaque push, le site est publié en HTTPS
   (`https://<utilisateur>.github.io/<depot>/`). L'HTTPS fiabilise l'accès caméra.

(Option sans workflow : **Settings → Pages → Deploy from a branch → `main` / root** ; on peut
alors supprimer `.github/workflows/deploy.yml`.)

## Déployer sur Netlify

Glisser-déposer le dossier sur https://app.netlify.com, ou connecter le dépôt. Pas de build ;
répertoire de publication : la racine.

## Personnalisation

- **Questions du quiz** : objet `QUIZ` dans `index.html` (une liste par langue ; `correct` =
  index de la bonne réponse dans `[a, b]`). Le nombre de questions par manche = `QUIZ_ROUND`.
- ⚠️ **Question « présidence du Conseil »** : datée. Actuellement **Irlande** (2ᵉ semestre 2026) —
  à mettre à jour chaque semestre (chercher `id:"presidency"`).
- **Slogan EuroPCom** : la question actuelle décrit EuroPCom comme « la plus grande conférence
  européenne de communication publique ». Adapter dans `QUIZ` si besoin.
- **Traductions d'interface** : objet `I18N`. **Couleurs** : variables CSS en haut du fichier.

## Note caméra

L'accès webcam exige un **contexte sécurisé** (`https://` ou `localhost`). Une caméra affichée
en noir vient en général d'une caméra virtuelle (VPN, OBS, outil de sécurité) qui tient le
matériel — il faut la libérer/désactiver.

## Technologies

TensorFlow.js · pose-detection (MoveNet MultiPose Lightning) · Canvas 2D · HTML/CSS/JS vanilla.
Licences : voir `NOTICE.md`.
