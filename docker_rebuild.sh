#! /bin/bash -u

IDIR="${BASH_SOURCE%/*}"
if [[ ! -d "$IDIR" ]]; then IDIR="$PWD"; fi

cd "$IDIR"

docker compose down
docker compose up --build --force-recreate --no-deps -d
