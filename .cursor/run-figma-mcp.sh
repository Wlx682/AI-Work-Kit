#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
set -a
# shellcheck source=/dev/null
source "$DIR/figma.env"
set +a
exec npx -y figma-developer-mcp --stdio
