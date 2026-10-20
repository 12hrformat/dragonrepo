#!/usr/bin/env bash
set -euo pipefail

# System-wide installer for DRAGON Report Generator.
#
# Installs the dragonrepo package from this source tree into an isolated
# virtual environment under /opt/dragonrepo and exposes the `dragonrepo`
# launcher on PATH via /usr/local/bin/dragonrepo.

APP_NAME="dragonrepo"
INSTALL_DIR="/opt/dragonrepo"
VENV_DIR="${INSTALL_DIR}/.venv"
LAUNCHER="/usr/local/bin/dragonrepo"
MIN_PYTHON="3.9"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Please run with sudo: sudo ./install.sh"
  exit 1
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required."
  exit 1
fi

PY_VERSION="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"

if ! python3 - "$MIN_PYTHON" <<'PY'
import sys
required = tuple(int(part) for part in sys.argv[1].split("."))
raise SystemExit(0 if sys.version_info >= required else 1)
PY
then
  echo "Python ${MIN_PYTHON}+ is required (found ${PY_VERSION})."
  exit 1
fi

echo "Installing ${APP_NAME} with Python ${PY_VERSION}..."

mkdir -p "${INSTALL_DIR}"
find "${INSTALL_DIR}" -mindepth 1 -maxdepth 1 ! -name '.venv' -exec rm -rf {} +

python3 -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/pip" install --upgrade pip >/dev/null
"${VENV_DIR}/bin/pip" install "${SCRIPT_DIR}"

cat > "${INSTALL_DIR}/dragonrepo" <<EOF
#!/usr/bin/env bash
exec "${VENV_DIR}/bin/dragonrepo" "\$@"
EOF
chmod +x "${INSTALL_DIR}/dragonrepo"
ln -sf "${INSTALL_DIR}/dragonrepo" "${LAUNCHER}"

echo "Installed ${APP_NAME} with Python ${PY_VERSION}."
echo "Run: dragonrepo"
echo "For live command tracking, add one of these to your shell rc file:"
echo '  eval "$(dragonrepo hook zsh)"'
echo '  eval "$(dragonrepo hook bash)"'
