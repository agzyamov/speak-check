#!/bin/bash

# CEFR Postman Collections Test Runner
# Usage: ./run-tests.sh [environment] [collection]
# Example: ./run-tests.sh local health

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POSTMAN_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
COLLECTIONS_DIR="${POSTMAN_DIR}/collections"
ENVIRONMENTS_DIR="${POSTMAN_DIR}/environments"
REPORTS_DIR="${POSTMAN_DIR}/reports"

# Default values
ENVIRONMENT="${1:-local}"
COLLECTION="${2:-all}"
OUTPUT_FORMAT="${3:-cli,json,html}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Newman is installed
check_newman() {
    if ! command -v newman &> /dev/null; then
        log_error "Newman CLI is not installed. Please install it with: npm install -g newman"
        exit 1
    fi
}

# Create reports directory
create_reports_dir() {
    mkdir -p "${REPORTS_DIR}"
}

# Validate environment file exists
validate_environment() {
    local env_file="${ENVIRONMENTS_DIR}/${ENVIRONMENT}.postman_environment.json"
    if [ ! -f "${env_file}" ]; then
        log_error "Environment file not found: ${env_file}"
        log_info "Available environments:"
        ls "${ENVIRONMENTS_DIR}"/*.postman_environment.json 2>/dev/null | xargs -n1 basename | sed 's/.postman_environment.json//' || echo "No environment files found"
        exit 1
    fi
    log_info "Using environment: ${ENVIRONMENT}"
}

# Run a single collection
run_collection() {
    local collection_name="$1"
    local collection_file="${COLLECTIONS_DIR}/${collection_name}.postman_collection.json"
    local env_file="${ENVIRONMENTS_DIR}/${ENVIRONMENT}.postman_environment.json"
    
    if [ ! -f "${collection_file}" ]; then
        log_warning "Collection file not found: ${collection_file}"
        return 1
    fi
    
    log_info "Running collection: ${collection_name}"
    
    # Prepare Newman command
    local newman_cmd="newman run \"${collection_file}\""
    newman_cmd+=" --environment \"${env_file}\""
    newman_cmd+=" --reporters ${OUTPUT_FORMAT}"
    
    # Add report file outputs
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local report_prefix="${REPORTS_DIR}/${collection_name}_${ENVIRONMENT}_${timestamp}"
    
    if [[ "$OUTPUT_FORMAT" == *"json"* ]]; then
        newman_cmd+=" --reporter-json-export \"${report_prefix}.json\""
    fi
    
    if [[ "$OUTPUT_FORMAT" == *"html"* ]]; then
        newman_cmd+=" --reporter-html-export \"${report_prefix}.html\""
    fi
    
    # Execute Newman command
    if eval "$newman_cmd"; then
        log_success "Collection '${collection_name}' completed successfully"
        return 0
    else
        log_error "Collection '${collection_name}' failed"
        return 1
    fi
}

# Run all collections
run_all_collections() {
    log_info "Running all collections..."
    
    local collections=(
        "health-monitoring"
        "external-apis"
        "database-operations"
        "development-testing"
    )
    
    local failed_collections=()
    local successful_collections=()
    
    for collection in "${collections[@]}"; do
        if run_collection "$collection"; then
            successful_collections+=("$collection")
        else
            failed_collections+=("$collection")
        fi
        echo "----------------------------------------"
    done
    
    # Summary
    echo ""
    log_info "Test Run Summary:"
    log_success "Successful collections: ${#successful_collections[@]}"
    for collection in "${successful_collections[@]}"; do
        echo "  ✓ $collection"
    done
    
    if [ ${#failed_collections[@]} -gt 0 ]; then
        log_error "Failed collections: ${#failed_collections[@]}"
        for collection in "${failed_collections[@]}"; do
            echo "  ✗ $collection"
        done
        return 1
    else
        log_success "All collections passed!"
        return 0
    fi
}

# Show usage information
show_usage() {
    echo "CEFR Postman Collections Test Runner"
    echo ""
    echo "Usage: $0 [environment] [collection] [output_format]"
    echo ""
    echo "Arguments:"
    echo "  environment    Environment to use (default: local)"
    echo "                 Options: local, docker, k8s"
    echo ""
    echo "  collection     Collection to run (default: all)"
    echo "                 Options: all, health-monitoring, external-apis,"
    echo "                         database-operations, development-testing"
    echo ""
    echo "  output_format  Output format (default: cli,json,html)"
    echo "                 Options: cli, json, html, junit"
    echo ""
    echo "Examples:"
    echo "  $0                           # Run all collections with local environment"
    echo "  $0 docker                   # Run all collections with docker environment"
    echo "  $0 local health-monitoring  # Run health-monitoring with local environment"
    echo "  $0 k8s all json             # Run all collections with k8s environment, JSON output only"
}

# Main execution
main() {
    # Show help if requested
    if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
        show_usage
        exit 0
    fi
    
    log_info "Starting CEFR Postman Collections Test Runner"
    log_info "Environment: ${ENVIRONMENT}"
    log_info "Collection: ${COLLECTION}"
    log_info "Output Format: ${OUTPUT_FORMAT}"
    echo ""
    
    # Validate prerequisites
    check_newman
    create_reports_dir
    validate_environment
    
    # Run tests
    if [ "$COLLECTION" == "all" ]; then
        if run_all_collections; then
            log_success "All tests completed successfully!"
            exit 0
        else
            log_error "Some tests failed!"
            exit 1
        fi
    else
        if run_collection "$COLLECTION"; then
            log_success "Test completed successfully!"
            exit 0
        else
            log_error "Test failed!"
            exit 1
        fi
    fi
}

# Execute main function
main "$@"