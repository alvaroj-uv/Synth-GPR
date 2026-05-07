#!/bin/bash
# ============================================================================
# Step 2: Run gprMax simulations
# ============================================================================
# This script runs gprMax simulations on all .in files in a directory,
# generating .out files with electromagnetic field data.
#
# Usage:
#   ./2_run_gprmax.sh [options]
#
# Options:
#   -i, --input DIR        Input directory containing .in files (required)
#   -p, --parallel N       Number of parallel processes (default: 1)
#   -f, --force            Force re-run even if .out files exist
#   -h, --help             Show this help message
# ============================================================================

set -e

# Default configuration
INPUT_DIR=""
PARALLEL=1
FORCE=false

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_usage() {
    grep "^#" "$0" | grep -v "#!/bin/bash" | sed 's/^# //' | sed 's/^#//'
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--input)
            INPUT_DIR="$2"
            shift 2
            ;;
        -p|--parallel)
            PARALLEL="$2"
            shift 2
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

# Validate input directory
if [ -z "$INPUT_DIR" ]; then
    echo -e "${RED}Error: Input directory is required${NC}"
    show_usage
    exit 1
fi

if [ ! -d "$INPUT_DIR" ]; then
    echo -e "${RED}Error: Directory not found: $INPUT_DIR${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE} Running gprMax simulations${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Configuration:"
echo "  Input directory:    $INPUT_DIR"
echo "  Parallel processes: $PARALLEL"
echo "  Force re-run:       $FORCE"
echo ""

# Count .in files
TOTAL=$(find "$INPUT_DIR" -name "*.in" | wc -l)

if [ "$TOTAL" -eq 0 ]; then
    echo -e "${RED}Error: No .in files found in $INPUT_DIR${NC}"
    exit 1
fi

echo -e "${BLUE}Found $TOTAL .in files${NC}"
echo ""

PROCESSED=0
SKIPPED=0
FAILED=0

# Process each .in file
for in_file in "$INPUT_DIR"/*.in; do
    if [ -f "$in_file" ]; then
        out_file="${in_file%.in}.out"
        basename_file=$(basename "$in_file")
        
        # Skip if .out exists and not forcing
        if [ -f "$out_file" ] && [ "$FORCE" = false ]; then
            echo -e "${YELLOW}⏭️  Skipping $basename_file (output exists)${NC}"
            ((SKIPPED++))
            continue
        fi
        
        echo -n "Processing $basename_file [$((PROCESSED+SKIPPED+FAILED+1))/$TOTAL]... "
        
        # Run gprMax
        if python -m gprMax "$in_file" -n "$PARALLEL" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC}"
            ((PROCESSED++))
        else
            echo -e "${RED}✗${NC}"
            ((FAILED++))
        fi
    fi
done

echo ""
echo -e "${BLUE}========================================${NC}"
echo "Summary:"
echo "  ✅ Processed: $PROCESSED"
echo "  ⏭️  Skipped:   $SKIPPED"
echo "  ❌ Failed:    $FAILED"
echo -e "${BLUE}========================================${NC}"

if [ "$PROCESSED" -gt 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Simulations complete!${NC}"
    echo ""
    echo "Next step:"
    echo "  ./3_extract_features.sh -i \"$INPUT_DIR\""
fi

if [ "$FAILED" -gt 0 ]; then
    exit 1
fi
