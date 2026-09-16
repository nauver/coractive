# LumoCoR

Mur & sol interactifs façon **Lumo Play** pour le Comité européen des régions (CoR).
33 jeux (particules, physique, nature, lumière, cibles, dalles, collecte, éducatif,
photobooth, fêtes, 2 joueurs) pilotés par **détection de mouvement webcam** ou par la
**caméra 3D Orbbec Astra Pro**. Une seule page, aucune dépendance externe (hors Google
Fonts), 100 % dans le navigateur — rien n'est envoyé sur un serveur.

Application autonome : `index.html` à la racine. C'est tout ce qu'il faut pour le web.

---

## Déployer sur GitHub Pages

### Méthode A — GitHub Actions (incluse, recommandée)

1. Crée un dépôt GitHub (ex. `lumocor`) et pousse ce dossier :
   ```bash
   git init
   git add .
   git commit -m "LumoCoR"
   git branch -M main
   git remote add origin https://github.com/<ton-compte>/lumocor.git
   git push -u origin main
   ```
2. Sur GitHub : **Settings → Pages → Build and deployment → Source : GitHub Actions**.
3. Le workflow `.github/workflows/deploy-pages.yml` se lance à chaque `push` sur `main`
   et publie le site. L'URL apparaît dans l'onglet **Actions** puis dans **Settings → Pages**
   (`https://<ton-compte>.github.io/lumocor/`).

### Méthode B — sans Actions (déploiement depuis une branche)

**Settings → Pages → Source : Deploy from a branch → `main` / `/ (root)`**.
GitHub sert alors `index.html` directement. Le fichier `.nojekyll` évite tout traitement Jekyll.

> L'app fonctionne à n'importe quelle sous-URL (site de projet `.../lumocor/`) :
> tous les chemins sont relatifs/inline.

---

## Utilisation

- Ouvre la page, clique **Caméra & calibrage**, puis **Activer la webcam**.
  La webcam sert de capteur de mouvement (aucune image n'est enregistrée ni transmise).
- Sans webcam, le mode **Souris/doigt** permet de tout tester.
- Règle **sensibilité**, **miroir** et **retournement** selon le placement caméra/projecteur.
- Trilingue **FR / EN / DE**.

> La webcam exige un contexte sécurisé : **HTTPS** (GitHub Pages l'est) ou **localhost**.

---

## Caméra 3D Orbbec Astra Pro (profondeur)

Le navigateur **ne peut pas** lire la profondeur Orbbec directement (via getUserMedia il
ne voit que la caméra couleur UVC). Le dossier `bridge/` contient un **pont local** qui lit
la profondeur (OpenNI2), en déduit une grille d'occupation et la diffuse en **WebSocket**.
L'app s'y connecte via *Caméra & calibrage → source « Orbbec 3D »*.

```bash
cd bridge
pip install -r requirements.txt      # numpy, websockets, + binding OpenNI2
python orbbec_depth_bridge.py --openni-redist "C:/Program Files/OpenNI2/Redist"
# test sans caméra :
python orbbec_depth_bridge.py --sim
```

**Contrainte importante — contenu mixte.** Une page servie en **HTTPS** (github.io) qui se
connecte à `ws://localhost:8765` (non chiffré) est bloquée par certains navigateurs.
Pour la profondeur, deux options fiables :

- **Servir la page en local** à côté du pont :
  ```bash
  python -m http.server 8080   # puis http://localhost:8080
  ```
  (localhost est un contexte sécurisé, le WebSocket local passe.)
- Ou exposer le pont en **wss://** (reverse-proxy TLS) si tu tiens à l'héberger sur Pages.

> Le mode **webcam frame-diff** marche parfaitement sur GitHub Pages ; seule la profondeur
> Orbbec demande un hébergement local (ou wss).

---

## Structure

```
index.html                         L'application (tout-en-un)
.nojekyll                          Désactive Jekyll sur GitHub Pages
netlify.toml                       Déploiement Netlify (bonus)
.github/workflows/deploy-pages.yml Déploiement GitHub Pages automatique
bridge/
  orbbec_depth_bridge.py           Pont profondeur Orbbec -> WebSocket
  requirements.txt
```

## Confidentialité (RGPD)

Au premier usage de la caméra, une **fenêtre de consentement** s'affiche et **bloque
l'activation** tant qu'elle n'est pas acceptée. Elle précise que la caméra sert
uniquement à détecter les mouvements, que les images sont traitées **localement dans le
navigateur**, que **rien n'est enregistré, transmis ni conservé**, et qu'il n'y a **aucune
reconnaissance faciale ni donnée biométrique**. L'utilisateur peut refuser et jouer à la
souris / au doigt. Le consentement est mémorisé localement (localStorage) ; le lien
« Confidentialité & crédits » en bas de page permet de rouvrir la note à tout moment.

## Crédits & mentions

- Contours des pays : **Natural Earth** (domaine public), via `world-atlas`.
- Drapeaux : **flag-icons** (licence MIT ; visuels du domaine public).
- Polices : **Bricolage Grotesque** & **Manrope** (Google Fonts, licence SIL OFL).
- Détection de mouvement : 100 % navigateur, sans dépendance externe.
- © 2026 LumoCoR — projet pour le Comité européen des régions.

## Licence

Code applicatif : à toi de choisir (MIT conseillé). Aucune dépendance JS externe embarquée
(hors Google Fonts). Le pont utilise numpy / websockets / OpenNI2 selon leurs licences.
