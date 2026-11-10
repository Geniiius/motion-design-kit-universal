# Storyboard cinématographique : méthodes adaptées

Inspiré des dix lois et bibliothèques de patterns du dépôt [motion-design-claude-code](https://github.com/cblain100-prog/motion-design-claude-code). Il s'agit d'un **résumé adapté original**, pas d'une copie de son code ou des exemples. Voir le dépôt amont pour la totalité des patterns, templates, scripts et exemples et respecter sa licence MIT et les avis tiers.

1. **Un monde visuel par acte**. Définir le décor narratif et piloter la caméra comme piste indépendante.
2. **Deux vitesses de mouvement**. Utiliser des accents rapides et des mouvements subtils persistants quand le genre l'exige ; conserver le calme pour une explication scientifique.
3. **Objets-ponts**. Faire évoluer un élément déjà vu vers la scène suivante, plutôt que superposer des transitions gratuites.
4. **Entrées en profondeur**. Prioriser la mise au point, l'échelle et la perspective plutôt que multiplier les fondus.
5. **Synchronisation narrative**. Les images explicatives peuvent précéder légèrement la parole, les impacts tombent sur la syllabe ; aligner les sous-titres sur les vrais timestamps, pas le rythme supposé.
6. **Coupes justifiées**. Changement de lieu, de chapitre, de temps ou de sujet. La continuité n'est pas obligatoire si elle nuit à la lisibilité.
7. **Métaphores visuelles**. Traduire l'action du verbe en action d'objet, avec une compréhension immédiate.
8. **Identité de mouvement**. Répéter un ou deux mécanismes signature et limiter les styles d'apparition.
9. **Profondeur et hiérarchie**. Avant-plan, sujet, arrière-plan ; le regard doit savoir où se poser.
10. **Finale narrative**. Reprendre et résoudre le problème posé ; ne pas forcer une CTA commerciale pour un documentaire.

## Contrat de plan entre sous-agents

Chaque séquence a : identifiant, timing entrée/sortie, rôle narratif, éléments visibles, entrée caméra, sortie caméra, objet-pont, narration correspondante, ambiance, droits des médias, moteur, format, contrôles à vérifier et 3 captures-clés. Ne jamais lancer dix scènes sans design system commun.

## Discipline de vérification

Produire des **images de style** avant les scènes coûteuses ; réaliser un plan pilote ; inspecter débuts/milieux/fins et raccords ; écouter audio; archiver le contact sheet. La méthode du dépôt amont est orientée clips SaaS de 30–60 s : ne pas la plaquer systématiquement sur une vidéo longue, un film interview ou un travail scientifique.

## Adapter au genre

Ces lois viennent de films de lancement. Elles ne s'appliquent pas telles quelles partout.

| Genre | Rythme | Caméra | Sous-titres | Fin |
|---|---|---|---|---|
| Lancement, publicité | Un événement toutes les 0,5 à 1 s | Jamais figée | Mot à mot, un mot clé | Un seul bouton |
| Vidéo scientifique, institutionnelle | Calme, une idée à la fois | Lente, ou fixe si les objets portent le mouvement | Discrets, phrase par phrase | Source et limites, pas de CTA |
| Tutoriel | Au rythme du geste | Cadre sur l'élément cité | Oui, avec les termes exacts | Récapitulatif |
| Documentaire, interview | Celui de la parole : ne jamais couper une phrase | Celle des rushes | Selon la diffusion | Sans CTA imposé |
| Comédie | Coupe sur le premier mot de chaque gag | Fixe, chute par l'objet | Selon le gag | Chute |
| Clip musical | Sur les temps vérifiés | Au beat | Paroles si droits | Au dernier temps |

Une séquence noire, silencieuse ou lente est correcte quand elle est écrite. Il faut la déclarer dans `quality.exceptions`, pas la corriger.

## Gabarit d'en-tête

```
# Storyboard : <titre> · <durée> s · <format> · voix <narrative | jouée | aucune>
MONDE      Acte n : scènes et coordonnées ; fond dont la texture rend la dérive visible ; couleurs par rôle
SIGNATURES Mécanisme 1 ou 2, occurrences datées ; un mouvement par registre de texte ; rime du logo
CAMÉRA     Dérive par acte ; événements : t · type · facteur · durée · cible
VOIX       mot@t ; silences > 0,4 s, chacun est un plan
COUPES     t · premier mot · raison
```

## Gabarit de plan

```
### P<n> · <in> → <out> · <acte>
VOIX            « mot@t mot@t … »
TEXTE ÉCRAN     « … » · registre · mot accent · écart (avance | synchro | aucun texte)
IMAGE DE DÉPART objets, échelle, position, fond
ÉTAPES          t : élément, propriété de → à, durée, courbe ; ce qui continue de bouger
CAMÉRA          dérive ; événements
PROFONDEUR      avant-plan / sujet / fond ; couches animées
OBJET-PONT      <objet> devient <rôle> au plan suivant, ou vecteur de sortie repris à l'entrée
SON             bruitage à t, calé sur un geste ou un mot
IMAGE CLÉ       t : la vignette, en une phrase
```

## Contrôle avant d'animer (film de lancement)

1. Le monde, les signatures et les registres de texte sont écrits.
2. Chaque plan a une piste caméra, sauf choix écrit.
3. Aucun trou de plus d'une seconde sans événement, sauf silence écrit.
4. Chaque tenue de plus de 0,5 s nomme ce qui reste vivant.
5. Chaque jonction nomme son objet-pont ou son vecteur, sans objet dédoublé.
6. Deux transitions « effet » au plus sur le film.
7. Chaque coupe a sa raison : temps, premier mot, acte.
8. Chaque entrée principale a un état de départ écrit, jamais un simple fondu.
9. Chaque mot-image a son écart ; chaque silence de plus de 0,4 s est un plan.
10. Un mécanisme ou un objet de l'accroche revient avant la fin.

## Films longs : scènes confiées séparément

Chaque scène reçoit le même contrat : design system, palette, typographies, décor, caméra, manifeste d'assets, marques de voix, état entrant et sortant. Une planche de raccord compare la dernière image d'une scène à la première de la suivante. Méthode décrite, non outillée : voir [ROADMAP.md](ROADMAP.md).
