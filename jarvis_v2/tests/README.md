# WebSocket Tool Server Endpoint Fix - Test Suite

## Overview

This test suite validates the bugfix for the WebSocket-Tool Server endpoint mismatch issue.

**Bug**: WebSocket server was calling `/execute` endpoint, but tool server only exposes `/action` endpoint, causing 404 errors.

**Fix**: Changed endpoint URL in `websocket_server_enhanced.py` line 93 from `/execute` to `/action`.

## Test Files

### 1. `test_websocket_endpoint_bug.py`
**Property 1: Fault Condition** - Bug condition exploration tests

These tests demonstrate the bug and verify the fix:
- Test various action types (open_app, web_search, set_volume)
- On unfixed code: Tests FAIL with 404 errors (expected)
- On fixed code: Tests PASS with successful execution

### 2. `test_websocket_preservation.py`
**Property 2: Preservation** - Preservation property tests

These tests verify that non-action operations remain unchanged:
- Connection management
- Message routing
- Error handling structure
- Timeout configuration
- Should PASS on both unfixed and fixed code

## Running Tests

### Prerequisites

1. Tool server must be running:
```bash
cd jarvis_v2
./start_tools.sh
```

2. Verify tool server is running:
```bash
curl http://localhost:8002/health
```

### Run All Tests

```bash
cd jarvis_v2/tests
chmod +x run_bugfix_tests.sh
./run_bugfix_tests.sh
```

### Run Individual Test Files

```bash
# Run preservation tests
python -m pytest test_websocket_preservation.py -v

# Run bug condition tests
python -m pytest test_websocket_endpoint_bug.py -v
```

### Run Specific Tests

```bash
# Run a specific test
python -m pytest test_websocket_endpoint_bug.py::TestWebSocketEndpointBug::test_open_app_action_fails_with_404 -v

# Run property-based test
python -m pytest test_websocket_endpoint_bug.py::test_property_based_all_actions_fail_with_404 -v
```

## Test Methodology

This test suite follows the **Bug Condition Methodology**:

1. **Exploration Phase** (Task 1)
   - Write tests that demonstrate the bug
   - Tests FAIL on unfixed code (expected)
   - Document counterexamples (404 errors)

2. **Preservation Phase** (Task 2)
   - Write tests for non-buggy behavior
   - Tests PASS on unfixed code
   - Ensure these still PASS after fix

3. **Implementation Phase** (Task 3)
   - Apply the fix
   - Re-run exploration tests → should now PASS
   - Re-run preservation tests → should still PASS

## Expected Results

### On Unfixed Code
- Preservation tests: ✓ PASS
- Bug condition tests: ✗ FAIL (404 errors)

### On Fixed Code
- Preservation tests: ✓ PASS
- Bug condition tests: ✓ PASS

## Integration Testing

After unit tests pass, test with real commands:

1. Start all services:
```bash
./start_tools.sh
./start_agent.sh  # or websocket server
./start_frontend.sh
```

2. Open frontend: http://localhost:5178

3. Test commands:
   - "open instagram" → Instagram should open
   - "search for python" → Browser should open with search
   - "volume 50" → Volume should change to 50%

## Troubleshooting

### Tool Server Not Running
```bash
# Check if running
lsof -i :8002

# Start if not running
cd jarvis_v2
./start_tools.sh
```

### Tests Fail with Connection Error
- Ensure tool server is running on port 8002
- Check firewall settings
- Verify no other service is using port 8002

### Tests Pass but Real Commands Fail
- Check WebSocket server is running on port 8001
- Check frontend is connected to WebSocket
- Check browser console for errors
- Verify brain service is processing commands correctly

## Test Coverage

- ✓ Action execution with correct endpoint
- ✓ Multiple action types (open_app, web_search, set_volume)
- ✓ Error handling preservation
- ✓ Connection management preservation
- ✓ Timeout configuration preservation
- ✓ Response format preservation
- ✓ Property-based testing for comprehensive coverage

## References

- Bugfix Requirements: `.kiro/specs/websocket-tool-server-endpoint-fix/bugfix.md`
- Design Document: `.kiro/specs/websocket-tool-server-endpoint-fix/design.md`
- Task List: `.kiro/specs/websocket-tool-server-endpoint-fix/tasks.md`
