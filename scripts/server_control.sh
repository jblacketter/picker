#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/dev_server.log"
PYTHON_BIN="${PYTHON_BIN:-python3}"
MANAGE_CMD="manage.py runserver 0.0.0.0:8000"

function usage() {
    cat <<USAGE
Usage: $(basename "$0") [restart|rebuild]

Commands:
  restart   Stop the Django dev server (if running) and start a fresh instance.
  rebuild   Recreate the virtual environment, install requirements, then restart the server.

If no command is provided, you'll be prompted to choose.
USAGE
}

function ensure_log_dir() {
    mkdir -p "$LOG_DIR"
}

function ensure_venv() {
    if [[ ! -d "$VENV_PATH" ]]; then
        echo "[INFO] No virtual environment detected. Creating one at $VENV_PATH"
        "$PYTHON_BIN" -m venv "$VENV_PATH"
    fi
}

function activate_venv() {
    # shellcheck disable=SC1091
    source "$VENV_PATH/bin/activate"
}

function stop_server() {
    if pgrep -f "manage.py runserver" >/dev/null 2>&1; then
        echo "[INFO] Stopping existing Django development server..."
        pkill -f "manage.py runserver" || true
    else
        echo "[INFO] No running Django development server found."
    fi
}

function start_server() {
    ensure_log_dir
    ensure_venv
    activate_venv

    echo "[INFO] Starting Django development server..."
    cd "$PROJECT_ROOT"
    nohup python manage.py runserver 0.0.0.0:8000 > "$LOG_FILE" 2>&1 &
    SERVER_PID=$!
    echo "[INFO] Server started (PID $SERVER_PID). Logs: $LOG_FILE"
}

function rebuild_environment() {
    echo "[INFO] Rebuilding virtual environment..."
    rm -rf "$VENV_PATH"
    "$PYTHON_BIN" -m venv "$VENV_PATH"
    activate_venv
    echo "[INFO] Upgrading pip..."
    pip install --upgrade pip
    echo "[INFO] Installing project requirements..."
    pip install -r "$PROJECT_ROOT/requirements.txt"
    if [[ -f "$PROJECT_ROOT/requirements-dev.txt" ]]; then
        pip install -r "$PROJECT_ROOT/requirements-dev.txt"
    fi
}

function prompt_choice() {
    echo "Choose an action:"
    select choice in "restart" "rebuild" "quit"; do
        case $choice in
            restart) ACTION="restart"; break ;;
            rebuild) ACTION="rebuild"; break ;;
            quit) exit 0 ;;
            *) echo "Invalid selection" ;;
        esac
    done
}

ACTION="${1:-}"

if [[ -z "$ACTION" ]]; then
    prompt_choice
fi

case "$ACTION" in
    restart)
        stop_server
        start_server
        ;;
    rebuild)
        stop_server
        rebuild_environment
        start_server
        ;;
    -h|--help|help)
        usage
        ;;
    *)
        echo "[ERROR] Unknown command: $ACTION" >&2
        usage
        exit 1
        ;;
esac
