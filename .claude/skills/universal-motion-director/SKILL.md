---
name: universal-motion-director
description: "Punto de entrada de cualquier petición audiovisual del kit Universal Studio: brief solo, logo, fotos, rushes, audio, documentos, datos, modelo 3D, proyecto existente o una mezcla. Lee los archivos de verdad, detecta las intenciones, separa el estilo del motor, crea un project.json validado y lanza el pipeline más sobrio. Usar antes que cualquier otra skill de vídeo."
---

# Enrutador universal

No impongas un flujo. Primero mira lo que hay. **El usuario no escribe comandos: habla, y tú lo haces todo.** Con él, palabras normales: «Voy a montar tus clips con tu logo», nunca nombres de motores, intenciones ni comandos.

## 0. Entender antes de enrutar

**Tú entiendes; el enrutador comprueba.** Solo reconoce palabras: en pruebas con frases nunca vistas acertó 22 de 30 y en las otras 8 dijo que no sabía. Lee el mensaje como una persona, en cualquier idioma: qué quiere conseguir, para quién y con qué. Luego dile al enrutador lo que has entendido.

| La persona dice, por ejemplo | Lo que necesita | Qué pasar al enrutador |
|---|---|---|
| «algo que llame la atención para mis redes», «una pub para mi tienda» | Vídeo corto creado desde cero | `--intent CREATE_FROM_SCRATCH --format 9:16` |
| «monta estos clips», «acórtalo», «ponle mi música», «añade mi logo» | Montaje de lo que ya existe | `--intent EDIT_FOOTAGE` |
| Con **un** vídeo suyo: «quita los silencios», «ponle subtítulos», «tradúcelo», «hazlo vertical», «saca extractos», «ponle capítulos» | Tratar ese vídeo, entero | `--workflow <id>` (skill `video-workflows`) |
| «una palabra detrás de mí», «que siga mi cara», «cosas alrededor de mi cabeza» | Efectos sobre la persona | `--effects` (skill `video-effects`) |
| «que parezca una pintura», «como un videojuego viejo», «como cine mudo» | Un estilo con nombre | `--style <id>`: búscalo por su sentido con `catalog` |
| «un muñequito que explique», «alguien que hable, pero no yo», «un robot que salude» | Un personaje | `--intent CHARACTER_ANIMATION` |
| «que mis clientes puedan hacer clic», «un mini sitio con mis tarifas» | HTML de verdad | `--intent INTERACTIVE_PRESENTATION` |
| «que se note que crecemos», con un archivo de datos | Datos explicados | `--intent DATA_EXPLAINER`, solo cifras reales |
| «conviértelo en dibujo animado», con su vídeo | Transformar el vídeo | `--intent RESTYLE_FOOTAGE`: hoy bloqueado, explica por qué y ofrece alternativas |
| «no queda profesional», «mejóralo» | Aún no se sabe | Mira primero: fotogramas, sonido, ritmo. Propón lo que ves antes de tocar nada |
| «como la última vez», «lo de siempre» | Lo que ya sabe el perfil | Aplica el perfil, sin preguntas |

Si **dudas de verdad**, una sola pregunta con la opción recomendada. Si dice «hazlo directamente», decide y dilo en una línea.

## 1. Enrutar con los archivos reales

```bash
python -m universal.cli route --brief "<sus palabras>" -i <archivo> -i <archivo::rol> --name <proyecto> -o out/<proyecto>/project.json
```
Roles: `logo`, `voice`, `music`, `character`, `product`, `source`. Añade lo que has entendido: `--intent` (repetible), `--workflow` (repetible), `--style`, `--format`, `--duration`, `--effects`.
Un solo vídeo entregado, sin formato pedido, **conserva su forma**: no lo conviertas a horizontal por costumbre.

Devuelve una ficha que resumes al usuario con sus palabras. Varias intenciones por proyecto son normales. Mira sus notas:

- «ce choix est un défaut»: el enrutador ha adivinado. **Nunca lo aceptes sin más**: decide tú y relanza, o pregunta. `run` se niega a ejecutar un manifiesto así: nada se entrega al azar.
- Marca, formato habitual, reglas aprendidas, defectos que se repiten: vienen de `perfil/`. **Aplícalos** y dilo en una línea («Lo hago vertical, como tus dos últimos vídeos»). Si te pide otra cosa, manda lo que pide.

Si hay vídeos o imágenes, crea una planche para verlos: `python -m universal.cli contact-sheet <archivos> -o out/<proyecto>/reperage.jpg`, y **mírala**.

## 2. Reglas de decisión

| La ficha dice | Qué hacer |
|---|---|
| `EDIT_FOOTAGE` | Motor `ffmpeg-edit`. Nada de 3D ni generación para una simple coupe. Skill `media-ingestion-and-edit` |
| Motor `video-workflow` | Tratamientos de un vídeo entregado (silencios, extractos, reencuadre, subtítulos, capítulos): skill `video-workflows` |
| Motor `video-effects` | Efectos alrededor de una persona filmada: skill `video-effects`. Exige su consentimiento |
| Motor `film-style` | Película escrita en código en un estilo con nombre: skill `film-styles`. Un estilo es una receta, no una plantilla |
| `ANIMATE_LOGO` | `Logo-*`. Logo exacto: no lo redibujes ni lo deformes |
| `ANIMATE_IMAGES` | `Parallaxe-*`. Una foto plana no contiene 3D: es una simulación |
| `DATA_EXPLAINER` | `Explainer-*`. Skill `infographic-director`. Nunca inventes cifras |
| `CHARACTER_ANIMATION` | `Personaje-*`. Skill `character-studio` |
| 3D o look de cine | `Escena3D-*`, `Hibrido-*`. Skill `cinematic-3d` |
| `INTERACTIVE_PRESENTATION` | HTML real. Skill `interactive-presentation`. Un MP4 no contiene botones |
| `RESTYLE_FOOTAGE` | **Bloqueado**: pide proveedor, presupuesto y consentimiento. Solo se ofrece una vista previa con filtros, y se dice que lo es |
| `REVISE_EXISTING_PROJECT` | Inspecciona estado y versiones, trabaja sobre una copia, conserva la versión anterior |

Prioridad: lo que el usuario pide con palabras manda sobre lo que deduce la extensión de un archivo.

## 3. Estilo y motor son decisiones separadas

- Catálogo: `python -m universal.cli catalog <palabras>` y `--presets`. Doc: `docs/STYLE-CATALOG.md`.
- Las direcciones deben diferir en encuadre, narración, lenguaje de animación y materiales, no solo en la paleta.
- **Hollywood**: encuadre, luz motivada, cámara, etalonaje, sonido, montaje. Nunca una promesa de calidad de superproducción.
- **5D**: no es un formato. Pregunta la forma: parallaxe 2.5D, escena 3D o experiencia interactiva. Nunca llames 5D a un vídeo normal.
- Adapta las leyes de `docs/STORYBOARD-AGENCY.md` al género: nada de ritmo publicitario ni CTA en un vídeo científico o institucional.

## 4. Preguntar y aprobar

Máximo 3 preguntas, solo si bloquean. Propón 3 direcciones solo si ayuda (`motion-director`); si dice «hazlo directamente», decide y empieza.
Siempre requieren un «sí»: gastos, voz o cara de una persona real, publicar o subir algo. `approval_required` lo lista en el manifiesto.

## 5. Producir y comprobar

```bash
python -m universal.cli run out/<proyecto>/project.json --profile draft   # luego review, final
```
Escribe el texto real en `props` del manifiesto (el arranque automático usa la frase del brief). Declara en `quality.exceptions` lo que sea
intencionado (`black`, `freeze`, `silence`, `no-audio`). `run` guarda solo el historial de cada entrega en `perfil/`. Después aplica `quality-reviewer`. Termina con `motion-memoria`, parte B.

`run` no siempre termina en «entregado». `needs-input`: el kit ha preparado un archivo y espera que lo leas o elijas; hazlo y relanza. `unchanged`: no había nada que cambiar; díselo a la persona, no hay archivo nuevo. Y si dice que la petición no se ha entendido, vuelve al paso 0: entiende, y enruta de nuevo diciéndole lo que has entendido.
