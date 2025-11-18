#!/usr/bin/env python3
"""
Script to verify access to Webex Converged Recordings API

This script tests:
1. Current token validity
2. Organization access
3. Recordings API access
4. Required scopes
"""
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from src.services.webex_oauth import webex_oauth
from src.services.webex_client import webex_client
import httpx
from datetime import datetime, timedelta


async def verify_recordings_access():
    """Verify access to Webex Recordings API"""

    print("=" * 80)
    print("WEBEX RECORDINGS API ACCESS VERIFICATION")
    print("=" * 80)
    print()

    # Step 1: Check token
    print("1️⃣  Checking OAuth Token...")
    print("-" * 80)

    token_info = webex_oauth.get_token_info()
    print(f"   Has access token: {token_info['has_access_token']}")
    print(f"   Has refresh token: {token_info['has_refresh_token']}")
    print(f"   Token expires at: {token_info['token_expires_at']}")
    print(f"   Is expired: {token_info['is_expired']}")

    if not token_info['has_access_token']:
        print()
        print("   ❌ NO TOKEN FOUND")
        print("   → Run: python -m uvicorn src.main:app --reload")
        print("   → Visit: http://localhost:8000/auth/login")
        return False

    if token_info['is_expired']:
        print()
        print("   ⚠️  TOKEN EXPIRED - Attempting to refresh...")
        try:
            await webex_oauth.refresh_access_token()
            print("   ✅ Token refreshed successfully")
        except Exception as e:
            print(f"   ❌ Failed to refresh: {e}")
            print("   → Re-authenticate: rm .webex_tokens.json && visit /auth/login")
            return False
    else:
        print("   ✅ Token is valid")

    print()

    # Step 2: Check organization access
    print("2️⃣  Checking Organization Access...")
    print("-" * 80)

    try:
        org = await webex_client.get_organization_info()
        print(f"   Organization: {org.get('displayName')}")
        print(f"   Org ID: {org.get('id')}")
        print("   ✅ Organization access confirmed")
    except Exception as e:
        print(f"   ❌ Failed to access organization: {e}")
        return False

    print()

    # Step 3: Check current scopes
    print("3️⃣  Checking Configured Scopes...")
    print("-" * 80)

    configured_scopes = os.getenv("WEBEX_SCOPES", "").split()
    print(f"   Configured scopes in .env:")
    for scope in configured_scopes:
        print(f"      - {scope}")

    # Check for recordings scopes
    has_recordings_scope = any(
        'recordings_read' in scope
        for scope in configured_scopes
    )

    if has_recordings_scope:
        print("   ✅ Recordings scope found in configuration")
    else:
        print("   ⚠️  NO recordings scope found in .env")
        print()
        print("   Required scopes (choose one set):")
        print("   Admin:")
        print("      - spark-admin:recordings_read")
        print("      - spark-admin:recordings_write")
        print("   Compliance:")
        print("      - spark-compliance:recordings_read")
        print("      - spark-compliance:recordings_write")
        print()
        print("   Note: Scopes in .env must match scopes granted during OAuth")

    print()

    # Step 4: Test Recordings API access
    print("4️⃣  Testing Recordings API Access...")
    print("-" * 80)

    try:
        token = await webex_oauth.get_valid_token()

        # Try to list recordings
        from_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S.000Z")

        # IMPORTANT: Use /admin/ endpoint for spark-admin:recordings_read scope
        url = "https://webexapis.com/v1/admin/convergedRecordings"
        params = {
            "serviceType": "calling",
            "from": from_date,
            "max": 10
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        print(f"   GET {url}")
        print(f"   Params: serviceType=calling, from={from_date}, max=10")
        print()

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params, headers=headers)

            print(f"   Status Code: {response.status_code}")
            print()

            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])

                print("   ✅ SUCCESS - Recordings API is accessible!")
                print()
                print(f"   Found {len(items)} recording(s) in the last 30 days")

                if items:
                    print()
                    print("   Sample recording:")
                    rec = items[0]
                    print(f"      ID: {rec.get('id')}")
                    print(f"      Created: {rec.get('createTime')}")
                    print(f"      Duration: {rec.get('durationSeconds')} seconds")
                    print(f"      Topic: {rec.get('topic', 'N/A')}")
                    print(f"      Owner: {rec.get('ownerId', 'N/A')}")

                return True

            elif response.status_code == 401:
                print("   ❌ UNAUTHORIZED (401)")
                print()
                print("   Possible causes:")
                print("      - Token is invalid or expired")
                print("      - Token was revoked")
                print()
                print("   Solution:")
                print("      rm .webex_tokens.json")
                print("      python -m uvicorn src.main:app --reload")
                print("      Visit: http://localhost:8000/auth/login")
                return False

            elif response.status_code == 403:
                print("   ❌ FORBIDDEN (403)")
                print()
                print("   This means your token is valid BUT lacks required permissions")
                print()
                print("   Root cause:")
                print("      Missing recordings scope during OAuth authorization")
                print()
                print("   Solution:")
                print("      1. Update scopes in Webex Developer Portal:")
                print("         https://developer.webex.com/my-apps")
                print("         Add: spark-admin:recordings_read (and _write)")
                print()
                print("      2. Update .env file:")
                print("         WEBEX_SCOPES=analytics:read_all spark:organizations_read")
                print("         spark:people_read spark-admin:recordings_read")
                print("         spark-admin:recordings_write")
                print()
                print("      3. Re-authenticate:")
                print("         rm .webex_tokens.json")
                print("         Visit: http://localhost:8000/auth/login")
                print()
                print("      4. Run this script again to verify")

                # Try to parse error message
                try:
                    error_data = response.json()
                    print()
                    print("   API Error Details:")
                    print(f"      Message: {error_data.get('message', 'N/A')}")
                    print(f"      Tracking ID: {error_data.get('trackingId', 'N/A')}")
                except:
                    pass

                return False

            elif response.status_code == 404:
                print("   ❌ NOT FOUND (404)")
                print()
                print("   Possible causes:")
                print("      - Converged Recordings API not available for your org")
                print("      - Recording feature not enabled")
                print()
                print("   Solution:")
                print("      Contact your Webex administrator to:")
                print("      1. Enable Webex Calling Recording")
                print("      2. Configure recording provider (Webex or BroadWorks)")
                print("      3. Verify org has proper licensing")
                return False

            else:
                print(f"   ❌ UNEXPECTED ERROR ({response.status_code})")
                print()
                print(f"   Response: {response.text[:500]}")
                return False

    except Exception as e:
        print(f"   ❌ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

    print()


async def main():
    """Main function"""
    print()
    success = await verify_recordings_access()

    print()
    print("=" * 80)

    if success:
        print("✅ VERIFICATION SUCCESSFUL")
        print()
        print("You have access to Webex Recordings API!")
        print("You can now proceed with the recordings integration implementation.")
    else:
        print("❌ VERIFICATION FAILED")
        print()
        print("Follow the instructions above to fix the issues.")
        print("Run this script again after making changes.")
        print()
        print("For detailed setup guide, see: RECORDINGS_SETUP_GUIDE.md")

    print("=" * 80)
    print()

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
