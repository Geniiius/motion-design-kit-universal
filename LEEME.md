# 🎬 Motion Design Kit Universal Studio

Un estudio audiovisual que manejas **hablando con Claude**. Parte de lo que tengas: una idea, un logo, fotos, vídeos grabados,
una voz, un documento, datos, un modelo 3D o una mezcla. Claude mira tus archivos, elige el camino más sencillo y entrega el resultado:
vídeo, película de datos, personaje 3D que habla o presentación interactiva con botones de verdad.

> **Resumen:** instala Claude Code → descomprime el kit → abre su carpeta en Claude Code y pega el mensaje de inicio
> (o doble clic en `INSTALAR.bat`) → el asistente te pregunta antes de instalar cada cosa → pide el vídeo que quieras.

**Todo funciona en local por defecto.** Nada de pago se usa sin que digas «sí».

---

## ✅ Antes de empezar

| Necesitas | Detalle |
|---|---|
| Un ordenador con **Windows 10 u 11** | Es donde el kit se ha probado entero. En macOS y Linux, mira [Compatibilidad](#-compatibilidad) |
| **Entre 2 y 6 GB libres** | 2 GB para lo imprescindible, hasta 6 GB con todas las opciones. Y conexión a internet durante la instalación |
| Una cuenta de **Claude** (Pro o Max) | para usar Claude Code |
| Una cuenta de **ElevenLabs** (opcional, de pago) | voces, música y efectos de alta calidad. Sin ella, el kit tiene una voz gratuita sin conexión |

No tienes que instalar nada a mano: el asistente mira lo que ya tienes y **te pregunta antes de instalar cada cosa**.

---

## 🛠️ Instalación (una sola vez)

### Paso 1 — Instala Claude Code
1. Descarga la app de escritorio de Claude: **https://claude.com/download**
2. Instálala e inicia sesión con tu cuenta de Claude.
3. Comprueba que ves la pestaña **Code** arriba en la app.

### Paso 2 — Descomprime el kit y deja que el asistente lo prepare
1. Haz clic derecho en el archivo `Motion-Design-Kit-Universal.zip` → **Propiedades** → marca
   **Desbloquear** (si aparece) → **Aceptar**.
2. Descomprímelo en una carpeta local fácil de encontrar, por ejemplo `Documentos\Motion-Design-Kit-Universal`.
   Evita una carpeta sincronizada con la nube (OneDrive, Dropbox): la instalación sería lenta.
3. Abre la app de Claude → pestaña **Code** → elige la carpeta del kit como carpeta de trabajo.
4. Copia este mensaje, **pégalo en Claude** y pulsa Enter (también está en `PROMPT-INSTALACION.txt`, en español, francés e inglés):

```text
Acabo de recibir este kit de vídeo y no sé programar. Ocúpate tú de todo y háblame con palabras sencillas, en español.

1. Mira primero mi equipo y lo que ya tengo instalado, sin cambiar nada.
2. Enséñame una tabla: qué hay ya, qué falta, qué es imprescindible y qué es opcional, para qué sirve cada cosa y cuánto ocupa.
3. No instales nada sin que yo diga «sí». Lo que ya funciona, no lo vuelvas a instalar.
4. Instala solo lo que yo acepte, comprueba que cada cosa funciona de verdad y haz un vídeo de prueba.
5. Dame un informe corto de lo que está listo y lo que no. Después pregúntame qué vídeo quiero hacer.

Nunca me pidas una clave o una contraseña en el chat.
```

5. Claude te pedirá permiso para ejecutar comandos: pulsa **Permitir / Allow**. Si Windows pregunta
   si quieres instalar un programa, pulsa **Sí**.

**Sin Claude:** haz doble clic en `INSTALAR.bat`. Se abre una ventana con el mismo asistente, que hace las mismas preguntas
(responde `s` para aceptar). Si Windows muestra «Windows protegió su PC»: **Más información** → **Ejecutar de todas formas**.
En macOS o Linux: `./instalar.sh`.

#### Lo que va a pasar, siempre en este orden

| Paso | Qué hace el asistente |
|---|---|
| 1. Mira | Tu sistema, procesador, memoria, tarjeta gráfica, espacio en disco, programas ya instalados y sus versiones. No cambia nada |
| 2. Explica | Una tabla: qué hay ya, qué falta, lo imprescindible y lo opcional, para qué sirve cada cosa y cuánto ocupa |
| 3. Pregunta | Nada se instala sin tu «sí». Lo que ya funciona no se reinstala |
| 4. Instala | Solo lo que aceptas, en la carpeta del kit. Las herramientas del equipo (Python, Node.js, FFmpeg) se nombran una a una |
| 5. Comprueba | Lanza cada motor y hace dos vídeos de prueba, que quedan en `out\essai-installation\` |
| 6. Informa | Cada elemento en uno de los cuatro estados de abajo |

| Estado | Qué significa |
|---|---|
| **READY** | Presente y comprobado |
| **WARNING** | Funciona, con un límite que se te explica |
| **FAILED** | Hay que repararlo |
| **OPTIONAL** | No instalado: disponible cuando lo pidas |

#### Lo que el asistente propone

| Elemento | Nivel | Tamaño | Para qué sirve |
|---|---|---|---|
| Python, FFmpeg, Node.js | Imprescindible | unos 320 MB | Hacer funcionar el kit, montar y exportar, crear |
| Motor de creación | Imprescindible | 1,2 GB | Crear un vídeo a partir de una idea |
| Subtítulos automáticos | Recomendado | 345 MB | Subtítulos, traducciones, extractos y capítulos, sin conexión |
| Voz en off gratuita | Opcional | 550 MB | Voz sintética sin conexión |
| Efectos alrededor de una persona | Opcional | 450 MB | Texto detrás de la cabeza, reencuadre que sigue la cara |
| Estilos de película | Opcional | 400 MB | Películas escritas en código en 66 estilos |
| Interfaces animadas | Opcional | 370 MB | Demostraciones de interfaz |
| HyperFrames, control de diseño | Opcional | variable, 20 MB | Bloques listos para usar, revisión de páginas |
| Blender, Git, uv | Opcional | herramientas del equipo | Render 3D de una mascota, demostraciones, instalación más rápida |

Si solo quieres montar y tratar vídeos que ya tienes, puedes rechazar el motor de creación: el informe lo anotará como una
elección tuya, no como un fallo. Una opción rechazada hoy se puede añadir más tarde: basta con pedirla.

### Paso 3 — ElevenLabs (opcional, de pago)

El kit funciona sin ElevenLabs. Si lo quieres, se usa de **dos maneras complementarias**:

**A. Tu API key (la usan los scripts y las skills del kit)**
1. Entra en **https://elevenlabs.io** y crea tu cuenta (o inicia sesión).
2. Ve a **https://elevenlabs.io/app/settings/api-keys** → **Create API key**.
3. Ponle un nombre (por ejemplo «Motion Kit») y activa al menos los permisos de
   **Text to Speech**, **Sound Effects**, **Music** y **Speech to Text**.
4. Copia la clave (empieza por `sk_…`). ⚠️ Solo se muestra una vez: guárdala en un sitio seguro.
5. Haz doble clic en `INSTALAR.bat`: al final, la ventana te la pide. **Pégala y pulsa Enter**
   (no se ve en pantalla, es normal).

> 🔒 Tu API key es personal: no la compartas, no la pegues en el chat y no la subas a internet.
> Queda guardada solo en tu PC (variable de entorno `ELEVENLABS_API_KEY`).

**B. El conector de ElevenLabs en Claude**
1. Abre **https://claude.ai** → tu foto de perfil → **Settings / Configuración** → **Connectors / Conectores**.
2. Busca **ElevenLabs** → **Connect / Conectar** → inicia sesión en ElevenLabs y acepta.
3. Para tener también **música**, añade el conector completo: **Add custom connector** →
   URL `https://api.elevenlabs.io/v1/mcp`.
4. En la app de escritorio, dentro de una sesión de Code, comprueba en el menú de conectores
   que ElevenLabs está **activado**.

### Paso 4 — Reinicia Claude Code
Cierra la app de Claude por completo y vuelve a abrirla. Las skills del kit se cargan al abrir su carpeta.

🎉 **¡Listo!**

---

## 🎥 Crear tu primer vídeo

1. Abre la app de Claude → pestaña **Code**.
2. Elige la carpeta del kit como carpeta de trabajo.
3. Escribe lo que quieres. Por ejemplo:

   > Quiero un Reel de 15 segundos para promocionar mi cafetería «La Taza». Público: jóvenes
   > de 20 a 35 años. Tono alegre. Con voz en off en español y música.

4. Claude trabaja como un **director de producción**:
   1. **Mira tus archivos de verdad** (formato, duración, rotación, transparencia, esqueleto de un modelo 3D…).
   2. Te resume en una ficha qué va a hacer, con qué herramienta, qué falta y qué costaría.
   3. Solo pregunta lo que bloquea (3 preguntas como máximo). Si el encargo es abierto, te propone **3 direcciones creativas**.
   4. Produce, **revisa los fotogramas** y te entrega el archivo.

   Si tienes prisa, añade «hazlo directamente» y se salta las propuestas.

### Ideas de peticiones

| Quieres… | Escribe algo como… |
|---|---|
| Un Reel / TikTok | «Reel de 20 s con 3 consejos para ahorrar, estilo tipografía cinética» |
| Un anuncio | «Anuncio de 15 s para mi tienda online, formatos 9:16 y 1:1, con mi logo (está en Escritorio\logo.png)» |
| Promocionar una web | «Haz un vídeo de lanzamiento de 30 s de https://miweb.com» |
| Una intro de logo | «Intro de logo de 4 s con mi logo, colores azul y blanco» |
| Un explainer con voz | «Explainer de 45 s en 16:9 que explique cómo funciona mi app, voz masculina tranquila» |
| El estilo prompt-motion.com | «Vídeo estilo Prompt Motion: un botón que se transforma en un panel de estadísticas» |
| Montar vídeos grabados | «Monta estos tres clips con mi logo y esta voz: C:\…\a.mp4, b.mp4, c.mp4, logo.png, voz.mp3» |
| Limpiar un vídeo tuyo | «Quita los silencios de este vídeo» |
| Subtítulos y traducciones | «Ponle subtítulos», «subtitúlalo en inglés y en francés» |
| Adaptarlo a otra red | «Ponlo en vertical para TikTok»: el encuadre sigue la cara o conserva la imagen entera |
| Extractos de un vídeo largo | «Saca tres extractos cortos de este pódcast para Instagram» |
| Capítulos de YouTube | «Escribe los capítulos de este tutorial» |
| Dar vida a unas fotos | «Haz un vídeo de 15 s con estas 5 fotos» |
| Un personaje 3D que habla | «Un personaje 3D que presente mi servicio con esta frase» |
| Un vídeo con tus datos | «Explica este CSV en un vídeo de 30 s, con la fuente visible» |
| Presentación con botones | «Presentación interactiva de mis 5 servicios, en HTML» |
| Efectos en un vídeo tuyo | «Pon la palabra VERANO detrás de mi cabeza del segundo 3 al 5» |
| Una película en un estilo concreto | «Una película de 20 s en acuarela sobre la lluvia» |
| Diseñar animaciones de una app | «Especifica las microinteracciones del botón de pago de mi app» |

**Consejos**
- Da tus **assets**: logo (PNG con fondo transparente), fotos, colores de marca, la URL de tu web.
- Indica la **plataforma** (Instagram, TikTok, YouTube, LinkedIn): Claude elige el formato correcto.
- Pide cambios con naturalidad: «más rápido», «cambia el color a verde», «la voz más enérgica».

### ¿Dónde están mis vídeos?

| Tipo de vídeo | Carpeta |
|---|---|
| Proyectos del enrutador | `out\<proyecto>\` |
| Vídeos Remotion | `template\out\` |
| Estilo Prompt Motion | `prompt-motion\out\` |
| Vídeos HyperFrames | carpeta del proyecto, subcarpeta `renders\` |
| Voz, música y efectos | `template\public\audio\` (`voz\`, `musica\`, `sfx\`) |

Claude siempre te dice la ruta exacta del archivo al terminar.

---

## 🧠 El kit aprende contigo

Cuantos más vídeos haces, mejor te conoce el kit y mejor salen:

| Cuándo | Qué hace Claude |
|---|---|
| **Al empezar** un vídeo | Lee tu perfil (gustos, marcas, lecciones) y aplica lo que ya sabe. Solo te hace las **2-3 preguntas que de verdad faltan**, siempre con una opción recomendada. Tras unos cuantos vídeos, casi no pregunta nada. |
| **Al terminar** | Pasa un **control de calidad automático** (volumen, picos, silencios, fotogramas negros, formato…), corrige lo que falle y te hace **3 preguntas rápidas** (nota del 1 al 5, qué cambiarías, qué quieres siempre así). |
| **Después** | Guarda lo aprendido: tus gustos, la ficha de tu marca (logo, colores, voz…) y las **reglas aprendidas**. Si un problema se repite 2 veces, se convierte en regla y propone arreglarlo en el kit. |

Todo se guarda en la carpeta **`perfil\`** de tu ordenador:

| Archivo | Contenido |
|---|---|
| `perfil\mi-estilo.md` | Tus gustos (estilo, voz, música, formato…) con su nivel de seguridad |
| `perfil\marcas\` | Una ficha por marca: logo, colores, voz, tono, frases obligatorias |
| `perfil\aprendizajes.md` | Reglas aprendidas + diario de cada vídeo |
| `perfil\calidad.jsonl` | Historial de medidas de calidad de tus vídeos |

- Puedes **editar estos archivos tú mismo** (son texto normal): lo que escribas manda.
- También puedes decírselo a Claude: «recuerda que mi marca usa verde», «nunca quiero música electrónica».
- Tu perfil es **personal**: no se incluye cuando compartes el kit con `empaquetar.ps1`.
- Para empezar de cero: borra tú la carpeta `perfil\`. El kit crea una vacía la próxima vez.

---

## 🔊 Audio

Por defecto: **tus archivos**, o la voz instalada en Windows, gratis y en local. Pregúntale a Claude qué idiomas tienes en este PC.

Gratis y sin conexión, tras una descarga que Claude te propone antes de hacerla: **voz Kokoro** en español, francés e inglés (354 Mo), **música y efectos sintetizados**, y **música con instrumentos reales** (de 78 a 416 Mo por banque).

Con **ElevenLabs**, cada generación consume créditos y Claude te pide un «sí» antes:

| Necesitas | Cómo pedirlo |
|---|---|
| Voz en off | «Añade una voz en off femenina, cálida, en español de España / de México» |
| Música | «Música electrónica suave a 120 BPM» |
| Efectos de sonido | «Añade un whoosh en cada transición y un clic en el botón» |
| Subtítulos | «Transcribe la voz y añade subtítulos animados» |

Cada generación consume **créditos de tu cuenta de ElevenLabs**. Consulta tu saldo en
https://elevenlabs.io/app/subscription.

---

## ❓ Problemas frecuentes

**Primero díselo a Claude: «algo no funciona, repara el kit».** Mira qué falla, te lo explica, te pide permiso y repara solo eso.
Sin Claude, vuelve a abrir `INSTALAR.bat`: es seguro repetirlo, lo que funciona no se reinstala.

| Problema | Solución |
|---|---|
| Windows no deja abrir `INSTALAR.bat` | Clic derecho en el ZIP → Propiedades → **Desbloquear**, y vuelve a descomprimir. O «Más información» → «Ejecutar de todas formas» |
| Una herramienta recién instalada «no se encuentra» | Cierra Claude (o la ventana) y vuelve a abrir: Windows solo la muestra a las ventanas abiertas después de instalarla |
| «winget no está disponible» | Instala **App Installer** desde Microsoft Store, o instala a mano lo que el asistente indique, desde el sitio oficial que te da |
| El informe dice **FAILED** | Pide «repara el kit». El detalle de la línea dice qué pasa |
| Todo va lento y el kit está en OneDrive o Dropbox | Mueve la carpeta del kit a una carpeta local |
| Claude no usa el kit | Comprueba que la carpeta abierta es la del kit y reinicia la app de Claude |
| «API key de ElevenLabs no válida» | Crea una nueva en https://elevenlabs.io/app/settings/api-keys y vuelve a abrir `INSTALAR.bat` |
| Sin voz / sin música | Revisa que tienes créditos en ElevenLabs y que el conector está activado. Para música, añade el conector completo (paso 3B.3) |
| El antivirus bloquea algo | Autoriza la carpeta del kit: los programas vienen de fuentes oficiales (Microsoft winget, npm, PyPI, GitHub) |

El último informe queda en `logs\dernier-rapport.md`. La carpeta `logs\` guarda el registro técnico de lo instalado y
comprobado: no contiene claves, ni tu nombre, ni la ruta de tu carpeta personal.

---

## 🧹 Desinstalar

Dile a Claude: «desinstala el kit». Te enseña lo que puede quitar y cuánto ocupa cada cosa (motores, opciones, modelos:
unos 2,4 GB cuando está todo) y quita solo lo que aceptas.

- **Tu perfil (`perfil\`), tus vídeos (`out\`) y tus ajustes nunca los borra el kit.** Para borrarlo todo, elimina tú la carpeta del kit.
- Lo que vive fuera de la carpeta (navegadores de render, herramientas del equipo que el kit instaló, tu API key) se te
  lista con la manera de quitarlo. El kit no lo quita solo: otros programas pueden usarlo.

---

## 🔄 Actualizar el kit

Pregunta a Claude: «¿está al día el kit?». Compara las versiones del kit con las últimas publicadas y te lo cuenta.
**No actualiza nada solo**: las versiones del kit están fijadas y comprobadas juntas.

Para pasar a una versión nueva del kit: descomprímela en otra carpeta, copia dentro `perfil\`, `out\` y
`kit.config.local.json`, y abre esa carpeta. El asistente comprueba el resto.

---

## 💻 Compatibilidad

| Sistema | Estado |
|---|---|
| Windows 10 y 11, 64 bits | **Probado entero**: instalación desde el ZIP, todos los motores, los dos vídeos de prueba |
| Linux (probado en WSL Ubuntu 24.04) | **En parte**: el asistente y las pruebas sin render funcionan; el render de vídeo no se ha ejecutado. Lo que pide la contraseña de administrador se te da para que lo escribas tú |
| macOS | **No probado.** El asistente usa Homebrew si está instalado |
| Windows o Linux con procesador ARM | No probado: las opciones de voz y efectos pueden no instalarse |

Instalar una herramienta del equipo con winget o Homebrew: la lógica está probada, pero en el equipo de pruebas todo
estaba ya instalado. La primera vez, comprueba el resultado con Claude.

---

## 📦 Qué contiene el kit

| Carpeta / archivo | Para qué sirve |
|---|---|
| `INSTALAR.bat` · `instalar.ps1` · `instalar.sh` | Abren el asistente de instalación, que pregunta antes de instalar |
| `kit.config.json` | Ajustes de fábrica. Los tuyos van en `kit.config.local.json`, que nunca se comparte |
| `kit-state.json` · `logs\` | Estado de la instalación en este equipo y registro técnico. Nunca se comparten |
| `universal\` | Enrutador, inventario de archivos, manifiesto, montaje, tratamientos de un vídeo entregado, voz local, control de calidad, asistente |
| `template\` | Proyecto **Remotion**: Promo, Reel de texto, logo, explainer de datos, personaje 3D, escena de cine, parallaxe |
| `prompt-motion\` | Motor del estilo **prompt-motion.com** |
| `hyperframes-starter\` | Proyecto **HyperFrames** 0.8.164 |
| `modules\` | Opcionales, se instalan dentro del kit con versiones fijadas: **efectos sobre una persona** (`video-effects`) y **66 estilos de película en código** (`opuscar`) |
| `presets\` | Catálogo de estilos y direcciones artísticas |
| `.claude\skills\` | Skills del kit: se cargan al abrir esta carpeta |
| `perfil-plantilla\` | Perfil vacío. `perfil\` se crea al instalar y nunca se comparte |
| `docs\` | Arquitectura, catálogo, pruebas reales, licencias, hoja de ruta |
| `examples\` | Datos, modelo 3D CC0 y ejemplos |
| `ejemplos\` | Dos vídeos de ejemplo |
| `empaquetar.ps1` | Crea un ZIP para compartir, sin tu perfil ni tus medios |

### Herramientas
Remotion · Three.js · HyperFrames · GSAP · Motion · lottie-web · Playwright · FFmpeg · Node.js · Python.
Opcionales: Herk Edit Kit, skills de terceros, ElevenLabs, Blender.

### Skills
| Grupo | Skills |
|---|---|
| **Entrada** | `kit-onboarding` (asistente), `universal-motion-director` (enrutador) |
| **Producción** | `media-ingestion-and-edit`, `infographic-director`, `character-studio`, `cinematic-3d`, `interactive-presentation`, `motion-kit`, `remotion-motion-graphics`, `prompt-motion-style`, `ffmpeg-video`, `playwright-capture` |
| **Vídeo entregado y módulos** | `video-workflows`, `video-effects`, `film-styles` |
| **Dirección y calidad** | `motion-director`, `motion-fundamentals`, `ui-microinteractions`, `video-storyboard`, `quality-reviewer`, `motion-memoria` |

Con `instalar.ps1 -ConSkillsTerceros` se añaden, en global, las de Remotion, HyperFrames, GSAP, LottieFiles y ElevenLabs.

---

## 🧑‍💻 Para usuarios avanzados

```powershell
# Asistente (Claude lo lanza por ti)
python -m universal.cli start                       # entrada única: primer arranque, reanudar, reparar o listo
python -m universal.cli setup plan                  # la tabla, sin cambiar nada
python -m universal.cli setup apply --approve engine-remotion --approve captions
python -m universal.cli setup verify --deep         # comprobación completa, con dos vídeos de prueba
python -m universal.cli repair                      # qué falla
python -m universal.cli uninstall                   # qué se puede quitar, con tamaños
python -m universal.cli updates                     # versiones fijadas frente a las últimas publicadas

# Enrutador
python -m universal.cli route --brief "Monta estos clips" -i a.mp4 -i logo.png::logo --name proyecto -o out/proyecto/project.json
python -m universal.cli run out/proyecto/project.json --profile draft    # draft, review, final, 4k
python -m universal.cli qc --video out/proyecto/proyecto.mp4 --frames out/pruebas
python -m universal.cli catalog logo
python -m universal.cli doctor

# Plantilla Remotion
cd template
npm run studio                                     # editor visual en el navegador
npx remotion render Promo-Reel out\promo.mp4        # renderizar una composición
.\scripts\render-all.ps1 -Filtro Promo              # todos los formatos de un vídeo
.\scripts\ffmpeg\add-audio.ps1 out\promo.mp4 -Musica public\audio\musica\pista.mp3 -Voz public\audio\voz\locucion.mp3
.\scripts\ffmpeg\social-export.ps1 out\promo-audio.mp4 -Plataforma instagram
.\scripts\control-calidad.ps1 out\promo-audio-instagram.mp4 -Proyecto "Promo" -Plataforma instagram
npm run capture -- https://miweb.com --format reel  # capturas de una web

# Estilo Prompt Motion
cd prompt-motion
node render.mjs compositions\studio-hud.html --stills 1,3,5   # imágenes de control
node render.mjs compositions\studio-hud.html                  # MP4

# HyperFrames
cd hyperframes-starter
npm run dev        # editor
npm run render     # MP4
```

Opciones de `instalar.ps1`: `-Idioma fr|es|en`, `-Aprobar "a,b"` (instala solo eso, sin preguntas), `-SoloElevenLabs`, `-SinElevenLabs`, `-ConHerk`, `-ConSkillsTerceros`.
Ajustes: `kit.config.json`; para cambiar uno, escribe la misma clave en `kit.config.local.json`. La lista está en `README.md` (en inglés).

---

## 📜 Créditos

El código del kit se publica con licencia MIT (archivo `LICENSE`). Seguridad: `SECURITY.md`. Ahorro de tokens: `docs/TOKEN-ECONOMY.md`. Versiones: `CHANGELOG.md`.

Las herramientas de terceros pertenecen a sus autores: Remotion, HyperFrames (HeyGen), ElevenLabs, GSAP (GreenSock), LottieFiles,
Three.js, Nate Herk (herk-edit-kit), Colin Blain (método de storyboard, MIT). Lista y licencias en `docs/THIRD-PARTY.md`: consúltalas antes de un uso comercial.
Remotion exige una licencia de empresa según el tamaño de la organización.
