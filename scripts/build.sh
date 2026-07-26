#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILDER="$ROOT/.builder/chaquopy"
CHAQUOPY_COMMIT=e01057c72fdd737f202bd1be1de85af51e06cad0
TARGET_VERSION=3.11.14-0
UNICORN_URL=https://files.pythonhosted.org/packages/source/u/unicorn/unicorn-2.1.4.tar.gz
UNICORN_SHA256=00567a70e323f749b419cd86bee4f9115beab7ebba32194581c090cbb7c59cff

: "${ANDROID_HOME:?ANDROID_HOME must point to an Android SDK}"

if [[ ! -d "$BUILDER/.git" ]]; then
  git clone https://github.com/chaquo/chaquopy.git "$BUILDER"
fi
git -C "$BUILDER" fetch --depth 1 origin "$CHAQUOPY_COMMIT"
git -C "$BUILDER" checkout --detach "$CHAQUOPY_COMMIT"

python3.11 -m venv "$BUILDER/server/pypi/env"
"$BUILDER/server/pypi/env/bin/pip" install \
  --requirement "$BUILDER/server/pypi/requirements.txt"

TARGET="$BUILDER/maven/com/chaquo/python/target/$TARGET_VERSION"
if [[ ! -d "$TARGET" ]]; then
  "$BUILDER/target/download-target.sh" "$TARGET"
fi

cd "$BUILDER/server/pypi"
SOURCE_CACHE="$ROOT/recipe/build/2.1.4/unicorn-2.1.4.tar.gz"
mkdir -p "$(dirname "$SOURCE_CACHE")"
curl --fail --location --output "$SOURCE_CACHE" "$UNICORN_URL"
echo "$UNICORN_SHA256  $SOURCE_CACHE" | sha256sum --check --strict
"$BUILDER/server/pypi/env/bin/python" ./build-wheel.py \
  --python 3.11 --abi arm64-v8a "$ROOT/recipe"

mkdir -p "$ROOT/dist"
cp dist/unicorn/*.whl "$ROOT/dist/"
python3.11 "$ROOT/scripts/verify-wheel.py" "$ROOT"/dist/*.whl
(cd "$ROOT/dist" && sha256sum ./*.whl > SHA256SUMS)
