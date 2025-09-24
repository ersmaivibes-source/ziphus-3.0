"""
Email System Module
Consolidated email functionality following ULTIMATE_ARCHITECTURE_DESIGN pattern.
"""

from .email_service import EmailService
from .email_templates import EmailTemplates
from .email_validation import EmailValidation
from .email_configuration import EmailConfiguration
from .email_sending import EmailSending
from .email_verification import EmailVerification

__all__ = [
    'EmailService',
    'EmailTemplates',
    'EmailValidation', 
    'EmailConfiguration',
    'EmailSending',
    'EmailVerification'
]