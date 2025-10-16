"""
Email Sender Guardrails
Additional safety and validation layers for email sending
"""

import re
from typing import Dict, List, Tuple
from datetime import datetime, timedelta


class EmailGuardrails:
    """
    Guardrail system specifically for email sending operations
    Provides multiple layers of validation and safety checks
    """
    
    def __init__(self):
        self.sent_count = 0
        self.daily_limit = 500  # Gmail's daily limit
        self.hourly_limit = 50
        self.send_history: List[datetime] = []
        
        # Spam indicator patterns
        self.spam_patterns = [
            r'!!!+',  # Multiple exclamation marks
            r'\$\$\$+',  # Multiple dollar signs
            r'FREE!!!',  # Excessive free offers
            r'CLICK HERE NOW',  # Pushy CTAs
            r'ACT NOW',
            r'LIMITED TIME',
            r'100% FREE',
            r'EARN \$\$\$',
        ]
        
        # Suspicious keywords
        self.suspicious_keywords = [
            'viagra', 'cialis', 'casino', 'lottery', 'winner',
            'nigerian prince', 'inheritance', 'bank transfer',
            'password', 'social security', 'credit card'
        ]
        
    def check_spam_score(self, subject: str, body: str) -> Dict[str, any]:
        """
        Calculate spam score for email content
        
        Args:
            subject: Email subject line
            body: Email body content
            
        Returns:
            Dict with spam score and details
        """
        spam_score = 0
        issues = []
        
        content = f"{subject} {body}".lower()
        
        # Check for spam patterns
        for pattern in self.spam_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                spam_score += 10
                issues.append(f"Spam pattern detected: {pattern}")
        
        # Check for suspicious keywords
        for keyword in self.suspicious_keywords:
            if keyword in content:
                spam_score += 15
                issues.append(f"Suspicious keyword: {keyword}")
        
        # Check for excessive caps
        caps_ratio = sum(1 for c in content if c.isupper()) / max(len(content), 1)
        if caps_ratio > 0.3:
            spam_score += 20
            issues.append(f"Excessive caps: {caps_ratio:.1%}")
        
        # Check for excessive exclamation marks
        exclaim_count = content.count('!')
        if exclaim_count > 3:
            spam_score += 5 * (exclaim_count - 3)
            issues.append(f"Too many exclamation marks: {exclaim_count}")
        
        # Check subject length (too short or too long)
        if len(subject) < 10:
            spam_score += 5
            issues.append("Subject too short")
        elif len(subject) > 100:
            spam_score += 5
            issues.append("Subject too long")
        
        is_spam = spam_score >= 30
        
        return {
            "is_spam": is_spam,
            "spam_score": spam_score,
            "issues": issues,
            "severity": "high" if spam_score >= 50 else "medium" if spam_score >= 30 else "low"
        }
    
    def check_rate_limits(self) -> Tuple[bool, str]:
        """
        Check if sending email would violate rate limits
        
        Returns:
            Tuple of (can_send: bool, message: str)
        """
        now = datetime.now()
        
        # Clean old history
        one_hour_ago = now - timedelta(hours=1)
        one_day_ago = now - timedelta(days=1)
        self.send_history = [ts for ts in self.send_history if ts > one_day_ago]
        
        # Check hourly limit
        recent_hour = [ts for ts in self.send_history if ts > one_hour_ago]
        if len(recent_hour) >= self.hourly_limit:
            return False, f"Hourly limit reached: {len(recent_hour)}/{self.hourly_limit} emails"
        
        # Check daily limit
        if len(self.send_history) >= self.daily_limit:
            return False, f"Daily limit reached: {len(self.send_history)}/{self.daily_limit} emails"
        
        return True, "Rate limits OK"
    
    def validate_email_format(self, email: str) -> Dict[str, any]:
        """
        Validate email address format
        
        Args:
            email: Email address to validate
            
        Returns:
            Dict with validation results
        """
        issues = []
        
        # Basic format check
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            issues.append("Invalid email format")
        
        # Check for common typos
        if '.con' in email or '.cmo' in email:
            issues.append("Possible typo in domain")
        
        # Check for disposable email domains
        disposable_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
        domain = email.split('@')[1] if '@' in email else ''
        if domain in disposable_domains:
            issues.append("Disposable email domain detected")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues
        }
    
    def check_content_safety(self, body: str) -> Dict[str, any]:
        """
        Check email content for safety issues
        
        Args:
            body: Email body content
            
        Returns:
            Dict with safety check results
        """
        issues = []
        
        # Check for links (potential phishing)
        link_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        links = re.findall(link_pattern, body)
        if len(links) > 5:
            issues.append(f"Too many links: {len(links)}")
        
        # Check for suspicious link patterns
        for link in links:
            if any(sus in link.lower() for sus in ['bit.ly', 'tinyurl', 'goo.gl']):
                issues.append(f"Shortened URL detected: {link}")
        
        # Check for potential phishing phrases
        phishing_phrases = [
            'verify your account',
            'confirm your identity',
            'update your information',
            'suspended account',
            'unusual activity'
        ]
        for phrase in phishing_phrases:
            if phrase in body.lower():
                issues.append(f"Potential phishing phrase: {phrase}")
        
        # Check for HTML injection
        if '<script' in body.lower() or 'javascript:' in body.lower():
            issues.append("Potential script injection detected")
        
        return {
            "is_safe": len(issues) == 0,
            "issues": issues,
            "severity": "high" if len(issues) > 3 else "medium" if len(issues) > 0 else "low"
        }
    
    def validate_personalization(self, body: str, recipient_name: str = None) -> Dict[str, any]:
        """
        Check if email has appropriate personalization
        
        Args:
            body: Email body content
            recipient_name: Optional recipient name to check for
            
        Returns:
            Dict with personalization check results
        """
        issues = []
        warnings = []
        
        # Check for generic greetings
        generic_greetings = ['dear sir/madam', 'to whom it may concern', 'dear customer']
        if any(greeting in body.lower() for greeting in generic_greetings):
            warnings.append("Generic greeting detected - consider personalizing")
        
        # Check for recipient name if provided
        if recipient_name and recipient_name.lower() not in body.lower():
            warnings.append(f"Recipient name '{recipient_name}' not found in email")
        
        # Check for merge tags that weren't replaced
        if '{{' in body or '}}' in body or '[NAME]' in body:
            issues.append("Unreplaced merge tags detected")
        
        return {
            "is_personalized": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def run_all_checks(self, 
                      subject: str, 
                      body: str, 
                      recipient_email: str,
                      recipient_name: str = None) -> Dict[str, any]:
        """
        Run all guardrail checks on email before sending
        
        Args:
            subject: Email subject
            body: Email body
            recipient_email: Recipient email address
            recipient_name: Optional recipient name
            
        Returns:
            Dict with all check results and overall pass/fail
        """
        results = {
            "passed": True,
            "checks": {},
            "blocking_issues": [],
            "warnings": []
        }
        
        # 1. Rate limit check
        can_send, rate_msg = self.check_rate_limits()
        results["checks"]["rate_limit"] = {
            "passed": can_send,
            "message": rate_msg
        }
        if not can_send:
            results["passed"] = False
            results["blocking_issues"].append(rate_msg)
        
        # 2. Email format validation
        email_validation = self.validate_email_format(recipient_email)
        results["checks"]["email_format"] = email_validation
        if not email_validation["is_valid"]:
            results["passed"] = False
            results["blocking_issues"].extend(email_validation["issues"])
        
        # 3. Spam score check
        spam_check = self.check_spam_score(subject, body)
        results["checks"]["spam"] = spam_check
        if spam_check["is_spam"]:
            results["passed"] = False
            results["blocking_issues"].append(
                f"High spam score: {spam_check['spam_score']}"
            )
        elif spam_check["spam_score"] > 15:
            results["warnings"].extend(spam_check["issues"])
        
        # 4. Content safety check
        safety_check = self.check_content_safety(body)
        results["checks"]["safety"] = safety_check
        if not safety_check["is_safe"] and safety_check["severity"] == "high":
            results["passed"] = False
            results["blocking_issues"].extend(safety_check["issues"])
        elif not safety_check["is_safe"]:
            results["warnings"].extend(safety_check["issues"])
        
        # 5. Personalization check (non-blocking)
        personalization = self.validate_personalization(body, recipient_name)
        results["checks"]["personalization"] = personalization
        if personalization["warnings"]:
            results["warnings"].extend(personalization["warnings"])
        
        return results
    
    def record_send(self):
        """Record that an email was sent"""
        self.send_history.append(datetime.now())
        self.sent_count += 1
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get statistics about email sending
        
        Returns:
            Dict with sending statistics
        """
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        one_day_ago = now - timedelta(days=1)
        
        recent_hour = [ts for ts in self.send_history if ts > one_hour_ago]
        recent_day = [ts for ts in self.send_history if ts > one_day_ago]
        
        return {
            "total_sent": self.sent_count,
            "sent_last_hour": len(recent_hour),
            "sent_last_24h": len(recent_day),
            "hourly_limit": self.hourly_limit,
            "daily_limit": self.daily_limit,
            "hourly_remaining": self.hourly_limit - len(recent_hour),
            "daily_remaining": self.daily_limit - len(recent_day)
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_guardrails():
    """Example of using email guardrails"""
    
    guardrails = EmailGuardrails()
    
    # Example 1: Good email
    print("=" * 60)
    print("Example 1: Professional Email")
    print("=" * 60)
    
    result1 = guardrails.run_all_checks(
        subject="Quick question about your compliance needs",
        body="""Hi John,

I noticed your company is in the fintech space and thought you might be 
interested in our AI-powered compliance solution.

Would you be open to a quick 15-minute call next week?

Best regards,
Sales Team""",
        recipient_email="john@company.com",
        recipient_name="John"
    )
    
    print(f"✅ Passed: {result1['passed']}")
    print(f"Blocking issues: {result1['blocking_issues']}")
    print(f"Warnings: {result1['warnings']}")
    
    # Example 2: Spammy email
    print("\n" + "=" * 60)
    print("Example 2: Spammy Email")
    print("=" * 60)
    
    result2 = guardrails.run_all_checks(
        subject="FREE!!! AMAZING OFFER!!! ACT NOW!!!",
        body="""CLICK HERE NOW!!! 100% FREE!!!

You've been selected as a WINNER!!!

CLICK HERE: http://bit.ly/suspicious

ACT NOW!!! LIMITED TIME!!!""",
        recipient_email="victim@email.com"
    )
    
    print(f"✅ Passed: {result2['passed']}")
    print(f"Blocking issues: {result2['blocking_issues']}")
    print(f"Spam score: {result2['checks']['spam']['spam_score']}")
    
    # Example 3: Get statistics
    print("\n" + "=" * 60)
    print("Sending Statistics")
    print("=" * 60)
    
    stats = guardrails.get_statistics()
    print(f"Sent last hour: {stats['sent_last_hour']}/{stats['hourly_limit']}")
    print(f"Sent last 24h: {stats['sent_last_24h']}/{stats['daily_limit']}")


if __name__ == "__main__":
    example_guardrails()
