#!/bin/bash
# ============================================================================
# Step 1: Generate .in files (gprMax input files)
# ============================================================================
# This script generates synthetic GPR input files with varying ballast 
# fouling levels using the balanced dataset generator.
#
# Usage:
#   ./1_generate_inputs.sh [options]
#
# Options:
#   -n, --num-samples N    Number of samples per class (default: 2)
#   -o, --output DIR       Output directory (default: output/generated)
#   -h, --help             Show this help message
# ============================================================================

set -e

# Default configuration
NUM_SAMPLES=2
OUTPUT_DIR="output/generated"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

show_usage() {
    grep "^#" "$0" | grep -v "#!/bin/bash" | sed 's/^# //' | sed 's/^#//'
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--num-samples)
            NUM_SAMPLES="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
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

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE} Generating .in files${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Configuration:"
echo "  Samples per class: $NUM_SAMPLES"
echo "  Output directory:  $OUTPUT_DIR"
echo ""

# Run generator
python generate_balanced_dataset.py \
    --count "$NUM_SAMPLES" \
    --output "$OUTPUT_DIR"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Generation complete!${NC}"
    
    # Find the latest timestamped directory
    LATEST_DIR=$(find "$OUTPUT_DIR" -maxdepth 1 -type d -name "20*" | sort -r | head -1)
    
    if [ -n "$LATEST_DIR" ]; then
        IN_COUNT=$(find "$LATEST_DIR" -name "*.in" | wc -l)
        echo -e "${BLUE}ℹ️  Created $IN_COUNT .in files in: $LATEST_DIR${NC}"
        echo ""
        echo "Next step:"
        echo "  ./2_run_gprmax.sh -i \"$LATEST_DIR\""
    fi
else
    echo -e "${RED}❌ Generation failed${NC}"
    exit 1
fi
