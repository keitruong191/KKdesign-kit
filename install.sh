#!/bin/sh
# Install KKdesign-kit from a pinned portable release; no checkout or Git required.
set -eu

VERSION=0.5.0a1
IDENTIFIER=kkdesign-kit
REPOSITORY=keitruong191/KKdesign-kit

usage() {
  cat <<'EOF'
Usage: install.sh --harness codex|claude-code [--scope project|user] [--project PATH]

Installs the pinned KKdesign-kit release. Project scope defaults to the current
working directory; user scope ignores --project. No prompts are read from stdin.
EOF
}
fail() { printf 'install.sh: %s\n' "$*" >&2; exit 1; }

harness=
scope=project
project=$PWD
while [ "$#" -gt 0 ]; do
  case "$1" in
    --harness|--scope|--project)
      [ "$#" -ge 2 ] || fail "missing value for $1"
      key=$1; value=$2; shift 2
      case "$key" in
        --harness) harness=$value ;;
        --scope) scope=$value ;;
        --project) project=$value ;;
      esac
      ;;
    -h|--help) usage; exit 0 ;;
    *) fail "unknown option: $1 (use --help)" ;;
  esac
done
case "$harness" in codex|claude-code) ;; *) fail 'specify --harness codex or claude-code' ;; esac
case "$scope" in project|user) ;; *) fail '--scope must be project or user' ;; esac

command -v python3 >/dev/null 2>&1 || fail 'python3 3.9 or newer is required; install Python 3 and retry (the python command is not used).'
command -v curl >/dev/null 2>&1 || fail 'curl is required; install curl and retry.'
python3 -I -B -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)' >/dev/null 2>&1 || fail 'Python 3.9 or newer is required; upgrade python3 and retry.'
python3 -I -B -c 'import venv, ensurepip' >/dev/null 2>&1 || fail 'python3 needs its venv and ensurepip components; install the matching Python venv package and retry (no sudo or system changes are performed).'
case "$(uname -s 2>/dev/null || printf unknown)" in
  Darwin|Linux) ;;
  *) fail 'supported operating systems are macOS and Linux.' ;;
esac

# The only alternate transport is for maintainers testing real downloads against
# a loopback fixture; arbitrary hosts and non-HTTP schemes are deliberately rejected.
if [ "${KKDESIGN_BOOTSTRAP_TEST_BASE_URL+x}" = x ]; then
  base=$KKDESIGN_BOOTSTRAP_TEST_BASE_URL
  case "$base" in
    http://127.0.0.1) ;;
    http://127.0.0.1:*)
      port=${base#http://127.0.0.1:}
      case "$port" in
        ''|*[!0-9]*) fail 'KKDESIGN_BOOTSTRAP_TEST_BASE_URL must be an http:// loopback URL with a numeric port.' ;;
      esac
      ;;
    *) fail 'KKDESIGN_BOOTSTRAP_TEST_BASE_URL must be an http:// loopback URL.' ;;
  esac
else
  base="https://github.com/$REPOSITORY/releases/download/v$VERSION"
fi

if [ "$scope" = project ]; then
  case "$project" in /*) ;; *) project="$PWD/$project" ;; esac
  [ -d "$project" ] && [ -w "$project" ] || fail "project destination is not an existing writable directory: $project"
else
  [ -d "${HOME:-}" ] && [ -w "$HOME" ] || fail 'user destination is not an existing writable home directory.'
fi

# The release checksum detects corruption; it is not a publisher signature.
work=$(mktemp -d "${TMPDIR:-/tmp}/kkdesign-install.XXXXXX") || fail 'cannot create temporary download directory.'
trap 'rm -rf "$work"' EXIT HUP INT TERM
# macOS commonly exposes TMPDIR through /var -> /private/var. Resolve only our
# disposable download directory; destination symlink refusal remains unchanged.
work=$(CDPATH= cd "$work" && pwd -P) || fail 'cannot resolve temporary download directory.'
archive=$work/$IDENTIFIER-$VERSION.zip
checksum=$archive.sha256
curl --fail --location --silent --show-error "$base/$IDENTIFIER-$VERSION.zip" -o "$archive" || fail 'release archive download failed.'
curl --fail --location --silent --show-error "$base/$IDENTIFIER-$VERSION.zip.sha256" -o "$checksum" || fail 'release checksum download failed.'
python3 -I -B - "$archive" "$checksum" <<'PY'
import hashlib, pathlib, re, sys
archive, checksum = map(pathlib.Path, sys.argv[1:])
text = checksum.read_text(encoding='ascii').strip()
match = re.fullmatch(r'([0-9a-fA-F]{64})[ \t]+(?:\\)?(?:[ *])?kkdesign-kit-0\.5\.0a1\.zip', text)
if not match:
    raise SystemExit('install.sh: malformed release SHA-256 checksum file.')
actual = hashlib.sha256(archive.read_bytes()).hexdigest()
if actual.lower() != match.group(1).lower():
    raise SystemExit('install.sh: release archive SHA-256 mismatch; refusing extraction.')
PY
# Validate the archive before extraction: only regular files under the expected root.
python3 -I -B - "$archive" "$work/extracted" <<'PY'
import pathlib, stat, sys, zipfile
archive, destination = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
with zipfile.ZipFile(archive) as z:
    for entry in z.infolist():
        path = pathlib.PurePosixPath(entry.filename)
        mode = entry.external_attr >> 16
        kind = stat.S_IFMT(mode)
        if (path.is_absolute() or not path.parts or path.parts[0] != 'kkdesign-kit'
                or '..' in path.parts or kind not in (0, stat.S_IFREG, stat.S_IFDIR)):
            raise SystemExit('install.sh: unsafe entry in release archive: ' + entry.filename)
    z.extractall(destination)
PY
source=$work/extracted/$IDENTIFIER
[ -d "$source/scripts" ] || fail 'release archive has an unexpected layout.'
set -- install --harness "$harness" --scope "$scope" --project "$project" --source "$source" --runtime
if [ "$scope" = user ]; then
  set -- "$@" --home "${HOME:?HOME must be set for user scope}"
fi
python3 -I -B "$source/scripts/kkdesign_install.py" "$@"
installed=$project/.agents/skills/$IDENTIFIER
if [ "$harness" = claude-code ]; then
  installed=$project/.claude/skills/$IDENTIFIER
fi
if [ "$scope" = user ]; then
  if [ "$harness" = codex ]; then installed=${HOME:?HOME must be set for user scope}/.agents/skills/$IDENTIFIER
  else installed=${HOME:?HOME must be set for user scope}/.claude/skills/$IDENTIFIER
  fi
fi
python3 -I -B "$installed/scripts/kkdesign_install.py" inspect --harness "$harness" --scope "$scope" --project "$project" --home "${HOME:?HOME must be set}"
python3 -B "$installed/scripts/kkdesign_run.py" materialize_example --output "$work/bootstrap-example"
python3 -B "$installed/scripts/kkdesign_run.py" kkdesign_core validate --design "$work/bootstrap-example/design" >/dev/null
printf '\nKKdesign-kit installed and helpers verified: %s\n' "$installed"
printf 'Runtime is managed outside the skill tree; no activation is needed.\n'
printf 'Helper launcher: python3 -B "%s/scripts/kkdesign_run.py" HELPER [arguments]\n' "$installed"
if [ "$harness" = codex ]; then
  printf 'Restart Codex in the destination project, then invoke $kkdesign-kit for the menu.\n'
else
  printf 'Restart Claude Code in the destination project, then invoke /kkdesign-kit for the menu.\n'
fi
printf 'File installation and helper smoke do not prove harness discovery or live design-tool access.\n'
