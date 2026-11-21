# Détection et localisation de falsifications d'images

Application locale (Streamlit) qui analyse une image avec un modèle de Deep Learning et
affiche les zones suspectes : heatmap, masque binaire et superposition sur l'image.
Projet universitaire (module G9).

Deux modèles sont intégrés, chacun avec son propre prétraitement et sa propre inférence,
adaptés vers un format de résultat commun :

| Modèle | Rôle | Résolution traitée | Score global |
|---|---|---|---|
| **FMAE** | détection et localisation | redimensionnée en 512 × 512 | non fourni par le checkpoint utilisé |
| **TruFor** | détection et localisation | taille d'origine (limitée à 2 Mpx) | oui |

## Fonctionnement

1. Importer une image JPG, JPEG ou PNG.
2. Choisir le modèle.
3. Cliquer sur « Analyser ».
4. Consulter l'image originale, la heatmap, le masque binaire, la superposition et les informations
   (modèle, temps d'inférence, surface suspecte, seuil, score si disponible).
5. Télécharger la heatmap, le masque et la superposition au format PNG.

Le curseur de seuil recalcule le masque sans relancer le modèle. Les images ne sont pas
enregistrées sur le disque : elles restent en mémoire pendant la session.

## Installation (testée sous Windows, Python 3.10)

```powershell
git clone https://github.com/FatiAllali123/ImageForgeryLocalization.git
cd ImageForgeryLocalization
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**PyTorch avec GPU NVIDIA (CUDA 12.6)** :

```powershell
pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu126
```

Sans GPU NVIDIA, installez la version CPU de PyTorch en suivant https://pytorch.org
(cette variante n'a pas été testée sous cette forme exacte par ce projet).

**Autres dépendances** :

```powershell
pip install -r requirements/fmae.txt
pip install -r requirements/trufor.txt
```

Les deux fichiers utilisent la même version de `timm` (1.0.11), ce qui permet aux deux modèles
de partager un seul environnement.

### Code officiel des modèles (non inclus dans ce dépôt)

Le code officiel n'est ni copié ni modifié : il est cloné dans `third_party/`, dossier ignoré par Git.

```powershell
git clone https://github.com/JulietChoo/FMAE.git third_party/FMAE
git clone https://github.com/grip-unina/TruFor.git third_party/TruFor
```

### Poids (non inclus dans ce dépôt)

| Fichier | Emplacement | Source |
|---|---|---|
| `mae_pretrain_vit_base.pth` (≈ 327 Mo) | `weights/fmae/` | lien du README de FMAE |
| `checkpoint-25.pth` (≈ 390 Mo) | `weights/fmae/` | lien du README de FMAE (poids de localisation) |
| `trufor.pth.tar` (≈ 269 Mo) | `third_party/TruFor/TruFor_train_test/pretrained_models/` | lien du README de TruFor |

Si un fichier manque, l'application affiche « Modèle indisponible » avec le détail, sans planter.

### Lancement

```powershell
streamlit run app.py
```

Les tests automatiques se lancent avec `python -m pytest tests`. Les tests qui nécessitent
les poids de FMAE sont ignorés automatiquement si ceux-ci sont absents.

## Interpréter les résultats

- **Heatmap** : sortie continue du modèle, entre 0 et 1.
- **Masque binaire** : heatmap ≥ seuil. Le seuil par défaut est 0,5 (valeur couramment utilisée
  dans les évaluations de FMAE). C'est un **réglage de l'utilisateur**, pas une valeur imposée par le modèle.
- **Score TruFor** : un score élevé indique une prédiction plutôt orientée vers une image falsifiée
  (déduit de la fonction de perte et des labels d'entraînement). **Ce n'est pas une probabilité
  calibrée.** Il est donné à titre indicatif.
- **FMAE** : aucun score global n'est affiché. Le checkpoint utilisé est celui de la localisation ;
  le dépôt officiel fournit un autre checkpoint pour la détection, non intégré ici.

## Limites connues

- **Taille des images pour TruFor** : le modèle traite l'image à sa taille d'origine, et la mémoire
  augmente plus vite que le nombre de pixels. Mesures sur une Quadro T1000 (4 Go) : 1,7 Mpx en 4 s,
  3 Mpx en 12 s avec débordement sur la RAM, 8 Mpx en erreur de mémoire. L'application refuse donc
  les images de plus de 2 Mpx avec TruFor et propose FMAE, qui redimensionne en 512 × 512 et n'a pas
  cette limite.
- **Le score TruFor dépend de la taille de l'image** : sur une même image, redimensionnée à plusieurs
  largeurs, il a varié entre 0,12 et 0,92. Il ne faut pas l'interpréter isolément.
- **Évaluation limitée** : la qualité a été vérifiée sur quelques images seulement (par exemple IoU de
  90 % pour FMAE sur une image d'IMD2020 avec seuil 0,5). Ce n'est pas une évaluation globale sur un jeu
  de données, et les performances réelles peuvent être très différentes.
- **Vitesse mesurée** : FMAE ≈ 0,4 s par image sur Quadro T1000, ≈ 4 s sur CPU ; TruFor ≈ 0,2 s
  sur une image de 0,1 Mpx (GPU). Le premier chargement d'un modèle prend quelques secondes de plus.

## Architecture

```
app.py                  point d'entrée Streamlit
components/             uploader, sidebar, affichage des résultats
models/base_model.py    contrat commun : BaseForgeryModel et PredictionResult
models/registry.py      registre des modèles (ajouter un modèle = un dossier + une ligne)
models/fmae/            adaptateur FMAE (config.py, predictor.py)
models/trufor/          adaptateur TruFor (config.py, predictor.py)
models/dummy/           modèle factice pour les tests
services/               lecture d'image, visualisation, gestionnaire de modèles
tests/                  tests automatiques
third_party/            code officiel des modèles (ignoré par Git)
weights/                poids FMAE (ignorés par Git)
```

Le gestionnaire de modèles (`services/inference_service.py`) garde un seul modèle en mémoire :
il décharge l'ancien avant de charger le suivant, ce qui est important avec 4 Go de VRAM.

## Licences et références

- **TruFor** (GRIP-UNINA, Université de Naples) : usage informatif et non commercial uniquement,
  avec conservation des mentions de copyright et citation des auteurs. Voir `LICENSE.txt` dans le dépôt
  officiel : https://github.com/grip-unina/TruFor
  Citation : article « TruFor : Leveraging all-round clues for trustworthy image forgery detection and
  localization » (CVPR 2023). À compléter avec la citation exacte donnée dans le README officiel.
- **FMAE** : « A Lottery Ticket Hypothesis Approach with Sparse Fine-tuning and MAE for Image Forgery
  Detection and Localization » (AAAI 2025). https://github.com/JulietChoo/FMAE
  Le dépôt ne contient pas de fichier de licence, et son code dérive de MAE (Meta). Ce projet l'utilise
  tel quel, dans un cadre académique, sans le redistribuer.
- Les poids appartiennent à leurs auteurs respectifs et ne sont pas redistribués ici.
