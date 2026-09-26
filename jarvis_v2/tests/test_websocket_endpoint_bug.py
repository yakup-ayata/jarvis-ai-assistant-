"""
Bug Condition Exploration Test - WebSocket Tool Server Endpoint Mismatch

This test demonstrates the bug where WebSocket server calls the wrong endpoint.
EXPECTED TO FAIL on unfixed code with 404 errors.
"""

import pytest
import asyncio
import aiohttp
from typing import Dict
import sys
import os

# Add parent directory to path to import websocket_server_enhanced
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.websocket_server_enhanced import ConnectionManager


@pytest.mark.asyncio
@pytest.mark.integration
class TestWebSocketEndpointBug:
    """
    Property 1: Fault Condition - WebSocket Server 404 Error on Action Execution
    
    This test demonstrates that the WebSocket server calls the wrong endpoint
    (/execute instead of /action) causing 404 errors.
    
    CRITICAL: This test MUST FAIL on unfixed code.
    """
    
    async def test_open_app_action_fails_with_404(self):
        """
        Test: open_app action fails with 404 error on unfixed code
        
        Bug Condition: isBugCondition(request) where
          - request.method == 'POST'
          - request.url == 'http://localhost:8002/execute'
          - toolServerHasNoExecuteEndpoint() == True
        
        Expected on UNFIXED code: 404 error
        Expected on FIXED code: Successful execution
        """
        manager = ConnectionManager()
        action_data = {
            "action": "open_app",
            "target": "instagram",
            "risk_level": "low"
        }
        
        result = await manager.execute_action(action_data)
        
        # On unfixed code: This will fail with 404
        # On fixed code: This will succeed
        assert result.get("success") is not False or "404" not in str(result.get("error", "")), \
            f"Bug confirmed: Got 404 error as expected on unfixed code. Result: {result}"
    
    async def test_web_search_action_fails_with_404(self):
        """
        Test: web_search action fails with 404 error on unfixed code
        """
        manager = ConnectionManager()
        action_data = {
            "action": "web_search",
            "target": "python",
            "risk_level": "low"
        }
        
        result = await manager.execute_action(action_data)
        
        # On unfixed code: This will fail with 404
        # On fixed code: This will succeed
        assert result.get("success") is not False or "404" not in str(result.get("error", "")), \
            f"Bug confirmed: Got 404 error as expected on unfixed code. Result: {result}"
    
    async def test_set_volume_action_fails_with_404(self):
        """
        Test: set_volume action fails with 404 error on unfixed code
        """
        manager = ConnectionManager()
        action_data = {
            "action": "set_volume",
            "target": "50",
            "risk_level": "low"
        }
        
        result = await manager.execute_action(action_data)
        
        # On unfixed code: This will fail with 404
        # On fixed code: This will succeed
        assert result.get("success") is not False or "404" not in str(result.get("error", "")), \
            f"Bug confirmed: Got 404 error as expected on unfixed code. Result: {result}"
    
    async def test_tool_server_offline_gives_connection_error_not_404(self):
        """
        Edge case: When tool server is offline, should get connection error, not 404
        
        This test helps distinguish between:
        - Tool server offline (connection error)
        - Wrong endpoint (404 error)
        """
        # Stop tool server first (manual step)
        # This test documents expected behavior when tool server is down
        
        manager = ConnectionManager()
        action_data = {
            "action": "open_app",
            "target": "test",
            "risk_level": "low"
        }
        
        # Note: This test requires tool server to be stopped
        # If tool server is running, skip this test
        try:
            result = await manager.execute_action(action_data)
            
            # If we get a result, tool server is running
            # Check that we don't get 404 (which would indicate wrong endpoint)
            if not result.get("success"):
                error_msg = str(result.get("error", ""))
                # Connection errors are acceptable, 404 is not
                assert "404" not in error_msg, \
                    "Got 404 error - this indicates wrong endpoint, not offline server"
        except Exception as e:
            # Connection errors are expected when server is offline
            assert "404" not in str(e), \
                "Got 404 error - this indicates wrong endpoint, not offline server"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_property_based_all_actions_fail_with_404():
    """
    Property-Based Test: All action execution requests fail with 404 on unfixed code
    
    This test generates multiple action types and verifies they all fail with 404
    on unfixed code due to wrong endpoint.
    """
    manager = ConnectionManager()
    
    # Generate various action types
    test_actions = [
        {"action": "open_app", "target": "chrome", "risk_level": "low"},
        {"action": "open_app", "target": "firefox", "risk_level": "low"},
        {"action": "web_search", "target": "test query", "risk_level": "low"},
        {"action": "set_volume", "target": "75", "risk_level": "low"},
        {"action": "set_volume", "target": "25", "risk_level": "low"},
    ]
    
    failures = []
    for action_data in test_actions:
        result = await manager.execute_action(action_data)
        
        # On unfixed code: expect 404 errors
        # On fixed code: expect success
        if result.get("success") is False and "404" in str(result.get("error", "")):
            failures.append({
                "action": action_data,
                "result": result
            })
    
    # Document counterexamples
    if failures:
        print("\n=== COUNTEREXAMPLES FOUND (Bug Confirmed) ===")
        for i, failure in enumerate(failures, 1):
            print(f"\nCounterexample {i}:")
            print(f"  Action: {failure['action']}")
            print(f"  Result: {failure['result']}")
        print("\nBug confirmed: All actions fail with 404 due to wrong endpoint")
        print("Expected: POST to /action endpoint")
        print("Actual: POST to /execute endpoint (which doesn't exist)")
    
    # On unfixed code: This assertion will fail (expected)
    # On fixed code: This assertion will pass
    assert len(failures) == 0, \
        f"Bug confirmed: {len(failures)} actions failed with 404 errors. See counterexamples above."


if __name__ == "__main__":
    # Run tests manually
    print("Running Bug Condition Exploration Tests...")
    print("=" * 60)
    print("IMPORTANT: These tests are EXPECTED TO FAIL on unfixed code")
    print("=" * 60)
    
    asyncio.run(test_property_based_all_actions_fail_with_404())
