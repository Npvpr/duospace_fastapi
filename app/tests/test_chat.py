import asyncio
import websockets
import json
import requests

async def test_websocket_connection():
    """Test WebSocket connection and messaging"""
    print("🧪 Testing WebSocket connection...")
    
    try:
        async with websockets.connect('ws://localhost:8000/ws') as websocket:
            # Send a test message
            test_message = {
                "text": "Hello from test!",
                "sender": "TestUser"
            }
            await websocket.send(json.dumps(test_message))
            
            # Receive the broadcasted message
            response = await websocket.recv()
            response_data = json.loads(response)
            
            assert response_data["text"] == test_message["text"]
            assert response_data["sender"] == test_message["sender"]
            print("✅ WebSocket test passed!")
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")

def test_rest_api():
    """Test REST API endpoints"""
    print("🧪 Testing REST API...")
    
    try:
        # Test health endpoint
        response = requests.get('http://localhost:8000/api/chat/health')
        assert response.status_code == 200
        print("✅ Health endpoint test passed!")
        
        # Test messages endpoint
        response = requests.get('http://localhost:8000/api/chat/messages')
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print("✅ Messages endpoint test passed!")
        
    except Exception as e:
        print(f"❌ REST API test failed: {e}")

async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting all tests...")
    await test_websocket_connection()
    test_rest_api()
    print("🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(run_all_tests())