"""
Send 3 Professional Emails with Guardrails Protection
Uses Gmail SMTP with comprehensive guardrail validation
"""

import os
from dotenv import load_dotenv
from email_sender import EmailConfig, GmailSender
from email_sender.guardrails_email import EmailGuardrails

# Load environment variables
load_dotenv()

class ProtectedEmailSender:
    """Gmail sender with integrated guardrails"""
    
    def __init__(self, config: EmailConfig):
        self.sender = GmailSender(config)
        self.guardrails = EmailGuardrails()
        self.sent_count = 0
    
    def send_with_guardrails(self, subject: str, body: str, to_email: str, recipient_name: str = None):
        """Send email with guardrail protection"""
        
        print(f"\n{'='*80}")
        print(f"📧 EMAIL #{self.sent_count + 1}: {subject}")
        print(f"{'='*80}")
        
        # Run all guardrails
        validation = self.guardrails.run_all_checks(
            subject=subject,
            body=body,
            recipient_email=to_email,
            recipient_name=recipient_name
        )
        
        # Display validation results
        print(f"\n🛡️ GUARDRAIL VALIDATION:")
        print(f"   Overall Status: {'✅ PASSED' if validation['passed'] else '❌ BLOCKED'}")
        
        # Spam Check
        spam = validation['checks']['spam']
        spam_emoji = "✅" if not spam['is_spam'] else "🚫"
        print(f"\n   {spam_emoji} Spam Score: {spam['spam_score']}/100 ({spam['severity']})")
        if spam.get('spam_indicators'):
            print(f"      Indicators: {', '.join(spam['spam_indicators'][:3])}")
        
        # Format Check
        format_check = validation['checks']['email_format']
        format_emoji = "✅" if format_check['is_valid'] else "❌"
        print(f"   {format_emoji} Email Format: {'Valid' if format_check['is_valid'] else 'Invalid'}")
        
        # Safety Check
        safety = validation['checks']['safety']
        safety_emoji = "✅" if safety['is_safe'] else "⚠️"
        print(f"   {safety_emoji} Content Safety: {'Safe' if safety['is_safe'] else 'Warning'}")
        
        # Rate Limit
        rate = validation['checks']['rate_limit']
        stats = self.guardrails.get_statistics()
        rate_emoji = "✅" if rate['passed'] else "🚫"
        print(f"   {rate_emoji} Rate Limit: {stats['sent_last_hour']}/50 hourly, {stats['sent_last_24h']}/500 daily")
        
        # Personalization (warnings only)
        if validation['warnings']:
            print(f"\n   ⚠️ Warnings ({len(validation['warnings'])}):")
            for warning in validation['warnings']:
                print(f"      • {warning}")
        
        # If validation failed, show blocking reasons
        if not validation['passed']:
            print(f"\n   🚫 BLOCKING REASONS:")
            for issue in validation['blocking_issues']:
                print(f"      • {issue}")
            print(f"\n   ❌ EMAIL NOT SENT (Blocked by guardrails)")
            return {
                "status": "blocked",
                "reason": validation['blocking_issues'],
                "validation": validation
            }
        
        # Send via Gmail SMTP
        print(f"\n   📤 Sending via Gmail SMTP...")
        try:
            send_result = self.sender.send_html_email(
                to_email=to_email,
                subject=subject,
                html_body=body
            )
            
            if send_result.get('success'):
                # Record successful send for rate limiting
                self.guardrails.record_send()
                self.sent_count += 1
                
                print(f"   ✅ EMAIL SENT SUCCESSFULLY!")
                print(f"   📧 To: {to_email}")
                print(f"   📊 Total Sent: {self.sent_count}")
                
                return {
                    "status": "success",
                    "sent": True,
                    "validation": validation,
                    "send_result": send_result
                }
            else:
                error_msg = send_result.get('error', send_result.get('message', 'Unknown error'))
                print(f"   ❌ SMTP Error: {error_msg}")
                return {
                    "status": "smtp_error",
                    "error": error_msg,
                    "validation": validation
                }
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "validation": validation
            }


def main():
    """Send 3 professional emails with guardrail protection"""
    
    print("\n" + "="*80)
    print("📧 PROTECTED EMAIL SENDER - 3 Professional Emails")
    print("🛡️ Guardrails: Spam Detection | Rate Limiting | Safety Checks")
    print("="*80)
    
    # Configure Gmail sender
    config = EmailConfig(
        gmail_email=os.getenv('GMAIL_EMAIL'),
        gmail_app_password=os.getenv('GMAIL_APP_PASSWORD')
    )
    
    recipient = os.getenv('RECIPIENT_EMAIL', 'robinochieng74@gmail.com')
    
    # Initialize protected sender
    protected_sender = ProtectedEmailSender(config)
    
    # Email 1: Project Update
    email1_subject = "Project Update: Q4 Milestones Achieved"
    email1_body = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .header { background-color: #4CAF50; color: white; padding: 20px; text-align: center; }
            .content { padding: 20px; }
            .milestone { background-color: #f4f4f4; padding: 10px; margin: 10px 0; border-left: 4px solid #4CAF50; }
            .footer { background-color: #f4f4f4; padding: 15px; text-align: center; font-size: 12px; color: #666; }
        </style>
    </head>
    <body>
        <div class="header">
            <h2>Q4 Project Milestones</h2>
        </div>
        <div class="content">
            <p>Hi Team,</p>
            
            <p>I'm pleased to share that we've successfully achieved our Q4 project milestones:</p>
            
            <div class="milestone">
                <strong>✅ Milestone 1:</strong> AI Agent System Implementation<br>
                Completed the multi-agent workflow with guardrails and structured outputs
            </div>
            
            <div class="milestone">
                <strong>✅ Milestone 2:</strong> Email Automation System<br>
                Integrated Gmail SMTP with comprehensive validation and safety checks
            </div>
            
            <div class="milestone">
                <strong>✅ Milestone 3:</strong> Testing Infrastructure<br>
                Created automated test suite with 100% pass rate on initial validation
            </div>
            
            <p>These achievements position us well for Q1 planning. Looking forward to discussing next steps in our upcoming meeting.</p>
            
            <p>Best regards,<br>Robin Ochieng<br>AI Systems Engineer</p>
        </div>
        <div class="footer">
            This is an automated message from the AI Agent System | Kenbright
        </div>
    </body>
    </html>
    """
    
    # Email 2: Meeting Invitation
    email2_subject = "Invitation: AI Strategy Review Meeting - October 23, 2025"
    email2_body = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .header { background-color: #2196F3; color: white; padding: 20px; text-align: center; }
            .content { padding: 20px; }
            .meeting-details { background-color: #E3F2FD; padding: 15px; margin: 15px 0; border-radius: 5px; }
            .agenda-item { padding: 8px 0; border-bottom: 1px solid #ddd; }
            .footer { background-color: #f4f4f4; padding: 15px; text-align: center; font-size: 12px; color: #666; }
        </style>
    </head>
    <body>
        <div class="header">
            <h2>📅 Meeting Invitation</h2>
        </div>
        <div class="content">
            <p>Dear Colleague,</p>
            
            <p>You are invited to attend our quarterly AI Strategy Review Meeting.</p>
            
            <div class="meeting-details">
                <h3>Meeting Details</h3>
                <p><strong>📅 Date:</strong> October 23, 2025<br>
                <strong>🕐 Time:</strong> 2:00 PM - 3:30 PM EAT<br>
                <strong>📍 Location:</strong> Virtual (Zoom link to follow)<br>
                <strong>👥 Attendees:</strong> AI Team, Product Managers, Tech Leads</p>
            </div>
            
            <h3>Agenda</h3>
            <div class="agenda-item">1. Review of Q4 AI Projects (15 min)</div>
            <div class="agenda-item">2. Guardrails Implementation Demo (20 min)</div>
            <div class="agenda-item">3. Q1 Strategy and Roadmap (30 min)</div>
            <div class="agenda-item">4. Technical Challenges Discussion (20 min)</div>
            <div class="agenda-item">5. Q&A and Next Steps (5 min)</div>
            
            <p>Please confirm your attendance by replying to this email.</p>
            
            <p>Looking forward to seeing you there!</p>
            
            <p>Best regards,<br>Robin Ochieng<br>AI Systems Team</p>
        </div>
        <div class="footer">
            Meeting organized via AI Agent System | Kenbright
        </div>
    </body>
    </html>
    """
    
    # Email 3: Technical Report
    email3_subject = "Technical Report: Guardrails System Performance Analysis"
    email3_body = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .header { background-color: #FF9800; color: white; padding: 20px; text-align: center; }
            .content { padding: 20px; }
            .metric { background-color: #FFF3E0; padding: 12px; margin: 10px 0; border-radius: 5px; }
            .metric-value { font-size: 24px; font-weight: bold; color: #FF9800; }
            .recommendation { background-color: #E8F5E9; padding: 12px; margin: 10px 0; border-left: 4px solid #4CAF50; }
            .footer { background-color: #f4f4f4; padding: 15px; text-align: center; font-size: 12px; color: #666; }
        </style>
    </head>
    <body>
        <div class="header">
            <h2>📊 Technical Performance Report</h2>
        </div>
        <div class="content">
            <p>Hello Team,</p>
            
            <p>Here's the performance analysis of our Guardrails System after initial deployment:</p>
            
            <h3>Key Metrics</h3>
            
            <div class="metric">
                <strong>Test Success Rate</strong><br>
                <span class="metric-value">100%</span><br>
                All 5 basic validation tests passed on first run
            </div>
            
            <div class="metric">
                <strong>Spam Detection Accuracy</strong><br>
                <span class="metric-value">100%</span><br>
                Correctly identified and blocked emails with spam score ≥30
            </div>
            
            <div class="metric">
                <strong>Rate Limit Tracking</strong><br>
                <span class="metric-value">Operational</span><br>
                Successfully tracking 50/hour and 500/day limits
            </div>
            
            <div class="metric">
                <strong>Email Validation</strong><br>
                <span class="metric-value">Active</span><br>
                Format validation, domain checks, and typo detection working
            </div>
            
            <h3>Technical Highlights</h3>
            <ul>
                <li><strong>Spam Score System:</strong> 0-100 scale with pattern-based detection (9 indicators identified)</li>
                <li><strong>Multi-layer Validation:</strong> Format → Spam → Safety → Rate Limit</li>
                <li><strong>Gmail Integration:</strong> Seamless SMTP integration with guardrail wrapper</li>
                <li><strong>Personalization Checks:</strong> Non-blocking warnings for better email quality</li>
            </ul>
            
            <h3>Recommendations</h3>
            
            <div class="recommendation">
                <strong>✅ Recommendation 1:</strong> Deploy to production - all tests passing<br>
                System is ready for production use with current configuration
            </div>
            
            <div class="recommendation">
                <strong>✅ Recommendation 2:</strong> Monitor rate limits during peak usage<br>
                Consider increasing limits if legitimate use cases require it
            </div>
            
            <div class="recommendation">
                <strong>✅ Recommendation 3:</strong> Enhance personalization detection<br>
                Add more sophisticated name matching algorithms
            </div>
            
            <p>Please review and provide feedback by end of week.</p>
            
            <p>Best regards,<br>Robin Ochieng<br>AI Systems Engineer<br>Technical Lead - Guardrails Project</p>
        </div>
        <div class="footer">
            Generated by AI Agent System | Kenbright | October 16, 2025
        </div>
    </body>
    </html>
    """
    
    # Send Email 1
    result1 = protected_sender.send_with_guardrails(
        subject=email1_subject,
        body=email1_body,
        to_email=recipient,
        recipient_name="Team"
    )
    
    # Send Email 2
    result2 = protected_sender.send_with_guardrails(
        subject=email2_subject,
        body=email2_body,
        to_email=recipient,
        recipient_name="Colleague"
    )
    
    # Send Email 3
    result3 = protected_sender.send_with_guardrails(
        subject=email3_subject,
        body=email3_body,
        to_email=recipient,
        recipient_name="Team"
    )
    
    # Final Summary
    print(f"\n{'='*80}")
    print(f"📊 FINAL SUMMARY")
    print(f"{'='*80}")
    print(f"   Total Emails Processed: 3")
    print(f"   ✅ Successfully Sent: {protected_sender.sent_count}")
    print(f"   🚫 Blocked by Guardrails: {3 - protected_sender.sent_count}")
    
    # Show individual results
    results = [
        ("Email 1: Project Update", result1),
        ("Email 2: Meeting Invitation", result2),
        ("Email 3: Technical Report", result3)
    ]
    
    print(f"\n   Individual Results:")
    for name, result in results:
        status_emoji = "✅" if result['status'] == 'success' else "❌"
        print(f"      {status_emoji} {name}: {result['status']}")
    
    print(f"\n{'='*80}")
    print(f"✅ Email sending complete! Check {recipient} for the messages.")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
