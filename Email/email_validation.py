"""
Email Validation
Consolidated email validation functionality
"""

import re
from typing import bool


class EmailValidation:
    """Email validation utilities."""
    
    def __init__(self):
        # Enhanced email regex pattern for better validation
        self.email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        # Common invalid email patterns
        self.invalid_patterns = [
            r'.*\.\..*',  # Double dots
            r'^\..*',     # Starting with dot
            r'.*\.$',     # Ending with dot
            r'.*@\..*',   # @ followed by dot
            r'.*\.@.*',   # Dot followed by @
        ]
        
        # Disposable email domains to block
        self.disposable_domains = {
            '10minutemail.com', 'guerrillamail.com', 'mailinator.com',
            'tempmail.org', 'trash-mail.com', 'yopmail.com',
            'dispostable.com', 'throwaway.email', 'getnada.com'
        }
    
    def validate_email(self, email: str) -> bool:
        """Validate email address format and security."""
        if not email or not isinstance(email, str):
            return False
        
        # Basic format check
        if not self.email_pattern.match(email.lower()):
            return False
        
        # Check for invalid patterns
        for pattern in self.invalid_patterns:
            if re.match(pattern, email.lower()):
                return False
        
        # Check length constraints
        if len(email) > 254:  # RFC 5321 limit
            return False
        
        username, domain = email.split('@')
        if len(username) > 64:  # RFC 5321 limit
            return False
        
        return True
    
    def is_disposable_email(self, email: str) -> bool:
        """Check if email is from a disposable email service."""
        if not email or '@' not in email:
            return False
        
        domain = email.split('@')[1].lower()
        return domain in self.disposable_domains
    
    def is_business_email(self, email: str) -> bool:
        """Check if email appears to be a business email."""
        if not self.validate_email(email):
            return False
        
        domain = email.split('@')[1].lower()
        
        # Common personal email domains
        personal_domains = {
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'icloud.com', 'aol.com', 'protonmail.com', 'zoho.com'
        }
        
        return domain not in personal_domains and not self.is_disposable_email(email)
    
    def normalize_email(self, email: str) -> str:
        """Normalize email address for storage."""
        if not self.validate_email(email):
            return email
        
        # Convert to lowercase
        email = email.lower().strip()
        
        # Handle Gmail dot normalization (optional)
        username, domain = email.split('@')
        if domain == 'gmail.com':
            # Remove dots from Gmail username (they're ignored by Gmail)
            username = username.replace('.', '')
            # Remove everything after + (Gmail alias)
            if '+' in username:
                username = username.split('+')[0]
            email = f"{username}@{domain}"
        
        return email
    
    def get_domain(self, email: str) -> str:
        """Extract domain from email address."""
        if not email or '@' not in email:
            return ''
        
        return email.split('@')[1].lower()
    
    def suggest_correction(self, email: str) -> str:
        """Suggest email correction for common typos."""
        if not email or '@' not in email:
            return email
        
        # Common domain typos
        domain_corrections = {
            'gamil.com': 'gmail.com',
            'gmai.com': 'gmail.com',
            'gmial.com': 'gmail.com',
            'yahooo.com': 'yahoo.com',
            'yaho.com': 'yahoo.com',
            'hotmial.com': 'hotmail.com',
            'hotmai.com': 'hotmail.com',
            'outlok.com': 'outlook.com',
            'outloo.com': 'outlook.com'
        }
        
        username, domain = email.split('@')
        corrected_domain = domain_corrections.get(domain.lower(), domain)
        
        return f"{username}@{corrected_domain}"