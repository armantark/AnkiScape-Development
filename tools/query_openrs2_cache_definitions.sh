#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "usage: $0 <disk.zip|cache-dir> <npc|object> <name-term|--id|--params|--combat-levels> [term|id ...]" >&2
  exit 2
fi

source_path=$1
kind=$2
shift 2
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
java_bin=${JAVA_BIN:-/opt/homebrew/opt/openjdk@25/bin/java}
javac_bin=${JAVAC_BIN:-/opt/homebrew/opt/openjdk@25/bin/javac}
gradle_cache=${GRADLE_CACHE:-$HOME/.gradle/caches/modules-2/files-2.1}

if [[ ! -x "$java_bin" || ! -x "$javac_bin" ]]; then
  echo "Java 25 launcher/compiler not found; set JAVA_BIN and JAVAC_BIN." >&2
  exit 1
fi
if [[ ! -d "$gradle_cache/rs.darkan/core/2.0.5" ]]; then
  echo "Darkan core 2.0.5 is not present under $gradle_cache." >&2
  exit 1
fi

temp_dir=$(mktemp -d "${TMPDIR:-/tmp}/ankiscape-openrs2-defs.XXXXXX")
cleanup() { rm -rf "$temp_dir"; }
trap cleanup EXIT

if [[ "$source_path" == *.zip ]]; then
  unzip -q "$source_path" -d "$temp_dir"
  cache_dir="$temp_dir/cache"
else
  cache_dir=$source_path
fi
if [[ ! -f "$cache_dir/main_file_cache.dat2" ]]; then
  echo "No RuneScape disk cache found at $cache_dir." >&2
  exit 1
fi

classpath=$(find "$gradle_cache" -name '*.jar' -print | paste -sd: -)
"$javac_bin" --release 25 -cp "$classpath" -d "$temp_dir/classes" \
  "$script_dir/OpenRs2CacheDefinitionSearch.java"
exec "$java_bin" --class-path "$temp_dir/classes:$classpath" \
  OpenRs2CacheDefinitionSearch "$cache_dir" "$kind" "$@"
