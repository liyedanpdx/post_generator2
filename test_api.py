#!/usr/bin/env python
"""
Test script for the Post Auto Editor API
"""
import requests
import json
import os
import argparse

def test_exchange_rates(base_url):
    """Test the exchange rate endpoints"""
    print("\n=== Testing Exchange Rate Endpoints ===")
    
    # Test get all rates
    print("\nGetting all exchange rates...")
    response = requests.get(f"{base_url}/api/exchange-rates")
    if response.status_code == 200:
        rates = response.json()
        print(f"Success! Found {len(rates)} currencies.")
        for currency, rate in rates.items():
            print(f"  {currency}: {rate}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
    
    # Test get specific rate
    currency = "CNY"
    print(f"\nGetting exchange rate for {currency}...")
    response = requests.get(f"{base_url}/api/exchange-rate/{currency}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success! 1 USD = {data['rate']} {data['currency']} ({data['description']})")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def test_generate_poster(base_url, output_file="test_poster.png"):
    """Test the poster generation endpoint"""
    print("\n=== Testing Poster Generation ===")
    
    # Prepare test data
    data = {
        "recipient_name": "Test User",
        "offer_amount": "12,345",
        "team_name": "Test Team"
    }
    
    print(f"\nGenerating poster with data: {json.dumps(data, indent=2)}")
    
    # Send request
    response = requests.post(
        f"{base_url}/api/generate-poster",
        json=data,
        stream=True  # Important for downloading files
    )
    
    # Check response
    if response.status_code == 200:
        # Save the file
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Get file size
        file_size = os.path.getsize(output_file) / 1024  # KB
        
        print(f"Success! Poster saved to {output_file} ({file_size:.2f} KB)")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def test_cleanup(base_url):
    """Test the cleanup endpoint"""
    print("\n=== Testing Cleanup Endpoint ===")
    
    data = {
        "max_age_hours": 48  # Clean files older than 48 hours
    }
    
    print(f"\nCleaning up files older than {data['max_age_hours']} hours...")
    
    response = requests.post(f"{base_url}/api/cleanup", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success! {result['message']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test the Post Auto Editor API")
    parser.add_argument("--url", default="http://localhost:5000", help="Base URL of the API")
    parser.add_argument("--output", default="test_poster.png", help="Output file for the generated poster")
    parser.add_argument("--test", choices=["all", "exchange", "poster", "cleanup"], default="all", 
                        help="Which test to run")
    
    args = parser.parse_args()
    
    print(f"Testing API at {args.url}")
    
    if args.test in ["all", "exchange"]:
        test_exchange_rates(args.url)
    
    if args.test in ["all", "poster"]:
        test_generate_poster(args.url, args.output)
    
    if args.test in ["all", "cleanup"]:
        test_cleanup(args.url)
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main() 