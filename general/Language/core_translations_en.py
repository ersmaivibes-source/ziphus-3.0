"""
general English language texts for Ziphus Bot.
General and general functionality that doesn't belong to specific domains.
"""

CORE_EN_TEXTS = {
    # general Messages
    'start_message': "Hello! Please select your language to continue:\n\n👋 Welcome to the **Ziphus Bot!\n\nI'm designed to help you manage your projects effectively, automate tasks, and connect with your team.\n\nTo get started, please select your preferred language below.",
    'welcome_text': "Hello dear {name}.\n\nFirst of all, welcome to our all-in-one bot🎉\n\nAnd secondly, we are happy for you to join the **Ziphus Union to use our tools⚙️\n\n🔺Now choose one of the options below to reach your goal",
    
    # Main Menu Buttons
    'tools': '🧰 Tools',
    'orders': '🛒 Orders',

    # Menu Header Texts
    'tools_text': '🔺Please select the desired option🔺',
    'orders_text': '🔺Please select the desired option🔺',

    # Navigation
    'back': '⬅️ Back',
    'back_to_main': '🏠 Back to Main Menu',
    'change_language': '🌐 Change Language',
    
    # Database Operations
    'clear_database_warning': '⚠️ Warning! ⚠️\n\n⚠️ You are requesting to delete all data from the database.\n\n⚠️ If you proceed, all saved information will be deleted permanently.\n\n❌ Do you agree to these terms?',
    'yes': '❌ I agree',
    'no': '✅ I disagree',
    'clear_success': '✅ Data deletion completed successfully.\n\nTo restart the bot, click the START button below.',
    'clear_cancelled': 'Data deletion cancelled. Returning to settings.',
    'deleting_data': '✅ Your data is being deleted...',
    
    # General Messages
    'language_changed': '🟢 Your language has been successfully changed.',
    'unknown_option': '🔺An unknown option has been selected.🔺',
    'not_available': 'N/A',
    'processing': 'Processing your request...',
    'complete_current_operation': 'Please complete your current operation before accessing other features.',
    
    # Content for Information Pages
    'help_support_content': '''🆘 **Help & Support**

Welcome to Ziphus Bot support center! Here you can find assistance with any issues or questions.

**📞 Contact Support:**
• 💬 Use the support chat feature in the bot
• 📧 Email: support@ziphus.net
• 🌐 Website: https://ziphus.net

**🔧 Common Issues:**
• Account problems
• Feature limitations  
• Payment issues
• Technical difficulties

**📝 How to Get Help:**
1. Describe your issue clearly
2. Include any error messages
3. Mention your subscription plan
4. Wait for support team response

**⏰ Response Time:**
• Premium users: 2-6 hours
• Free users: 24-48 hours

We're here to help! 🤝''',

    'about_us_content': '''ℹ️ **About Ziphus Bot**

**🚀 Welcome to Ziphus - Your All-in-One Digital Assistant!**

Ziphus Bot is a comprehensive Telegram bot designed to simplify your digital life with powerful tools and features.

**🌟 What We Offer:**
• 📥 Media downloading and conversion
• 🔄 File format conversion
• 🌐 Sanctions bypass tools
• 🛡️ Security and antivirus scanning
• 🤖 AI-powered features
• 📊 Analytics and insights
• And much more!

**📈 Our Mission:**
To provide users with reliable, secure, and easy-to-use digital tools that enhance productivity and simplify everyday tasks.

**🎯 Why Choose Ziphus:**
• ✅ User-friendly interface
• ✅ Regular updates and new features
• ✅ 24/7 availability
• ✅ Strong privacy protection
• ✅ Flexible subscription plans

**👥 Contact Us:**
• Website: https://ziphus.net
• Email: info@ziphus.net
• Support: Available through bot

Thank you for choosing Ziphus Bot! 🙏''',

    'faq_menu_content': '''❓ **Frequently Asked Questions**

Find quick answers to common questions about using Ziphus Bot.

**📚 Browse FAQ Topics:**

Use the buttons below to explore different help categories and find the information you need.

**💡 Can't find what you're looking for?**
Contact our support team for personalized assistance.

Choose a topic to get started:''',

    # Chat Information
    'chat_information': 'Chat Information',
    'private_chat': 'Private Chat',
    'group': 'Group',
    'supergroup': 'Supergroup',
    'channel': 'Channel',
    'yes_bool': 'Yes',
    'no_bool': 'No',
    'type': 'Type',
    'members': 'Members',
    'added_at': 'Added At',
    
    # Bot Management
    'bot_chats_list': 'Bot Chats List',
    'no_chats_found': 'No chats found where bot is present.',
    'chat_banned': 'This chat has been banned from adding the bot.',
    'bot_added_to_chat': '🤖 Bot has been added to {chat_title} ({chat_type})',
    'restart_button': '🔄 Start Bot',
    
    # General Error Messages
    'unauthorized': 'Unauthorized',
    'access_denied': 'Access denied',
    'session_expired': 'Session expired',
    'cancelled': 'Cancelled',
    'running_health_check': '🔍 Running health check...',
    'invalid_plan_selected': 'Invalid plan selected',
    'session_data_invalid': 'Session data invalid. Please select a plan again.',
    'please_start_bot': 'Please start the bot with /start',
    'service_temporarily_unavailable': 'Service temporarily unavailable',
    'debug_test_executed': 'Debug test executed - check logs',
    
    # Navigation & General
    'cancel': '❌ Cancel',
    'confirm': '✅ Confirm',
    'try_again': '🔄 Try Again',
    
    # Language Selection
    'persian_language_button': 'فارسی 🇮🇷',
    'english_language_button': 'ENGLISH 🇬🇧',
    
    # Tools & Features
    'url_shortener': '🔗 URL Shortener',
    'qr_code_generator': '📱 QR Code Generator',
    'password_generator': '🔐 Password Generator',
    'hash_generator': '🔒 Hash Generator',
    'base64_encoder_decoder': '📄 Base64 Encoder/Decoder',
    'json_formatter': '📋 JSON Formatter',
    'color_palette_generator': '🎨 Color Palette Generator',
    'unit_converter': '⚖️ Unit Converter',
    'timestamp_converter': '⏰ Timestamp Converter',
    'regex_tester': '🔍 Regex Tester',
    'markdown_to_html': '📝 Markdown to HTML',
    'image_resizer': '🖼️ Image Resizer',
    'text_counter': '📊 Text Counter',
    'smart_feed_reader': '📰 Smart Feed Reader',
    'smart_translator': '🌍 Smart Translator',
    'live_stock_market': '📈 Live Stock Market',
    'temporary_email_sms': '📧 Temporary Email & SMS',
    'apply_assistant': '📝 Apply Assistant',
    'telegram_search': '🔍 Telegram Search',
    'voice_text_converter': '🎤 Voice to Text Converter',
    'movie_series_downloader': '🎬 Movie & Series Downloader',
    
    # FAQ Topics
    'faq_registration': '📝 Registration',
    'faq_password': '🔐 Password',
    'faq_email': '📧 Email',
    'faq_security': '🔒 Security',
    'faq_account_recovery': '🔄 Account Recovery',
}