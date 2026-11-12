#!/usr/bin/env bash
#
# Sirve este repositorio por HTTP en segundo plano para revisar index.html y la
# documentación de docs/ con sus estilos y sus enlaces resueltos: abiertas como file://
# no cargan. Deja su registro y su pid en .run/.
#
#   ./serve-web.sh          arranca el servidor si no está ya en marcha
#   ./serve-web.sh status   dice si está en marcha y dónde escucha
#   ./serve-web.sh stop     lo para
#
# La raíz es el repositorio: las páginas de docs/ enlazan assets y entradas fuera de su
# carpeta, que solo resuelven desde ahí. El puerto es 8766, y `PORT` lo cambia: hay que
# dar el mismo valor en start, status y stop.
#
# El servidor se reconoce por el puerto en el que escucha y no por el pid que guardó este
# script: si se arrancó a mano con `python3 -m http.server`, también se ve y se para
# desde aquí. Un proceso ajeno en ese puerto no se toca.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$root"

state="$root/.run"
pidfile="$state/web.pid"
logfile="$state/web.log"
port="${PORT:-8766}"
address="http://127.0.0.1:$port"

# listening devuelve el pid que escucha en el puerto, o nada.
listening() {
	local out=""
	if command -v ss >/dev/null 2>&1; then
		out="$(ss -lptnH "sport = :$port" 2>/dev/null | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2 || true)"
	fi
	if [[ -z "$out" ]] && command -v lsof >/dev/null 2>&1; then
		out="$(lsof -ti "tcp:$port" -sTCP:LISTEN 2>/dev/null | head -1 || true)"
	fi
	printf '%s' "$out"
}

# ours dice si el pid es un servidor de ficheros y no otro proceso: el pid de un fichero
# que envejeció puede ser de cualquiera, y matarlo sería el error.
ours() {
	local pid="${1:-}"
	[[ -n "$pid" ]] || return 1
	ps -p "$pid" -o args= 2>/dev/null | grep -q -- '-m http[.]server'
}

# server devuelve el pid del servidor en marcha, lo arrancara quien lo arrancara.
server() {
	local pid
	pid="$(cat "$pidfile" 2>/dev/null || true)"
	if ours "$pid"; then
		printf '%s' "$pid"
		return 0
	fi
	pid="$(listening)"
	if ours "$pid"; then
		printf '%s' "$pid"
	fi
	return 0
}

# busy nombra al proceso que ocupa el puerto sin ser el servidor. No se toca: se dice.
busy() {
	local pid
	pid="$(listening)"
	[[ -n "$pid" ]] || return 1
	echo "El puerto $port lo ocupa otro proceso (pid $pid: $(ps -p "$pid" -o args= 2>/dev/null)): no se toca." >&2
	return 0
}

# failed cuenta por qué no arrancó y retira el pid que ya no vale.
failed() {
	echo "El servidor no arrancó. Registro:" >&2
	cat "$logfile" >&2 2>/dev/null || true
	rm -f "$pidfile"
}

start() {
	local pid
	pid="$(server)"
	if [[ -n "$pid" ]]; then
		echo "El servidor ya está en marcha (pid $pid): $address"
		return
	fi

	busy && return 1

	if ! command -v python3 >/dev/null 2>&1; then
		echo "Falta python3: se usa su servidor HTTP para servir los archivos." >&2
		return 1
	fi

	mkdir -p "$state"
	: >"$logfile"

	nohup python3 -m http.server --bind 127.0.0.1 "$port" >>"$logfile" 2>&1 &
	echo $! >"$pidfile"

	# Se espera a que el puerto atienda y a que lo atienda este servidor: el proceso
	# puede seguir vivo sin haber tomado el puerto, y el puerto puede tomarlo otro.
	for _ in {1..50}; do
		kill -0 "$(cat "$pidfile")" 2>/dev/null || { failed; return 1; }
		ours "$(listening)" && break
		sleep 0.1
	done
	sleep 0.2
	ours "$(listening)" || { failed; return 1; }

	echo "Servidor en marcha (pid $(cat "$pidfile")): $address"
	echo "  Portada:            $address/index.html"
	echo "  Documentación:      $address/docs/index.html"
	echo "Registro: $logfile"
}

stop() {
	local pid
	pid="$(server)"
	if [[ -z "$pid" ]]; then
		rm -f "$pidfile"
		busy && return 1
		echo "El servidor no está en marcha."
		return
	fi

	kill "$pid" 2>/dev/null || true

	# El servidor cierra al recibir la señal: se le da tiempo antes de darlo por colgado.
	for _ in {1..50}; do
		kill -0 "$pid" 2>/dev/null || break
		sleep 0.1
	done
	kill -9 "$pid" 2>/dev/null || true

	rm -f "$pidfile"
	echo "Servidor parado."
}

status() {
	local pid
	pid="$(server)"
	if [[ -n "$pid" ]]; then
		echo "En marcha (pid $pid): $address"
		echo "  Portada:       $address/index.html"
		echo "  Documentación: $address/docs/index.html"
	else
		echo "Parado."
	fi
}

case "${1:-start}" in
start) start ;;
stop) stop ;;
status) status ;;
*)
	echo "Uso: $0 [start|stop|status]" >&2
	exit 2
	;;
esac
