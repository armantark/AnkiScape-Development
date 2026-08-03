#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $0 <disk.zip|cache-dir> <count|dump|find> [interface-id [component-id ...]|needle]" >&2
  exit 2
fi

source_path=$1
shift
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
java_bin=${JAVA_BIN:-/opt/homebrew/opt/openjdk@25/bin/java}
gradle_cache=${GRADLE_CACHE:-$HOME/.gradle/caches/modules-2/files-2.1}

if [[ ! -x "$java_bin" ]]; then
  echo "Java 25 launcher not found at $java_bin; set JAVA_BIN." >&2
  exit 1
fi
if [[ ! -d "$gradle_cache/rs.darkan/core/2.0.5" ]]; then
  echo "Darkan core 2.0.5 is not present under $gradle_cache." >&2
  exit 1
fi

temp_dir=
cleanup() {
  if [[ -n "$temp_dir" ]]; then
    rm -rf "$temp_dir"
  fi
}
trap cleanup EXIT

if [[ "$source_path" == *.zip ]]; then
  temp_dir=$(mktemp -d "${TMPDIR:-/tmp}/ankiscape-openrs2-interfaces.XXXXXX")
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
exec "$java_bin" --class-path "$classpath" \
  "$script_dir/OpenRs2InterfaceQuery.java" "$cache_dir" "$@"
