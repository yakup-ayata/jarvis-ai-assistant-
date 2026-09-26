"""
Manual Integration Test Script

This script provides a simple way to manually test the endpoint fix
by sending real action requests to the WebSocket server.

Run this after the fix is applied to verify it works end-to-end.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.websocket_server_enhanced import ConnectionManager


async def test_action(manager, action_data, description):
    """Test a single action and print results"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Action: {action_data}")
    print(f"{'='*60}")
    
    result = await manager.execute_action(action_data)
    
    print(f"\nResult:")
    print(f"  Success: {result.get('success', 'N/A')}")
    
    if result.get('success'):
        print(f"  ✓ Action executed successfully")
        if 'action' in result:
            print(f"  Action: {result['action']}")
        if 'target' in result:
            print(f"  Target: {result['target']}")
    else:
        print(f"  ✗ Action failed")
        print(f"  Error: {result.get('error', 'Unknown error')}")
        if 'note' in result:
            print(f"  Note: {result['note']}")
    
    return result.get('success', False)


async def main():
    """Run manual integration tests"""
    print("🧪 WebSocket Tool Server Endpoint Fix - Manual Integration Test")
    print("="*60)
    print("\nThis script tests the endpoint fix by sending real action requests.")
    print("Make sure the tool server is running on port 8002.")
    print("\nPress Ctrl+C to stop at any time.")
    
    # Wait for user confirmation
    input("\nPress Enter to start testing...")
    
    manager = ConnectionManager()
    
    # Test cases
    test_cases = [
        {
            "action_data": {
                "action": "open_app",
                "target": "Calculator",
                "risk_level": "low"
            },
            "description": "Open Calculator app"
        },
        {
            "action_data": {
                "action": "web_search",
                "target": "python programming",
                "risk_level": "low"
            },
            "description": "Web search for 'python programming'"
        },
        {
            "action_data": {
                "action": "get_volume",
                "target": "",
                "risk_level": "low"
            },
            "description": "Get current volume level"
        },
    ]
    
    results = []
    
    for test_case in test_cases:
        success = await test_action(
            manager,
            test_case["action_data"],
            test_case["description"]
        )
        results.append({
            "description": test_case["description"],
            "success": success
        })
        
        # Wait between tests
        await asyncio.sleep(1)
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    total = len(results)
    passed = sum(1 for r in results if r["success"])
    failed = total - passed
    
    for result in results:
        status = "✓ PASS" if result["success"] else "✗ FAIL"
        print(f"  {status}: {result['description']}")
    
    print(f"\nTotal: {total} | Passed: {passed} | Failed: {failed}")
    
    if failed == 0:
        print("\n✓ All tests passed! The endpoint fix is working correctly.")
        print("\nThe WebSocket server is now successfully calling the /action endpoint.")
    else:
        print(f"\n✗ {failed} test(s) failed. Please check:")
        print("  1. Is the tool server running? (./start_tools.sh)")
        print("  2. Is it listening on port 8002?")
        print("  3. Does it have the /action endpoint?")
    
    print("\nNext steps:")
    print("  • Test with the frontend UI")
    print("  • Try commands: 'open instagram', 'search for python', 'volume 50'")
    print("  • Verify metrics are displayed correctly")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
