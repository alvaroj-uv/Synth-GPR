#!/bin/bash

# Configuration
OUTPUT_DIR="test_run_mac"
NUM_SAMPLES=2  # Small number for testing
START_ID=5000

function show_usage {
    echo "Usage: ./run_pipeline_mac.sh [mode]"
    echo ""
    echo "Modes:"
    echo "  generate  - Generates test .in files in '$OUTPUT_DIR'"
    echo "  analyze   - Extracts features from .out files and trains model"
    echo ""
    echo "Example Flow:"
    echo "  1. ./run_pipeline_mac.sh generate"
    echo "  2. (You run gprMax separately on the generated files)"
    echo "  3. ./run_pipeline_mac.sh analyze"
}

function run_generate {
    echo "=========================================="
    echo " [Step 1] Generating Data"
    echo "=========================================="
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    
    echo "Output Directory: $OUTPUT_DIR"
    echo "Generating $NUM_SAMPLES samples per class..."
    
    # Run generation script
    python scripts/main/generate_dataset.py "$OUTPUT_DIR" --labels CL -n "$NUM_SAMPLES" --start_id "$START_ID"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Generation complete."
        echo ""
        echo "=========================================="
        echo " NEXT STEPS: Run gprMax Simulations"
        echo "=========================================="
        echo "Please run gprMax on the files in '$OUTPUT_DIR'."
        echo "Example command (if you have gprMax installed):"
        echo "  python -m gprMax $OUTPUT_DIR/s_*.in -n <num_processes>"
        echo ""
        echo "Once simulations are done and .out files exist, run:"
        echo "  ./run_pipeline_mac.sh analyze"
    else
        echo "❌ Generation failed."
        exit 1
    fi
}

function run_analyze {
    echo "=========================================="
    echo " [Step 2] Analysis (Features & Graphs)"
    echo "=========================================="
    
    if [ ! -d "$OUTPUT_DIR" ]; then
        echo "❌ Error: Directory '$OUTPUT_DIR' does not exist."
        echo "Run './run_pipeline_mac.sh generate' first."
        exit 1
    fi

    # Check for .out files
    count=$(find "$OUTPUT_DIR" -maxdepth 1 -name "*.out" | wc -l)
    if [ "$count" -eq 0 ]; then
        echo "❌ No .out files found in '$OUTPUT_DIR'."
        echo "Please run your gprMax simulations first."
        exit 1
    fi
    
    echo "Found $count .out files."
    
    # 1. Extract Features
    echo ""
    echo "--- Extracting Features ---"
    python scripts/main/extract_features.py "$OUTPUT_DIR" --output feature_dataset.csv
    
    if [ $? -ne 0 ]; then
        echo "❌ Feature extraction failed."
        exit 1
    fi
    
    # 2. Train and Graph
    echo ""
    echo "--- Training Model & Generating Graphs ---"
    python ml/train_model.py --input "$OUTPUT_DIR/feature_dataset.csv" --output_dir "$OUTPUT_DIR"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Analysis complete."
        echo "Results (graphs and reports) are in: $OUTPUT_DIR"
    else
        echo "❌ Modeling failed."
        exit 1
    fi
}

# Main Logic
if [ "$1" == "generate" ]; then
    run_generate
elif [ "$1" == "analyze" ]; then
    run_analyze
else
    show_usage
fi
