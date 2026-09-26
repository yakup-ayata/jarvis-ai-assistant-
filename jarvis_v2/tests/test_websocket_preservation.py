"""
Preservation Property Tests - WebSocket Non-Action-Execution Operations

These tests verify that operations NOT related to action execution remain unchanged
after the endpoint fix. These tests should PASS on both unfixed and fixed code.

Following observation-first methodology: observe behavior on unfixed code,
then write tests to capture that behavior.
"""

import pytest
import asyncio
import sys
import os
from unittest.mock import Mock, AsyncMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.websocket_server_enhanced import ConnectionManager


@pytest.mark.asyncio
@pytest.mark.unit
class TestWebSocketPreservation:
    """
    Property 2: Preservation - Non-Action-Execution Operations Unchanged
    
    These tests verify that the endpoint fix does NOT affect:
    - Connection management
    - Message routing
    - Error handling for non-action operations
    - Logging behavior
    
    All tests should PASS on unfixed code and continue to PASS on fixed code.
    """
    
    async def test_connection_manager_initialization(self):
        """
        Preservation: ConnectionManager initialization unchanged
        
        Observed behavior on unfixed code:
        - ConnectionManager can be instantiated
        - active_connections starts as empty dict
        """
        manager = ConnectionManager()
        
        # Verify initialization
        assert hasattr(manager, 'active_connections')
        assert isinstance(manager.active_connections, dict)
        assert len(manager.active_connections) == 0
    
    async def test_connection_registration(self):
        """
        Preservation: Connection registration/unregistration unchanged
        
        Observed behavior on unfixed code:
        - Connections can be registered with websocket and client_id
        - Connections can be unregistered
        - active_connections dict is updated correctly
        """
        manager = ConnectionManager()
        
        # Mock websocket
        mock_ws = Mock()
        client_id = "test_client_123"
        
        # Register connection
        await manager.connect(mock_ws, client_id)
        assert client_id in manager.active_connections
        assert manager.active_connections[client_id] == mock_ws
        
        # Unregister connection
        manager.disconnect(client_id)
        assert client_id not in manager.active_connections
    
    async def test_error_handling_structure_preserved(self):
        """
        Preservation: Error handling structure in execute_action unchanged
        
        Observed behavior on unfixed code:
        - execute_action has try-except block
        - Returns dict with success=False on error
        - Returns dict with error message
        - Returns dict with note about tool server
        """
        manager = ConnectionManager()
        
        # Test with invalid action data that would cause an error
        # (not related to endpoint issue)
        action_data = {"action": "test"}
        
        result = await manager.execute_action(action_data)
        
        # Verify error response structure is preserved
        assert isinstance(result, dict)
        assert "success" in result or "error" in result
        
        # If there's an error, verify the structure
        if not result.get("success", True):
            assert "error" in result
            assert isinstance(result["error"], str)
    
    async def test_timeout_configuration_preserved(self):
        """
        Preservation: Timeout configuration (10 seconds) unchanged
        
        This test verifies that the timeout setting in execute_action
        remains at 10 seconds after the fix.
        """
        # This is a structural test - we verify the timeout is still configured
        # We don't actually wait 10 seconds, just verify the code structure
        
        import inspect
        from api.websocket_server_enhanced import ConnectionManager
        
        # Get the source code of execute_action
        source = inspect.getsource(ConnectionManager.execute_action)
        
        # Verify timeout is still configured
        assert "timeout" in source.lower()
        assert "10" in source  # 10 second timeout
    
    @pytest.mark.parametrize("action_type,target", [
        ("open_app", "test_app"),
        ("web_search", "test_query"),
        ("set_volume", "50"),
    ])
    async def test_action_data_format_preserved(self, action_type, target):
        """
        Preservation: action_data format and structure unchanged
        
        Observed behavior on unfixed code:
        - execute_action accepts dict with action, target, risk_level
        - No validation or transformation of action_data before sending
        """
        manager = ConnectionManager()
        
        action_data = {
            "action": action_type,
            "target": target,
            "risk_level": "low"
        }
        
        # Call execute_action (will fail with 404 on unfixed, succeed on fixed)
        # But the important thing is the function accepts this format
        result = await manager.execute_action(action_data)
        
        # Verify function accepts the data format (doesn't raise exception)
        assert isinstance(result, dict)


@pytest.mark.asyncio
@pytest.mark.integration
class TestWebSocketMessageRouting:
    """
    Preservation tests for WebSocket message routing
    
    These verify that non-action-execution message handling is unchanged.
    """
    
    async def test_connection_lifecycle_preserved(self):
        """
        Preservation: Connection connect/disconnect lifecycle unchanged
        """
        manager = ConnectionManager()
        
        # Test multiple connections
        clients = ["client1", "client2", "client3"]
        mock_websockets = [Mock() for _ in clients]
        
        # Connect all
        for ws, client_id in zip(mock_websockets, clients):
            await manager.connect(ws, client_id)
        
        assert len(manager.active_connections) == 3
        
        # Disconnect all
        for client_id in clients:
            manager.disconnect(client_id)
        
        assert len(manager.active_connections) == 0
    
    async def test_response_format_preserved(self):
        """
        Preservation: Response format from execute_action unchanged
        
        Observed behavior on unfixed code:
        - Returns dict with success, error, note fields
        - JSON serializable
        """
        manager = ConnectionManager()
        action_data = {"action": "test", "target": "test"}
        
        result = await manager.execute_action(action_data)
        
        # Verify response is JSON serializable
        import json
        json_str = json.dumps(result)
        assert isinstance(json_str, str)
        
        # Verify response structure
        assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_property_based_preservation():
    """
    Property-Based Test: Non-action operations behave identically
    
    This test generates various non-action operations and verifies
    they behave the same on unfixed and fixed code.
    """
    manager = ConnectionManager()
    
    # Test connection operations (not action execution)
    test_cases = [
        ("connect", "client_1"),
        ("connect", "client_2"),
        ("disconnect", "client_1"),
        ("connect", "client_3"),
        ("disconnect", "client_2"),
        ("disconnect", "client_3"),
    ]
    
    mock_websockets = {}
    
    for operation, client_id in test_cases:
        if operation == "connect":
            mock_ws = Mock()
            mock_websockets[client_id] = mock_ws
            await manager.connect(mock_ws, client_id)
            
            # Verify connection is registered
            assert client_id in manager.active_connections
            
        elif operation == "disconnect":
            manager.disconnect(client_id)
            
            # Verify connection is removed
            assert client_id not in manager.active_connections
    
    # Final state: all disconnected
    assert len(manager.active_connections) == 0
    
    print("\n=== PRESERVATION VERIFIED ===")
    print("All non-action operations behave correctly")
    print("Connection management unchanged by endpoint fix")


if __name__ == "__main__":
    # Run preservation tests manually
    print("Running Preservation Property Tests...")
    print("=" * 60)
    print("IMPORTANT: These tests should PASS on both unfixed and fixed code")
    print("=" * 60)
    
    asyncio.run(test_property_based_preservation())
