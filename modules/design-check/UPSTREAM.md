# Origine et usage

[pbakaus/impeccable](https://github.com/pbakaus/impeccable), paquet npm `impeccable` 4.8.0 et moteur `@impeccable/cli-*` 0.1.18, licence Apache-2.0.

## Ce que le kit utilise

Uniquement `detect`, sur les pages HTML livrées, automatiquement. Le moteur est lancé directement, après vérification de son empreinte contre le manifeste du paquet. Le kit n'utilise ni `impeccable install`, ni les skills, ni le « hook », ni l'extension, ni les fonctions qui contactent impeccable.style, et le lanceur npm n'est pas appelé : il pourrait sinon télécharger le moteur dans le dossier de l'utilisateur.

## Audit, 2026-11-03

- **Code lu sans exécution.** Le module `detect` n'a aucune dépendance réseau, et son code est identique à l'étiquette `engine-v0.1.18`. La télémétrie est ailleurs (fonction de choix de directions), jamais appelée ici.
- **Moteur non recompilé.** Son empreinte est vérifiée, mais rien ne prouve qu'il correspond exactement au code lu.
- **Écritures.** Aucune dans le dossier de l'utilisateur pendant l'essai.

## Limites vérifiées sur les pages du kit

Sur 17 alertes, 14 étaient justes et 3 fausses :

- `cramped-padding` sur un bloc dont les couches ont leur propre marge intérieure (bloc avant/après).
- `low-contrast` sur un texte blanc posé sur un élément sombre animé : la lecture statique ne voit pas ce fond.

Le film Risograph n'obtient aucune alerte parce que son texte est dessiné sur un canvas, invisible pour lui : cela ne prouve rien. Une partie des règles (catégorie `slop`) relève du goût. D'où un rôle de conseil : il ne bloque jamais une livraison, et Claude juge ses alertes en regardant la page.
