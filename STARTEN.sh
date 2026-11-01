#!/usr/bin/env bash
set -Eeuo pipefail
cd -- "$(dirname -- "$0")"
export PYTHONPATH="$PWD"
if ! command -v python3 >/dev/null 2>&1; then
  printf 'Python 3 fehlt. Bitte über die Paketverwaltung installieren.\n' >&2
  exit 2
fi
if ! python3 -c 'import sys;assert sys.version_info>=(3,11)' 2>/dev/null; then
  printf 'Python mindestens 3.11 notwendig.\n' >&2
  exit 2
fi
exec python3 -m videozoom "$@"
