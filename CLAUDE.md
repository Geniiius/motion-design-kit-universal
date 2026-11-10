# Motion Design Kit Universal Studio — instrucciones para Claude

- **Idioma**: lee `perfil/preferencias.json`. Con `idioma_respuesta: "auto"`, responde en el idioma de la última petición
  (español, francés o inglés). Sin ese archivo, usa el idioma del usuario y, en caso de duda, español. Sé claro y sin jerga:
  muchos usuarios no son técnicos.
- **El usuario nunca escribe comandos.** Habla con normalidad y tú lo haces todo: lees sus archivos, entiendes qué necesita, decides, ejecutas y compruebas. No le enseñes comandos, nombres de motores ni rutas internas, ni le pidas que lance nada, salvo que lo pida. Nada se instala ni se descarga sin su «sí»: pregúntalo en una frase, con el tamaño («¿Descargo la voz gratuita? Son 550 MB»).
- **Primer mensaje de cada conversación**: lanza `python -m universal.cli start`. Si responde `ready`, no reinstales nada y no abras ninguna skill para esto: una línea y a trabajar. En cualquier otro caso (`first-launch`, `resume`, `repair`), sigue la skill **`kit-onboarding`** antes de cualquier otra. Instalar, comprobar, reparar, desinstalar y «¿está al día?» pasan también por esa skill. Lo que ya está instalado y funciona se dice y no se toca.
- **No impongas el camino «texto → storyboard → vídeo».** Para **toda** petición de vídeo, animación, logo, fotos, montaje, 3D,
  infografía o presentación, empieza por la skill **`universal-motion-director`**: lee los archivos de verdad, enruta y crea un
  `project.json` validado. Crear, montar, modificar y transformar son tareas distintas.
- **Perfil**: al empezar, aplica la parte A de `motion-memoria` (`perfil/`, máx. 3 preguntas, con opción recomendada). Al terminar,
  la parte B. Si `perfil/` no existe, créalo copiando `perfil-plantilla/`. El perfil de un usuario nunca se comparte.
- **Solo preguntas que bloqueen**, 3 como máximo. Si dice «hazlo directamente», toma la mejor hipótesis, dila en una línea y empieza.
  Lo que nunca se salta: **aprobar gastos, voces o caras de personas reales, y publicar**.
- **Coste**: todo es local por defecto. Una llamada de pago (ElevenLabs u otro proveedor) exige un «sí» explícito para esa llamada.
  Nunca pidas ni muestres una API key en el chat; si falta, skill `setup-api-key` o `INSTALAR.bat`.
- **No prometas lo que no se ha probado.** Di «no probado» o «bloqueado» cuando sea así. «Hollywood» se traduce en criterios de
  fabricación; «5D» no es un formato: pregunta la forma final. Una biblioteca 3D anima modelos, no crea humanos fotorrealistas desde un texto.
- **Originales intactos**: toda transformación destructiva trabaja sobre una copia.
- **Verifica siempre**: `python -m universal.cli qc` y además **mira los fotogramas** y la planche de contacto: el control técnico
  no ve un subtítulo repetido ni una escena mal calada. Di la ruta exacta del archivo final.
- Al entregar un vídeo indica: formato · duración · plataforma · restricciones de marca.
- Para **escribir** una composición, lee antes su skill: `remotion-motion-graphics` en `template/`, `hyperframes-core` en `hyperframes-starter/`.
- Montaje complejo de cara a cámara: Herk Edit Kit es opcional (`instalar.ps1 -ConHerk`) y se abre en `workspaces/herk-edit-kit/`.
- **Un vídeo entregado para tratarlo** (quitar silencios, extractos, vertical, subtítulos, traducciones, capítulos): skill `video-workflows`. El vídeo se conserva entero y con su forma; nada se entrega si la petición no se ha entendido.
- **Efectos sobre una persona filmada**: skill `video-effects`. **Película escrita en código en un estilo con nombre** (acuarela, ukiyo-e, risografía…): skill `film-styles`. Son módulos opcionales: `python -m universal.cli modules status`.
- Referencias: `docs/ARCHITECTURE.md`, `docs/STYLE-CATALOG.md`, `docs/STORYBOARD-AGENCY.md`, `docs/TEST-REPORT.md`.
