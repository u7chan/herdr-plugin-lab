#!/usr/bin/env bash
set -euo pipefail

herdr_bin="${HERDR_BIN_PATH:-herdr}"

"$herdr_bin" plugin pane open \
  --plugin "${HERDR_PLUGIN_ID:-dev.u7chan.plugin-lab.hello}" \
  --entrypoint welcome
