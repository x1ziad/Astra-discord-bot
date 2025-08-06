"""
Freepik API Diagnostic Script
Analyzes the authentication issue based on the error logs
"""

import os
import sys
import json
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("freepik_diagnostic")


def analyze_freepik_error():
    """Analyze the Freepik API error from the logs"""
    
    print("🔍 FREEPIK API ERROR ANALYSIS")
    print("="*50)
    
    # Error from the logs
    error_response = {
        "message": "Unauthorized: No API key provided. Please obtain an API key at https://www.freepik.com/api. If you already have one, verify it at https://www.freepik.com/developers/dashboard/api-key. For more details, refer to our API documentation: https://docs.freepik.com/introduction."
    }
    
    api_key_used = "FPSXecf0a3...cdd6"  # From the logs
    status_code = 401
    
    print(f"❌ Error: {error_response['message']}")
    print(f"🔑 API Key Used: {api_key_used}")
    print(f"📡 HTTP Status: {status_code}")
    
    print("\n🔍 ANALYSIS:")
    
    # Analysis based on the error message
    issues = []
    solutions = []
    
    if "No API key provided" in error_response['message']:
        issues.append("❌ Server claims no API key was provided")
        solutions.append("🔧 API key may not be reaching the server correctly")
        
    if status_code == 401:
        issues.append("❌ Authentication failure")
        solutions.append("🔧 API key format or transmission method incorrect")
    
    if api_key_used.startswith("FPSX"):
        print("✅ API key format looks correct (starts with FPSX)")
    else:
        issues.append("❌ API key format may be incorrect")
        solutions.append("🔧 Verify API key starts with 'FPSX'")
    
    print("\n📊 IDENTIFIED ISSUES:")
    for issue in issues:
        print(f"  {issue}")
    
    print("\n💡 POTENTIAL SOLUTIONS:")
    for solution in solutions:
        print(f"  {solution}")
    
    print("\n🔧 AUTHENTICATION METHOD RECOMMENDATIONS:")
    print("Based on the error, try these authentication methods:")
    
    auth_recommendations = [
        {
            "method": "X-Freepik-API-Key Header",
            "reason": "Some APIs require custom header names",
            "headers": {
                "X-Freepik-API-Key": "YOUR_API_KEY",
                "Content-Type": "application/json"
            }
        },
        {
            "method": "freepikkey Header",
            "reason": "Freepik might use a specific header name",
            "headers": {
                "freepikkey": "YOUR_API_KEY",
                "Content-Type": "application/json"
            }
        },
        {
            "method": "API Key in URL Parameters",
            "reason": "Some APIs expect key as URL parameter",
            "url": "https://api.freepik.com/v1/ai/text-to-image?api_key=YOUR_API_KEY"
        },
        {
            "method": "Authorization with API prefix",
            "reason": "Some APIs need specific Authorization format",
            "headers": {
                "Authorization": "API YOUR_API_KEY",
                "Content-Type": "application/json"
            }
        }
    ]
    
    for i, rec in enumerate(auth_recommendations, 1):
        print(f"\n{i}. {rec['method']}")
        print(f"   Reason: {rec['reason']}")
        if 'headers' in rec:
            print(f"   Headers: {json.dumps(rec['headers'], indent=6)}")
        if 'url' in rec:
            print(f"   URL: {rec['url']}")
    
    print("\n🌐 NEXT STEPS:")
    print("1. Update the FreepikAPIClient to try these authentication methods")
    print("2. Test each method until one works")
    print("3. Check Freepik API documentation for correct auth method")
    print("4. Verify API key permissions and account status")
    
    return auth_recommendations


def create_fixed_api_client_code():
    """Generate improved API client code based on analysis"""
    
    print("\n" + "="*60)
    print("🛠️  IMPROVED API CLIENT CODE")
    print("="*60)
    
    code = '''
async def _authenticate_request(self, session, url, payload):
    """Try multiple authentication methods until one works"""
    
    auth_methods = [
        # Method 1: X-Freepik-API-Key header (most likely)
        {
            "name": "X-Freepik-API-Key",
            "headers": {
                "X-Freepik-API-Key": self.api_key,
                "Content-Type": "application/json",
                "User-Agent": "AstraBot/2.0"
            }
        },
        # Method 2: Custom freepik header
        {
            "name": "freepikkey", 
            "headers": {
                "freepikkey": self.api_key,
                "Content-Type": "application/json",
                "User-Agent": "AstraBot/2.0"
            }
        },
        # Method 3: API prefix in Authorization
        {
            "name": "API Authorization",
            "headers": {
                "Authorization": f"API {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "AstraBot/2.0"
            }
        },
        # Method 4: Bearer token (standard but might not work)
        {
            "name": "Bearer Token",
            "headers": {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json", 
                "User-Agent": "AstraBot/2.0"
            }
        }
    ]
    
    # Try URL parameter method
    url_with_key = f"{url}?api_key={self.api_key}"
    try:
        async with session.post(url_with_key, json=payload) as response:
            if response.status != 401:
                logger.info("✅ URL parameter authentication worked!")
                return response
    except:
        pass
    
    # Try header methods
    for method in auth_methods:
        try:
            async with session.post(url, headers=method["headers"], json=payload) as response:
                if response.status != 401:
                    logger.info(f"✅ {method['name']} authentication worked!")
                    return response
                else:
                    logger.warning(f"❌ {method['name']} failed with 401")
        except Exception as e:
            logger.warning(f"❌ {method['name']} failed with error: {e}")
    
    # If all methods fail, return the last response for error handling
    return response
'''
    
    print(code)
    
    return code


def main():
    """Run the diagnostic analysis"""
    print("🚀 Starting Freepik API Diagnostic Analysis")
    print("Based on the error logs from your Railway deployment\n")
    
    # Analyze the error
    recommendations = analyze_freepik_error()
    
    # Generate improved code
    improved_code = create_fixed_api_client_code()
    
    print("\n🎯 SUMMARY:")
    print("The issue is likely that Freepik API doesn't use standard Bearer token authentication.")
    print("The server is saying 'No API key provided' even though we're sending one.")
    print("This suggests the API key is not being sent in the expected format/location.")
    print("\n🔧 ACTION REQUIRED:")
    print("Update the FreepikAPIClient to try the recommended authentication methods.")


if __name__ == "__main__":
    main()
