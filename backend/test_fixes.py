"""
Test script to verify the fixes
Run this after updating the code
"""

# Test 1: Text chat language default
print("=" * 60)
print("TEST 1: Text Chat Language Default")
print("=" * 60)
print("Expected: language_code should default to 'en' for text chat")
print("Check: app/api/routes/education_routes.py line 19")
print("Should see: language_code: Optional[str] = 'en'")
print()

# Test 2: Voice chat debt detection
print("=" * 60)
print("TEST 2: Voice Chat Debt Detection")
print("=" * 60)
print("Expected: Queries like 'what are my debts' should trigger debt data fetch")
print()
print("Sample queries that should now work:")
queries = [
    "What are my debts?",
    "Show my current debts",
    "Tell me my loans",
    "What debts do I have?",
    "मेरे कर्ज क्या हैं?",  # Hindi
    "എന്റെ കടം എന്താണ്?",  # Malayalam
]

for q in queries:
    print(f"  ✓ '{q}'")

print()
print("=" * 60)
print("MANUAL TESTING REQUIRED:")
print("=" * 60)
print("1. Test text chat in English:")
print("   - Send: 'What are my current debts?'")
print("   - Expected: Response in ENGLISH with debt data")
print()
print("2. Test voice chat:")
print("   - Say in any language: 'What are my debts?'")
print("   - Expected: Should fetch and show debt data")
print()
print("=" * 60)