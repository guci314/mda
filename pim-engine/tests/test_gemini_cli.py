"""Test Gemini CLI availability and functionality in Docker"""

import pytest
import subprocess
import os
import json
from typing import Dict, Any


class TestGeminiCLI:
    """Test suite for Gemini CLI integration"""
    
    def test_gemini_cli_installed(self):
        """Test if Gemini CLI is installed in the container"""
        # Try different possible command names
        possible_commands = ['gemini', 'generative-ai-cli', 'genai']
        
        found_command = None
        for cmd in possible_commands:
            result = subprocess.run(
                ['which', cmd],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                found_command = cmd
                print(f"✓ Found Gemini CLI as: {cmd}")
                print(f"  Path: {result.stdout.strip()}")
                break
        
        assert found_command is not None, f"Gemini CLI not found. Tried: {possible_commands}"
        
        # Store the found command for other tests
        os.environ['GEMINI_CLI_COMMAND'] = found_command
        
    def test_gemini_cli_help(self):
        """Test if Gemini CLI help command works"""
        cmd = os.environ.get('GEMINI_CLI_COMMAND', 'gemini')
        
        result = subprocess.run(
            [cmd, '--help'],
            capture_output=True,
            text=True
        )
        
        print(f"\n{cmd} --help output:")
        print(result.stdout)
        
        assert result.returncode == 0, f"Failed to run {cmd} --help"
        assert 'help' in result.stdout.lower() or 'usage' in result.stdout.lower()
        
    def test_gemini_cli_version(self):
        """Test if Gemini CLI version command works"""
        cmd = os.environ.get('GEMINI_CLI_COMMAND', 'gemini')
        
        # Try both --version and version
        for version_flag in ['--version', 'version']:
            result = subprocess.run(
                [cmd, version_flag],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"\n{cmd} {version_flag} output:")
                print(result.stdout)
                return
        
        # If neither worked, try without any flag (some CLIs show version in help)
        result = subprocess.run(
            [cmd],
            capture_output=True,
            text=True
        )
        
        print(f"\nCLI output without flags:")
        print(result.stdout)
        print(result.stderr)
        
    def test_api_key_environment(self):
        """Test if API key is properly set in environment"""
        api_key = os.environ.get('GOOGLE_AI_STUDIO_KEY') or os.environ.get('GEMINI_API_KEY')
        
        assert api_key is not None, "No API key found in environment"
        assert len(api_key) > 10, "API key seems too short"
        print(f"✓ API key found: {api_key[:10]}...")
        
    def test_proxy_configuration(self):
        """Test if proxy is properly configured"""
        proxy_vars = {
            'HTTP_PROXY': os.environ.get('HTTP_PROXY'),
            'HTTPS_PROXY': os.environ.get('HTTPS_PROXY'),
            'http_proxy': os.environ.get('http_proxy'),
            'https_proxy': os.environ.get('https_proxy'),
            'NO_PROXY': os.environ.get('NO_PROXY'),
        }
        
        print("\nProxy configuration:")
        for var, value in proxy_vars.items():
            if value:
                print(f"  {var}: {value}")
        
        # Check if proxy is set
        proxy_set = any(v for k, v in proxy_vars.items() if k.lower().startswith('http'))
        assert proxy_set, "No proxy configuration found"
        
    def test_simple_prompt(self):
        """Test a simple prompt with Gemini CLI"""
        cmd = os.environ.get('GEMINI_CLI_COMMAND', 'gemini')
        api_key = os.environ.get('GOOGLE_AI_STUDIO_KEY') or os.environ.get('GEMINI_API_KEY')
        
        if not api_key:
            pytest.skip("No API key available")
        
        # Simple test prompt
        test_prompt = "Reply with just 'Hello World' and nothing else"
        
        # Try different argument formats
        cmd_variations = [
            [cmd, '--api-key', api_key, '-p', test_prompt],
            [cmd, '--key', api_key, '-p', test_prompt],
            [cmd, '-p', test_prompt],  # API key might be in env
        ]
        
        success = False
        for cmd_args in cmd_variations:
            print(f"\nTrying command: {' '.join(cmd_args[:3])}...")
            
            # Set API key in environment as well
            env = os.environ.copy()
            env['GEMINI_API_KEY'] = api_key
            env['GOOGLE_AI_API_KEY'] = api_key
            
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=1200,  # 20 分钟超时
                env=env
            )
            
            if result.returncode == 0:
                print(f"✓ Success! Output: {result.stdout}")
                success = True
                break
            else:
                print(f"✗ Failed with return code {result.returncode}")
                print(f"  stderr: {result.stderr}")
        
        assert success, "Failed to execute prompt with Gemini CLI"
        
    def test_code_generation_prompt(self):
        """Test code generation with Gemini CLI"""
        cmd = os.environ.get('GEMINI_CLI_COMMAND', 'gemini')
        api_key = os.environ.get('GOOGLE_AI_STUDIO_KEY') or os.environ.get('GEMINI_API_KEY')
        
        if not api_key:
            pytest.skip("No API key available")
        
        # Code generation prompt
        code_prompt = """Generate a simple Python function that adds two numbers. 
Only output the code, no explanation. Start with 'def add' and nothing before it."""
        
        env = os.environ.copy()
        env['GEMINI_API_KEY'] = api_key
        env['GOOGLE_AI_API_KEY'] = api_key
        
        result = subprocess.run(
            [cmd, '--api-key', api_key, '-p', code_prompt],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        
        if result.returncode == 0:
            print(f"\nGenerated code:\n{result.stdout}")
            
            # Verify it's actually code
            assert 'def add' in result.stdout, "Generated output doesn't contain expected function"
            assert 'return' in result.stdout, "Generated function doesn't have return statement"
        else:
            pytest.fail(f"Code generation failed: {result.stderr}")


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '-s'])