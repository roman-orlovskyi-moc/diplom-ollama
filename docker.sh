#!/bin/bash
# Helper script for Docker operations

set -e

PROJECT_NAME="thesis"
COMPOSE_FILE="docker-compose.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Commands
cmd_start() {
    print_info "Starting services..."
    docker compose up -d
    print_success "Services started"
    print_info "Waiting for Ollama to be ready..."
    sleep 10
    cmd_status
}

cmd_stop() {
    print_info "Stopping services..."
    docker compose down
    print_success "Services stopped"
}

cmd_restart() {
    cmd_stop
    cmd_start
}

cmd_status() {
    echo ""
    echo "=== Service Status ==="
    docker compose ps
    echo ""
}

cmd_logs() {
    SERVICE=${1:-}
    if [ -z "$SERVICE" ]; then
        docker compose logs -f
    else
        docker compose logs -f "$SERVICE"
    fi
}

cmd_shell() {
    print_info "Opening shell in app container..."
    docker compose exec app bash
}

cmd_setup() {
    print_info "Setting up project..."

    # Check if services are running
    if ! docker compose ps | grep -q "thesis-ollama.*running"; then
        print_error "Services not running. Starting them first..."
        cmd_start
    fi

    # Pull Ollama model
    print_info "Pulling Ollama model (this may take a few minutes)..."
    docker compose exec ollama ollama pull llama3.2

    # Setup database
    print_info "Setting up database..."
    docker compose exec app python scripts/setup_db.py

    print_success "Setup complete!"
}

cmd_test() {
    print_info "Running setup verification..."
    docker compose exec app python scripts/test_setup.py
}

cmd_demo() {
    print_info "Running simple demo..."
    docker compose exec app python scripts/run_simple_test.py
}

cmd_experiment() {
    print_info "Running full experiments..."
    docker compose exec app python scripts/run_experiments.py
}

cmd_report() {
    print_info "Generating thesis report..."
    docker compose exec app python scripts/generate_report.py
    print_success "Report generated in data/exports/"
}

cmd_build() {
    print_info "Building containers..."
    docker compose build --no-cache
    print_success "Build complete"
}

cmd_clean() {
    print_info "Cleaning up..."

    read -p "This will remove all containers and data. Continue? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker compose down -v
        rm -rf data/results/*.db data/exports/* logs/*.log
        print_success "Cleanup complete"
    else
        print_info "Cleanup cancelled"
    fi
}

cmd_results() {
    print_info "Test results:"
    echo ""
    ls -lh data/results/ 2>/dev/null || echo "No results yet"
    echo ""
    print_info "Exports:"
    echo ""
    ls -lh data/exports/ 2>/dev/null || echo "No exports yet"
    echo ""
}

cmd_help() {
    cat << EOF
Thesis Project Docker Helper

Usage: ./docker.sh <command>

Commands:
    start           Start all services
    stop            Stop all services
    restart         Restart all services
    status          Show service status
    logs [service]  Show logs (optionally for specific service)
    shell           Open bash shell in app container

Setup & Testing:
    setup           Initial setup (pull model, setup DB)
    test            Run setup verification tests
    demo            Run simple demo (1 attack, 3 defenses)
    experiment      Run full experiments (all attacks)
    report          Generate thesis report

Utilities:
    build           Rebuild containers
    clean           Remove all containers and data
    results         Show current results
    help            Show this help message

Examples:
    ./docker.sh start           # Start services
    ./docker.sh setup           # First-time setup
    ./docker.sh demo            # Quick demo
    ./docker.sh experiment      # Full experiments
    ./docker.sh logs ollama     # View Ollama logs
    ./docker.sh shell           # Interactive shell

For more details, see DOCKER_GUIDE.md
EOF
}

# Main
case "${1:-help}" in
    start)
        cmd_start
        ;;
    stop)
        cmd_stop
        ;;
    restart)
        cmd_restart
        ;;
    status)
        cmd_status
        ;;
    logs)
        cmd_logs "${2:-}"
        ;;
    shell)
        cmd_shell
        ;;
    setup)
        cmd_setup
        ;;
    test)
        cmd_test
        ;;
    demo)
        cmd_demo
        ;;
    experiment)
        cmd_experiment
        ;;
    report)
        cmd_report
        ;;
    build)
        cmd_build
        ;;
    clean)
        cmd_clean
        ;;
    results)
        cmd_results
        ;;
    help|--help|-h)
        cmd_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        cmd_help
        exit 1
        ;;
esac