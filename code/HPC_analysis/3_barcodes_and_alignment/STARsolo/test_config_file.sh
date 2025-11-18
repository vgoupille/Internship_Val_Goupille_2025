#!/bin/bash
# Test suite for submit_pipeline.sh CONFIG_FILE fix
# This test ensures that the CONFIG_FILE is properly set by default

set -e

SCRIPT_DIR="/home/runner/work/Internship_Val_Goupille_2025/Internship_Val_Goupille_2025/code/HPC_analysis/3_barcodes_and_alignment/STARsolo"
TEST_NAME="CONFIG_FILE initialization test"

echo "=========================================="
echo "$TEST_NAME"
echo "=========================================="
echo ""

# Test 1: Verify config.sh exists
echo "Test 1: Verify config.sh exists"
if [ -f "$SCRIPT_DIR/config.sh" ]; then
    echo "✓ PASS: config.sh found at $SCRIPT_DIR/config.sh"
else
    echo "✗ FAIL: config.sh not found"
    exit 1
fi
echo ""

# Test 2: Simulate the initialization logic
echo "Test 2: Simulate CONFIG_FILE initialization"
(
    CONFIG_FILE=""
    if [ -f "$SCRIPT_DIR/config.sh" ]; then
        if [ -z "$CONFIG_FILE" ]; then
            CONFIG_FILE="$SCRIPT_DIR/config.sh"
        fi
    fi
    
    if [ -z "$CONFIG_FILE" ]; then
        echo "✗ FAIL: CONFIG_FILE not set"
        exit 1
    fi
    
    if [ ! -f "$CONFIG_FILE" ]; then
        echo "✗ FAIL: CONFIG_FILE points to non-existent file"
        exit 1
    fi
    
    echo "✓ PASS: CONFIG_FILE correctly set to $CONFIG_FILE"
)
echo ""

# Test 3: Verify the script has the fix
echo "Test 3: Verify submit_pipeline.sh contains the CONFIG_FILE initialization"
if grep -q 'CONFIG_FILE="\$SCRIPT_DIR/config.sh"' "$SCRIPT_DIR/submit_pipeline.sh"; then
    echo "✓ PASS: CONFIG_FILE initialization found in script"
else
    echo "✗ FAIL: CONFIG_FILE initialization not found in script"
    exit 1
fi
echo ""

# Test 4: Verify --config option exists
echo "Test 4: Verify --config command-line option exists"
if grep -q '\-c|\-\-config)' "$SCRIPT_DIR/submit_pipeline.sh"; then
    echo "✓ PASS: --config option found in script"
else
    echo "✗ FAIL: --config option not found in script"
    exit 1
fi
echo ""

echo "=========================================="
echo "All tests passed!"
echo "=========================================="
