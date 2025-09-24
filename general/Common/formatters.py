"""
Formatting utilities for admin panel and user interfaces.
Handles message formatting, data presentation, and UI components.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from hydrogram.types import User, Chat
from hydrogram.enums import ChatType
from general.Language.Translations import get_text_sync

def format_user_statistics(stats: Dict[str, Any], lang_code: str) -> str:
    """Format user statistics for admin display."""
        # Language is handled automatically in new system
    
    message = f"📊 **{get_text_sync('user_statistics', lang_code or "en")}**\n\n"
    
    message += f"👥 **{get_text_sync('total_users', lang_code or "en")}:** {stats.get('total_users', 0):,}\n"
    message += f"🚫 **{get_text_sync('banned_users', lang_code or "en")}:** {stats.get('banned_users', 0):,}\n"
    message += f"🆕 **{get_text_sync('new_users_today', lang_code or "en")}:** {stats.get('new_users_today', 0):,}\n"
    message += f"📅 **{get_text_sync('new_users_week', lang_code or "en")}:** {stats.get('new_users_week', 0):,}\n"
    message += f"📆 **{get_text_sync('new_users_month', lang_code or "en")}:** {stats.get('new_users_month', 0):,}\n"
    message += f"🟢 **{get_text_sync('active_users_week', lang_code or "en")}:** {stats.get('active_users_week', 0):,}\n"
    message += f"📧 **{get_text_sync('users_with_accounts', lang_code or "en")}:** {stats.get('users_with_accounts', 0):,}\n"
    
    growth_rate = stats.get('growth_rate', 0)
    growth_emoji = "📈" if growth_rate > 0 else "📉" if growth_rate < 0 else "➡️"
    message += f"{growth_emoji} **{get_text_sync('growth_rate', lang_code or "en")}:** {growth_rate:+.1f}%\n\n"
    
    # Language distribution
    if 'language_distribution' in stats:
        message += f"🌐 **{get_text_sync('language_distribution', lang_code or "en")}:**\n"
        for lang_stat in stats['language_distribution']:
            lang_code_stat = lang_stat.get('Language_Code', 'unknown')
            count = lang_stat.get('count', 0)
            percentage = (count / stats.get('total_users', 1)) * 100
            message += f"• {lang_code_stat.upper()}: {count:,} ({percentage:.1f}%)\n"
    
    return message

def format_chat_statistics(stats: Dict[str, Any], lang_code: str) -> str:
    """Format chat statistics for admin display."""
        # Language is handled automatically in new system
    
    message = f"💬 **{get_text_sync('chat_statistics', lang_code or "en")}**\n\n"
    
    message += f"🔢 **{get_text_sync('total_chats', lang_code or "en")}:** {stats.get('total_chats', 0):,}\n"
    message += f"📺 **{get_text_sync('channels', lang_code or "en")}:** {stats.get('channel_count', 0):,}\n"
    message += f"👥 **{get_text_sync('groups', lang_code or "en")}:** {stats.get('group_count', 0) + stats.get('supergroup_count', 0):,}\n"
    message += f"👤 **{get_text_sync('private_chats', lang_code or "en")}:** {stats.get('private_count', 0):,}\n"
    message += f"🆕 **{get_text_sync('new_chats_today', lang_code or "en")}:** {stats.get('new_chats_today', 0):,}\n"
    message += f"📅 **{get_text_sync('new_chats_week', lang_code or "en")}:** {stats.get('new_chats_week', 0):,}\n"
    message += f"👥 **{get_text_sync('total_members', lang_code or "en")}:** {stats.get('total_members', 0):,}\n"
    message += f"📊 **{get_text_sync('avg_members_per_chat', lang_code or "en")}:** {stats.get('avg_members_per_chat', 0):.1f}\n"
    
    return message

def format_bot_chats_list(chats: List[Dict], lang_code: str, banned: bool = False) -> str:
    """Format bot chats list with enhanced information."""
        # Language is handled automatically in new system
    
    if not chats:
        if banned:
            return f"📋 **{get_text_sync('banned_chats', lang_code or "en")}**\n\n✅ {get_text_sync('no_banned_chats', lang_code or "en")}"
        else:
            return f"📋 **{get_text_sync('bot_chats', lang_code or "en")}**\n\n❌ {get_text_sync('no_chats_found', lang_code or "en")}"
    
    title = get_text_sync('banned_chats', lang_code or "en") if banned else get_text_sync('bot_chats', lang_code or "en")
    message = f"📋 **{title} ({len(chats)})**\n\n"
    
    for i, chat in enumerate(chats[:10], 1):  # Limit to 10 chats
        chat_id = chat.get('Chat_Id', 'Unknown')
        chat_title = chat.get('Chat_Title', 'No Title')
        chat_type = chat.get('Chat_Type', 'unknown')
        member_count = chat.get('Member_Count', 0) or 0
        username = chat.get('Chat_Username', '')
        added_at = chat.get('Added_At', 'Unknown')
        
        # Format date
        if isinstance(added_at, datetime):
            added_at = added_at.strftime('%Y-%m-%d %H:%M')
        elif isinstance(added_at, str):
            try:
                # Try to parse ISO format
                dt = datetime.fromisoformat(added_at.replace('Z', '+00:00'))
                added_at = dt.strftime('%Y-%m-%d %H:%M')
            except:
                pass
        
        # Chat type emoji
        type_emojis = {
            'channel': '📺',
            'group': '👥',
            'supergroup': '👥',
            'private': '👤'
        }
        type_emoji = type_emojis.get(chat_type, '❓')
        
        message += f"**{i}. {type_emoji} {sanitize_for_markdown(chat_title)}**\n"
        message += f"   {get_text_sync('admin_chat_id_field', lang_code or "en")} `{chat_id}`\n"
        message += f"   {get_text_sync('admin_chat_type_field', lang_code or "en")} {chat_type.title()}\n"
        message += f"   {get_text_sync('admin_chat_members_field', lang_code or "en")} {member_count:,}\n"
        
        if username:
            message += f"   🔗 @{username}\n"
        
        message += f"   {get_text_sync('admin_chat_added_field', lang_code or "en")} {added_at}\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    if len(chats) > 10:
        message += f"... {(get_text_sync('and_more', lang_code or "en") or 'and {count} more').format(count=len(chats) - 10)}\n"
    
    return message

def format_search_results(users: List[Dict], lang_code: str, page: int = 1) -> str:
    """Format user search results with pagination."""
        # Language is handled automatically in new system
    
    if not users:
        return f"🔍 **{get_text_sync('search_results', lang_code or "en")}**\n\n❌ {get_text_sync('no_results_found', lang_code or "en")}"
    
    message = f"🔍 **{get_text_sync('search_results', lang_code or "en")} ({len(users)})**\n\n"
    
    for i, user in enumerate(users, 1):
        chat_id = user.get('Chat_Id', 'Unknown')
        first_name = user.get('First_Name', 'Unknown')
        last_name = user.get('Last_Name', '') or ''
        username = user.get('User_Name', '')
        email = user.get('Email', 'Not set')
        stars = user.get('Stars', 0)
        referrals = user.get('Total_Referrals', 0)
        is_banned = user.get('Is_Banned', False)
        role = user.get('Role', 'user')
        created_at = user.get('Created_At', 'Unknown')
        
        # Format name
        full_name = f"{first_name} {last_name}".strip()
        username_display = f" (@{username})" if username else ""
        
        # Status indicators
        status_indicators = []
        if is_banned:
            status_indicators.append("🚫 Banned")
        if role != 'user':
            status_indicators.append(f"👑 {role.title()}")
        
        status_text = " | ".join(status_indicators) if status_indicators else "✅ Active"
        
        # Format date
        if isinstance(created_at, datetime):
            created_at = created_at.strftime('%Y-%m-%d')
        elif isinstance(created_at, str):
            try:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                created_at = dt.strftime('%Y-%m-%d')
            except:
                pass
        
        message += f"**{i}. {sanitize_for_markdown(full_name)}**{username_display}\n"
        message += f"   🆔 ID: `{chat_id}`\n"
        message += f"   📧 Email: {sanitize_for_markdown(email)}\n"
        message += f"   ⭐ Stars: {stars} | 👥 Referrals: {referrals}\n"
        message += f"   📊 Status: {status_text}\n"
        message += f"   📅 Joined: {created_at}\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    return message

def format_feature_analytics(analytics: List[Dict], lang_code: str) -> str:
    """Format feature usage analytics."""
        # Language is handled automatically in new system
    
    if not analytics:
        return f"📈 **{get_text_sync('feature_analytics', lang_code or "en")}**\n\n❌ {get_text_sync('no_data_available', lang_code or "en")}"
    
    message = f"📈 **{get_text_sync('feature_analytics', lang_code or "en")}**\n\n"
    message += f"📊 **{get_text_sync('most_used_features', lang_code or "en")}:**\n\n"
    
    for i, feature in enumerate(analytics[:10], 1):  # Top 10 features
        feature_name = feature.get('Feature_Name', 'Unknown')
        unique_users = feature.get('unique_users', 0)
        total_usage = feature.get('total_usage', 0)
        avg_usage = feature.get('avg_usage', 0)
        
        # Format feature name
        display_name = feature_name.replace('_', ' ').title()
        
        # Usage intensity indicator
        if avg_usage > 10:
            intensity = "🔥 High"
        elif avg_usage > 5:
            intensity = "🔥 Medium"
        else:
            intensity = "🔥 Low"
        
        message += f"**{i}. {display_name}**\n"
        message += f"   👥 Users: {unique_users:,}\n"
        message += f"   📊 Total Usage: {total_usage:,}\n"
        message += f"   📈 Avg per User: {avg_usage:.1f}\n"
        message += f"   🔥 Intensity: {intensity}\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Add usage trends
    if analytics:
        total_users = sum(f.get('unique_users', 0) for f in analytics)
        total_usage = sum(f.get('total_usage', 0) for f in analytics)
        
        message += f"📋 **{get_text_sync('summary', lang_code or "en")}:**\n"
        message += f"• Total Active Users: {total_users:,}\n"
        message += f"• Total Feature Usage: {total_usage:,}\n"
        message += f"• Features Tracked: {len(analytics)}\n"
    
    return message

def format_ticket_notification(ticket_id: int, user_id: int, lang_code: str, subject: str, 
                              category: str, priority: str) -> Dict[str, Any]:
    """Format ticket notification for admins."""
    # Category emojis
    category_emojis = {
        'technical': '🔧',
        'billing': '💳',
        'general': '💬',
        'bug': '🐛',
        'feature': '💡'
    }
    
    # Priority emojis
    priority_emojis = {
        'low': '🟢',
        'medium': '🟡',
        'high': '🔴'
    }
    
    category_emoji = category_emojis.get(category, '📋')
    priority_emoji = priority_emojis.get(priority, '⚪')
    
    # Using optimized language system - no manager instance needed
        # Language is handled automatically in new system  # Default to English for admin notifications
    
    message = f"🎫 **{get_text_sync('new_support_ticket', lang_code or "en")}**\n\n"
    message += f"{category_emoji} **Category:** {category.title()}\n"
    message += f"👤 **User:** `{user_id}`\n"
    message += f"📝 **Subject:** {sanitize_for_markdown(subject)}\n"
    message += f"🆔 **Ticket ID:** #{ticket_id}\n"
    message += f"{priority_emoji} **Priority:** {priority.title()}\n\n"
    message += f"🚀 **{get_text_sync('quick_actions', lang_code or "en")}:**"
    
    # Create action buttons
    from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🔍 View #{ticket_id}", callback_data=f'admin_view_ticket_{ticket_id}')],
        [
            InlineKeyboardButton('💬 Reply', callback_data=f'admin_reply_ticket_{ticket_id}'),
            InlineKeyboardButton('🟡 Progress', callback_data=f'admin_mark_progress_{ticket_id}')
        ],
        [InlineKeyboardButton('📋 All Tickets', callback_data='admin_tickets')]
    ])
    
    return {
        'text': message,
        'keyboard': keyboard
    }

def format_growth_analytics(daily_data: List[Dict], lang_code: str, days: int) -> str:
    """Format growth analytics data."""
        # Language is handled automatically in new system
    
    message = f"📈 **{get_text_sync('growth_analytics', lang_code or "en")} ({days} {get_text_sync('days', lang_code or "en")})**\n\n"
    
    if not daily_data:
        return message + f"❌ {get_text_sync('no_data_available', lang_code or "en")}"
    
    # Calculate totals
    total_new_users = sum(item.get('new_users', 0) for item in daily_data)
    total_new_chats = sum(item.get('new_chats', 0) for item in daily_data)
    
    message += f"📊 **{get_text_sync('summary', lang_code or "en")}:**\n"
    message += f"• New Users: {total_new_users:,}\n"
    message += f"• New Chats: {total_new_chats:,}\n"
    message += f"• Avg Daily Users: {total_new_users / max(days, 1):.1f}\n\n"
    
    message += f"📅 **{get_text_sync('daily_breakdown', lang_code or "en")}:**\n"
    
    for item in daily_data[-7:]:  # Last 7 days
        date = item.get('date', 'Unknown')
        new_users = item.get('new_users', 0)
        new_chats = item.get('new_chats', 0)
        
        # Format date
        if isinstance(date, datetime):
            date_str = date.strftime('%m-%d')
        elif isinstance(date, str):
            try:
                dt = datetime.fromisoformat(date)
                date_str = dt.strftime('%m-%d')
            except:
                date_str = str(date)
        else:
            date_str = str(date)
        
        message += f"• {date_str}: {new_users:,} users, {new_chats:,} chats\n"
    
    return message

def format_system_health(health_stats: Dict[str, Any], lang_code: str) -> str:
    """Format system health statistics."""
        # Language is handled automatically in new system
    
    message = f"🔧 **{get_text_sync('system_health', lang_code or "en")}**\n\n"
    
    # Database status
    db_status = health_stats.get('database_status', 'unknown')
    status_emoji = "🟢" if db_status == 'connected' else "🔴"
    message += f"{status_emoji} **Database:** {db_status.title()}\n"
    
    if db_status == 'connected':
        db_size = health_stats.get('database_size_mb', 0)
        message += f"💾 **Size:** {db_size} MB\n\n"
        
        # Table statistics
        message += f"📊 **{get_text_sync('table_statistics', lang_code or "en")}:**\n"
        tables = [
            ('users_count', 'Users'),
            ('bot_chats_count', 'Bot Chats'),
            ('referrals_count', 'Referrals'),
            ('subscriptions_count', 'Subscriptions'),
            ('tickets_count', 'Tickets')
        ]
        
        for count_key, label in tables:
            count = health_stats.get(count_key, 0)
            message += f"• {label}: {count:,}\n"
        
        message += f"\n⏰ **{get_text_sync('last_24_hours', lang_code or "en")}:**\n"
        message += f"• New Users: {health_stats.get('new_users_24h', 0):,}\n"
        message += f"• New Chats: {health_stats.get('new_chats_24h', 0):,}\n"
        message += f"• New Referrals: {health_stats.get('new_referrals_24h', 0):,}\n"
    
    return message

def format_pagination_info(current_page: int, total_pages: int, total_items: int) -> str:
    """Format pagination information."""
    return f"📄 Page {current_page}/{total_pages} • {total_items:,} total items"

def format_user_profile(user: Dict[str, Any], lang_code: str) -> str:
    """Format detailed user profile for admin view."""
        # Language is handled automatically in new system
    
    chat_id = user.get('Chat_Id', 'Unknown')
    first_name = user.get('First_Name', 'Unknown')
    last_name = user.get('Last_Name', '') or ''
    username = user.get('User_Name', '')
    email = user.get('Email', 'Not set')
    language = user.get('Language_Code', 'en')
    stars = user.get('Stars', 0)
    referrals = user.get('Total_Referrals', 0)
    is_banned = user.get('Is_Banned', False)
    role = user.get('Role', 'user')
    created_at = user.get('Created_At', 'Unknown')
    login_date = user.get('Login_Date', 'Unknown')
    
    # Format dates
    if isinstance(created_at, datetime):
        created_at = created_at.strftime('%Y-%m-%d %H:%M')
    if isinstance(login_date, datetime):
        login_date = login_date.strftime('%Y-%m-%d')
    
    full_name = f"{first_name} {last_name}".strip()
    username_display = f" (@{username})" if username else ""
    
    message = f"👤 **{get_text_sync('user_profile', lang_code or "en")}**\n\n"
    message += f"**{sanitize_for_markdown(full_name)}**{username_display}\n\n"
    
    message += f"🆔 **ID:** `{chat_id}`\n"
    message += f"📧 **Email:** {sanitize_for_markdown(email)}\n"
    message += f"🌐 **Language:** {language.upper()}\n"
    message += f"👑 **Role:** {role.title()}\n"
    message += f"⭐ **Stars:** {stars:,}\n"
    message += f"👥 **Referrals:** {referrals:,}\n"
    message += f"📅 **Joined:** {created_at}\n"
    message += f"🔄 **Last Login:** {login_date}\n"
    
    # Status
    status = "🚫 Banned" if is_banned else "✅ Active"
    message += f"📊 **Status:** {status}\n"
    
    return message

def sanitize_for_markdown(text: str) -> str:
    """Sanitize text for Telegram markdown."""
    if not text:
        return "N/A"
    
    # Characters that need escaping in Telegram MarkdownV2
    chars_to_escape = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    text = str(text)
    for char in chars_to_escape:
        text = text.replace(char, f'\\{char}')
    
    return text

def format_error_report(error: Exception, context: Dict[str, Any]) -> str:
    """Format error report for admin notification."""
    error_type = type(error).__name__
    error_message = str(error)
    
    message = f"🚨 **SYSTEM ERROR REPORT**\n\n"
    message += f"⚠️ **Type:** {error_type}\n"
    message += f"📝 **Message:** {sanitize_for_markdown(error_message[:200])}\n"
    
    if context:
        message += f"\n📋 **Context:**\n"
        for key, value in context.items():
            if key == 'user_id':
                message += f"• User ID: `{value}`\n"
            elif key == 'handler':
                message += f"• Handler: {value}\n"
            elif key == 'operation':
                message += f"• Operation: {value}\n"
    
    message += f"\n⏰ **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return message

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length."""
    if not text:
        return ""
    
    text = str(text)
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def format_account_history(history: List[Dict[str, Any]], lang_code: str) -> str:
    """Format account history for display."""
    # Using optimized language system - no manager instance needed
        # Language is handled automatically in new system
    
    if not history:
        return get_text_sync('no_account_history', lang_code or "en") or 'No account history available.'
    
    message = f"📋 **{get_text_sync('account_history', lang_code or "en") or 'Account History'}**\n\n"
    
    for i, record in enumerate(history[:10], 1):  # Show last 10 records
        date = record.get('date', 'Unknown')
        action = record.get('action', 'Unknown action')
        details = record.get('details', '')
        
        message += f"**{i}. {action}**\n"
        message += f"   📅 Date: {date}\n"
        if details:
            message += f"   ℹ️ Details: {details}\n"
        message += "\n"
    
    if len(history) > 10:
        message += f"... {get_text_sync('and_more', lang_code or "en") or 'and'} {len(history) - 10} {get_text_sync('more_records', lang_code or "en") or 'more records'}"
    
    return message
    
def format_user_mention(user: User) -> str:
    """Format user mention with fallback to name."""
    if user.username:
        return f"@{user.username}"
    
    name = user.first_name or ""
    if user.last_name:
        name += f" {user.last_name}"
    
    return name or f"User {user.id}"

def format_chat_title(chat: Chat) -> str:
    """Format chat title with type indicator."""
    title = chat.title or "Unknown Chat"
    
    if chat.type == ChatType.PRIVATE:
        return f"👤 {title}"
    elif chat.type == ChatType.GROUP:
        return f"👥 {title}"
    elif chat.type == ChatType.SUPERGROUP:
        return f"🏢 {title}"
    elif chat.type == ChatType.CHANNEL:
        return f"📢 {title}"
    
    return title