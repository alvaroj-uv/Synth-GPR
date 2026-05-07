#!/bin/bash
# ============================================================================
# Step 4: Create blueprint visualizations
# ============================================================================
# This script creates visual blueprints for all .in files, showing the
# geometry and signal analysis if .out files are available.
#
# Usage:
#   ./4_create_blueprints.sh [options]
#
# Options:
#   -i, --input DIR        Input directory containing .in files (required)
#   -f, --force            Force re-creation even if blueprints exist
#   -s, --show             Show blueprints after creation
#   -h, --help             Show this help message
# ============================================================================

set -e

# Default configuration
INPUT_DIR=""
FORCE=false
SHOW=false

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
        -f|--force)
            FORCE=true
            shift
            ;;
        -s|--show)
            SHOW=true
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

BLUEPRINT_SCRIPT="scripts/tools/visualization/visualize_gprmax_blueprint.py"

if [ ! -f "$BLUEPRINT_SCRIPT" ]; then
    echo -e "${RED}Error: Blueprint script not found: $BLUEPRINT_SCRIPT${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE} Creating blueprints${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Configuration:"
echo "  Input directory: $INPUT_DIR"
echo "  Force re-create: $FORCE"
echo "  Show blueprints: $SHOW"
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
        basename_no_ext=$(basename "$in_file" .in)
        blueprint_file="$INPUT_DIR/${basename_no_ext}_blueprint.png"
        basename_file=$(basename "$in_file")
        
        # Skip if blueprint exists and not forcing
        if [ -f "$blueprint_file" ] && [ "$FORCE" = false ]; then
            echo -e "${YELLOW}⏭️  Skipping $basename_file (blueprint exists)${NC}"
            ((SKIPPED++))
            continue
        fi
        
        echo -n "Creating blueprint for $basename_file [$((PROCESSED+SKIPPED+FAILED+1))/$TOTAL]... "
        
        # Create blueprint (with or without --no-show based on SHOW flag)
        if [ "$SHOW" = true ]; then
            if python "$BLUEPRINT_SCRIPT" "$in_file" -o "$blueprint_file" 2>&1 | grep -q "ERROR"; then
                echo -e "${RED}✗${NC}"
                ((FAILED++))
            else
                echo -e "${GREEN}✓${NC}"
                ((PROCESSED++))
            fi
        else
            if python "$BLUEPRINT_SCRIPT" "$in_file" -o "$blueprint_file" --no-show > /dev/null 2>&1; then
                echo -e "${GREEN}✓${NC}"
                ((PROCESSED++))
            else
                echo -e "${RED}✗${NC}"
                ((FAILED++))
            fi
        fi
    fi
done

echo ""
echo -e "${BLUE}========================================${NC}"
echo "Summary:"
echo "  ✅ Created:  $PROCESSED"
echo "  ⏭️  Skipped:  $SKIPPED"
echo "  ❌ Failed:   $FAILED"
echo -e "${BLUE}========================================${NC}"

if [ "$PROCESSED" -gt 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Blueprints created!${NC}"
    echo ""
    echo "View blueprints:"
    echo "  open $INPUT_DIR/*_blueprint.png"
fi

if [ "$FAILED" -gt 0 ]; then
    exit 1
fi
