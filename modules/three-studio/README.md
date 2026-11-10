# Three Studio — démonstrateur 3D optionnel

Exécuter depuis ce répertoire : `npm install` puis `npm run dev`. Ouvrir l'adresse locale. Sans asset externe, une mascotte 3D procédurale est affichée et animée. Pour importer un personnage (licence vérifiée), placer `character.glb` dans `public/`. Utiliser la souris/tactile pour tourner autour.

Ce composant nécessite de télécharger les dépendances npm une première fois. Ce n'est **pas** une vidéo MP4 ni un acteur photoréaliste ; c'est un aperçu WebGL réellement volumétrique. Pour fabriquer une vidéo, utiliser le chemin Blender ou adapter la scène à `@remotion/three`, puis faire un rendu déterministe. Le script de démonstration emploie `requestAnimationFrame` pour un aperçu navigateur temps réel : ne pas intégrer tel quel dans un rendu Remotion image par image.
