# Migration et retour arrière

## Depuis l'ancien Motion Design Kit

Rien n'est à convertir. Le nouveau kit vit dans son propre dossier, l'ancien continue de fonctionner.

| Pour garder | Faire |
|---|---|
| Vos goûts et marques | Copier `perfil/` de l'ancien kit dans le nouveau. Il n'est jamais écrasé ni partagé |
| Une ancienne composition | La copier dans `template/src/compositions/` et l'enregistrer dans `Root.tsx`. Vérifier le rendu : voir ci-dessous |
| Vos médias | Les passer en entrée de `route`, ou les copier dans `template/public/` |

## Changements qui peuvent toucher une ancienne composition

| Changement | Effet |
|---|---|
| Remotion 4.0.536 → 4.0.540, zod 3 → 4 | Les schémas zod simples passent tels quels |
| Polices `@remotion/google-fonts` → `@fontsource` local | Mêmes familles dans `theme.ts`. Une composition qui charge d'autres polices Google reste dépendante du réseau |
| Skills dans `.claude/skills/` | Chargés à l'ouverture du dossier. Une copie globale de même nom a la priorité sur ce PC |
| `instalar.ps1` | Ne copie plus rien en global, Herk et skills tiers sur option |

## Langue

« Toujours en espagnol » devient `perfil/preferencias.json`. `auto` suit la langue de la demande. Un ancien profil reçoit ce fichier à l'installation, sans autre modification.

## Depuis V2

| V2 | Maintenant |
|---|---|
| `python -m universal.cli plan`, `render`, `qc`, `present`, `infographic`, `character3d` | Toujours là |
| `plan` renvoyait `workflow` | Renvoie le manifeste complet : `intent`, `engines`, `deliverables` |
| `INSTALAR-UNIVERSAL.ps1`, `instalar-universal.sh` | `instalar.ps1`, `instalar.sh` |
| Skills `character-3d`, `cinematic-agency`, `interactive-services`, `universal-quality-reviewer` | `character-studio`, `cinematic-3d`, `interactive-presentation`, `quality-reviewer` |
| `UniversalInfographic` | `Explainer-*` |
| `output-demos/` | `out/demos/` et `docs/preuves/` |

## Revenir en arrière

Dans ce dossier, le dépôt Git garde chaque étape :

```bash
git log --oneline
git switch --detach <commit>
```

Pour revenir à V2 : `Motion-Design-Kit-Universal-V2.zip` n'a pas été modifié. Après un retour, relancer `npm ci` dans `template/` : les dépendances changent selon le commit.
