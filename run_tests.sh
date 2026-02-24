#!/bin/bash

# Crimson Trails Automated Test Suite

# ANSI Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "========================================"
echo "   Crimson Trails: Running Tests"
echo "========================================"

# 1. Build the C engine
echo -e "\n[1/3] Compiling C Engine..."
make clean > /dev/null
make > /dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}SUCCESS: C Engine compiled.${NC}"
else
    echo -e "${RED}FAILURE: Compilation failed.${NC}"
    exit 1
fi

# 2. Run C Bridge Tests
echo -e "\n[2/3] Running C Bridge Tests..."
export PYTHONPATH=.
python3 tests/test_c_bridge.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}PASSED: C Bridge verification.${NC}"
else
    echo -e "${RED}FAILED: C Bridge verification.${NC}"
    exit 1
fi

# 3. Run Python Logic Tests
echo -e "\n[3/3] Running Python Logic Tests..."
export PYTHONPATH=.
python3 tests/test_python_logic.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}PASSED: Python logic verification.${NC}"
else
    echo -e "${RED}FAILED: Python logic verification.${NC}"
    exit 1
fi

echo -e "\n========================================"
echo -e "${GREEN}ALL TESTS PASSED SUCCESSFULLY${NC}"
echo "========================================"
