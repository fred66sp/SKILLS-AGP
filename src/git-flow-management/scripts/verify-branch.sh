#!/usr/bin/env bash
# verify-branch.sh — comprueba ascendencia y contención entre dos referencias Git.
#
# Uso: scripts/verify-branch.sh <ancestro> <descendiente> [remoto]
#
# Sale 0 cuando la contención se verifica, 1 cuando no se cumple y 2 cuando el
# uso o las referencias son inválidos. Es de solo lectura: no crea ramas, no
# prepara archivos y no toca el índice ni las referencias.

set -uo pipefail

prog="$(basename "$0")"
estado_ok="OK"
estado_fallo="FALLO"
estado_error="ERROR DE USO"
ancho=16

fila() {
  printf '%-*s %s\n' "$ancho" "$1" "$2"
}

fila_err() {
  printf '%s: %s\n' "$prog" "$1" >&2
}

uso() {
  cat >&2 <<'FIN'
Uso: verify-branch.sh <ancestro> <descendiente> [remoto]

  <ancestro>      rama o SHA que debe estar contenido (por ejemplo, develop)
  <descendiente>  rama o SHA que debe contenerlo (por ejemplo, main)
  [remoto]        opcional; si se indica, informa de si ambas referencias
                  están publicadas en ese remoto

Códigos de salida: 0 contenido verificado, 1 contenido no verificado,
2 uso o referencias inválidos. El comando no modifica el repositorio.
FIN
}

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  fila_err "hacen falta 2 o 3 argumentos y se han recibido $#."
  uso
  exit 2
fi

ancestro="$1"
descendiente="$2"
remoto="${3:-}"

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  fila_err "el directorio actual no está dentro de un repositorio Git."
  fila_err "Fix: ejecuta el comando desde el árbol de trabajo del repositorio."
  exit 2
fi

resolver() {
  git rev-parse --verify --quiet "${1}^{commit}" 2>/dev/null
}

sha_ancestro="$(resolver "$ancestro")"
if [ -z "$sha_ancestro" ]; then
  fila_err "'$ancestro' no resuelve a ningún commit."
  fila_err "Fix: comprueba el nombre exacto con 'git branch -a -vv' o pasa un SHA completo."
  exit 2
fi

sha_descendiente="$(resolver "$descendiente")"
if [ -z "$sha_descendiente" ]; then
  fila_err "'$descendiente' no resuelve a ningún commit."
  fila_err "Fix: comprueba el nombre exacto con 'git branch -a -vv' o pasa un SHA completo."
  exit 2
fi

if [ -n "$remoto" ]; then
  if ! git remote get-url "$remoto" >/dev/null 2>&1; then
    fila_err "el remoto '$remoto' no está configurado en este repositorio."
    fila_err "Fix: usa uno de 'git remote -v' o ejecuta el comando sin el tercer argumento."
    exit 2
  fi
fi

corto_ancestro="$(git rev-parse --short "$sha_ancestro")"
corto_descendiente="$(git rev-parse --short "$sha_descendiente")"

echo "Verificación de contención · solo lectura"
fila "ancestro:" "$ancestro ($corto_ancestro)"
fila "descendiente:" "$descendiente ($corto_descendiente)"

base="$(git merge-base "$sha_ancestro" "$sha_descendiente" 2>/dev/null)"
if [ "$base" = "$sha_ancestro" ]; then
  fila "ascendencia:" "sí · ancestro común $corto_ancestro"
  contenido=0
else
  fila "ascendencia:" "no · ancestro común ${base:0:7}"
  contenido=1
fi

if [ -n "$remoto" ]; then
  for ref in "$ancestro" "$descendiente"; do
    if git ls-remote --exit-code --heads "$remoto" "$ref" >/dev/null 2>&1; then
      fila "publicada:" "$ref en $remoto"
    else
      fila "no publicada:" "$ref en $remoto"
    fi
  done
else
  fila "remoto:" "no comprobado (sin tercer argumento)"
fi

if [ "$contenido" -eq 0 ]; then
  fila "resultado:" "$estado_ok · '$ancestro' está contenido en '$descendiente'"
  exit 0
fi

fila "resultado:" "$estado_fallo · '$ancestro' NO está contenido en '$descendiente'"
echo "$prog: la condición obligatoria de ascendencia no se cumple." >&2
echo "$prog Fix: integra '$ancestro' en '$descendiente' o revisa si el origen y el destino del plan están invertidos." >&2
exit 1
