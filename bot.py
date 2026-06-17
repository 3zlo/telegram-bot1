import requests
import random
import string
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# ========== توكن البوت ==========
# ملاحظة: استبدل هذا التوكن بالتوكن الجديد من @BotFather إذا كان لا يعمل
BOT_TOKEN = "8962868238:AAFAExc87c6jcUcZUHhEUbSGHHz-7IzdFcI"

# ========== USERNAME CHECKER ==========
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
PLATFORMS = {
    'tiktok': 'https://www.tiktok.com/@{username}',
    'discord': 'https://discord.com/api/v9/users/{username}'
}
AVAILABLE_USERNAMES = []

def check_username(username, platform):
    url = PLATFORMS[platform].format(username=username)
    try:
        response = requests.get(url, headers=HEADERS, timeout=3)
        return response.status_code == 404
    except:
        return None

def generate_usernames(count=50, length=4):
    chars = string.ascii_lowercase + string.digits
    usernames = [''.join(random.choices(chars, k=length)) for _ in range(count)]
    return list(dict.fromkeys(usernames))

def scan_multiple_usernames(usernames, platforms):
    results = {}
    global AVAILABLE_USERNAMES
    AVAILABLE_USERNAMES = []
    for username in usernames:
        results[username] = {}
        for platform in platforms:
            status = check_username(username, platform)
            if status is None:
                results[username][platform] = '⚠️ خطأ'
            elif status:
                results[username][platform] = '✅ متاح'
                if username not in AVAILABLE_USERNAMES:
                    AVAILABLE_USERNAMES.append(username)
            else:
                results[username][platform] = '❌ محجوز'
            time.sleep(0.05)
    return results

# ========== KEYBOARDS ==========
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎵 TikTok", callback_data="tiktok"), InlineKeyboardButton("🎮 Discord", callback_data="discord")],
        [InlineKeyboardButton("🔍 فحص يوزرات", callback_data="username_checker"), InlineKeyboardButton("📋 المتاحة", callback_data="show_available")],
        [InlineKeyboardButton("ℹ️ عن البوت", callback_data="about")]
    ]
    return InlineKeyboardMarkup(keyboard)

def username_checker_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎲 توليد 20 يوزر وفحص", callback_data="check_20")],
        [InlineKeyboardButton("🎲 توليد 50 يوزر وفحص", callback_data="check_50")],
        [InlineKeyboardButton("🎲 توليد 100 يوزر وفحص", callback_data="check_100")],
        [InlineKeyboardButton("📝 فحص يوزر واحد", callback_data="check_single")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_keyboard(back_to):
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data=back_to)]])

def tiktok_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("📊 فحص حساب TikTok", callback_data="tiktok_check")], [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]])

def discord_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🤖 أفضل بوتات", callback_data="discord_bots")], [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]])

# ========== CONTENT ==========
CONTENT = {
    "about": {"text": "ℹ️ *عن البوت*\n\nبوت فحص يوزرات TikTok و Discord.\n\n📌 الأوامر:\n/start — القائمة الرئيسية", "back": "main_menu"},
    "tiktok_check": {"text": "📊 *فحص حساب TikTok*\n\nاستخدم أداة فحص اليوزرات من القائمة الرئيسية.", "back": "tiktok"},
    "discord_bots": {"text": "🤖 *أفضل بوتات Discord*\n\n• MEE6 — إدارة\n• Dyno — مشرف", "back": "discord"}
}

# ========== HANDLERS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 أهلاً! بوت فحص يوزرات TikTok و Discord.\nاختر ما تريد:", parse_mode="Markdown", reply_markup=main_menu_keyboard())

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📋 القائمة الرئيسية:", reply_markup=main_menu_keyboard())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ /start - البداية\n/menu - القائمة\n/help - المساعدة")

async def show_available(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global AVAILABLE_USERNAMES
    if not AVAILABLE_USERNAMES:
        await update.message.reply_text("📋 *لا توجد يوزرات متاحة حالياً*\n\nقم بفحص يوزرات أولاً.", parse_mode="Markdown")
        return
    msg = "📋 *اليوزرات المتاحة:*\n\n" + "\n".join([f"{i}. {u}" for i, u in enumerate(AVAILABLE_USERNAMES, 1)])
    await update.message.reply_text(msg, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "main_menu":
        await query.edit_message_text("📋 القائمة الرئيسية:", reply_markup=main_menu_keyboard())
    elif data == "show_available":
        global AVAILABLE_USERNAMES
        if not AVAILABLE_USERNAMES:
            await query.edit_message_text("📋 *لا توجد يوزرات متاحة حالياً*", parse_mode="Markdown", reply_markup=back_keyboard("main_menu"))
            return
        msg = "📋 *اليوزرات المتاحة:*\n\n" + "\n".join([f"{i}. {u}" for i, u in enumerate(AVAILABLE_USERNAMES, 1)])
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=back_keyboard("main_menu"))
    elif data == "username_checker":
        await query.edit_message_text("🔍 *أداة فحص اليوزرات*\n\nاختر عدد اليوزرات لتوليدها وفحصها تلقائياً:", parse_mode="Markdown", reply_markup=username_checker_keyboard())
    elif data == "check_single":
        await query.edit_message_text("📝 *فحص يوزر واحد*\n\nأرسل اسم المستخدم للفحص", parse_mode="Markdown", reply_markup=back_keyboard("username_checker"))
        context.user_data['mode'] = 'check_single'
    elif data in ["check_20", "check_50", "check_100"]:
        count = int(data.split('_')[1])
        await query.edit_message_text(f"🎲 *جاري توليد وفحص {count} يوزر...*\n\n⏳ يرجى الانتظار...", parse_mode="Markdown", reply_markup=None)
        platforms = ['tiktok', 'discord']
        usernames = generate_usernames(count, 4)
        results = scan_multiple_usernames(usernames, platforms)
        
        msg = f"🎯 *نتائج فحص {count} يوزر:*\n\n"
        for username, platforms_result in results.items():
            if any('✅' in status for status in platforms_result.values()):
                available_platforms = [p for p, s in platforms_result.items() if '✅' in s]
                msg += f"✅ {username}: متاح على {', '.join(available_platforms)}\n"
            else:
                msg += f"❌ {username}: محجوز\n"
        
        if not any('✅' in s for result in results.values() for s in result.values()):
            msg += "\n❌ لا توجد يوزرات متاحة"
        else:
            msg += f"\n📊 إجمالي المتاحة: {len(AVAILABLE_USERNAMES)}"
        
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=back_keyboard("username_checker"))
    elif data in CONTENT:
        content = CONTENT[data]
        await query.edit_message_text(content["text"], parse_mode="Markdown", reply_markup=back_keyboard(content["back"]))
    elif data in {"tiktok", "discord"}:
        platform_map = {"tiktok": tiktok_keyboard, "discord": discord_keyboard}
        await query.edit_message_text(f"📂 *قسم {data.title()}*:", parse_mode="Markdown", reply_markup=platform_map[data]())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    mode = context.user_data.get('mode', '')
    platforms = ['tiktok', 'discord']

    if mode == 'check_single':
        if not text:
            await update.message.reply_text("⚠️ الرجاء إدخال اسم مستخدم")
            return
        global AVAILABLE_USERNAMES
        msg = f"🔍 *نتائج فحص {text}:*\n\n"
        for platform in platforms:
            status = check_username(text, platform)
            if status is None:
                msg += f"⚠️ خطأ في {platform}\n"
            elif status:
                msg += f"✅ متاح على {platform}\n"
            else:
                msg += f"❌ محجوز على {platform}\n"
            time.sleep(0.05)
        await update.message.reply_text(msg, parse_mode="Markdown")
        context.user_data['mode'] = None
        return

    await update.message.reply_text("استخدم /start للبدء", reply_markup=main_menu_keyboard())

def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN غير موجود")
        return
    print("🚀 البوت شغال...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("available", show_available))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ البوت جاهز...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
