#!/bin/bash
# Enhanced debugging script with automated log analysis

echo " Starting Enhanced Debug Session with Automated Log Analysis"
echo "=============================================================="
echo ""

# Function to run log analysis
run_analysis() {
    echo " Running automated log analysis..."
    python debug_helpers/analyze_logs.py
    
    if [ $? -eq 0 ]; then
        echo " No errors found in logs"
    else
        echo "  Errors detected - check report above"
    fi
    echo ""
}

# Function to check servers
check_servers() {
    echo " Checking server status..."
    
    # Check if servers are running
    if lsof -i :5173 > /dev/null 2>&1; then
        echo " Frontend server is running on port 5173"
    else
        echo " Frontend server is NOT running"
        echo "   Run: npm run dev"
    fi
    
    if lsof -i :3001 > /dev/null 2>&1; then
        echo " API server is running on port 3001"
    else
        echo " API server is NOT running"
        echo "   Run: npm run dev:api"
    fi
    
    echo ""
}

# Function to clear old logs
clear_old_logs() {
    echo " Clearing old debug artifacts..."
    
    # Remove old debug screenshots
    find . -name "debug*.png" -mtime +1 -delete 2>/dev/null
    
    # Remove old analysis reports
    find debug_helpers -name "log_analysis_*.txt" -mtime +7 -delete 2>/dev/null
    find debug_helpers -name "log_analysis_*.json" -mtime +7 -delete 2>/dev/null
    find debug_helpers -name "log_analysis_*.html" -mtime +7 -delete 2>/dev/null
    
    echo " Cleaned up old debug files"
    echo ""
}

# Main workflow
main() {
    # Parse arguments
    case "$1" in
        "--clean")
            clear_old_logs
            ;;
        "--check")
            check_servers
            run_analysis
            ;;
        "--analyze")
            run_analysis
            ;;
        "--help")
            echo "Usage: ./debug_with_analysis.sh [option]"
            echo ""
            echo "Options:"
            echo "  --check    Check servers and run analysis (default)"
            echo "  --analyze  Run log analysis only"
            echo "  --clean    Clean old debug artifacts"
            echo "  --help     Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./debug_with_analysis.sh          # Full check"
            echo "  ./debug_with_analysis.sh --analyze # Just analyze logs"
            ;;
        *)
            # Default: full check
            check_servers
            run_analysis
            
            echo " Next Steps:"
            echo "1. Review the analysis report above"
            echo "2. Address any critical findings first"
            echo "3. Run your debug script with integrated analysis:"
            echo "   node debug_helpers/example_debug_with_log_analysis.js"
            echo ""
            echo " For detailed guidance, see:"
            echo "   debug_helpers/LOG_ANALYSIS_GUIDE.md"
            ;;
    esac
}

# Run main function
main "$@"