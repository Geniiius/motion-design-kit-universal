---
name: kit-onboarding
description: "Primer arranque, instalación, comprobación, reparación, desinstalación y puesta al día del Motion Design Kit. Usar cuando `python -m universal.cli start` no responde `ready`, y cuando el usuario diga «instala el kit», «¿funciona todo?», «algo no va», «repara», «desinstala», «¿está al día?», o cuando algo falle porque falta una herramienta o una opción."
---

# Asistente del kit

**Regla de oro: nada se instala, se descarga ni se borra sin un «sí» del usuario para ese elemento.** Tú miras, explicas, preguntas, haces solo lo aceptado y compruebas. Con el usuario, palabras normales y en su idioma: nunca comandos, nombres de paquetes ni rutas internas.

## 1. Al primer mensaje

```bash
python -m universal.cli start --language <fr|es|en>
```
Es la única entrada. Tarda medio segundo si el kit ya está configurado. Mira `phase` y sigue `next`.

| `phase` | Qué pasa | Qué haces |
|---|---|---|
| `ready` | Todo comprobado antes | **No reinstales nada.** Una línea («Todo listo, comprobado el…»), el consejo de `advice` si viene al caso, y pregunta qué vídeo quiere. Si ya ha pedido algo, hazlo sin más preámbulo |
| `first-launch` | Nunca se ha configurado en este equipo | Sección 2 |
| `resume` | Una instalación empezó y no terminó | Di qué quedó a medias (`interrupted`, `failed`), pregunta si la retomas, y sigue en la sección 2 desde «instalar» |
| `repair` | Algo que funcionaba ya no responde (`lost`) | Sección 4 |

Si el comando no arranca porque **falta Python**: explícalo («El kit necesita Python, gratuito, unos 30 MB»), pide permiso y, con su «sí», instálalo con el gestor del sistema (en Windows, winget con el paquete `Python.Python.3.13`; di que la instalación acepta su licencia). O indícale el doble clic en `INSTALAR.bat`, que pregunta lo mismo.

## 2. Primer arranque: mirar, explicar, preguntar, instalar, comprobar

**Mirar.** `start` ya lo ha hecho, sin cambiar nada: `machine` (sistema, procesador, memoria, tarjeta gráfica, disco), `rows` (cada elemento), `conflicts`, `advice`.

**Explicar.** Presenta en una tabla corta, con sus palabras:

| Elemento | ¿Ya está? | Versión | Nivel | Qué haré |
|---|---|---|---|---|

- `state: present` → «ya instalado, no lo toco». Dilo claramente: es lo primero que tranquiliza.
- `state: outdated` → demasiado antiguo: propón actualizarlo.
- `level`: `required` (imprescindible), `recommended`, `optional`. Usa `why` para decir para qué sirve cada cosa y `size_mb` para el tamaño.
- Si hay `conflicts`, explícalos antes de instalar: un `FAILED` (disco lleno, sistema de 32 bits) bloquea de verdad.

**Preguntar.** Como máximo tres preguntas:
1. Lo imprescindible que falta (`to_approve.required`), junto: «¿Instalo lo que falta para que el kit funcione? Son 1,3 GB, gratis».
2. Lo recomendado (`to_approve.recommended`).
3. Las opciones (`to_approve.optional`): enséñalas como una lista para elegir. Ninguna hace falta para empezar.

Di siempre lo que la fila indica: `licence` (instalar con winget acepta la licencia de la herramienta), `outside` (lo que queda fuera de la carpeta del kit), `needs` (lo que hay que instalar antes). `by_hand` son cosas que hace la persona: en Linux, la línea con `sudo`; la clave de ElevenLabs, que se escribe en la ventana de `INSTALAR.bat` y **nunca en el chat**.

**Instalar solo lo aceptado.**
```bash
python -m universal.cli setup apply --approve <id> --approve <id>
python -m universal.cli setup decline <id>          # un imprescindible rechazado: el informe dirá «a petición tuya», no «fallo»
```
Cada elemento se comprueba al terminar. `already`: ya estaba, no se ha rehecho. `blocked`: le falta otro antes. `manual`: lo hace la persona. `failed`: lee `detail`, explica, propón reintentar.

**Comprobar de verdad, y solo entonces decir «listo».**
```bash
python -m universal.cli setup verify --deep        # alrededor de un minuto
```
Lanza cada motor, hace dos vídeos de prueba (un montaje y una creación) y prueba los codificadores de la tarjeta gráfica. Entrega el informe con sus cuatro estados:

| Estado | Significa |
|---|---|
| `READY` | Presente y comprobado |
| `WARNING` | Funciona con un límite: explícalo |
| `FAILED` | Hay que repararlo |
| `OPTIONAL` | No instalado; disponible cuando lo pida |

`verdict: FAILED` → no digas que está listo: sección 4. Los vídeos de prueba quedan en `out/essai-installation/`: di la ruta, puede abrirlos. Sin `--deep` la comprobación es rápida y **no** autoriza a decir «listo».

Después, pregunta qué proyecto de vídeo quiere realizar.

## 3. Mientras se trabaja

- Un error `ConsentRequired` o «non installé» significa que falta una opción. Pregunta en una frase, con el tamaño («Para los subtítulos necesito una herramienta gratuita de 345 MB que funciona sin conexión. ¿La instalo?»), y con su «sí»: `setup apply --approve <opción>`. Luego sigue con lo que estabas haciendo.
- Si dice «instala lo gratuito sin preguntarme», anótalo una vez en sus ajustes: `python -c "from universal import config; config.set_local('consent.free_modules', 'auto')"`. Las herramientas del equipo y las descargas de pago se siguen preguntando siempre.
- **Elegir según el equipo y lo instalado.** Lo gratuito y local primero; si falta algo, hay otra vía:

| Falta | Mientras tanto |
|---|---|
| Motor de creación | Montaje, tratamientos de un vídeo entregado y presentación web siguen funcionando |
| Subtítulos automáticos | La persona da el texto o un `.srt`; o se instala la opción |
| Voz gratuita | Voz del sistema, o ElevenLabs (de pago, con su «sí» en cada llamada) |
| Efectos y seguimiento de la cara | Reencuadre al centro o imagen entera sobre fondo desenfocado |
| Blender | El 3D del motor de creación |
| Tarjeta gráfica | El render pasa solo a modo software: más lento, mismo resultado |

`advice` resume lo que el equipo aconseja (poca memoria → borrador y vídeos cortos; sin tarjeta gráfica → evitar 3D largo; codificador comprobado → exportación rápida de vídeos largos).

## 4. Reparar, desinstalar, poner al día

Cuando la persona pida reparar, desinstalar, saber si el kit está al día o dónde se guarda cada cosa, lee `MANTENIMIENTO.md` en esta misma carpeta. No hace falta leerlo para instalar ni para trabajar.

## Lo que no se ha probado

- Instalar una herramienta del equipo con winget o brew: la lógica está probada, pero en el equipo de desarrollo todo estaba ya instalado y no se ejecutó de verdad. La primera vez, comprueba el resultado con el usuario.
- macOS no se ha probado. Linux se ha probado en parte (WSL, sin FFmpeg).
