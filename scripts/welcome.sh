#!/usr/bin/env bash
set -euo pipefail

# ANSI colors are used intentionally: plugin panes are terminal-based UI.
green=$'\033[1;32m'
yellow=$'\033[1;33m'
dim=$'\033[2m'
reset=$'\033[0m'

clear
printf '\n\n'
printf '          %s🎉  Herdr Plugin Lab  🎉%s\n' "$yellow" "$reset"
printf '\n'
printf '        %s✓ プラグインが動きました！%s\n' "$green" "$reset"
printf '\n'
printf '        🐑  Hello from Herdr\n'
printf '\n'
printf '        %s何かキーを押すと閉じます%s\n' "$dim" "$reset"

IFS= read -rsn 1 _ || true
