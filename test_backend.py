# Test backend API endpoints
import requests
import json

BASE_URL = "http://localhost:8000"

print("🔬 Testing Backend API Endpoints...")
print("=" * 50)

# Test health endpoint
print("\n1. Testing /health endpoint...")
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test readiness endpoint
print("\n2. Testing /health/ready endpoint...")
try:
    response = requests.get(f"{BASE_URL}/health/ready")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test projects endpoint
print("\n3. Testing /api/v1/projects endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/v1/projects")
    print(f"   Status: {response.status_code}")
    projects = response.json()
    print(f"   Found {len(projects)} projects")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 50)
print("✅ Backend tests complete!")
