#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
skills_root="$repo_root/skills"
target_root="${CODEX_SKILLS_DIR:-${CODEX_HOME:-$HOME/.codex}/skills}"

install_one() {
  local skill_name="$1"
  local source_dir="$skills_root/$skill_name"
  local target_dir="$target_root/$skill_name"

  if [[ ! -f "$source_dir/SKILL.md" ]]; then
    echo "Skill not found: $skill_name" >&2
    exit 1
  fi

  mkdir -p "$target_root"
  rm -rf "$target_dir"
  cp -R "$source_dir" "$target_dir"
  echo "Installed $skill_name -> $target_dir"
}

if [[ $# -gt 0 ]]; then
  for skill_name in "$@"; do
    install_one "$skill_name"
  done
else
  while IFS= read -r skill_dir; do
    install_one "$(basename "$skill_dir")"
  done < <(find "$skills_root" -mindepth 1 -maxdepth 1 -type d | sort)
fi
