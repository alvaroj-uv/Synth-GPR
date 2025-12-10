#!/bin/bash
# ============================================================================
# Step 3: Extract features from .out files
# ============================================================================
# This script extracts signal features from gprMax .out files and creates
# a features.csv file for machine learning.
#
# Usage:
#   ./3_extract_features.sh [options]
#
# Options:
#   -i, --input DIR        Input directory containing .out files (required)
#   -o, --output FILE      Output CSV file (default: <input_dir>/features.csv)
#   -h, --help             Show this help message
# ============================================================================

set -e

# Default configuration
INPUT_DIR=""
OUTPUT_FILE=""

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
        -i|--input)
            INPUT_DIR="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
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

# Set default output file if not specified
if [ -z "$OUTPUT_FILE" ]; then
    OUTPUT_FILE="$INPUT_DIR/features.csv"
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE} Extracting features${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Configuration:"
echo "  Input directory: $INPUT_DIR"
echo "  Output file:     $OUTPUT_FILE"
echo ""

# Check for .out files
OUT_COUNT=$(find "$INPUT_DIR" -name "*.out" | wc -l)

if [ "$OUT_COUNT" -eq 0 ]; then
    echo -e "${RED}Error: No .out files found in $INPUT_DIR${NC}"
    echo "Run gprMax simulations first (./2_run_gprmax.sh)"
    exit 1
fi

echo -e "${BLUE}Found $OUT_COUNT .out files${NC}"
echo ""

# Check for metadata.csv
if [ ! -f "$INPUT_DIR/metadata.csv" ]; then
    echo -e "${RED}Error: metadata.csv not found in $INPUT_DIR${NC}"
    exit 1
fi

# Run feature extraction
python create_feature_dataset.py "$INPUT_DIR"

if [ $? -eq 0 ]; then
    if [ -f "$OUTPUT_FILE" ]; then
        echo ""
        echo -e "${GREEN}✅ Feature extraction complete!${NC}"
        
        # Show statistics
        FEATURE_COUNT=$(head -1 "$OUTPUT_FILE" | tr ',' '\n' | wc -l)
        SAMPLE_COUNT=$(tail -n +2 "$OUTPUT_FILE" | wc -l)
        
        echo ""
        echo "Statistics:"
        echo "  Features:  $FEATURE_COUNT"
        echo "  Samples:   $SAMPLE_COUNT"
        echo "  File:      $OUTPUT_FILE"
        echo ""
        echo "Next step:"
        echo "  ./4_create_blueprints.sh -i \"$INPUT_DIR\""
    else
        echo -e "${RED}Error: Output file not created${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Feature extraction failed${NC}"
    exit 1
fi
