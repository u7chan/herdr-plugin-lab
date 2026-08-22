#!/usr/bin/env bash
set -euo pipefail

herdr_bin="${HERDR_BIN_PATH:-herdr}"

cat <<EOF
Hello from ${HERDR_PLUGIN_ID:-unknown-plugin}!

plugin root:  ${HERDR_PLUGIN_ROOT:-<unset>}
config dir:   ${HERDR_PLUGIN_CONFIG_DIR:-<unset>}
state dir:    ${HERDR_PLUGIN_STATE_DIR:-<unset>}
workspace id: ${HERDR_WORKSPACE_ID:-<unset>}
action id:    ${HERDR_PLUGIN_ACTION_ID:-<unset>}
context:      ${HERDR_PLUGIN_CONTEXT_JSON:-<unset>}
herdr:        $("$herdr_bin" --version)
EOF
