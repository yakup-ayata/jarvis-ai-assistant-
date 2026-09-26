#!/bin/bash

# Test runner for WebSocket Tool Server Endpoint Fix
# This script verifies the bug fix by running the test suite

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧪 WebSocket Tool Server Endpoint Fix - Test Suite${NC}"
echo "================================================================"

# Check if tool server is running
echo -e "\n${BLUE}Checking prerequisites...${NC}"

if lsof -i :8002 > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓ Tool server is running on port 8002${NC}"
else
    echo -e "  ${RED}✗ Tool server is NOT running on port 8002${NC}"
    echo -e "  ${YELLOW}Please start the tool server first:${NC}"
    echo -e "    cd jarvis_v2 && ./start_tools.sh"
    exit 1
fi

# Check if tool server has /action endpoint
echo -e "\n${BLUE}Verifying tool server endpoints...${NC}"
HEALTH_CHECK=$(curl -s http://localhost:8002/health)
if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✓ Tool server /health endpoint responding${NC}"
else
    echo -e "  ${RED}✗ Tool server /health endpoint not responding${NC}"
    exit 1
fi

# Run preservation tests first (should pass on both unfixed and fixed code)
echo -e "\n${BLUE}Running Preservation Tests...${NC}"
echo -e "${YELLOW}These tests verify that non-action operations are unchanged${NC}"
echo "================================================================"

cd "$(dirname "$0")/.."
python -m pytest tests/test_websocket_preservation.py -v --tb=short

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ Preservation tests PASSED${NC}"
    echo -e "  Non-action operations are preserved correctly"
else
    echo -e "\n${RED}✗ Preservation tests FAILED${NC}"
    echo -e "  This indicates a regression in non-action functionality"
    exit 1
fi

# Run bug condition exploration tests (should fail on unfixed, pass on fixed)
echo -e "\n${BLUE}Running Bug Condition Exploration Tests...${NC}"
echo -e "${YELLOW}These tests verify the endpoint fix works correctly${NC}"
echo "================================================================"

python -m pytest tests/test_websocket_endpoint_bug.py -v --tb=short

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ Bug condition tests PASSED${NC}"
    echo -e "  The endpoint fix is working correctly"
    echo -e "  Actions are now sent to /action endpoint"
else
    echo -e "\n${RED}✗ Bug condition tests FAILED${NC}"
    echo -e "  The bug still exists or there's a new issue"
    exit 1
fi

# Summary
echo -e "\n${GREEN}================================================================${NC}"
echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
echo -e "${GREEN}================================================================${NC}"
echo -e "\nBug fix verified:"
echo -e "  • WebSocket server now calls /action endpoint"
echo -e "  • Actions execute successfully (no more 404 errors)"
echo -e "  • Non-action operations preserved"
echo -e "\nNext steps:"
echo -e "  • Test with real commands: 'open instagram', 'search for python'"
echo -e "  • Verify integration with frontend"
echo ""
