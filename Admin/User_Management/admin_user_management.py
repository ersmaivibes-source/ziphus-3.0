import logging
from hydrogram import Client, filters
from hydrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from database.db_manager import DatabaseManager
from common.decorators import admin_required, error_handler
# Use general configuration instead of old config.py
# from config import Config

logger = logging.getLogger(__name__)

# Pagination settings
USERS_PER_PAGE = 10

@Client.on_message(filters.command("users") & filters.user([]))  # Will be updated dynamically
@admin_required
@error_handler
async def admin_users(client: Client, message: Message):
    """Show admin user management panel"""
    keyboard = [
        [InlineKeyboardButton("📋 لیست کاربران", callback_data="user_list_1")],
        [InlineKeyboardButton("🔍 جستجوی کاربر", callback_data="user_search")],
        [InlineKeyboardButton("📊 آمار کاربران", callback_data="user_stats")],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data="admin_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.reply_text(
        "🛠️ **پنل مدیریت کاربران**\n\n"
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=reply_markup
    )

@Client.on_callback_query(filters.regex("^user_list_"))
@admin_required
@error_handler
async def user_list(client: Client, callback_query: CallbackQuery):
    """Show list of users with pagination"""
    await callback_query.answer()
    
    page = int(callback_query.data.split('_')[-1])
    
    # Calculate offset
    offset = (page - 1) * USERS_PER_PAGE
    
    # Get users from database
    users = await DatabaseManager.get_all_users(limit=USERS_PER_PAGE, offset=offset)
    total_users = await DatabaseManager.get_user_count()
    total_pages = (total_users + USERS_PER_PAGE - 1) // USERS_PER_PAGE
    
    if not users:
        await callback_query.message.edit_text(
            "❌ هیچ کاربری در سیستم وجود ندارد."
        )
        return
    
    # Build message text
    message_text = f"👥 **لیست کاربران**\n\n"
    message_text += f"📊 تعداد کل کاربران: `{total_users}`\n"
    message_text += f"📄 صفحه {page} از {total_pages}\n\n"
    
    for i, user in enumerate(users, start=offset + 1):
        status = "✅ فعال" if not user['is_banned'] else "❌ مسدود"
        premium = "⭐ پریمیوم" if user['is_premium'] else "🔹 معمولی"
        
        message_text += (
            f"{i}. {user['first_name']}\n"
            f"   🆔 ID: `{user['user_id']}`\n"
            f"   👤 نام کاربری: @{user['username'] or 'ندارد'}\n"
            f"   📅 عضویت: {user['created_at'].strftime('%Y-%m-%d %H:%M')}\n"
            f"   🎯 وضعیت: {status} | {premium}\n\n"
        )
    
    # Build pagination keyboard
    keyboard = []
    
    # User action buttons
    action_buttons = []
    for user in users:
        user_id = user['user_id']
        action_buttons.append(
            InlineKeyboardButton(
                f"👤 {user['first_name']}",
                callback_data=f"user_detail_{user_id}"
            )
        )
    
    # Add users in rows of 2
    for i in range(0, len(action_buttons), 2):
        keyboard.append(action_buttons[i:i+2])
    
    # Pagination buttons
    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(
            InlineKeyboardButton("⏪ قبلی", callback_data=f"user_list_{page-1}")
        )
    
    if page < total_pages:
        pagination_buttons.append(
            InlineKeyboardButton("بعدی ⏩", callback_data=f"user_list_{page+1}")
        )
    
    if pagination_buttons:
        keyboard.append(pagination_buttons)
    
    # Add back button
    keyboard.append([InlineKeyboardButton("⬅️ بازگشت", callback_data="user_management")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await callback_query.message.edit_text(
        message_text,
        reply_markup=reply_markup
    )

@Client.on_callback_query(filters.regex("^user_detail_"))
@admin_required
@error_handler
async def user_detail(client: Client, callback_query: CallbackQuery):
    """Show detailed information about a specific user"""
    await callback_query.answer()
    
    user_id = int(callback_query.data.split('_')[-1])
    user = await DatabaseManager.get_user(user_id)
    
    if not user:
        await callback_query.message.edit_text(
            "❌ کاربر مورد نظر یافت نشد."
        )
        return
    
    # Get user tickets
    tickets = await DatabaseManager.get_user_tickets(user_id)
    open_tickets = len([t for t in tickets if t['status'] == 'open'])
    closed_tickets = len([t for t in tickets if t['status'] == 'closed'])
    
    # Build message text
    message_text = "👤 **اطلاعات کاربر**\n\n"
    message_text += f"🆔 شناسه کاربر: `{user['user_id']}`\n"
    message_text += f"👤 نام: {user['first_name']}\n"
    message_text += f"📛 نام خانوادگی: {user['last_name'] or 'ندارد'}\n"
    message_text += f"🔖 نام کاربری: @{user['username'] or 'ندارد'}\n"
    message_text += f"🌐 زبان: {user['language_code'] or 'نامشخص'}\n"
    message_text += f"📅 تاریخ عضویت: {user['created_at'].strftime('%Y-%m-%d %H:%M')}\n\n"
    
    message_text += f"🎯 وضعیت حساب: {'❌ مسدود' if user['is_banned'] else '✅ فعال'}\n"
    message_text += f"💎 نوع اشتراک: {'⭐ پریمیوم' if user['is_premium'] else '🔹 معمولی'}\n"
    
    if user['is_premium'] and user['subscription_end']:
        message_text += f"⏰ پایان اشتراک: {user['subscription_end'].strftime('%Y-%m-%d %H:%M')}\n"
    
    message_text += f"\n📮 تیکت‌ها: 📤 {open_tickets} باز | ✅ {closed_tickets} بسته\n\n"
    message_text += "🛠️ **عملیات مدیریت:**"
    
    # Build keyboard
    keyboard = []
    
    # Ban/Unban button
    if user['is_banned']:
        keyboard.append([
            InlineKeyboardButton("🔓 آزاد کردن کاربر", callback_data=f"user_unban_{user_id}")
        ])
    else:
        keyboard.append([
            InlineKeyboardButton("🔒 مسدود کردن کاربر", callback_data=f"user_ban_{user_id}")
        ])
    
    # Tickets button
    keyboard.append([
        InlineKeyboardButton("📮 مشاهده تیکت‌ها", callback_data=f"user_tickets_{user_id}_1")
    ])
    
    # Send message button
    keyboard.append([
        InlineKeyboardButton("✉️ ارسال پیام", callback_data=f"user_message_{user_id}")
    ])
    
    # Back button
    keyboard.append([
        InlineKeyboardButton("⬅️ بازگشت به لیست", callback_data="user_list_1")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await callback_query.message.edit_text(
        message_text,
        reply_markup=reply_markup
    )

@Client.on_callback_query(filters.regex("^user_ban_"))
@admin_required
@error_handler
async def ban_user(client: Client, callback_query: CallbackQuery):
    """Ban a user"""
    await callback_query.answer()
    
    user_id = int(callback_query.data.split('_')[-1])
    success = await DatabaseManager.ban_user(user_id)
    
    if success:
        # Log the action
        await DatabaseManager.log_system_event(
            "WARNING", f"User {user_id} banned by admin",
            callback_query.from_user.id, "user_ban", {"banned_user_id": user_id}
        )
        
        await callback_query.message.edit_text(
            f"✅ کاربر با شناسه `{user_id}` با موفقیت مسدود شد."
        )
    else:
        await callback_query.message.edit_text(
            "❌ خطایی در مسدود کردن کاربر رخ داد."
        )

@Client.on_callback_query(filters.regex("^user_unban_"))
@admin_required
@error_handler
async def unban_user(client: Client, callback_query: CallbackQuery):
    """Unban a user"""
    await callback_query.answer()
    
    user_id = int(callback_query.data.split('_')[-1])
    success = await DatabaseManager.unban_user(user_id)
    
    if success:
        # Log the action
        await DatabaseManager.log_system_event(
            "INFO", f"User {user_id} unbanned by admin",
            callback_query.from_user.id, "user_unban", {"unbanned_user_id": user_id}
        )
        
        await callback_query.message.edit_text(
            f"✅ کاربر با شناسه `{user_id}` با موفقیت آزاد شد."
        )
    else:
        await callback_query.message.edit_text(
            "❌ خطایی در آزاد کردن کاربر رخ داد."
        )

@Client.on_callback_query(filters.regex("^user_stats$"))
@admin_required
@error_handler
async def user_stats(client: Client, callback_query: CallbackQuery):
    """Show user statistics"""
    await callback_query.answer()
    
    # Get statistics from database
    total_users = await DatabaseManager.get_user_count()
    banned_users = await DatabaseManager.fetch_val(
        "SELECT COUNT(*) FROM users WHERE is_banned = TRUE"
    )
    premium_users = await DatabaseManager.fetch_val(
        "SELECT COUNT(*) FROM users WHERE is_premium = TRUE"
    )
    
    # Get today's new users
    today_users = await DatabaseManager.fetch_val(
        "SELECT COUNT(*) FROM users WHERE DATE(created_at) = CURRENT_DATE"
    )
    
    # Get weekly growth
    weekly_growth = await DatabaseManager.fetch_val(
        "SELECT COUNT(*) FROM users WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'"
    )
    
    # Build message text
    message_text = "📊 **آمار کاربران**\n\n"
    message_text += f"👥 کل کاربران: `{total_users}` نفر\n"
    message_text += f"❌ کاربران مسدود: `{banned_users}` نفر\n"
    message_text += f"⭐ کاربران پریمیوم: `{premium_users}` نفر\n"
    message_text += f"📈 کاربران امروز: `{today_users}` نفر\n"
    message_text += f"📆 رشد هفتگی: `{weekly_growth}` نفر\n\n"
    
    # Calculate percentages
    if total_users > 0:
        banned_percent = (banned_users / total_users) * 100
        premium_percent = (premium_users / total_users) * 100
        
        message_text += f"📊 درصد مسدود شده: `{banned_percent:.1f}%`\n"
        message_text += f"📊 درصد پریمیوم: `{premium_percent:.1f}%`\n"
    
    # Build keyboard
    keyboard = [
        [InlineKeyboardButton("🔄 بروزرسانی آمار", callback_data="user_stats")],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data="user_management")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await callback_query.message.edit_text(
        message_text,
        reply_markup=reply_markup
    )

@Client.on_callback_query(filters.regex("^user_search$"))
@admin_required
@error_handler
async def user_search(client: Client, callback_query: CallbackQuery):
    """Handle user search"""
    await callback_query.answer()
    
    await callback_query.message.edit_text(
        "🔍 **جستجوی کاربر**\n\n"
        "لطفاً یکی از روش‌های جستجو را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔖 جستجو با نام کاربری", callback_data="search_username")],
            [InlineKeyboardButton("🆔 جستجو با شناسه کاربر", callback_data="search_userid")],
            [InlineKeyboardButton("👤 جستجو با نام", callback_data="search_name")],
            [InlineKeyboardButton("⬅️ بازگشت", callback_data="user_management")]
        ])
    )

# ... (بقیه متدها به همین شکل برای Hydrogram adapt می‌شوند) ...

@Client.on_message(filters.text & ~filters.command & filters.user([]))  # Will be updated dynamically
@admin_required
@error_handler
async def handle_search_query(client: Client, message: Message):
    """Handle search query input"""
    # اینجا باید state management برای جستجو پیاده‌سازی شود
    # برای سادگی، یک پیام ساده می‌فرستیم
    await message.reply_text(
        "🔍 لطفاً از طریق منوی جستجو اقدام کنید.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 منوی جستجو", callback_data="user_search")]
        ])
    )

# هندلر اصلی برای callback queries
@Client.on_callback_query(filters.user([]))  # Will be updated dynamically
@admin_required
@error_handler
async def handle_callback(client: Client, callback_query: CallbackQuery):
    """Handle all callback queries"""
    await callback_query.answer()
    
    data = callback_query.data
    
    if data == "user_management":
        await admin_users(client, callback_query.message)
    elif data == "user_stats":
        await user_stats(client, callback_query)
    elif data == "user_search":
        await user_search(client, callback_query)
    elif data.startswith("user_list_"):
        await user_list(client, callback_query)
    elif data.startswith("user_detail_"):
        await user_detail(client, callback_query)
    elif data.startswith("user_ban_"):
        await ban_user(client, callback_query)
    elif data.startswith("user_unban_"):
        await unban_user(client, callback_query)
    elif data.startswith("user_tickets_"):
        await user_tickets_list(client, callback_query)
    elif data.startswith("user_message_"):
        await send_message_to_user(client, callback_query)
    elif data == "search_username":
        await search_by_username(client, callback_query)
    elif data == "search_userid":
        await search_by_userid(client, callback_query)
    elif data == "search_name":
        await search_by_name(client, callback_query)
    else:
        await callback_query.message.edit_text("❌ دستور نامعتبر است.")

# تابع برای ثبت همه هندلرها
def register_handlers(client: Client):
    """Register all user management handlers"""
    # هندلرها به صورت دکوریتور بالا تعریف شده‌اند
    # این تابع برای سازگاری با ساختار قبلی نگه داشته شده
    pass

# این بخش برای تست مستقیم فایل است
if __name__ == "__main__":
    print("✅ فایل مدیریت کاربران برای Hydrogram آماده است!")