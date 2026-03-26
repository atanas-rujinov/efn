"""
Simple test script to verify Gemini API works
Run this before starting the full API server
"""
from gemini_service import get_ai_advice

# Test the Gemini service directly
print("Testing Gemini API...\n")

test_disability = "Mobility impairment - wheelchair user"
test_description = "I need to go to the supermarket to buy groceries and household items"

print(f"Disability: {test_disability}")
print(f"Request: {test_description}\n")
print("=" * 70)

advice = get_ai_advice(
    disability=test_disability,
    request_description=test_description,
    request_type="drive"
)

print(advice)
print("=" * 70)
print("\n✓ Advice generated successfully!")
