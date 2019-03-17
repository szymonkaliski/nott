#!/usr/bin/env bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR/.." || exit 1

nodemon -e sh,py,ck -x ./scripts/dev-sync.sh
