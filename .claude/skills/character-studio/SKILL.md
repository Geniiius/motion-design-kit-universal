---
name: character-studio
description: "Personajes 3D reutilizables del kit: personaje original Nodo (composición Personaje-Nodo-*) o modelo .glb/.gltf con licencia (Personaje-GLB-*), gestos, voz y boca sincronizada con visemas reales, cámara y luz. Usar cuando se pida un personaje, mascota, avatar o presentador 3D."
---

# Character Studio

**Una biblioteca 3D muestra y anima modelos: no crea un humano fotorrealista desde un texto.** La creación de assets es una etapa aparte.

## Personaje incluido: Nodo
- Ficha única: `template/src/universal/personajes/nodo.json` (paleta, proporciones, gestos, continuidad). Es la identidad: no se cambia entre planos.
- Gestos (`gestos.ts`): `saludar`, `senalar`, `asentir`, `reaccionar`, `contar`, `saltar`, más reposo y habla. Todo es función del tiempo.
- Referencia completa: `universal/demos.py` → `demo_personnage`.

## Voz y boca
```bash
python -m universal.cli voice --text "..." --language en -o out/voz.wav --srt out/voz.srt
```
Escribe `out/voz.json` con palabras y visemas. **En este momento la voz local depende de las voces de Windows**: mira `doctor` → `voices_local`.
Si el idioma no está, `language_match` sale en falso: dilo. Otro idioma: voz aportada por el usuario, o ElevenLabs tras un «sí» a esa llamada:
```bash
python -m universal.cli voice --provider elevenlabs --approve --voice-id <id> --text "..." --language fr -o out/voz.mp3 --srt out/voz.srt
```
Sin `--approve` no se envía nada. El mismo texto no se paga dos veces (`out/cache-voix`). Elige una voz con `verified_languages` para ese idioma. Con ElevenLabs la boca sigue las letras cronometradas, no fonemas: dilo si se pide más precisión.

**Gratis en FR, ES y EN**, tras descargar el modelo con su acuerdo: `python -m universal.cli voice --provider kokoro --language fr --text "..." -o out/voz.wav --srt out/voz.srt`. El texto escrito manda; la transcripción local solo da los tiempos, con unos 0,2 s de margen. La boca sigue las letras. Que el usuario escuche la voz: solo hay una francesa.

Con un audio ya hecho no hay visemas: usa `envolvente` (`voice.amplitude_envelope`), repliegue por amplitud.

## Importar un modelo
1. `python -m universal.cli inventory modelo.glb`: lee esqueleto, animaciones y morphs reales.
2. **Comprueba la licencia** y anótala en `rights` del manifiesto. Sin licencia clara, no se usa.
3. `Personaje-GLB-*` con `clips` (`nombre`, `inicio`, `fin`, `expresion`). Reproducción determinista.
4. Sin morphs de boca: no hay lip-sync, la cabeza sigue la voz. Dilo.

## No probado aquí
VRM (`@pixiv/three-vrm` no instalado), Rigify y Blender (`character3d`, Blender ausente), FBX (convertir a GLB).

## Control
Mismo personaje en todos los planos, manos fuera de la cara, cortes en la primera palabra de la idea. Ejemplo CC0: `examples/modelos/RobotExpressive/`.
