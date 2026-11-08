#!/usr/bin/env bash
#
# Abre un artefacto HTML de explain-html en el navegador del entorno actual:
# WSL (wslview o explorer.exe) o escritorio Linux (xdg-open). Si no hay
# navegador disponible, imprime la ruta para abrir a mano y termina en error,
# para que el agente informe la alternativa en lugar de reintentar.
#
#   ./open-artifact.sh .explanations/<slug>.html
#
set -euo pipefail

if [[ $# -ne 1 ]]; then
	echo "Uso: $0 <ruta.html>" >&2
	exit 2
fi

artifact="$1"
if [[ ! -f "$artifact" ]]; then
	echo "No existe el artefacto '$artifact'. Genera el .html antes de abrirlo." >&2
	exit 1
fi

absolute="$(cd "$(dirname "$artifact")" && pwd)/$(basename "$artifact")"

open_with() {
	local tool="$1"
	shift
	if "$@" >/dev/null 2>&1; then
		echo "Abierto en el navegador con $tool: $absolute"
		return 0
	fi
	return 1
}

# explorer.exe devuelve código distinto de 0 aunque abra la ventana, así que su
# éxito se da por el proceso, no por el código de salida.
if command -v wslview >/dev/null 2>&1 && open_with wslview wslview "$absolute"; then
	exit 0
fi
if [[ -x /mnt/c/Windows/explorer.exe ]]; then
	/mnt/c/Windows/explorer.exe "$(wslpath -w "$absolute")" || true
	echo "Abierto en el navegador de Windows con explorer.exe: $absolute"
	exit 0
fi
if command -v xdg-open >/dev/null 2>&1 && open_with xdg-open xdg-open "$absolute"; then
	exit 0
fi

echo "No hay navegador disponible en este entorno (ni wslview, ni explorer.exe, ni xdg-open)." >&2
echo "Abre a mano esta ruta: file://$absolute" >&2
if [[ -x "$(pwd)/serve-web.sh" ]]; then
	echo "O sirve el proyecto con ./serve-web.sh y navega a la ruta relativa." >&2
fi
exit 1
