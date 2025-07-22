"""Simple test for Gemini CLI in Docker"""

import subprocess
import os
import json


def test_gemini_cli():
    """Test Gemini CLI availability and basic functionality"""
    
    print("\n=== Testing Gemini CLI ===\n")
    
    # 1. Check if gemini command exists
    print("1. Checking for 'gemini' command:")
    result = subprocess.run(['which', 'gemini'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"   ✓ Found at: {result.stdout.strip()}")
        gemini_cmd = 'gemini'
    else:
        print("   ✗ 'gemini' command not found")
        
        # Try with npx
        print("\n2. Trying with npx:")
        result = subprocess.run(['npx', '@google/gemini-cli', '--help'], capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✓ npx @google/gemini-cli works")
            gemini_cmd = 'npx @google/gemini-cli'
        else:
            print("   ✗ npx @google/gemini-cli failed")
            print(f"   Error: {result.stderr}")
            raise AssertionError("Gemini CLI not available")
    
    # 2. Test with API key
    api_key = os.environ.get('GOOGLE_AI_STUDIO_KEY')
    if not api_key:
        print("\n3. Skipping API test - GOOGLE_AI_STUDIO_KEY not set")
        return
    print(f"\n3. Testing with API key: {api_key[:10]}...")
    
    # Simple test prompt
    test_prompt = "Say 'Hello World' and nothing else"
    
    # Set environment
    env = os.environ.copy()
    env['GOOGLE_AI_STUDIO_KEY'] = api_key
    env['GEMINI_API_KEY'] = api_key
    
    # Test command
    if gemini_cmd == 'gemini':
        cmd = ['gemini', '--api-key', api_key, '-p', test_prompt]
    else:
        # For npx version
        cmd = ['npx', '@google/gemini-cli', '--api-key', api_key, '-p', test_prompt]
    
    print(f"\n4. Running command: {' '.join(cmd[:4])}...")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1200,  # 20 分钟超时
            env=env
        )
        
        print(f"   Return code: {result.returncode}")
        print(f"   Output: {result.stdout[:100]}...")
        if result.stderr:
            print(f"   Error: {result.stderr[:100]}...")
            
        if result.returncode == 0:
            print("\n✓ Gemini CLI test passed!")
            return True
        else:
            print("\n✗ Gemini CLI test failed")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n✗ Command timed out")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


if __name__ == '__main__':
    success = test_gemini_cli()
    exit(0 if success else 1)