# Character Studio — démonstrateur Blender (optionnel)

`python -m universal.cli character3d --config examples/universal/character3d.json --output out/mascot.mp4`

Requiert Blender installé et accessible dans PATH (non inclus dans le ZIP). Produit un personnage stylisé **3D réel**, lumière, géométrie et caméra avec mouvement de bras, tête et bouche illustratif. Ce démonstrateur ne génère **pas** un humain photoréaliste, ne fait **pas** de rigging d'humains importés et n'effectue **pas** de synchronisation labiale phonème/visème. S'il reçoit une voix autorisée, elle est ajoutée au fichier vidéo, mais le mouvement de bouche reste générique. Pour des personnages professionnels : modèles GLB/VRM licenciés, armatures, retargeting et visèmes à intégrer selon les assets.
