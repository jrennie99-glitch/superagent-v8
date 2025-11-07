#!/usr/bin/env python3
"""
Test all AI providers to ensure they work correctly
"""
import os
import sys

def test_gemini():
    """Test Google Gemini API"""
    print("\n" + "="*60)
    print("Testing Google Gemini API")
    print("="*60)
    
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if not gemini_key:
        print("❌ No Gemini API key found")
        print("   Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable")
        return False
    
    print(f"✓ API Key found: {gemini_key[:10]}...{gemini_key[-4:]}")
    
    try:
        import google.generativeai as genai
        print("✓ google-generativeai library installed")
    except ImportError as e:
        print(f"❌ google-generativeai library not installed: {e}")
        print("   Run: pip install google-generativeai")
        return False
    
    try:
        genai.configure(api_key=gemini_key)
        print("✓ API configured")
        
        # Test with gemini-2.0-flash-exp
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        print("✓ Model initialized: gemini-2.0-flash-exp")
        
        response = model.generate_content("Say 'Hello from Gemini!' and nothing else")
        print(f"✓ API call successful")
        print(f"Response: {response.text}")
        
        return True
    except Exception as e:
        print(f"❌ Gemini API failed: {e}")
        return False

def test_groq():
    """Test Groq API"""
    print("\n" + "="*60)
    print("Testing Groq API")
    print("="*60)
    
    groq_key = os.getenv("GROQ_API_KEY")
    
    if not groq_key:
        print("❌ No Groq API key found")
        print("   Set GROQ_API_KEY environment variable")
        return False
    
    print(f"✓ API Key found: {groq_key[:10]}...{groq_key[-4:]}")
    
    try:
        import requests
        print("✓ requests library available")
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-70b-versatile",
                "messages": [{"role": "user", "content": "Say 'Hello from Groq!' and nothing else"}]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            message = result["choices"][0]["message"]["content"]
            print(f"✓ API call successful")
            print(f"Response: {message}")
            return True
        else:
            print(f"❌ Groq API returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Groq API failed: {e}")
        return False

def test_openai():
    """Test OpenAI API"""
    print("\n" + "="*60)
    print("Testing OpenAI API")
    print("="*60)
    
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_key:
        print("❌ No OpenAI API key found")
        print("   Set OPENAI_API_KEY environment variable")
        return False
    
    print(f"✓ API Key found: {openai_key[:10]}...{openai_key[-4:]}")
    
    try:
        from openai import OpenAI
        print("✓ openai library installed")
    except ImportError as e:
        print(f"❌ openai library not installed: {e}")
        print("   Run: pip install openai")
        return False
    
    try:
        client = OpenAI(api_key=openai_key)
        print("✓ Client initialized")
        
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": "Say 'Hello from OpenAI!' and nothing else"}]
        )
        
        message = response.choices[0].message.content
        print(f"✓ API call successful")
        print(f"Response: {message}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API failed: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("SuperAgent v8 - AI Provider Test Suite")
    print("="*60)
    
    results = {
        "Gemini": test_gemini(),
        "Groq": test_groq(),
        "OpenAI": test_openai()
    }
    
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    
    for provider, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{provider}: {status}")
    
    working_count = sum(results.values())
    total_count = len(results)
    
    print("\n" + "="*60)
    if working_count == 0:
        print("❌ NO AI PROVIDERS WORKING")
        print("   SuperAgent will use template generator as fallback")
        print("\nTo fix:")
        print("1. Get API keys from:")
        print("   - Gemini: https://makersuite.google.com/app/apikey")
        print("   - Groq: https://console.groq.com/keys")
        print("   - OpenAI: https://platform.openai.com/api-keys")
        print("2. Set environment variables:")
        print("   export GEMINI_API_KEY='your-key'")
        print("   export GROQ_API_KEY='your-key'")
        print("   export OPENAI_API_KEY='your-key'")
        return 1
    elif working_count < total_count:
        print(f"⚠️  {working_count}/{total_count} AI providers working")
        print("   SuperAgent will use working providers")
        return 0
    else:
        print(f"✅ ALL {total_count} AI PROVIDERS WORKING")
        print("   SuperAgent is fully operational!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
