#!/bin/bash

# CEFR Postman Test Data Cleanup Script
# Usage: ./cleanup.sh [environment]

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POSTMAN_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPORTS_DIR="${POSTMAN_DIR}/reports"

# Default values
ENVIRONMENT="${1:-local}"

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

# Clean test reports
clean_reports() {
    log_info "Cleaning test reports..."
    
    if [ -d "${REPORTS_DIR}" ]; then
        local report_count=$(find "${REPORTS_DIR}" -name "*.json" -o -name "*.html" | wc -l)
        
        if [ "$report_count" -gt 0 ]; then
            find "${REPORTS_DIR}" -name "*.json" -delete
            find "${REPORTS_DIR}" -name "*.html" -delete
            log_success "Removed ${report_count} report files"
        else
            log_info "No report files found to clean"
        fi
    else
        log_info "Reports directory does not exist"
    fi
}

# Clean temporary test data from database (via API)
clean_database_test_data() {
    log_info "Cleaning database test data..."
    
    # This would require API endpoints to be implemented
    # For now, just show what would be cleaned
    log_warning "Database cleanup requires API endpoints to be implemented"
    log_info "Test data that should be cleaned:"
    echo "  - Sessions with metadata.test=true"
    echo "  - Recordings with metadata.created_by='postman'"
    echo "  - Transcripts with metadata.created_by='postman'"
    echo "  - Evaluations with metadata.created_by='postman'"
}

# Clean temporary files
clean_temp_files() {
    log_info "Cleaning temporary files..."
    
    # Clean any generated audio files
    local temp_audio_count=0
    if find /tmp -name "sample-test-audio*.wav" 2>/dev/null | grep -q .; then
        temp_audio_count=$(find /tmp -name "sample-test-audio*.wav" | wc -l)
        find /tmp -name "sample-test-audio*.wav" -delete 2>/dev/null || true
    fi
    
    if [ "$temp_audio_count" -gt 0 ]; then
        log_success "Removed ${temp_audio_count} temporary audio files"
    else
        log_info "No temporary audio files found"
    fi
}

# Reset Postman global variables (if using Newman)
reset_postman_globals() {
    log_info "Resetting Postman global variables..."
    
    # This would clear variables like test_session_id, sample_transcription, etc.
    log_info "Global variables that should be reset:"
    echo "  - test_session_id"
    echo "  - test_recording_id"
    echo "  - test_transcript_id"
    echo "  - test_evaluation_id"
    echo "  - sample_transcription"
    echo "  - sample_assessment"
    echo "  - performance_data"
    echo "  - test_summary"
    
    log_warning "Global variable reset requires manual action in Postman or Newman configuration"
}

# Show cleanup summary
show_cleanup_summary() {
    echo ""
    log_info "Cleanup Summary:"
    echo "✓ Test reports cleaned"
    echo "⚠ Database test data (requires API implementation)"
    echo "✓ Temporary files cleaned"
    echo "⚠ Postman global variables (requires manual reset)"
    echo ""
    log_success "Cleanup completed!"
}

# Show usage information
show_usage() {
    echo "CEFR Postman Test Data Cleanup Script"
    echo ""
    echo "Usage: $0 [environment]"
    echo ""
    echo "Arguments:"
    echo "  environment    Environment that was tested (default: local)"
    echo "                 Options: local, docker, k8s"
    echo ""
    echo "This script cleans up:"
    echo "  - Test report files (JSON/HTML)"
    echo "  - Temporary audio files"
    echo "  - Database test data (when API endpoints are available)"
    echo "  - Postman global variables (manual action required)"
    echo ""
    echo "Examples:"
    echo "  $0           # Clean up after local environment tests"
    echo "  $0 docker    # Clean up after docker environment tests"
}

# Main execution
main() {
    # Show help if requested
    if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
        show_usage
        exit 0
    fi
    
    log_info "Starting CEFR Postman Test Data Cleanup"
    log_info "Environment: ${ENVIRONMENT}"
    echo ""
    
    # Confirm cleanup
    read -p "Are you sure you want to clean up test data for environment '${ENVIRONMENT}'? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        clean_reports
        clean_temp_files
        clean_database_test_data
        reset_postman_globals
        show_cleanup_summary
    else
        log_info "Cleanup cancelled"
        exit 0
    fi
}

# Execute main function
main "$@"