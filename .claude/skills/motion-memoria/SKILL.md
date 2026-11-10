---
name: motion-memoria
description: "Memoria y mejora continua del Motion Design Kit: hace que el kit aprenda los gustos de cada usuario y mejore la calidad vídeo tras vídeo. Usar SIEMPRE al empezar un vídeo (leer el perfil, las marcas y los aprendizajes, y elegir solo las preguntas que de verdad faltan) y SIEMPRE al terminarlo (control de calidad automático, retrospectiva de 1 minuto y actualización del perfil). También cuando el usuario diga «recuerda que…», «siempre quiero…», «no me gusta…» o hable de su marca."
---

# Memoria y mejora continua

El kit no aprende solo: **aprende porque Claude escribe lo aprendido** en la carpeta `perfil/`
(personal, nunca se comparte en el ZIP):

| Archivo | Contiene |
|---|---|
| `perfil/mi-estilo.md` | Gustos del usuario con nivel de **seguridad** (baja / media / alta) |
| `perfil/marcas/<marca>.md` | Ficha de cada marca: logo, colores, voz, tono, claims, prohibiciones |
| `perfil/aprendizajes.md` | **Reglas aprendidas** + diario de cada vídeo |
| `perfil/calidad.jsonl` | Historial de medidas de calidad. Lo escribe `run` en cada entrega |
| `perfil/historial.jsonl` | Formato, estilo e idioma de cada entrega. De aquí sale el formato habitual |

Si `perfil/` no existe, créalo copiando `perfil-plantilla/`.

## A. Al EMPEZAR un vídeo (antes de las 3 direcciones de `motion-director`)

1. **Lee** `perfil/mi-estilo.md` y las 5 últimas entradas de `perfil/aprendizajes.md`. La ficha del enrutador ya trae en sus notas
   la marca (si se menciona o si solo hay una), el formato habitual, las reglas aprendidas y los defectos que se repiten: aplícalos.
2. **Aplica sin preguntar** lo que tenga seguridad **alta** y dilo en una línea:
   > «Aplico tu estilo habitual: fondo claro, voz cálida, subtítulos y tu logo abajo a la derecha.»
3. **Pregunta solo lo que falta**, con el banco `references/preguntas.md`:
   - Máximo **3 preguntas** por mensaje, ordenadas por impacto.
   - Cada pregunta con **opciones** y una **recomendada** basada en el perfil («¿La misma voz que la última vez? (recomendado) / otra voz»).
   - Nunca preguntes algo que ya esté en el brief, en el perfil con seguridad alta o en la ficha de marca.
   - Si el perfil tiene seguridad media/baja, conviértelo en confirmación rápida en vez de pregunta abierta.
4. **Previene lo que se repite**: un problema en 2 o más registros de `calidad.jsonl` llega como nota del enrutador.
   Prevenlo desde el principio y dilo («Los 2 últimos vídeos salieron con silencio al inicio: esta vez el sonido arranca en el primer segundo»).

## B. Al TERMINAR un vídeo (antes de dar la entrega por cerrada)

1. **Control de calidad**: `run` lo hace y guarda el resultado en el perfil, sin que nadie lo pida. Si entregaste sin `run`:
   `python -m universal.cli qc --video <final.mp4> --project <project.json> --registrar`.
   Si hay bloqueos o avisos, corrígelos y vuelve a medir **antes** de entregar. Indica en la entrega, en palabras normales,
   que el control salió bien.
2. **Retrospectiva de 1 minuto** (en el mismo mensaje de entrega, al final):
   > **Para que el próximo salga aún mejor (responde solo lo que quieras):**
   > 1. Del 1 al 5, ¿cuánto te gusta el resultado?
   > 2. ¿Qué cambiarías? (estilo, ritmo, voz, música, textos…)
   > 3. ¿Hay algo que quieras que haga **siempre** así?
3. Con la respuesta (o con lo observado durante el proyecto si no responde):
   - Añade una **entrada** en `perfil/aprendizajes.md` (formato de la plantilla).
   - Actualiza `perfil/mi-estilo.md`: sube la seguridad de lo que se repite (baja → media → alta);
     lo que el usuario diga «siempre» o «nunca» pasa directo a **alta**. Si contradice algo anterior,
     sustitúyelo (lo último manda).
   - Actualiza o crea la ficha `perfil/marcas/<marca>.md` y añade el vídeo a su tabla.
4. **Regla aprendida**: si un mismo problema o petición aparece **2 veces**, escríbelo en
   «Reglas aprendidas». Si la solución es técnica (un script, una skill, una plantilla del kit),
   **propón** el cambio al usuario y aplícalo solo si acepta; anótalo en la regla.

## C. Durante el proyecto
- Cuando el usuario dé una preferencia explícita («me gusta más así», «la próxima vez…»), anótala en
  el perfil en ese momento, no esperes al final.
- Cuando se rehaga algo (cambio de estilo, de voz, de ritmo), anota la causa: es la lección más valiosa.

## Reglas
- Nunca guardes en el perfil API keys, contraseñas ni datos personales sensibles.
- El perfil es del usuario: si edita los archivos a mano, sus cambios mandan.
- Mantén los archivos cortos: resume, no copies conversaciones. Si el diario supera ~40 entradas,
  condensa las antiguas en reglas.
