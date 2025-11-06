# Les imagettes

## Quels sont les caracteristiques des imagettes ou vignettes ou thumbnail ?

Dans le fichier `thumbnail.py`, les caractéristiques attendues pour une imagette (thumbnail) sont :

- Largeur maximale : `max_width` (par exemple 60 px, selon le commentaire)
- Hauteur maximale : `max_height` (par exemple 60 px)
- Formats supportés : PNG, GIF, JPEG, WebP
- L’image doit être accessible via une URL extraite des métadonnées (balise `graphicOverview`)
- L’image est considérée valide si :  
  - Sa largeur ≤ `max_width`
  - Sa hauteur ≤ `max_height`

La fonction `get_valid_thumbnail_from_mtd` retourne l’URL de la première image respectant ces critères, sinon `None`.  
La détection du format et des dimensions se fait automatiquement via la fonction `get_image_dimensions`.

## y'a t il aussi une notion de taille ?

Non, dans le code fourni, il n’y a pas de vérification explicite sur la taille (en octets) de l’image, uniquement sur ses dimensions (largeur et hauteur en pixels).

La taille maximale téléchargée pour l’analyse dépend du format (par exemple, 100 à 16384 octets), mais ce n’est qu’une limite technique pour lire les dimensions, pas un critère de sélection de la vignette.  
Donc :  
  La sélection se fait uniquement sur la largeur et la hauteur (en pixels), pas sur le poids (en Ko/Mo) de l’image.