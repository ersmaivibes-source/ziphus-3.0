"""
Email Templates
Consolidated email template functionality
"""

from general.Language.Translations import get_text_sync


class EmailTemplates:
    """Email template manager for all email types."""
    
    def __init__(self):
        pass
    
    def verification_email_template(self, code: str, lang_code: str = 'en') -> str:
        """Create verification email template."""
        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{get_text_sync('email_verification_subject', lang_code)}</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                <h2 style="color: #007bff; text-align: center;">🔐 {get_text_sync('email_verification_title', lang_code, default='Email Verification')}</h2>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    {get_text_sync('email_verification_greeting', lang_code, default='Hello!')}
                </p>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    {get_text_sync('email_verification_message', lang_code, default='Please use the following verification code to complete your registration:')}
                </p>
                
                <div style="background-color: #007bff; color: white; text-align: center; padding: 15px; margin: 20px 0; border-radius: 5px; font-size: 24px; font-weight: bold; letter-spacing: 3px;">
                    {code}
                </div>
                
                <p style="font-size: 14px; color: #666; line-height: 1.6;">
                    {get_text_sync('email_verification_expiry', lang_code, default='This code will expire in 10 minutes for security reasons.')}
                </p>
                
                <p style="font-size: 14px; color: #666; line-height: 1.6;">
                    {get_text_sync('email_verification_ignore', lang_code, default='If you did not request this verification, please ignore this email.')}
                </p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                
                <p style="font-size: 12px; color: #999; text-align: center;">
                    {get_text_sync('email_footer', lang_code, default='This is an automated message. Please do not reply to this email.')}
                </p>
            </div>
        </body>
        </html>
        """
        return template
    
    def password_reset_template(self, reset_link: str, lang_code: str = 'en') -> str:
        """Create password reset email template."""
        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{get_text_sync('password_reset_subject', lang_code)}</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                <h2 style="color: #dc3545; text-align: center;">🔐 {get_text_sync('password_reset_title', lang_code, default='Password Reset Request')}</h2>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    {get_text_sync('password_reset_greeting', lang_code, default='Hello!')}
                </p>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    {get_text_sync('password_reset_message', lang_code, default='You have requested to reset your password. Click the button below to reset your password:')}
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" style="background-color: #dc3545; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                        {get_text_sync('reset_password_button', lang_code, default='Reset Password')}
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666; line-height: 1.6;">
                    {get_text_sync('password_reset_expiry', lang_code, default='This link will expire in 1 hour for security reasons.')}
                </p>
                
                <p style="font-size: 14px; color: #666; line-height: 1.6;">
                    {get_text_sync('password_reset_ignore', lang_code, default='If you did not request this password reset, please ignore this email.')}
                </p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                
                <p style="font-size: 12px; color: #999; text-align: center;">
                    {get_text_sync('email_footer', lang_code, default='This is an automated message. Please do not reply to this email.')}
                </p>
            </div>
        </body>
        </html>
        """
        return template
    
    def subscription_confirmation_template(self, plan: str, lang_code: str = 'en') -> str:
        """Create subscription confirmation email template."""
        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{get_text_sync('subscription_confirmation_subject', lang_code)}</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                <h2 style="color: #28a745; text-align: center;">🎉 {get_text_sync('subscription_confirmation_title', lang_code, default='Subscription Activated!')}</h2>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    {get_text_sync('subscription_confirmation_greeting', lang_code, default='Congratulations!')}
                </p>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    {get_text_sync('subscription_confirmation_message', lang_code, plan=plan, default=f'Your {plan} subscription has been activated successfully.')}
                </p>
                
                <div style="background-color: #28a745; color: white; text-align: center; padding: 15px; margin: 20px 0; border-radius: 5px;">
                    <h3 style="margin: 0;">{plan.upper()} PLAN ACTIVATED</h3>
                </div>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    {get_text_sync('subscription_benefits', lang_code, default='You now have access to all premium features. Enjoy your enhanced experience!')}
                </p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                
                <p style="font-size: 12px; color: #999; text-align: center;">
                    {get_text_sync('email_footer', lang_code, default='This is an automated message. Please do not reply to this email.')}
                </p>
            </div>
        </body>
        </html>
        """
        return template
    
    def email_change_verification_template(self, code: str, lang_code: str = 'en') -> str:
        """Create email change verification template."""
        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{get_text_sync('email_change_verification_subject', lang_code, default='Email Change Verification')}</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                <h2 style="color: #17a2b8; text-align: center;">📧 {get_text_sync('email_change_title', lang_code, default='Email Change Verification')}</h2>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    {get_text_sync('email_change_greeting', lang_code, default='Hello!')}
                </p>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    {get_text_sync('email_change_message', lang_code, default='Please use the following verification code to confirm your email change:')}
                </p>
                
                <div style="background-color: #17a2b8; color: white; text-align: center; padding: 15px; margin: 20px 0; border-radius: 5px; font-size: 24px; font-weight: bold; letter-spacing: 3px;">
                    {code}
                </div>
                
                <p style="font-size: 14px; color: #666; line-height: 1.6;">
                    {get_text_sync('email_change_expiry', lang_code, default='This code will expire in 10 minutes for security reasons.')}
                </p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                
                <p style="font-size: 12px; color: #999; text-align: center;">
                    {get_text_sync('email_footer', lang_code, default='This is an automated message. Please do not reply to this email.')}
                </p>
            </div>
        </body>
        </html>
        """
        return template
    
    def welcome_email_template(self, username: str, lang_code: str = 'en') -> str:
        """Create welcome email template."""
        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{get_text_sync('welcome_email_subject', lang_code, default='Welcome!')}</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                <h2 style="color: #007bff; text-align: center;">🎉 {get_text_sync('welcome_title', lang_code, default='Welcome to Ziphus!')}</h2>
                
                <p style="font-size: 18px; line-height: 1.6;">
                    {get_text_sync('welcome_greeting', lang_code, username=username, default=f'Hello {username}!')}
                </p>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    {get_text_sync('welcome_message', lang_code, default='Thank you for joining Ziphus! We are excited to have you as part of our community.')}
                </p>
                
                <div style="background-color: #007bff; color: white; padding: 20px; margin: 20px 0; border-radius: 5px;">
                    <h3 style="margin: 0 0 10px 0;">{get_text_sync('getting_started', lang_code, default='Getting Started:')}</h3>
                    <ul style="margin: 0; padding-left: 20px;">
                        <li>{get_text_sync('welcome_step1', lang_code, default='Explore our powerful tools and features')}</li>
                        <li>{get_text_sync('welcome_step2', lang_code, default='Set up your profile and preferences')}</li>
                        <li>{get_text_sync('welcome_step3', lang_code, default='Join our community and start creating')}</li>
                    </ul>
                </div>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    {get_text_sync('welcome_support', lang_code, default='If you have any questions, our support team is here to help. Welcome aboard!')}
                </p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                
                <p style="font-size: 12px; color: #999; text-align: center;">
                    {get_text_sync('email_footer', lang_code, default='This is an automated message. Please do not reply to this email.')}
                </p>
            </div>
        </body>
        </html>
        """
        return template