# Motion Design Kit Universal Studio — guide de démarrage

Un studio vidéo qu'on pilote **en parlant à Claude**. Vous partez de ce que vous avez : une idée, une vidéo déjà filmée, un logo, des photos, une voix, des données, ou un mélange. Vous dites ce que vous voulez avec vos mots ; Claude regarde vos fichiers, choisit le chemin le plus simple, fabrique la vidéo et la vérifie.

**Aucune commande à taper. Tout fonctionne sur votre ordinateur par défaut. Rien ne s'installe et rien de payant ne se lance sans votre « oui ».**

| Vous voulez | Le kit sait faire |
|---|---|
| Une vidéo pour YouTube, TikTok, Instagram ou Shorts | Formats 16:9, 9:16, 1:1 et 4:5, longs ou courts |
| Travailler une vidéo déjà filmée | Enlever les silences, sous-titrer, traduire les sous-titres, recadrer en vertical, sortir des extraits, écrire les chapitres |
| Créer une vidéo à partir d'une idée | Promo, publicité, logo animé, photos animées, graphiques, personnage 3D, film dans un style précis |
| Monter | Clips, photos, logo, voix et musique, avec le son au bon niveau |
| Autre chose qu'un MP4 | Une présentation interactive, avec de vrais boutons |

---

## 1. Avant de commencer

| Il vous faut | Détail |
|---|---|
| Un ordinateur sous **Windows 10 ou 11** | C'est là que le kit a été essayé en entier. Sous macOS et Linux, voir [Compatibilité](#9-compatibilité) |
| **2 à 6 Go libres** | 2 Go pour l'indispensable, jusqu'à 6 Go avec toutes les options. Et une connexion internet pendant l'installation |
| Un compte **Claude** (Pro ou Max) | Pour utiliser Claude Code |
| Un compte **ElevenLabs** | Optionnel et payant : voix, musique et bruitages de haute qualité. Sans lui, le kit a une voix gratuite hors ligne |

Vous n'avez rien à installer à la main : l'assistant regarde ce que vous avez déjà et **demande avant d'installer chaque élément**.

---

## 2. Installation, une seule fois

**Étape 1 — Installer Claude.** Téléchargez l'application sur https://claude.com/download, connectez-vous, et vérifiez que l'onglet **Code** apparaît en haut.

**Étape 2 — Décompresser le kit.** Clic droit sur le fichier ZIP → **Propriétés** → cochez **Débloquer** s'il apparaît → **OK**. Décompressez-le dans un dossier simple à retrouver, par exemple `Documents\Motion-Design-Kit-Universal`. Évitez un dossier synchronisé avec le cloud (OneDrive, Dropbox) : l'installation y serait lente.

**Étape 3 — Laisser l'assistant préparer le kit.** Dans Claude, onglet **Code**, choisissez le dossier du kit. Copiez ce message, collez-le et validez :

```text
Je viens de recevoir ce kit vidéo et je ne sais pas programmer. Occupe-toi de tout et parle-moi avec des mots simples, en français.

1. Regarde d'abord mon ordinateur et ce qui est déjà installé, sans rien changer.
2. Montre-moi un tableau : ce qui est déjà là, ce qui manque, ce qui est indispensable et ce qui est optionnel, à quoi sert chaque élément et combien il pèse.
3. N'installe rien sans que je dise « oui ». Ce qui fonctionne déjà, ne le réinstalle pas.
4. Installe seulement ce que j'accepte, vérifie que chaque élément fonctionne pour de vrai et fais une vidéo d'essai.
5. Donne-moi un court bilan de ce qui est prêt et de ce qui ne l'est pas. Ensuite, demande-moi quelle vidéo je veux faire.

Ne me demande jamais une clé ou un mot de passe dans la conversation.
```

Le même message existe en espagnol et en anglais dans `PROMPT-INSTALACION.txt`. Claude vous demandera la permission de lancer des commandes : cliquez sur **Autoriser**. Si Windows demande s'il peut installer un programme, cliquez sur **Oui**.

**Sans Claude :** double-cliquez sur `INSTALAR.bat`. Une fenêtre s'ouvre avec le même assistant, qui pose les mêmes questions (répondez `o` pour accepter). Si Windows affiche « Windows a protégé votre ordinateur » : **Informations complémentaires** → **Exécuter quand même**. Sous macOS ou Linux : `./instalar.sh`.

### Ce qui se passe, toujours dans cet ordre

| Étape | Ce que fait l'assistant |
|---|---|
| 1. Il regarde | Système, processeur, mémoire, carte graphique, place sur le disque, logiciels déjà présents et leurs versions. Il ne change rien |
| 2. Il explique | Un tableau : ce qui est déjà là, ce qui manque, l'indispensable et l'optionnel, à quoi sert chaque élément, son poids |
| 3. Il demande | Rien ne s'installe sans votre « oui ». Ce qui fonctionne déjà n'est pas réinstallé |
| 4. Il installe | Seulement ce que vous acceptez, dans le dossier du kit. Les outils de l'ordinateur (Python, Node.js, FFmpeg) sont nommés un par un |
| 5. Il vérifie | Il lance chaque moteur et fabrique deux vidéos d'essai, gardées dans `out\essai-installation\` |
| 6. Il rend compte | Chaque élément dans l'un des quatre états ci-dessous |

| État | Ce que cela veut dire |
|---|---|
| **READY** | Présent et vérifié |
| **WARNING** | Fonctionne, avec une limite qui vous est expliquée |
| **FAILED** | À réparer |
| **OPTIONAL** | Pas installé : disponible quand vous le demanderez |

### Ce que l'assistant propose

| Élément | Niveau | Poids | À quoi il sert |
|---|---|---|---|
| Python, FFmpeg, Node.js | Indispensable | environ 320 Mo | Faire tourner le kit, monter et exporter, créer |
| Moteur de création | Indispensable | 1,2 Go | Créer une vidéo à partir d'une idée |
| Sous-titres automatiques | Recommandé | 345 Mo | Sous-titres, traductions, extraits, chapitres, hors ligne |
| Voix off gratuite | Optionnel | 550 Mo | Voix de synthèse hors ligne |
| Effets autour d'une personne | Optionnel | 450 Mo | Texte derrière la tête, recadrage qui suit le visage |
| Styles de films | Optionnel | 400 Mo | Films écrits en code dans 66 styles |
| Interfaces animées | Optionnel | 370 Mo | Démonstrations d'interface |
| HyperFrames, contrôle de design | Optionnel | variable, 20 Mo | Blocs prêts à l'emploi, relecture des pages |
| Blender, Git, uv | Optionnel | outils de l'ordinateur | Rendu 3D d'une mascotte, démonstrations, installation plus rapide |

Si vous voulez seulement monter et travailler des vidéos que vous avez déjà, vous pouvez refuser le moteur de création : le bilan le notera comme votre choix, pas comme une panne. Une option refusée aujourd'hui peut être ajoutée plus tard, il suffit de la demander.

**ElevenLabs** (optionnel, payant) : créez une clé sur https://elevenlabs.io/app/settings/api-keys, puis double-cliquez sur `INSTALAR.bat`. À la fin, la fenêtre vous demande la clé : collez-la et validez, elle ne s'affiche pas. **Ne l'écrivez jamais dans la conversation.**

---

## 3. Votre première vidéo

Ouvrez le dossier du kit dans Claude, onglet **Code**, et écrivez ce que vous voulez. Par exemple :

> Je veux une vidéo de 15 secondes pour annoncer l'ouverture de mon café « La Tasse ». Pour Instagram, ton chaleureux.

Claude regarde vos fichiers pour de vrai, résume ce qu'il va faire, pose seulement les questions qui bloquent (trois au maximum), fabrique, regarde le résultat image par image et vous donne le chemin du fichier. Dites « fais-le directement » pour aller plus vite.

### Vous avez déjà une vidéo

| Vous écrivez | Ce que vous recevez |
|---|---|
| « Enlève les silences de ma vidéo » | La même vidéo, sans les blancs, chaque coupe gardant un souffle |
| « Ajoute des sous-titres » | Les sous-titres incrustés. Claude relit le texte avant : la transcription se trompe sur les noms propres |
| « Sous-titre-la en anglais et en espagnol » | Une vidéo par langue |
| « Mets-la au format TikTok » | Une vidéo verticale : le cadre suit le visage, ou l'image entière est gardée sur un fond flou |
| « Fais trois extraits courts pour Instagram » | Trois fichiers, coupés sur des fins de mots. Claude lit la transcription pour choisir des moments qui tiennent debout seuls |
| « Écris les chapitres pour YouTube » | Le texte des chapitres, prêt à coller dans la description |
| « Monte ces trois clips avec mon logo et ma musique » | Un montage, le son au bon niveau |

Votre vidéo est gardée **en entier** et **dans sa forme** : une vidéo verticale reste verticale si vous ne demandez pas autre chose. Rien n'est raccourci sans que vous l'ayez demandé.

### Vous partez d'une idée

| Type de vidéo | Vous écrivez, par exemple |
|---|---|
| Publicité, promo | « Une pub de 15 secondes pour ma boutique, en vertical et en carré, avec mon logo » |
| Short, Reel, TikTok | « Un Reel de 20 secondes avec 3 conseils pour économiser » |
| Tutoriel | « Explique en 45 secondes comment fonctionne mon application » |
| Vidéo de données | « Explique ce tableau de chiffres en 30 secondes, source visible » |
| Logo | « Anime mon logo en 4 secondes » |
| Photos | « Un film de 15 secondes avec ces 5 photos » |
| Personnage | « Un personnage 3D qui présente mon service » |
| Style précis | « Un film de 20 secondes en aquarelle sur la pluie » |
| Interview, podcast, documentaire | Donnez la vidéo filmée : le kit la nettoie, la sous-titre, la découpe en extraits et écrit les chapitres |
| Plusieurs langues | « Sous-titres en français, anglais et espagnol », ou une voix off dans une autre langue |

**Conseils.** Donnez vos fichiers (logo sur fond transparent, photos, couleurs). Nommez la plateforme : Claude choisit le bon format. Demandez les changements naturellement : « plus rapide », « en vert », « la voix plus énergique ».

### Où sont mes vidéos ?

Dans le dossier `out\`, un sous-dossier par projet. Claude donne toujours le chemin exact du fichier final.

---

## 4. Le kit apprend

Au début d'une vidéo, Claude relit ce qu'il sait de vous (goûts, marque, défauts déjà rencontrés) et ne pose que les questions qui manquent. À la fin, il mesure la qualité, vous pose trois questions rapides et retient les réponses. Tout cela vit dans le dossier `perfil\` de votre ordinateur : c'est du texte, vous pouvez le lire et le corriger. Il n'est jamais partagé avec le kit.

Vous pouvez aussi le dire directement : « retiens que ma marque utilise le vert », « je ne veux jamais de musique électronique ».

---

## 5. Voix et sons

- **Gratuit, sur votre ordinateur :** vos propres fichiers, la voix de Windows, ou la voix off gratuite du kit (français, espagnol, anglais) si vous avez accepté cette option. Une seule voix française existe : écoutez-la avant de la garder.
- **Payant, avec ElevenLabs :** voix, musique et bruitages. Chaque appel consomme vos crédits, et Claude vous demande un « oui » **à chaque fois**.

---

## 6. Si quelque chose ne marche pas

**Dites-le d'abord à Claude : « quelque chose ne marche pas, répare le kit ».** Il regarde ce qui est en panne, vous l'explique, demande votre accord et ne répare que cela. Sans Claude, rouvrez `INSTALAR.bat` : c'est sans risque, ce qui fonctionne n'est pas réinstallé.

| Problème | Solution |
|---|---|
| Windows refuse d'ouvrir `INSTALAR.bat` | Clic droit sur le ZIP → Propriétés → **Débloquer**, puis décompressez de nouveau. Ou « Informations complémentaires » → « Exécuter quand même » |
| Un outil tout juste installé est « introuvable » | Fermez Claude (ou la fenêtre) et rouvrez : Windows ne le montre qu'aux fenêtres ouvertes après l'installation |
| « winget n'est pas disponible » | Installez **App Installer** depuis le Microsoft Store, ou installez à la main ce que l'assistant indique, depuis le site officiel qu'il vous donne |
| Le bilan affiche **FAILED** | Demandez « répare le kit ». Le détail de la ligne dit ce qui se passe |
| Tout est lent et le kit est dans OneDrive ou Dropbox | Déplacez le dossier du kit dans un dossier local |
| L'antivirus bloque un fichier | Autorisez le dossier du kit : les programmes viennent de sources officielles (Microsoft winget, npm, PyPI, GitHub) |
| Claude n'utilise pas le kit | Vérifiez que c'est bien le dossier du kit qui est ouvert, puis relancez Claude |

Le dernier bilan est gardé dans `logs\dernier-rapport.md`. Le dossier `logs\` tient le journal technique de ce qui a été installé et vérifié : il ne contient ni clé, ni votre nom, ni le chemin de votre dossier personnel.

---

## 7. Désinstaller

Dites à Claude : « désinstalle le kit ». Il montre ce qui peut partir et le poids de chaque élément (moteurs, options, modèles : environ 2,4 Go quand tout est installé) et ne retire que ce que vous acceptez.

- **Votre profil (`perfil\`), vos vidéos (`out\`) et vos réglages ne sont jamais supprimés par le kit.** Pour tout effacer, supprimez vous-même le dossier du kit.
- Ce qui vit hors du dossier (navigateurs de rendu, outils de l'ordinateur que le kit a installés, votre clé ElevenLabs) vous est listé avec la façon de l'enlever. Le kit ne l'enlève pas tout seul : d'autres logiciels peuvent s'en servir.

---

## 8. Mettre à jour

Demandez à Claude : « est-ce que le kit est à jour ? ». Il compare les versions du kit avec les dernières publiées et vous le dit. **Rien n'est mis à jour tout seul** : les versions du kit sont fixées et vérifiées ensemble.

Pour passer à une nouvelle version du kit : décompressez-la dans un autre dossier, copiez-y `perfil\`, `out\` et `kit.config.local.json`, puis ouvrez ce dossier. L'assistant vérifie le reste.

---

## 9. Compatibilité

| Système | État |
|---|---|
| Windows 10 et 11, 64 bits | **Essayé en entier** : installation depuis le ZIP, tous les moteurs, les deux vidéos d'essai |
| Linux (essayé sous WSL Ubuntu 24.04) | **En partie** : l'assistant et les tests sans rendu fonctionnent ; le rendu vidéo n'y a pas été lancé. Ce qui demande le mot de passe administrateur vous est donné à taper vous-même |
| macOS | **Pas essayé.** L'assistant utilise Homebrew s'il est installé |
| Windows ou Linux sur processeur ARM | Pas essayé : les options de voix et d'effets peuvent ne pas s'installer |

---

## 10. Ce que le kit ne fait pas

- **Pas de photoréalisme ni d'acteur généré.** Le « look cinéma » est une 3D stylisée. Blender rend ce qu'on lui fournit : pour du réalisme, il faut de vrais modèles et de vraies matières, avec leurs droits.
- **Pas de vrai restylage d'une vidéo filmée** (« transforme-moi en dessin animé ») sans service externe, budget et consentement. Seul un aperçu par filtres est local, et il est annoncé comme tel.
- **Pas de « 5D »** : ce n'est pas un format. Claude demande quelle forme vous voulez.
- **Pas de boutons dans un MP4** : les boutons existent dans la version page web.
- **Il ne choisit pas seul « les meilleurs moments »** : Claude lit la transcription pour les choisir. Il n'enlève pas les « euh » ni les reprises, seulement les silences.
- **Recadrage qui suit le visage :** essayé avec des trajectoires simulées, pas avec une vraie personne filmée. Regardez le résultat en entier avant de le publier.
- **Installer un outil de l'ordinateur avec winget ou Homebrew :** la logique est testée, mais sur la machine d'essai tout était déjà installé. La première fois, vérifiez le résultat avec Claude.

Ce qui a été essayé pour de vrai, avec les preuves : [docs/TEST-REPORT.md](docs/TEST-REPORT.md).

---

## Pour aller plus loin

[Vue d'ensemble technique, en anglais](README.md) · [Sécurité](SECURITY.md) · [Économie de tokens](docs/TOKEN-ECONOMY.md) · [Historique des versions](CHANGELOG.md) · [Recettes](docs/RECETTES-DE-PRODUCTION.md) · [Architecture](docs/ARCHITECTURE.md) · [Styles](docs/STYLE-CATALOG.md) · [Storyboard](docs/STORYBOARD-AGENCY.md) · [Licences](docs/THIRD-PARTY.md) · [Suite](docs/ROADMAP.md) · [Guía en español](LEEME.md)
