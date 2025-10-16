"""
Test 2: Guardrails with Gmail SMTP Integration
Tests guardrails protecting actual email sending via Gmail SMTP
"""
import sys
import os
import asyncio

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from email_sender import EmailConfig, GmailSender
from email_sender.guardrails_email import EmailGuardrails


class ProtectedGmailSender:
    """
    Gmail sender with integrated guardrails
    All emails are validated before sending
    """
    
    def __init__(self, config: EmailConfig):
        self.sender = GmailSender(config)
        self.guardrails = EmailGuardrails()
        self.config = config
    
    def send_with_guardrails(self, subject: str, body: str, to_email: str = None) -> dict:
        """
        Send email with full guardrail protection
        
        Returns:
            dict with result including guardrail checks
        """
        recipient = to_email or self.config.recipient_email
        
        print(f"\n🛡️  Running guardrail checks...")
        
        # Run all guardrails
        validation = self.guardrails.run_all_checks(
            subject=subject,
            body=body,
            recipient_email=recipient
        )
        
        # Display guardrail results
        print(f"\n📊 Guardrail Results:")
        print(f"   Overall: {'✅ PASSED' if validation['passed'] else '❌ FAILED'}")
        print(f"   Spam Score: {validation['checks']['spam']['spam_score']}/100")
        print(f"   Severity: {validation['checks']['spam']['severity']}")
        
        if validation['blocking_issues']:
            print(f"\n❌ BLOCKING ISSUES:")
            for issue in validation['blocking_issues']:
                print(f"   - {issue}")
        
        if validation['warnings']:
            print(f"\n⚠️  WARNINGS:")
            for warning in validation['warnings']:
                print(f"   - {warning}")
        
        # Check statistics
        stats = self.guardrails.get_statistics()
        print(f"\n📧 Sending Statistics:")
        print(f"   This hour: {stats['sent_last_hour']}/{stats['hourly_limit']}")
        print(f"   Today: {stats['sent_last_24h']}/{stats['daily_limit']}")
        
        # Decision point
        if not validation['passed']:
            print(f"\n🚫 EMAIL BLOCKED BY GUARDRAILS")
            return {
                "status": "blocked",
                "reason": validation['blocking_issues'],
                "validation": validation,
                "sent": False
            }
        
        # Send the email
        print(f"\n✅ Guardrails passed - sending email...")
        
        try:
            send_result = self.sender.send_html_email(
                subject=subject,
                html_body=body,
                to_email=recipient
            )
            
            # Record the send for rate limiting
            self.guardrails.record_send()
            
            print(f"📬 Email sent successfully!")
            print(f"   Status: {send_result.get('message', 'Success')}")
            
            return {
                "status": "success",
                "sent": True,
                "send_result": send_result,
                "validation": validation,
                "recipient": recipient
            }
            
        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "validation": validation,
                "sent": False
            }


def test_protected_professional_email():
    """Test 2.1: Send professional email with guardrails (should succeed)"""
    print("\n" + "=" * 70)
    print("TEST 2.1: Protected Professional Email (Should Send)")
    print("=" * 70)
    
    # Load configuration
    print("\n1. Loading Gmail configuration...")
    config = EmailConfig.from_env()
    print(f"   ✅ Gmail: {config.gmail_email}")
    print(f"   ✅ Recipient: {config.recipient_email}")
    
    # Create protected sender
    print("\n2. Creating protected Gmail sender...")
    protected_sender = ProtectedGmailSender(config)
    print(f"   ✅ Protected sender ready with guardrails")
    
    # Prepare professional email
    subject = "AI Agent System - Test Email with Guardrails"
    body = """<html>
<body>
<h2>Hello!</h2>

<p>This is a <strong>test email</strong> from our AI agent system with integrated guardrails.</p>

<h3>Guardrail Features:</h3>
<ul>
    <li>✅ Spam detection (0-100 scoring)</li>
    <li>✅ Content safety validation</li>
    <li>✅ Rate limiting (50/hour, 500/day)</li>
    <li>✅ Email format validation</li>
    <li>✅ Personalization checking</li>
</ul>

<p>This email passed all guardrail checks before being sent!</p>

<p><strong>Test Status:</strong> Professional email with low spam score</p>

<p>Best regards,<br>
AI Agent System<br>
Protected by Guardrails 🛡️</p>
</body>
</html>"""
    
    print(f"\n3. Preparing email...")
    print(f"   Subject: {subject}")
    print(f"   To: {config.recipient_email}")
    
    # Send with guardrails
    print(f"\n4. Sending with guardrail protection...")
    result = protected_sender.send_with_guardrails(
        subject=subject,
        body=body
    )
    
    # Verify results
    print(f"\n5. Verifying results...")
    assert result['status'] == 'success', f"Expected success, got {result['status']}"
    assert result['sent'], "Email should have been sent"
    assert result['validation']['passed'], "Guardrails should have passed"
    
    print(f"\n✅ TEST 2.1 PASSED: Professional email sent successfully with guardrails")
    print(f"   📬 Check your inbox at: {config.recipient_email}")
    
    return True


def test_protected_spammy_email_blocked():
    """Test 2.2: Spammy email should be blocked (should NOT send)"""
    print("\n" + "=" * 70)
    print("TEST 2.2: Protected Spammy Email (Should Block)")
    print("=" * 70)
    
    # Load configuration
    print("\n1. Loading Gmail configuration...")
    config = EmailConfig.from_env()
    
    # Create protected sender
    print("\n2. Creating protected Gmail sender...")
    protected_sender = ProtectedGmailSender(config)
    
    # Prepare spammy email (should be blocked)
    subject = "FREE MONEY!!! CLICK NOW!!! LIMITED TIME!!!"
    body = """<html>
<body>
<h1>🎉 YOU'VE WON!!! 🎉</h1>

<p><strong>CLICK HERE NOW!!!</strong></p>

<p>GET YOUR FREE $$$ NOW!!!</p>

<p><a href="http://bit.ly/suspicious">CLICK HERE FOR FREE MONEY!!!</a></p>

<p>ACT NOW!!! LIMITED TIME OFFER!!!</p>

<p>100% FREE!!! NO STRINGS ATTACHED!!!</p>

<p>WINNER WINNER CHICKEN DINNER!!!</p>
</body>
</html>"""
    
    print(f"\n3. Preparing spammy email...")
    print(f"   Subject: {subject}")
    print(f"   (This should be blocked by guardrails)")
    
    # Attempt to send (should be blocked)
    print(f"\n4. Attempting to send (should be blocked)...")
    result = protected_sender.send_with_guardrails(
        subject=subject,
        body=body
    )
    
    # Verify results
    print(f"\n5. Verifying block...")
    assert result['status'] == 'blocked', f"Expected blocked, got {result['status']}"
    assert not result['sent'], "Email should NOT have been sent"
    assert not result['validation']['passed'], "Guardrails should have failed"
    assert result['validation']['checks']['spam']['spam_score'] >= 30, "Spam score should be high"
    
    print(f"\n✅ TEST 2.2 PASSED: Spammy email correctly blocked by guardrails")
    print(f"   🚫 Email was NOT sent (as expected)")
    print(f"   Spam Score: {result['validation']['checks']['spam']['spam_score']}/100")
    
    return True


def test_rate_limit_protection():
    """Test 2.3: Rate limiting with actual Gmail sender"""
    print("\n" + "=" * 70)
    print("TEST 2.3: Rate Limit Protection")
    print("=" * 70)
    
    # Load configuration
    print("\n1. Loading Gmail configuration...")
    config = EmailConfig.from_env()
    
    # Create protected sender
    print("\n2. Creating protected Gmail sender...")
    protected_sender = ProtectedGmailSender(config)
    
    # Get initial statistics
    stats_before = protected_sender.guardrails.get_statistics()
    print(f"\n3. Initial statistics:")
    print(f"   Sent this hour: {stats_before['sent_last_hour']}/{stats_before['hourly_limit']}")
    
    # Send a test email
    subject = "Rate Limit Test - Gmail with Guardrails"
    body = """<html>
<body>
<p>This is a rate limit test email.</p>
<p>Testing that guardrails track sending statistics correctly.</p>
</body>
</html>"""
    
    print(f"\n4. Sending test email...")
    result = protected_sender.send_with_guardrails(
        subject=subject,
        body=body
    )
    
    # Get updated statistics
    stats_after = protected_sender.guardrails.get_statistics()
    print(f"\n5. Updated statistics:")
    print(f"   Sent this hour: {stats_after['sent_last_hour']}/{stats_after['hourly_limit']}")
    print(f"   Total sent: {stats_after['total_sent']}")
    
    # Verify statistics were updated
    if result['sent']:
        assert stats_after['total_sent'] > stats_before['total_sent'], "Send count should increase"
        print(f"\n✅ TEST 2.3 PASSED: Rate limit tracking working correctly")
    else:
        print(f"\n⚠️  Email was not sent (possibly blocked by guardrails)")
        print(f"   This is acceptable for rate limit test")
    
    return True


def test_multiple_emails_with_guardrails():
    """Test 2.4: Send multiple emails with different spam scores"""
    print("\n" + "=" * 70)
    print("TEST 2.4: Multiple Emails with Different Spam Scores")
    print("=" * 70)
    
    # Load configuration
    print("\n1. Loading Gmail configuration...")
    config = EmailConfig.from_env()
    
    # Create protected sender
    print("\n2. Creating protected Gmail sender...")
    protected_sender = ProtectedGmailSender(config)
    
    # Test emails with different spam levels
    test_cases = [
        {
            "name": "Low spam score",
            "subject": "Professional inquiry about services",
            "body": "<p>Hello, I'm interested in learning more about your services. Thank you.</p>",
            "should_send": True
        },
        {
            "name": "Medium spam score",
            "subject": "Great opportunity! Act fast!",
            "body": "<p>This is an amazing opportunity! Don't miss out!</p>",
            "should_send": True  # Medium is still allowed
        },
        {
            "name": "High spam score",
            "subject": "FREE!!! WIN NOW!!! CLICK HERE!!!",
            "body": "<p>FREE MONEY!!! CLICK NOW!!! LIMITED TIME!!!</p>",
            "should_send": False  # Should be blocked
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print(f"   Subject: {test_case['subject']}")
        
        result = protected_sender.send_with_guardrails(
            subject=test_case['subject'],
            body=test_case['body']
        )
        
        spam_score = result['validation']['checks']['spam']['spam_score']
        print(f"   Spam Score: {spam_score}/100")
        print(f"   Status: {'✅ Sent' if result['sent'] else '🚫 Blocked'}")
        
        results.append({
            "name": test_case['name'],
            "spam_score": spam_score,
            "sent": result['sent'],
            "expected_send": test_case['should_send']
        })
    
    # Verify all results
    print(f"\n3. Verifying results...")
    all_correct = True
    for r in results:
        if r['sent'] == r['expected_send']:
            print(f"   ✅ {r['name']}: Correct (spam: {r['spam_score']})")
        else:
            print(f"   ❌ {r['name']}: Incorrect (spam: {r['spam_score']})")
            all_correct = False
    
    assert all_correct, "All emails should behave as expected"
    
    print(f"\n✅ TEST 2.4 PASSED: Multiple emails handled correctly")
    
    return True


def run_all_tests():
    """Run all Gmail integration tests"""
    print("\n" + "=" * 70)
    print("🛡️  GMAIL SMTP + GUARDRAILS INTEGRATION TEST SUITE")
    print("=" * 70)
    print("\nTesting guardrails with actual Gmail SMTP sending...")
    print("\n⚠️  NOTE: These tests will send actual emails!")
    print("Make sure your .env file is configured correctly.")
    
    # Check if config exists
    try:
        from email_sender import EmailConfig
        config = EmailConfig.from_env()
        print(f"\n✅ Configuration loaded:")
        print(f"   Gmail: {config.gmail_email}")
        print(f"   Recipient: {config.recipient_email}")
    except Exception as e:
        print(f"\n❌ Configuration error: {str(e)}")
        print("\nPlease ensure:")
        print("1. .env file exists in project root")
        print("2. GMAIL_EMAIL is set")
        print("3. GMAIL_APP_PASSWORD is set")
        print("4. RECIPIENT_EMAIL is set")
        return False
    
    input("\n⏸️  Press Enter to continue with tests (or Ctrl+C to cancel)...")
    
    tests = [
        ("Professional Email", test_protected_professional_email),
        ("Spammy Email Block", test_protected_spammy_email_blocked),
        ("Rate Limit Protection", test_rate_limit_protection),
        ("Multiple Emails", test_multiple_emails_with_guardrails),
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
            import traceback
            traceback.print_exc()
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
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"   Guardrails are working correctly with Gmail SMTP!")
        print(f"\n📬 Check your inbox at: {config.recipient_email}")
        print(f"   You should have received test emails that passed guardrails.")
    else:
        print(f"\n⚠️  Some tests failed. Please review the output above.")
    
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
