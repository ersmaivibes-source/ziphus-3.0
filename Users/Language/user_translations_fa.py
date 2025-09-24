"""
Persian user-specific language texts for Ziphus Bot.
"""

USER_TRANSLATIONS_FA = {
    # general User Messages
    'start_message': "سلام! لطفاً زبان خود را انتخاب کنید تا ادامه دهیم:\n\n👋 به ربات خوش آمدید!\n\nمن برای کمک به شما در مدیریت موثر پروژه‌ها، خودکارسازی وظایف و ارتباط با تیمتان طراحی شده‌ام.\n\nبرای شروع، لطفاً زبان مورد نظر خود را انتخاب کنید.",
    'welcome_text': "سلام {name} عزیز.\n\nاول از همه به ربات همه کاره ما خوش اومدی🎉\n\nو دوم اینکه خوشحالیم بابت پیوستن شما به اتحاد زیفوس برای استفاده از ابزارهای ما⚙️\n\n🔺حالا یکی از گزینه های زیر رو انتخاب کن",
    
    # Account Management
    'account': 'مدیریت حساب کاربری 🗂️',
    'account_text': '🔺لطفا گزینه مورد نظر را انتخاب کنید🔺',
    'account_setting': 'تنظیمات حساب ⚙️',
    'user_profile': '👤 پروفایل کاربری',
    'account_upgrade': 'ارتقاء حساب🔝',
    'account_history': 'تاریخچه اکانت من 📜',
    'activate_with_email': '📩فعال سازی با ایمیل',
    'plan_limits': '📊 محدودیت‌ها و استفاده',
    'check_bot_limits': '🔗 محدودیت اضافه کردن ربات',
    'invite_friends': 'دعوت از دوستان 🗣️',
    
    # Registration and Authentication
    'register_email': 'ثبت ایمیل 📧',
    'sign_in_with_email': 'ورود با ایمیل 🔐',
    'change_email': 'تغییر ایمیل 📧',
    'change_password': 'تغییر رمز عبور 🔐',
    'email_request': '📨لطفا آدرس ایمیل معتبر خود را وارد کنید.',
    'invalid_email': '⚠️آدرس ایمیلی که وارد کردید نامعتبر است. لطفا دوباره آن را وارد کنید.',
    'email_exists': 'این آدرس ایمیل قبلاً توسط حساب کاربری دیگری ثبت شده است. لطفاً از ایمیل دیگری استفاده کنید.',
    'password_request': '🔓لطفا رمز خود را وارد کنید.\n\n🔺نکته: از حروف بزرگ و کوچک و علائم نگارشی استفاده کنید.\n🔺رمز باید حداقل 8 کاراکتر باشد.\n🔺علائم مجاز: ? ! @ $ * ( )',
    'email_code_sent': 'کد تایید به {email} ارسال شد. لطفا آن را وارد کنید.',
    'email_send_failed': 'ارسال ایمیل تایید ناموفق بود. لطفا دوباره امتحان کنید.',
    'incorrect_code': 'کد وارد شده اشتباه است. لطفا ایمیل خود را بررسی کرده و دوباره تلاش کنید.',
    'email_verified': 'تایید ایمیل با موفقیت انجام شد! حساب شما به روزرسانی شد.',
    'registration_complete': '🟢اطلاعات شما با موفقیت تکمیل شده و ثبت نام انجام شد.',
    
    # Sign-in Process
    'sign_in_email_request': '📧 لطفاً آدرس ایمیل ثبت شده خود را وارد کنید:',
    'sign_in_password_request': '🔑 لطفاً رمز عبور خود را وارد کنید:',
    'sign_in_successful': '✅ ورود موفقیت‌آمیز! خوش برگشتید!',
    'sign_in_failed': '❌ ایمیل یا رمز عبور نادرست است. لطفاً دوباره تلاش کنید.',
    'sign_in_failed_attempts_remaining': '❌ ایمیل یا رمز عبور نادرست است. {remaining} تلاش دیگر تا قفل شدن حساب باقی مانده است.',
    'account_temporarily_locked': '🔒 حساب شما به دلیل تلاش‌های متعدد برای ورود موقتاً مسدود شده است. لطفاً {minutes} دقیقه دیگر تلاش کنید.',
    'account_locked_due_to_attempts': '🔒 حساب شما به دلیل 5 تلاش ناموفق قفل شده است. لطفاً 15 دقیقه دیگر تلاش کنید.',
    'email_not_registered': '⚠️ این ایمیل ثبت نشده است. لطفاً ابتدا ثبت‌نام کنید یا ایمیل خود را بررسی کنید.',
    'sign_in_cancelled': 'ورود لغو شد.',
    
    # Password Validation
    'password_error_length': '🔴 خطا: رمز عبور باید حداقل 8 کاراکتر باشد.',
    'password_error_uppercase': '🔴 خطا: رمز عبور باید حداقل یک حرف بزرگ داشته باشد.',
    'password_error_lowercase': '🔴 خطا: رمز عبور باید حداقل یک حرف کوچک داشته باشد.',
    'password_error_digit': '🔴 خطا: رمز عبور باید حداقل یک عدد داشته باشد.',
    'password_error_special': '🔴 خطا: رمز عبور باید حداقل یک کاراکتر خاص داشته باشد.',
    'password_error_chars': '🔴 خطا: رمز عبور حاوی کاراکترهای غیرمجاز است.',
    'password_error_complexity': '🔴 خطا: رمز عبور باید شرایط پیچیدگی را داشته باشد.',
    'password_error_weak': '🔴 خطا: رمز عبور خیلی ضعیف است. لطفاً رمز قوی‌تری انتخاب کنید.',
    'password_error_repetitive': '🔴 خطا: رمز عبور حاوی الگوهای تکراری است.',
    'password_error_sequential': '🔴 خطا: رمز عبور حاوی الگوهای متوالی است.',
    'password_error_too_long': '🔴 خطا: رمز عبور خیلی طولانی است.',
    
    # Account Changes
    'current_email': 'ایمیل فعلی',
    'new_email': 'ایمیل جدید',
    'confirm_new_email': 'تایید ایمیل جدید',
    'current_password': 'رمز عبور فعلی',
    'new_password': 'رمز عبور جدید',
    'confirm_new_password': 'تایید رمز عبور جدید',
    'email_change_success': '✅ ایمیل با موفقیت تغییر یافت!',
    'email_change_failed': '❌ تغییر ایمیل ناموفق بود.',
    'password_change_success': '✅ رمز عبور با موفقیت تغییر یافت!',
    'password_change_failed': '❌ تغییر رمز عبور ناموفق بود.',
    'invalid_current_password': '❌ رمز عبور فعلی اشتباه است.',
    'emails_dont_match': '❌ آدرس‌های ایمیل یکسان نیستند.',
    'passwords_dont_match': '❌ رمزهای عبور یکسان نیستند.',
    'enter_current_email': 'ایمیل فعلی خود را وارد کنید:',
    'enter_new_email': 'آدرس ایمیل جدید را وارد کنید:',
    'confirm_email_address': 'آدرس ایمیل جدید را تایید کنید:',
    'enter_current_password': 'رمز عبور فعلی خود را وارد کنید:',
    'confirm_change_email': '✅ تایید تغییر ایمیل',
    'cancel_change_email': '❌ لغو تغییر ایمیل',
    'confirm_change_password': '✅ تایید تغییر رمز عبور',
    'cancel_change_password': '❌ لغو تغییر رمز عبور',
    'password_changed_successfully': '✅ رمز عبور شما با موفقیت تغییر کرد.',
    'current_email_is': 'ایمیل فعلی شما: {email}',
    'email_change_code_sent': '📧 کد تأیید به آدرس ایمیل جدید شما ارسال شد.',
    'no_email_set': '❌ هیچ آدرس ایمیلی برای حساب شما تنظیم نشده است.',
    'no_password_set': '❌ هیچ رمز عبوری برای حساب شما تنظیم نشده است.',
    'incorrect_current_password': '❌ رمز عبور فعلی که وارد کرده‌اید اشتباه است.',
    'resend_verification': '📧 ارسال مجدد کد تایید',
    'change_email_address': '📧 تغییر آدرس ایمیل',
    'recover_with_email': '📧 بازیابی با ایمیل',
    'reset_account_data': '🔄 بازنشانی اطلاعات حساب',
    
    # User Account Information
    'password_not_set': '❌ برای حساب شما رمز عبوری تنظیم نشده است. لطفاً ابتدا با ایمیل ثبت نام کنید.',
    'account_help_text': '💡 **راهنما و پشتیبانی حساب**\n\nیکی از موضوعات زیر را برای دریافت اطلاعات بیشتر انتخاب کنید:',
    
    # Referral System
    'referral_link_text': '🌟 **برنامه زیرمجموعه‌گیری** 🌟\n\nلینک منحصر به فرد خود را با دوستانتان به اشتراک بگذارید! هنگامی که یک کاربر جدید از طریق لینک شما وارد شود، **5 ستاره** دریافت می‌کنید.\n\n🔗 **لینک معرف شما:**\n`{link}`\n\n✨ **ستاره‌های فعلی شما:** {stars}\n\nبرای کپی کردن لینک، روی آن کلیک کنید!',
    'referral_new_user': 'به ربات زیفوس خوش آمدید!\n شما توسط {referrer_name} معرفی شدید و {stars_amount} ستاره دریافت کردید! ⭐',
    'referral_referrer': 'تبریک! {new_user_name} با استفاده از لینک ارجاع شما به ما پیوست. شما 5 ستاره کسب کردید! ⭐',
    
    # Milestones
    'milestone_5_stars': '🎉 تبریک! شما به 50 ستاره رسیدید! این جایزه شماست: 🔸',
    'milestone_15_stars': '🎉 فوق‌العاده! شما به 100 ستاره رسیدید! این جایزه شماست: 🔸🔸',
    'milestone_20_stars': '🎉 باورنکردنی! شما به 200 ستاره رسیدید! این جایزه شماست: 🔸🔸🔸',
    'milestone_10_stars': '🎉 تبریک! شما به 50 ستاره رسیدید! این جایزه شماست: 🔸',
    'milestone_25_stars': '🎉 عالی! شما به 500 ستاره رسیدید! این جایزه شماست: 🔸🔸🔸🔸',
    'milestone_30_stars': '🎉 افسانه‌ای! شما به 1000 ستاره رسیدید! این جایزه شماست: 🔸🔸🔸🔸🔸',
    
    # Account History Fields
    'field_chat_id': 'شناسه چت',
    'field_first_name': 'نام',
    'field_last_name': 'نام خانوادگی',
    'field_username': 'نام کاربری',
    'field_email': 'ایمیل',
    'field_acc_status': 'وضعیت حساب',
    'field_login_date': 'آخرین تاریخ ورود',
    'field_login_time': 'آخرین زمان ورود',
    'field_stars': 'ستاره',
    'field_id': 'شناسه',
    'field_lang_code': 'کد زبان',
    'field_total_referral_links': 'تعداد کل معرفی‌ها',
    'account_details': 'جزئیات حساب',
    'field_referral_by': 'معرف',
    'field_referrer_name': 'نام معرف',
    'field_referrer_username': 'یوزرنیم معرف',
    
    # Account History Sections
    'personal_information': 'اطلاعات شخصی',
    'account_status': 'وضعیت حساب',
    'rewards_and_referrals': 'جوایز و ارجاعات',
    'referral_information': 'اطلاعات ارجاع',
    'account_statistics': 'آمار حساب',
    'account_created': 'حساب ایجاد شده',
    'last_updated': 'آخرین به‌روزرسانی',
    
    # Subscription Management
    'upgrade_current_plan': '⬆️ ارتقاء طرح فعلی',
    'subscription_activated_successfully': '🎉 اشتراک شما با موفقیت فعال شد!',
    'subscription_management_text': '📋 **مدیریت اشتراک**\n\nطرح اشتراک فعلی و تنظیمات خود را مدیریت کنید.',
    'account_upgrade_text': '🚀 **ارتقاء حساب**\n\nامکانات ویژه را باز کنید و تجربه خود را بهبود بخشید!\n\n✨ از پلن‌های فوق‌العاده ما انتخاب کنید:',
    'select_subscription_plan': '📋 **انتخاب طرح اشتراک**\n\nطرحی را انتخاب کنید که بهترین گزینه برای شماست:',
    'expires_on': 'تاریخ انقضا',
    
    # Language Selection
    'persian_language_button': 'فارسی 🇮🇷',
    'english_language_button': 'ENGLISH 🇬🇧',
    'back_to_account_upgrade_menu': '⬅️ بازگشت به ارتقاء حساب',
    
    # User Statistics (for admins)
    'user_statistics_header': '📊 **آمار کاربر**',
    'user_name_label': '👤 **نام:**',
    'chat_id_label': '🆔 **شناسه چت:**',
    'email_label': '📧 **ایمیل:**',
    'language_label': '🌐 **زبان:**',
    'stars_label': '⭐ **ستاره‌ها:**',
    'referrals_label': '👥 **معرفی‌ها:**',
    'joined_label': '📅 **تاریخ عضویت:**',
    'last_login_label': '🔄 **آخرین ورود:**',
    'subscription_label': '💎 **اشتراک:**',
    'banned_status': '🚫 مسدود',
    'active_status': '✅ فعال',
    
    # User Limit Messages
    'limit_exceeded': 'محدودیت استفاده تجاوز کرده است',
    'upgrade_for_more': 'حساب خود را ارتقا دهید تا امکانات بیشتری داشته باشید',
    
    # Data Cleanup
    'clear_database_warning': '⚠️ هشدار! ⚠️\n\n⚠️شما درخواست حذف تمام اطلاعات از پایگاه داده را دارید\n\n⚠️در صورت موافقت تمامی اطلاعات به طور کامل حذف خواهد شد.\n\n❌با این شرایط موافقت میکنید؟',
    'clear_success': '✅حذف اطلاعات با موفقیت انجام شد.\n\nبرای شروع مجدد ربات، روی دکمه START زیر کلیک کنید.',
    'clear_cancelled': 'لغو حذف اطلاعات. بازگشت به تنظیمات.',
    'deleting_data': '✅اطلاعات شما در حال حذف است...',
    'yes': '❌موافقم',
    'no': '✅مخالفم',
    
    # FAQ Content for Users (Persian)
    'faq_registration_content': '📝 **سوالات متداول ثبت نام**\n\n**س: چطور حساب کاربری بسازم؟**\nج: از گزینه "ثبت ایمیل" در تنظیمات حساب استفاده کنید.\n\n**س: آیا حتماً باید حساب بسازم؟**\nج: خیر، می‌توانید بدون حساب از بیشتر امکانات استفاده کنید. حساب کاربری امکان دسترسی از دستگاه‌های مختلف را فراهم می‌کند.',
    'faq_password_content': '🔐 **سوالات متداول رمز عبور**\n\n**س: رمز عبور قوی چگونه باشد؟**\nج: حداقل 8 کاراکتر با حروف بزرگ، کوچک، عدد و علائم خاص (?, !, @, $, *, (, )).\n\n**س: چطور رمز عبورم را تغییر دهم؟**\nج: به تنظیمات حساب > تغییر رمز عبور بروید.',
    'faq_email_content': '📧 **سوالات متداول ایمیل**\n\n**س: چرا باید ایمیلم را تایید کنم؟**\nج: تایید ایمیل امنیت حساب و امکان بازیابی رمز عبور را فراهم می‌کند.\n\n**س: آیا می‌توانم ایمیلم را تغییر دهم؟**\nج: بله، به تنظیمات حساب > تغییر ایمیل بروید.',
    'faq_security_content': '🔒 **سوالات متداول امنیت**\n\n**س: اطلاعاتم چطور محافظت می‌شود؟**\nج: ما از رمزگذاری و امنیت استاندارد صنعت استفاده می‌کنیم.\n\n**س: اگر رمز عبورم را فراموش کنم چکار کنم؟**\nج: از گزینه "بازیابی با ایمیل" استفاده کنید.',
    'faq_account_recovery_content': '🔄 **سوالات متداول بازیابی حساب**\n\n**س: چطور حسابم را بازیابی کنم؟**\nج: اگر ایمیل تایید شده دارید، از گزینه "بازیابی با ایمیل" استفاده کنید.\n\n**س: اگر دسترسی به ایمیلم را ندارم چکار کنم؟**\nج: برای کمک در بازیابی حساب با پشتیبانی تماس بگیرید.',
    
    # Common User Error Messages
    'user_not_found': 'کاربر یافت نشد',
    'session_expired': 'جلسه منقضی شده است',
    'unauthorized': 'غیرمجاز',
    'access_denied': 'دسترسی رد شد',
    'please_start_bot': 'لطفاً ربات را با /start شروع کنید',
    'user_data_not_found': 'اطلاعات کاربر یافت نشد',
    
    # Navigation
    'back': 'بازگشت⬅️',
    'back_to_main': 'بازگشت به منوی اصلی🏠',
    'change_language': 'تغییر زبان 🌐',
    'language_changed': '🟢 زبان شما با موفقیت تغییر یافت.',
    'processing': 'درخواست شما در حال پردازش است...',
    'complete_current_operation': 'لطفاً عملیات فعلی خود را تکمیل کنید قبل از دسترسی به سایر امکانات.',
    'cancelled': 'لغو شد',
    
    # Additional User Features (Persian)
    'settings': 'تنظیمات ⚙️',
    'settings_text': '🔺لطفا گزینه مورد نظر را انتخاب کنید🔺',
    'settings_account': '⚙️ تنظیمات و حساب کاربری',
    'settings_account_text': 'تنظیمات حساب کاربری، ترجیحات و اطلاعات پروفایل خود را از این منوی یکپارچه مدیریت کنید.',
    'payment_method_text': 'روش پرداخت',
    'status_label': 'وضعیت',
    'not_set': 'تنظیم نشده',
    'more_records': '📄 رکوردهای بیشتر',
    'contact_admin': '👨‍💼 تماس با ادمین',
    'contact_support': '🎧 تماس با پشتیبانی',
    
    # Email Templates and Notifications (Persian)
    'password_reset_subject': '🔒 درخواست بازنشانی رمز عبور',
    'password_reset_body': 'شما درخواست بازنشانی رمز عبور داده‌اید. رمز عبور موقت جدید شما: {password}',
    'subscription_confirmation_subject': '🎉 اشتراک فعال شد',
    'subscription_confirmation_body': 'تبریک! اشتراک {plan} شما با موفقیت فعال شد.',
    
    # Plan Comparison (Persian)
    'upgrade_plan': '🚀 ارتقاء پلن',
    'compare_plans': '📊 مقایسه پلن‌ها',
    'plan_comparison_title': 'مقایسه پلن‌ها',
    'cryptocurrency_not_supported': '❌ این ارز دیجیتال پشتیبانی نمی‌شود',
    'click_start_to_begin': '🔄 برای شروع START را کلیک کنید:',
    'select_payment_method': '💳 **انتخاب روش پرداخت**\n\nگزینه پرداخت مورد نظر خود را انتخاب کنید:',
    
    # Support and Tickets (Persian)
    'create_support_ticket': '🎫 ایجاد تیکت پشتیبانی',
    'view_my_tickets': '📄 تیکت‌های من',
    'ticket_subject': '📝 موضوع تیکت',
    'ticket_message': '💬 پیام',
    'submit_ticket': '✅ ارسال تیکت',
    'ticket_submitted': '🎫 تیکت با موفقیت ارسال شد! به‌زودی پاسخ خواهیم داد.',
    'ticket_updated': '✅ تیکت با موفقیت به‌روزرسانی شد.',
    'view_ticket': '📖 مشاهده تیکت',
    'subject_too_short': '⚠️ موضوع خیلی کوتاه است. حداقل 5 کاراکتر وارد کنید.',
    'subject_too_long': '⚠️ موضوع خیلی طولانی است. کمتر از 100 کاراکتر باشد.',
    'message_too_short': '⚠️ پیام خیلی کوتاه است. حداقل 10 کاراکتر وارد کنید.',
    'message_too_long': '⚠️ پیام خیلی طولانی است. کمتر از 2000 کاراکتر باشد.',
    'message_added_successfully': '✅ پیام شما با موفقیت به تیکت اضافه شد.',
    'failed_to_add_message': '❌ اضافه کردن پیام ناموفق بود. دوباره تلاش کنید.',
    'ticket_created_successfully': '🎫 تیکت #{ticket_id} با موفقیت ایجاد شد! تیم پشتیبانی به‌زودی پاسخ خواهد داد.',
    'failed_to_create_ticket': '❌ ایجاد تیکت ناموفق بود. دوباره تلاش کنید.',
    'ticket_not_found': 'تیکت یافت نشد',
}