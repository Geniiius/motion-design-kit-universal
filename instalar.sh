#!/usr/bin/env bash
# macOS / Linux / WSL: lanza el asistente del kit. No instala nada sin preguntar.
#   ./instalar.sh                         el asistente pregunta por cada elemento que falta
#   ./instalar.sh --language fr           en francés (fr, es, en)
#   ./instalar.sh --no-questions --approve engine-remotion   instala solo eso, sin preguntas
# En Linux, lo que pide la contraseña de administrador no lo ejecuta el kit: te da la línea para que la escribas tú.
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONUTF8=1 DO_NOT_TRACK=1 HYPERFRAMES_NO_TELEMETRY=1 HYPERFRAMES_NO_UPDATE_CHECK=1 HYPERFRAMES_SKIP_SKILLS=1
py=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    py="$c"
    break
  fi
done
if [ -z "$py" ]; then
  echo "El kit necesita Python 3.10 o superior: es gratuito. No se ha instalado nada."
  echo "  macOS : brew install python@3.13      (o https://www.python.org/downloads/)"
  echo "  Linux : sudo apt-get install -y python3 python3-venv      (o el gestor de tu distribución)"
  exit 1
fi
exec "$py" -m universal.cli setup wizard "$@"
