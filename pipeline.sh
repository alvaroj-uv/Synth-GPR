#!/bin/bash
# ============================================================================
# GPR Data Pipeline - Complete Workflow
# ============================================================================
# This script runs the complete GPR data generation and analysis pipeline:
#   1. Generate .in files (gprMax input files)
#   2. Run gprMax simulations to create .out files
#   3. Extract features from .out files
#   4. Create blueprint visualizations
#
# Usage:
#   ./pipeline.sh [options]
#
# Options:
#   -n, --num-samples N    Number of samples per class (default: 2)
#   -o, --output DIR       Output directory (default: output/pipeline_run)
#   -s, --start-id ID      Starting sample ID (default: 0)
#   -p, --parallel N       Number of parallel processes for gprMax (default: 1)
#   -h, --help             Show this help message
#
# Examples:
#   ./pipeline.sh                           # Run with defaults
#   ./pipeline.sh -n 10 -p 4                # 10 samples/class, 4 parallel processes
#   ./pipeline.sh -o my_dataset -n 5        # Custom output directory
# ============================================================================

set -e  # Exit on error

# Default configuration
NUM_SAMPLES=2
OUTPUT_DIR="output/pipeline_run"
START_ID=0
PARALLEL=1

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

show_usage() {
    grep "^#" "$0" | grep -v "#!/bin/bash" | sed 's/^# //' | sed 's/^#//'
}

# Parse command line arguments
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
        -s|--start-id)
            START_ID="$2"
            shift 2
            ;;
        -p|--parallel)
            PARALLEL="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Create timestamped output directory
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RUN_DIR="${OUTPUT_DIR}/${TIMESTAMP}"
mkdir -p "$RUN_DIR"

print_header "GPR Data Pipeline"
print_info "Configuration:"
echo "  Samples per class: $NUM_SAMPLES"
echo "  Output directory:  $RUN_DIR"
echo "  Starting ID:       $START_ID"
echo "  Parallel processes: $PARALLEL"
echo ""

# ============================================================================
# STEP 1: Generate .in files
# ============================================================================
print_header "Step 1/4: Generating .in files"

python generate_balanced_dataset.py \
    --count "$NUM_SAMPLES" \
    --output "$OUTPUT_DIR"

if [ $? -eq 0 ]; then
    print_success "Generated .in files successfully"
    
    # Count generated files
    IN_COUNT=$(find "$RUN_DIR" -name "*.in" | wc -l)
    print_info "Created $IN_COUNT .in files"
else
    print_error "Failed to generate .in files"
    exit 1
fi

# ============================================================================
# STEP 2: Run gprMax simulations
# ============================================================================
print_header "Step 2/4: Running gprMax simulations"

print_info "This may take a while depending on the number of samples..."

# Count .in files to process
TOTAL_IN=$(find "$RUN_DIR" -name "*.in" | wc -l)
PROCESSED=0

# Run gprMax on each .in file
for in_file in "$RUN_DIR"/*.in; do
    if [ -f "$in_file" ]; then
        out_file="${in_file%.in}.out"
        
        # Skip if .out file already exists
        if [ -f "$out_file" ]; then
            print_warning "Skipping $(basename "$in_file") (output already exists)"
            ((PROCESSED++))
            continue
        fi
        
        echo -n "  Processing $(basename "$in_file") [$((PROCESSED+1))/$TOTAL_IN]... "
        
        # Run gprMax
        if python -m gprMax "$in_file" -n "$PARALLEL" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${RED}✗${NC}"
            print_error "Failed to process $(basename "$in_file")"
        fi
        
        ((PROCESSED++))
    fi
done

# Verify .out files were created
OUT_COUNT=$(find "$RUN_DIR" -name "*.out" | wc -l)
if [ "$OUT_COUNT" -gt 0 ]; then
    print_success "Simulations complete: $OUT_COUNT .out files created"
else
    print_error "No .out files were created"
    exit 1
fi

# ============================================================================
# STEP 3: Extract features
# ============================================================================
print_header "Step 3/4: Extracting features"

python create_feature_dataset.py "$RUN_DIR"

if [ $? -eq 0 ]; then
    if [ -f "$RUN_DIR/features.csv" ]; then
        print_success "Features extracted successfully"
        
        # Show feature count
        FEATURE_COUNT=$(head -1 "$RUN_DIR/features.csv" | tr ',' '\n' | wc -l)
        SAMPLE_COUNT=$(tail -n +2 "$RUN_DIR/features.csv" | wc -l)
        print_info "Extracted $FEATURE_COUNT features from $SAMPLE_COUNT samples"
    else
        print_warning "Feature extraction completed but features.csv not found"
    fi
else
    print_error "Failed to extract features"
    exit 1
fi

# ============================================================================
# STEP 4: Create blueprints
# ============================================================================
print_header "Step 4/4: Creating blueprint visualizations"

BLUEPRINT_SCRIPT="scripts/tools/visualization/visualize_gprmax_blueprint.py"

if [ ! -f "$BLUEPRINT_SCRIPT" ]; then
    print_error "Blueprint script not found: $BLUEPRINT_SCRIPT"
    exit 1
fi

PROCESSED=0
TOTAL_IN=$(find "$RUN_DIR" -name "*.in" | wc -l)

for in_file in "$RUN_DIR"/*.in; do
    if [ -f "$in_file" ]; then
        basename_no_ext=$(basename "$in_file" .in)
        blueprint_file="$RUN_DIR/${basename_no_ext}_blueprint.png"
        
        # Skip if blueprint already exists
        if [ -f "$blueprint_file" ]; then
            print_warning "Skipping $(basename "$in_file") (blueprint already exists)"
            ((PROCESSED++))
            continue
        fi
        
        echo -n "  Creating blueprint for $(basename "$in_file") [$((PROCESSED+1))/$TOTAL_IN]... "
        
        # Create blueprint
        if python "$BLUEPRINT_SCRIPT" "$in_file" -o "$blueprint_file" --no-show > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${RED}✗${NC}"
            print_error "Failed to create blueprint for $(basename "$in_file")"
        fi
        
        ((PROCESSED++))
    fi
done

# Count created blueprints
BLUEPRINT_COUNT=$(find "$RUN_DIR" -name "*_blueprint.png" | wc -l)
if [ "$BLUEPRINT_COUNT" -gt 0 ]; then
    print_success "Blueprints created: $BLUEPRINT_COUNT images"
else
    print_warning "No blueprints were created"
fi

# ============================================================================
# Summary
# ============================================================================
print_header "Pipeline Complete!"

echo ""
echo "Summary:"
echo "  📁 Output directory: $RUN_DIR"
echo "  📄 Input files:      $IN_COUNT"
echo "  📊 Output files:     $OUT_COUNT"
echo "  🔬 Features file:    $([ -f "$RUN_DIR/features.csv" ] && echo "✓" || echo "✗")"
echo "  🖼️  Blueprints:       $BLUEPRINT_COUNT"
echo ""

print_success "All steps completed successfully!"
print_info "Next steps:"
echo "  - Review features:   cat $RUN_DIR/features.csv"
echo "  - View blueprints:   open $RUN_DIR/*_blueprint.png"
echo "  - Train ML model:    python ml/train_model.py --input $RUN_DIR/features.csv"
echo ""
