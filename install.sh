#!/usr/bin/env bash
set -euo pipefail

APP_NAME="dragonrepo"
INSTALL_DIR="/opt/dragonrepo"
LAUNCHER="/usr/local/bin/dragonrepo"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Please run with sudo: sudo bash install.sh"
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required."
  exit 1
fi

PY_VERSION="$(python3 - <<'PY'
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}")
PY
)"

python3 - <<'PY'
import sys
if sys.version_info < (3, 12):
    raise SystemExit("Python 3.12+ is required.")
PY

mkdir -p "${INSTALL_DIR}"
find "${INSTALL_DIR}" -mindepth 1 -maxdepth 1 ! -name '.venv' -exec rm -rf {} +
cp -a dragonrepo.py requirements.txt templates modules assets reports "${INSTALL_DIR}/"
python3 -m venv "${INSTALL_DIR}/.venv"
"${INSTALL_DIR}/.venv/bin/pip" install --upgrade pip
"${INSTALL_DIR}/.venv/bin/pip" install -r "${INSTALL_DIR}/requirements.txt"
chmod +x "${INSTALL_DIR}/dragonrepo.py"

cat > "${INSTALL_DIR}/dragonrepo" <<'EOF'
#!/usr/bin/env bash
exec /opt/dragonrepo/.venv/bin/python /opt/dragonrepo/dragonrepo.py "$@"
EOF

chmod +x "${INSTALL_DIR}/dragonrepo"
ln -sf "${INSTALL_DIR}/dragonrepo" "${LAUNCHER}"

echo "Installed ${APP_NAME} with Python ${PY_VERSION}."
echo "Run: dragonrepo"
echo "For live command tracking, add one of these to your shell rc file:"
echo '  eval "$(dragonrepo hook zsh)"'
echo '  eval "$(dragonrepo hook bash)"'
