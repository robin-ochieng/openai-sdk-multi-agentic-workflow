"""
Test 1: Basic Guardrails Functionality
Tests guardrail validation without sending actual emails
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from email_sender.guardrails_email import EmailGuardrails


def test_professional_email():
    """Test 1.1: Professional email should PASS all guardrails"""
    print("\n" + "=" * 70)
    print("TEST 1.1: Professional Email (Should PASS)")
    print("=" * 70)
    
    guardrails = EmailGuardrails()
    
    subject = "Quick question about your compliance solution"
    body = """Hi John,

I noticed your company is in the fintech space and thought you might be 
interested in our AI-powered compliance solution for SOC2 preparation.

Our tool has helped over 100 companies achieve compliance 50% faster.

Would you be open to a quick 15-minute call next week to discuss?

Best regards,
Sales Team
ComplAI"""
    
    result = guardrails.run_all_checks(
        subject=subject,
        body=body,
        recipient_email="john@company.com",
        recipient_name="John"
    )
    
    # Display results
    print(f"\n📧 Subject: {subject}")
    print(f"📬 To: john@company.com")
    print(f"\n📊 RESULTS:")
    print(f"   Overall: {'✅ PASSED' if result['passed'] else '❌ FAILED'}")
    print(f"   Spam Score: {result['checks']['spam']['spam_score']}/100 ({result['checks']['spam']['severity']})")
    print(f"   Email Format: {'✅ Valid' if result['checks']['email_format']['is_valid'] else '❌ Invalid'}")
    print(f"   Content Safety: {'✅ Safe' if result['checks']['safety']['is_safe'] else '❌ Unsafe'}")
    print(f"   Rate Limit: {'✅ OK' if result['checks']['rate_limit']['passed'] else '❌ Exceeded'}")
    
    if result['blocking_issues']:
        print(f"\n❌ BLOCKING ISSUES:")
        for issue in result['blocking_issues']:
            print(f"   - {issue}")
    
    if result['warnings']:
        print(f"\n⚠️  WARNINGS:")
        for warning in result['warnings']:
            print(f"   - {warning}")
    
    # Assert expectations
    assert result['passed'], "Professional email should pass guardrails"
    assert result['checks']['spam']['spam_score'] < 30, "Spam score should be low"
    
    print(f"\n✅ TEST 1.1 PASSED: Professional email approved by guardrails")
    return True


def test_spammy_email():
    """Test 1.2: Spammy email should FAIL guardrails"""
    print("\n" + "=" * 70)
    print("TEST 1.2: Spammy Email (Should FAIL)")
    print("=" * 70)
    
    guardrails = EmailGuardrails()
    
    subject = "FREE!!! AMAZING OFFER!!! ACT NOW!!!"
    body = """CLICK HERE NOW!!! 100% FREE!!!

You've been selected as a WINNER!!! 

Get your FREE PRIZE NOW: http://bit.ly/suspicious-link

LIMITED TIME OFFER!!! ACT NOW!!!

CLICK HERE TO CLAIM YOUR $$$!!!"""
    
    result = guardrails.run_all_checks(
        subject=subject,
        body=body,
        recipient_email="victim@email.com"
    )
    
    # Display results
    print(f"\n📧 Subject: {subject}")
    print(f"📬 To: victim@email.com")
    print(f"\n📊 RESULTS:")
    print(f"   Overall: {'✅ PASSED' if result['passed'] else '❌ FAILED (Expected)'}")
    print(f"   Spam Score: {result['checks']['spam']['spam_score']}/100 ({result['checks']['spam']['severity']})")
    print(f"   Email Format: {'✅ Valid' if result['checks']['email_format']['is_valid'] else '❌ Invalid'}")
    
    if result['blocking_issues']:
        print(f"\n❌ BLOCKING ISSUES (Expected):")
        for issue in result['blocking_issues']:
            print(f"   - {issue}")
    
    if result['checks']['spam']['issues']:
        print(f"\n📋 SPAM INDICATORS DETECTED:")
        for issue in result['checks']['spam']['issues']:
            print(f"   - {issue}")
    
    # Assert expectations
    assert not result['passed'], "Spammy email should be blocked"
    assert result['checks']['spam']['spam_score'] >= 30, "Spam score should be high"
    assert result['checks']['spam']['is_spam'], "Should be flagged as spam"
    
    print(f"\n✅ TEST 1.2 PASSED: Spammy email correctly blocked by guardrails")
    return True


def test_invalid_email_format():
    """Test 1.3: Invalid email format should FAIL"""
    print("\n" + "=" * 70)
    print("TEST 1.3: Invalid Email Format (Should FAIL)")
    print("=" * 70)
    
    guardrails = EmailGuardrails()
    
    result = guardrails.run_all_checks(
        subject="Test email",
        body="This is a test message",
        recipient_email="invalid-email-format"  # Invalid format
    )
    
    print(f"\n📬 To: invalid-email-format")
    print(f"\n📊 RESULTS:")
    print(f"   Overall: {'✅ PASSED' if result['passed'] else '❌ FAILED (Expected)'}")
    print(f"   Email Format: {'✅ Valid' if result['checks']['email_format']['is_valid'] else '❌ Invalid (Expected)'}")
    
    if result['blocking_issues']:
        print(f"\n❌ BLOCKING ISSUES (Expected):")
        for issue in result['blocking_issues']:
            print(f"   - {issue}")
    
    # Assert expectations
    assert not result['passed'], "Invalid email should be blocked"
    assert not result['checks']['email_format']['is_valid'], "Email format should be invalid"
    
    print(f"\n✅ TEST 1.3 PASSED: Invalid email format correctly blocked")
    return True


def test_rate_limiting():
    """Test 1.4: Rate limiting functionality"""
    print("\n" + "=" * 70)
    print("TEST 1.4: Rate Limiting")
    print("=" * 70)
    
    guardrails = EmailGuardrails()
    
    # Simulate sending emails
    print("\n📧 Simulating email sends...")
    for i in range(5):
        guardrails.record_send()
        print(f"   Email {i+1} recorded")
    
    # Check statistics
    stats = guardrails.get_statistics()
    
    print(f"\n📊 STATISTICS:")
    print(f"   Total sent: {stats['total_sent']}")
    print(f"   Sent last hour: {stats['sent_last_hour']}/{ stats['hourly_limit']}")
    print(f"   Sent last 24h: {stats['sent_last_24h']}/{stats['daily_limit']}")
    print(f"   Hourly remaining: {stats['hourly_remaining']}")
    print(f"   Daily remaining: {stats['daily_remaining']}")
    
    # Check rate limits
    can_send, message = guardrails.check_rate_limits()
    print(f"\n🚦 Rate Limit Check: {'✅ Can send' if can_send else '❌ Blocked'}")
    print(f"   Message: {message}")
    
    # Assert expectations
    assert stats['total_sent'] == 5, "Should have recorded 5 sends"
    assert can_send, "Should still be under rate limits"
    
    print(f"\n✅ TEST 1.4 PASSED: Rate limiting working correctly")
    return True


def test_personalization_warnings():
    """Test 1.5: Personalization check (non-blocking)"""
    print("\n" + "=" * 70)
    print("TEST 1.5: Personalization Warnings")
    print("=" * 70)
    
    guardrails = EmailGuardrails()
    
    # Test with generic greeting
    subject = "Business opportunity"
    body = """Dear Sir/Madam,

I wanted to reach out regarding our product.

Best regards,
Sales Team"""
    
    result = guardrails.run_all_checks(
        subject=subject,
        body=body,
        recipient_email="prospect@company.com",
        recipient_name="Sarah"  # Name not in email
    )
    
    print(f"\n📧 Subject: {subject}")
    print(f"📬 To: prospect@company.com")
    print(f"👤 Expected Name: Sarah")
    
    print(f"\n📊 RESULTS:")
    print(f"   Overall: {'✅ PASSED' if result['passed'] else '❌ FAILED'}")
    
    if result['warnings']:
        print(f"\n⚠️  WARNINGS (Expected):")
        for warning in result['warnings']:
            print(f"   - {warning}")
    
    # Assert expectations
    assert result['passed'], "Should pass despite personalization warnings"
    assert len(result['warnings']) > 0, "Should have personalization warnings"
    
    print(f"\n✅ TEST 1.5 PASSED: Personalization warnings detected (non-blocking)")
    return True


def run_all_tests():
    """Run all basic guardrail tests"""
    print("\n" + "=" * 70)
    print("🛡️  BASIC GUARDRAILS TEST SUITE")
    print("=" * 70)
    print("\nTesting guardrail functionality without sending emails...")
    
    tests = [
        ("Professional Email", test_professional_email),
        ("Spammy Email", test_spammy_email),
        ("Invalid Email Format", test_invalid_email_format),
        ("Rate Limiting", test_rate_limiting),
        ("Personalization", test_personalization_warnings),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {test_name}")
            print(f"   Error: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"\n❌ TEST ERROR: {test_name}")
            print(f"   Error: {str(e)}")
            failed += 1
    
    # Final summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"   Total Tests: {len(tests)}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   Success Rate: {(passed/len(tests)*100):.1f}%")
    
    if failed == 0:
        print(f"\n🎉 ALL TESTS PASSED! Guardrails are working correctly.")
    else:
        print(f"\n⚠️  Some tests failed. Please review the output above.")
    
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
