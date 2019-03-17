#!/usr/bin/env bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR/../backend" || exit 1

nodemon -e ck -x ../scripts/dev-backend.sh
