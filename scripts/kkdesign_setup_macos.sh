#!/bin/sh
# Internal marketplace Setup only. Invoked by the agent after reading setup.md.
set -eu
umask 077
LC_ALL=C
export LC_ALL
unset PYTHONHOME PYTHONPATH PERL5OPT PERL5LIB TAR_OPTIONS GZIP \
    DYLD_LIBRARY_PATH DYLD_INSERT_LIBRARIES

fail() {
    printf '%s\n' "$*" >&2
    printf '%s\n' '{"plugin":"loaded","runtime":"error","externalTools":"unverified","status":"error","phase":"failed"}'
    exit 1
}
package=
consent=
while [ "$#" -gt 0 ]; do
    case "$1" in
        --package-root) [ "$#" -ge 2 ] || fail 'Missing package root'; package=$2; shift 2 ;;
        --consent) consent=--consent; shift ;;
        *) fail 'Unknown Setup argument' ;;
    esac
done
case "$package" in /*) ;; *) fail 'An explicit absolute package root is required' ;; esac
[ -f "$package/SKILL.md" ] && [ -f "$package/scripts/kkdesign_setup.py" ] || fail 'Invalid package root'
[ "$(/usr/bin/uname -s)" = Darwin ] || fail 'This internal Setup entrypoint requires macOS'
case "$(/usr/bin/uname -m)" in
    arm64) target=aarch64; digest=6ceba34fe78802853a30bde6f303a0a54f71f6ab07a673da34e90c0aa06c786e ;;
    x86_64) target=x86_64; digest=9b8589eefb153cbe7cb652993d0ecc94aeb2fa13c1a2e8bc240f5f74f23bb21b ;;
    *) fail 'No pinned Python artifact for this macOS architecture' ;;
esac
# No project metadata, PATH Python or author-checkout paths enter this decision.
case "$HOME" in /*) ;; *) fail 'User home must be absolute' ;; esac
uid=$(/usr/bin/id -u)
private_path() {
    path=$1
    while [ "$path" != / ]; do
        [ ! -L "$path" ] || fail 'Symlink in user cache ancestry; preserve and inspect it'
        if [ -e "$path" ] && [ "$path" != "$HOME" ] && [ "${path#"$HOME"/}" != "$path" ]; then
            [ "$(/usr/bin/stat -f %u "$path")" = "$uid" ] || fail 'User cache has another owner'
            [ -z "$(/usr/bin/find "$path" -prune -perm +022 -print)" ] || fail 'User cache is writable by another account'
        fi
        path=$(/usr/bin/dirname "$path")
    done
}
base=$HOME/.kkdesign-kit
root=$base/bootstrap
cache=$root/cpython-3.12.12-20251014-$target
private_path "$cache"
[ "$(/usr/bin/stat -f %u "$HOME")" = "$uid" ] || fail 'User home has another owner'
[ -z "$(/usr/bin/find "$HOME" -prune -perm +022 -print)" ] || fail 'User home is writable by another account'
if [ ! -e "$cache" ] && [ -z "$consent" ]; then
    printf 'Setup needs pinned CPython 3.12.12 (Astral python-build-standalone release 20251014) from GitHub HTTPS and requirements.txt dependencies from the package index. Storage: %s and %s/runtimes. Network, private user-cache writes and local execution are required; no admin, system Python or shell changes. Obtain explicit consent before --consent.\n' "$cache" "$base" >&2
    printf '%s\n' '{"plugin":"loaded","runtime":"setup-required","externalTools":"unverified","status":"consent-required","phase":"consent-required"}'
    exit 0
fi
/bin/mkdir -p "$root" || fail 'Cache write denied; use authorized user storage, never sudo'
private_path "$root"
/bin/mkdir "$root/lock" 2>/dev/null || fail 'Bootstrap busy or interrupted; inspect the retained lock before recovery'
stage=
cleanup() {
    [ -z "$stage" ] || /bin/rm -rf "$stage"
    /bin/rm -f "$root/lock/current"
    /bin/rmdir "$root/lock"
}
trap cleanup EXIT
trap 'exit 1' HUP INT TERM
# The receipt covers all regular files, symlink targets and directories. A new
# file or changed library is rejected before even starting the cached Python.
inventory() {
    /usr/bin/find -s python -type d -print || return 1
    /usr/bin/find -s python -type f -exec /usr/bin/shasum -a 256 {} + || return 1
    /usr/bin/find -s python -type l -exec /bin/sh -c '
        for link do
            printf "%s -> " "$link"
            /usr/bin/readlink "$link" || exit 1
        done
    ' sh {} + || return 1
}
verify_cache() {
    [ -d "$cache" ] && [ ! -L "$cache" ] || fail 'Incomplete bootstrap cache; preserve and inspect it'
    [ -z "$(/usr/bin/find "$cache" ! -user "$uid" -print)" ] || fail 'Bootstrap cache has another owner'
    [ -z "$(/usr/bin/find "$cache" ! -type l -perm +022 -print)" ] || fail 'Bootstrap cache is writable by another account'
    [ -z "$(/usr/bin/find "$cache" ! -type d ! -type f ! -type l -print)" ] || fail 'Unexpected cache file type'
    for entry in archive.tar.gz inventory.sha256 python; do
        [ ! -L "$cache/$entry" ] || fail 'Symlinked bootstrap metadata'
    done
    actual=$(/usr/bin/shasum -a 256 "$cache/archive.tar.gz") || fail 'Unreadable cached artifact'
    [ "${actual%% *}" = "$digest" ] || fail 'Cached artifact checksum mismatch; preserve and inspect it'
    (cd "$cache" && inventory) > "$root/lock/current" || fail 'Cannot verify cached Python tree'
    /usr/bin/cmp -s "$root/lock/current" "$cache/inventory.sha256" || fail 'Cached Python tree changed; preserve and inspect it'
    /bin/rm "$root/lock/current"
    [ -x "$cache/python/bin/python3" ] || fail 'Managed bootstrap interpreter is missing'
}
if [ ! -e "$cache" ]; then
    printf '%s\n' '{"phase":"downloading-python","runtime":"setup-required","externalTools":"unverified"}'
    stage=$(/usr/bin/mktemp -d "$root/.preparing.XXXXXXXX") || fail 'Cannot create private staging directory'
    artifact=cpython-3.12.12+20251014-$target-apple-darwin-install_only.tar.gz
    /usr/bin/curl --disable --fail --silent --show-error --location --proto '=https' --proto-redir '=https' \
        --tlsv1.2 --connect-timeout 20 --max-time 240 \
        "https://github.com/astral-sh/python-build-standalone/releases/download/20251014/$artifact" \
        --output "$stage/archive.tar.gz" || fail 'Python download failed; restore approved network access before retrying'
    actual=$(/usr/bin/shasum -a 256 "$stage/archive.tar.gz") || fail 'Cannot hash downloaded artifact'
    [ "${actual%% *}" = "$digest" ] || fail 'Downloaded Python checksum mismatch; nothing was executed'
    # Only the exact reviewed, pinned upstream archive is extracted. BSD tar's
    # traversal protections remain enabled; never use -P or relax host policy.
    /usr/bin/tar -xzf "$stage/archive.tar.gz" -C "$stage" || fail 'Python extraction failed'
    (cd "$stage" && inventory) > "$stage/inventory.sha256" || fail 'Cannot record Python inventory'
    /bin/mv "$stage" "$cache" || fail 'Cannot commit private bootstrap cache'
    stage=
fi
verify_cache
# -I ignores ambient Python configuration, -B prevents plugin/cache bytecode.
# The same canonical Python Setup handles requirements, locks, helper validation
# and its readiness receipt. There is no second installer or dispatcher.
"$cache/python/bin/python3" -I -B "$package/scripts/kkdesign_setup.py" --package-root "$package" ${consent:+--consent}
