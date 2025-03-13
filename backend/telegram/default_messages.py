"""
Default messages for the Telegram bot.
These will be used if the messages are not found in the database.
"""

default_messages = {
    # Welcome and language
    'welcome': {
        'fa': "به ربات V2Ray خوش آمدید! 👋\nلطفا زبان خود را انتخاب کنید:",
        'en': "Welcome to V2Ray Bot! 👋\nPlease select your language:"
    },
    
    # Main menu
    'main_menu': {
        'fa': "🏠 منوی اصلی\nاز دکمه‌های زیر می‌توانید استفاده کنید:",
        'en': "🏠 Main Menu\nYou can use the buttons below:"
    },
    
    # Buttons
    'btn_my_accounts': {
        'fa': "🔑 اکانت‌های من",
        'en': "🔑 My Accounts"
    },
    'btn_buy_subscription': {
        'fa': "🛒 خرید اشتراک",
        'en': "🛒 Buy Subscription"
    },
    'btn_payment': {
        'fa': "💰 پرداخت",
        'en': "💰 Payment"
    },
    'btn_support': {
        'fa': "📞 پشتیبانی",
        'en': "📞 Support"
    },
    'btn_profile': {
        'fa': "👤 پروفایل من",
        'en': "👤 My Profile"
    },
    'btn_admin': {
        'fa': "⚙️ پنل مدیریت",
        'en': "⚙️ Admin Panel"
    },
    'btn_language': {
        'fa': "🌐 تغییر زبان",
        'en': "🌐 Change Language"
    },
    'btn_back_main': {
        'fa': "🔙 بازگشت به منوی اصلی",
        'en': "🔙 Back to Main Menu"
    },
    'btn_back_accounts': {
        'fa': "🔙 بازگشت به لیست اکانت‌ها",
        'en': "🔙 Back to Accounts List"
    },
    
    # Account related
    'no_active_accounts': {
        'fa': "❌ شما هیچ اکانت فعالی ندارید.\nبرای خرید اشتراک از دکمه زیر استفاده کنید:",
        'en': "❌ You don't have any active accounts.\nUse the button below to buy a subscription:"
    },
    'accounts_list': {
        'fa': "📋 لیست اکانت‌های شما:\nبرای مشاهده جزئیات روی هر اکانت کلیک کنید:",
        'en': "📋 Your accounts list:\nClick on each account to see details:"
    },
    'account_details': {
        'fa': """
📊 *جزئیات اکانت*

🔰 *پلن*: {plan_name}
🖥 *سرور*: {server_name}
⏱ *روزهای باقیمانده*: {remaining_days} روز
📅 *تاریخ انقضا*: {expiry_date}
📊 *میزان مصرف*: {data_usage} از {data_limit}
📉 *درصد مصرف*: {usage_percentage}

برای دریافت لینک اتصال، از دکمه‌های زیر استفاده کنید:
""",
        'en': """
📊 *Account Details*

🔰 *Plan*: {plan_name}
🖥 *Server*: {server_name}
⏱ *Remaining Days*: {remaining_days} days
📅 *Expiry Date*: {expiry_date}
📊 *Data Usage*: {data_usage} of {data_limit}
📉 *Usage Percentage*: {usage_percentage}

To get connection links, use the buttons below:
"""
    },
    'config_not_found': {
        'fa': "❌ تنظیمات اکانت شما یافت نشد! لطفاً با پشتیبانی تماس بگیرید.",
        'en': "❌ Your account configuration was not found! Please contact support."
    },
    'config_not_available': {
        'fa': "❌ این نوع کانفیگ برای اکانت شما در دسترس نیست.",
        'en': "❌ This config type is not available for your account."
    },
    'config_link': {
        'fa': "🔗 لینک اتصال {config_type} برای پلن {plan_name} در سرور {server_name}:",
        'en': "🔗 {config_type} connection link for {plan_name} plan on {server_name} server:"
    },
    'qrcode_coming_soon': {
        'fa': "🔜 امکان ارسال QR Code به زودی اضافه خواهد شد.",
        'en': "🔜 QR Code feature will be added soon."
    },
    'btn_vmess_config': {
        'fa': "📲 دریافت کانفیگ VMess",
        'en': "📲 Get VMess Config"
    },
    'btn_vless_config': {
        'fa': "📲 دریافت کانفیگ VLess",
        'en': "📲 Get VLess Config"
    },
    'btn_trojan_config': {
        'fa': "📲 دریافت کانفیگ Trojan",
        'en': "📲 Get Trojan Config"
    },
    'btn_shadowsocks_config': {
        'fa': "📲 دریافت کانفیگ ShadowSocks",
        'en': "📲 Get ShadowSocks Config"
    },
    'btn_subscription_url': {
        'fa': "🔄 دریافت لینک اشتراک",
        'en': "🔄 Get Subscription URL"
    },
    'btn_qrcode': {
        'fa': "📱 دریافت QR Code",
        'en': "📱 Get QR Code"
    },
    
    # Plan related
    'plans_list': {
        'fa': "📋 لیست پلن‌های موجود:\nبرای خرید هر پلن روی آن کلیک کنید:",
        'en': "📋 Available plans:\nClick on each plan to purchase:"
    },
    'no_active_plans': {
        'fa': "❌ در حال حاضر هیچ پلن فعالی وجود ندارد. لطفاً بعداً دوباره تلاش کنید.",
        'en': "❌ No active plans are available at the moment. Please try again later."
    },
    'unlimited_traffic': {
        'fa': "ترافیک نامحدود",
        'en': "Unlimited Traffic"
    },
    'days': {
        'fa': "روز",
        'en': "days"
    },
    'unlimited': {
        'fa': "نامحدود",
        'en': "Unlimited"
    },
    'currency': {
        'fa': "تومان",
        'en': "Toman"
    },
    
    # Payment related
    'payment_menu': {
        'fa': "💰 منوی پرداخت\nاز این قسمت می‌توانید حساب خود را شارژ کنید یا وضعیت پرداخت‌های قبلی را ببینید:",
        'en': "💰 Payment Menu\nYou can recharge your account or check previous payments:"
    },
    'btn_recharge_wallet': {
        'fa': "💸 شارژ کیف پول",
        'en': "💸 Recharge Wallet"
    },
    'btn_payment_history': {
        'fa': "📃 تاریخچه پرداخت‌ها",
        'en': "📃 Payment History"
    },
    'btn_check_payment': {
        'fa': "🔍 پیگیری پرداخت",
        'en': "🔍 Check Payment Status"
    },
    'btn_back_payment': {
        'fa': "🔙 بازگشت به منوی پرداخت",
        'en': "🔙 Back to Payment Menu"
    },
    'no_payment_methods': {
        'fa': "❌ در حال حاضر هیچ روش پرداختی فعال نیست. لطفاً بعداً مجدد تلاش کنید.",
        'en': "❌ No payment methods are currently active. Please try again later."
    },
    'select_payment_method': {
        'fa': "💳 لطفاً روش پرداخت را انتخاب کنید:",
        'en': "💳 Please select a payment method:"
    },
    'enter_payment_amount': {
        'fa': "💲 لطفاً مبلغ مورد نظر برای شارژ کیف پول را به تومان وارد کنید:",
        'en': "💲 Please enter the amount (in Toman) you want to charge your wallet:"
    },
    'invalid_amount': {
        'fa': "❌ مبلغ وارد شده نامعتبر است. لطفاً یک عدد مثبت وارد کنید.",
        'en': "❌ Invalid amount. Please enter a positive number."
    },
    'card_payment_info': {
        'fa': """
💳 *اطلاعات پرداخت کارت به کارت*

💰 *مبلغ*: {amount} تومان
💳 *شماره کارت*: `{card_number}`
👤 *به نام*: {card_holder}

لطفاً مبلغ را به کارت فوق واریز کرده و سپس اطلاعات زیر را وارد کنید:
""",
        'en': """
💳 *Card Payment Information*

💰 *Amount*: {amount} Toman
💳 *Card Number*: `{card_number}`
👤 *Card Holder*: {card_holder}

Please transfer the amount to the above card and then enter the following information:
"""
    },
    'enter_card_number': {
        'fa': "🔢 لطفاً شماره کارت خود را وارد کنید (۱۶ رقم بدون فاصله یا خط تیره):",
        'en': "🔢 Please enter your card number (16 digits without spaces or dashes):"
    },
    'invalid_card_number': {
        'fa': "❌ شماره کارت نامعتبر است. لطفاً یک شماره کارت ۱۶ رقمی وارد کنید.",
        'en': "❌ Invalid card number. Please enter a 16-digit card number."
    },
    'enter_reference_number': {
        'fa': "🧾 لطفاً شماره پیگیری یا شناسه مرجع تراکنش را وارد کنید:",
        'en': "🧾 Please enter the transaction reference or tracking number:"
    },
    'invalid_reference': {
        'fa': "❌ شماره پیگیری نامعتبر است. لطفاً شماره پیگیری تراکنش خود را وارد کنید.",
        'en': "❌ Invalid reference number. Please enter your transaction reference number."
    },
    'enter_transfer_time': {
        'fa': "🕒 لطفاً تاریخ و زمان تراکنش را به صورت YYYY-MM-DD HH:MM وارد کنید (مثال: 1402-05-15 14:30):",
        'en': "🕒 Please enter the transaction date and time in format YYYY-MM-DD HH:MM (example: 2023-08-06 14:30):"
    },
    'invalid_date_format': {
        'fa': "❌ فرمت تاریخ نامعتبر است. لطفاً به صورت YYYY-MM-DD HH:MM وارد کنید (مثال: 1402-05-15 14:30).",
        'en': "❌ Invalid date format. Please enter in format YYYY-MM-DD HH:MM (example: 2023-08-06 14:30)."
    },
    'payment_creation_failed': {
        'fa': "❌ خطا در ثبت پرداخت. لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.",
        'en': "❌ Failed to create payment. Please try again or contact support."
    },
    'payment_created': {
        'fa': """
✅ *پرداخت شما با موفقیت ثبت شد*

💰 *مبلغ*: {amount} تومان
🔑 *کد پیگیری*: `{verification_code}`

این پرداخت در انتظار تایید ادمین است و پس از تایید، به کیف پول شما اضافه خواهد شد.
برای پیگیری وضعیت پرداخت، می‌توانید از بخش "پیگیری پرداخت" استفاده کنید.
""",
        'en': """
✅ *Your payment was successfully registered*

💰 *Amount*: {amount} Toman
🔑 *Verification Code*: `{verification_code}`

This payment is waiting for admin verification and after confirmation, it will be added to your wallet.
You can check the payment status using the "Check Payment Status" option.
"""
    },
    'zarinpal_coming_soon': {
        'fa': "🔜 پرداخت از طریق زرین‌پال به زودی اضافه خواهد شد.",
        'en': "🔜 Zarinpal payment will be added soon."
    },
    'enter_verification_code': {
        'fa': "🔑 لطفاً کد پیگیری پرداخت خود را وارد کنید:",
        'en': "🔑 Please enter your payment verification code:"
    },
    'payment_not_found': {
        'fa': "❌ پرداختی با این کد پیگیری یافت نشد. لطفاً کد را بررسی کرده و دوباره وارد کنید.",
        'en': "❌ No payment found with this verification code. Please check the code and try again."
    },
    'payment_info': {
        'fa': """
📋 *اطلاعات پرداخت*

💰 *مبلغ*: {amount} تومان
📊 *وضعیت تراکنش*: {status}
📊 *وضعیت پرداخت کارتی*: {card_status}
📅 *تاریخ ثبت*: {date}
💳 *شماره کارت*: {card_number}
🧾 *شماره پیگیری*: {reference}

اگر پرداخت شما هنوز تایید نشده است، لطفاً منتظر بمانید. تایید پرداخت ممکن است تا ۲۴ ساعت زمان ببرد.
""",
        'en': """
📋 *Payment Information*

💰 *Amount*: {amount} Toman
📊 *Transaction Status*: {status}
📊 *Card Payment Status*: {card_status}
📅 *Date*: {date}
💳 *Card Number*: {card_number}
🧾 *Reference Number*: {reference}

If your payment is not yet verified, please wait. Payment verification may take up to 24 hours.
"""
    },
    'no_payment_history': {
        'fa': "❌ شما هیچ تراکنش مالی ندارید.",
        'en': "❌ You don't have any transaction history."
    },
    'payment_history': {
        'fa': "📃 تاریخچه پرداخت‌های شما:",
        'en': "📃 Your payment history:"
    },
    'payment_history_item': {
        'fa': "🧾 *شناسه*: {id}\n💰 *مبلغ*: {amount} تومان\n📊 *وضعیت*: {status}\n📋 *نوع*: {type}\n📅 *تاریخ*: {date}",
        'en': "🧾 *ID*: {id}\n💰 *Amount*: {amount} Toman\n📊 *Status*: {status}\n📋 *Type*: {type}\n📅 *Date*: {date}"
    },
    
    # Transaction status
    'status_pending': {
        'fa': "⏳ در انتظار",
        'en': "⏳ Pending"
    },
    'status_completed': {
        'fa': "✅ تکمیل شده",
        'en': "✅ Completed"
    },
    'status_failed': {
        'fa': "❌ ناموفق",
        'en': "❌ Failed"
    },
    'status_expired': {
        'fa': "⌛ منقضی شده",
        'en': "⌛ Expired"
    },
    'status_refunded': {
        'fa': "↩️ بازگشت وجه",
        'en': "↩️ Refunded"
    },
    'status_verified': {
        'fa': "✅ تایید شده",
        'en': "✅ Verified"
    },
    'status_rejected': {
        'fa': "❌ رد شده",
        'en': "❌ Rejected"
    },
    
    # Transaction types
    'type_deposit': {
        'fa': "💰 شارژ کیف پول",
        'en': "💰 Wallet Deposit"
    },
    'type_purchase': {
        'fa': "🛒 خرید",
        'en': "🛒 Purchase"
    },
    'type_refund': {
        'fa': "↩️ بازگشت وجه",
        'en': "↩️ Refund"
    },
    'type_admin': {
        'fa': "⚙️ تنظیم ادمین",
        'en': "⚙️ Admin Adjustment"
    },
    
    # Support related
    'support_message': {
        'fa': "📞 پشتیبانی\nپیام خود را ارسال کنید تا به زودی پاسخ داده شود:",
        'en': "📞 Support\nSend your message and we'll respond shortly:"
    },
    'support_sent': {
        'fa': "✅ پیام شما با موفقیت ارسال شد. به زودی با شما تماس خواهیم گرفت.",
        'en': "✅ Your message was sent successfully. We'll contact you shortly."
    },
    
    # Profile related
    'profile_info': {
        'fa': """
👤 *اطلاعات کاربری*

🆔 *نام کاربری*: {username}
💰 *موجودی کیف پول*: {wallet_balance} تومان
📅 *تاریخ عضویت*: {date_joined}
🌐 *زبان*: {language}
""",
        'en': """
👤 *User Profile*

🆔 *Username*: {username}
💰 *Wallet Balance*: {wallet_balance} Toman
📅 *Join Date*: {date_joined}
🌐 *Language*: {language}
"""
    },
    
    # Admin related
    'admin_menu': {
        'fa': "⚙️ پنل مدیریت\nاز این بخش می‌توانید به عنوان مدیر سیستم به تنظیمات دسترسی داشته باشید:",
        'en': "⚙️ Admin Panel\nFrom this section, you can access system settings as an administrator:"
    },
    'btn_admin_servers': {
        'fa': "🖥 مدیریت سرورها",
        'en': "🖥 Manage Servers"
    },
    'btn_admin_users': {
        'fa': "👥 مدیریت کاربران",
        'en': "👥 Manage Users"
    },
    'btn_admin_plans': {
        'fa': "📋 مدیریت پلن‌ها",
        'en': "📋 Manage Plans"
    },
    'btn_admin_payments': {
        'fa': "💰 مدیریت پرداخت‌ها",
        'en': "💰 Manage Payments"
    },
    'btn_admin_discounts': {
        'fa': "🎁 مدیریت تخفیف‌ها",
        'en': "🎁 Manage Discounts"
    },
    'btn_admin_broadcast': {
        'fa': "📢 ارسال پیام گروهی",
        'en': "📢 Broadcast Message"
    },
    'btn_admin_settings': {
        'fa': "⚙️ تنظیمات ربات",
        'en': "⚙️ Bot Settings"
    },
    
    # Help message
    'help': {
        'fa': """
*راهنمای استفاده از ربات*

/start - شروع مجدد ربات
/help - نمایش این راهنما
/language - تغییر زبان
/cancel - لغو عملیات جاری

برای خرید اشتراک و مدیریت اکانت‌های خود، از منوی اصلی استفاده کنید.
در صورت نیاز به راهنمایی بیشتر، با پشتیبانی تماس بگیرید.
""",
        'en': """
*Bot Help Guide*

/start - Restart the bot
/help - Show this help
/language - Change language
/cancel - Cancel current operation

To purchase a subscription and manage your accounts, use the main menu.
If you need further assistance, contact support.
"""
    },
    
    # Error messages
    'error_general': {
        'fa': "❌ خطایی رخ داده است. لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.",
        'en': "❌ An error has occurred. Please try again or contact support."
    },
    'error_user_not_found': {
        'fa': "❌ کاربر یافت نشد. لطفاً دوباره با /start شروع کنید.",
        'en': "❌ User not found. Please start again with /start."
    }
}

def get_default_message(name, lang='fa'):
    """Get a default message by name and language"""
    if name in default_messages:
        if lang in default_messages[name]:
            return default_messages[name][lang]
        # Fallback to English
        return default_messages[name].get('en', f"Message '{name}' not found.")
    # Message not found
    return f"Message '{name}' not found." 