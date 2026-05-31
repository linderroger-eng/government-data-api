#!/usr/bin/env python3
"""
Test the Government Data API with real data
"""
import requests
import json

def test_api():
    """Test API endpoints with real data"""
    base_url = "http://localhost:8000"
    
    print("🚀 Testing Government Data API")
    print("=" * 50)
    
    # Test 1: API Status
    print("\n1. Testing API Status...")
    response = requests.get(f"{base_url}/")
    if response.status_code == 200:
        print("✅ API is running!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ API Status failed: {response.status_code}")
        return
    
    # Test 2: Get Contracts
    print("\n2. Testing Contracts Endpoint...")
    response = requests.get(f"{base_url}/contracts?limit=3")
    if response.status_code == 200:
        contracts = response.json()
        print(f"✅ Found {len(contracts)} contracts")
        if contracts:
            print("Sample contract:")
            print(json.dumps(contracts[0], indent=2))
    else:
        print(f"❌ Contracts failed: {response.status_code}")
    
    # Test 3: Get Agencies
    print("\n3. Testing Agencies Endpoint...")
    response = requests.get(f"{base_url}/agencies")
    if response.status_code == 200:
        agencies = response.json()
        print(f"✅ Found {len(agencies)} agencies")
        if agencies:
            print("Sample agencies:")
            for agency in agencies[:3]:
                print(f"  - {agency.get('agency_code', 'N/A')}: {agency.get('agency_name', 'N/A')}")
    else:
        print(f"❌ Agencies failed: {response.status_code}")
    
    # Test 4: Get Stats
    print("\n4. Testing Stats Endpoint...")
    response = requests.get(f"{base_url}/stats")
    if response.status_code == 200:
        stats = response.json()
        print("✅ API Statistics:")
        print(json.dumps(stats, indent=2))
    else:
        print(f"❌ Stats failed: {response.status_code}")
    
    print(f"\n🎯 API Testing Complete!")
    print(f"📖 View full documentation at: {base_url}/docs")

if __name__ == "__main__":
    test_api()