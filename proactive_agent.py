import asyncio
import os
import logging
import json
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from dotenv import load_dotenv
from agent import DishaAgent
from proactive_agent import ProactiveDishaAgent

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEFAULT_USER_PHONE = "9876543210"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize agents
disha = DishaAgent()
proactive_disha = ProactiveDishaAgent(TELEGRAM_BOT_TOKEN)

# User registry file (simple JSON for hackathon)
USERS_FILE = "registered_users.json"


def load_registered_users():
    """Load registered users from file"""
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}


def save_registered_user(phone: str, chat_id: int, user_info: dict):
    """Save user registration"""
    users = load_registered_users()
    users[phone] = {
        "chat_id": chat_id,
        "name": user_info.get("name", "User"),
        "registered_at": user_info.get("timestamp")
    }
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)
    
    # Register with proactive agent
    proactive_disha.register_user(phone, chat_id)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = """
🙏 *Namaste! Main Disha hoon - Aapki AI Financial Advisor!*

Main aapki financial health monitor karti hoon aur automatically alerts bhejti hoon jab:
• Balance low ho
• Bills due ho
• Festival aa raha ho
• Gambling zyada ho gayi
• Savings ka time ho

📱 *Setup:* Apna bank-registered phone number bhejo (10 digits)
Example: 9876543210

Ya /skip dabao demo ke liye.
    """
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown'
    )


async def skip_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /skip - use demo account"""
    chat_id = update.effective_chat.id
    context.user_data['phone'] = DEFAULT_USER_PHONE
    context.user_data['user_name'] = "Raju"
    
    # Register for proactive notifications
    save_registered_user(
        DEFAULT_USER_PHONE, 
        chat_id,
        {
            "name": "Raju (Demo)",
            "timestamp": str(asyncio.get_event_loop().time())
        }
    )
    
    await update.message.reply_text(
        "✅ Demo account connected!\n\n"
        "🤖 *Proactive Mode Enabled!*\n"
        "Main ab automatically aapko alerts bhejungi:\n"
        "• Low balance warnings\n"
        "• Bill reminders\n"
        "• Gambling alerts\n"
        "• Savings tips\n\n"
        "Aap mujhse normally baat bhi kar sakte ho! 💬\n\n"
        "/help - Commands dekhne ke liye",
        parse_mode='Markdown'
    )


async def notifications_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle proactive notifications"""
    phone = context.user_data.get('phone')
    if not phone:
        await update.message.reply_text("Pehle /start dabao!")
        return
    
    # Toggle setting
    current = context.user_data.get('notifications', True)
    context.user_data['notifications'] = not current
    
    status = "enabled" if not current else "disabled"
    emoji = "🔔" if not current else "🔕"
    
    await update.message.reply_text(
        f"{emoji} Proactive notifications {status}!\n\n"
        f"{'Ab main automatically alerts bhejungi.' if not current else 'Ab sirf aap puchoge to reply karungi.'}"
    )


async def test_alerts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manually trigger proactive check (for testing)"""
    phone = context.user_data.get('phone')
    if not phone:
        await update.message.reply_text("Pehle /start dabao!")
        return
    
    await update.message.reply_text("🔍 Running proactive checks...")
    
    # Run all checks
    chat_id = update.effective_chat.id
    checks = [
        proactive_disha.check_low_balance(phone),
        proactive_disha.check_excessive_spending(phone),
        proactive_disha.check_gambling_pattern(phone),
        proactive_disha.check_upcoming_bills(phone),
        proactive_disha.check_no_emergency_fund(phone),
        proactive_disha.check_good_income_day(phone),
    ]
    
    results = await asyncio.gather(*checks)
    
    sent_count = 0
    for message in results:
        if message:
            await update.message.reply_text(message, parse_mode='Markdown')
            sent_count += 1
            await asyncio.sleep(1)
    
    if sent_count == 0:
        await update.message.reply_text(
            "✅ Sab kuch theek hai! Koi alert nahi. 👍"
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help with proactive features"""
    help_text = """
🤖 *Disha - Your Proactive Financial Advisor*

*Proactive Features (Automatic):*
⚠️ Low balance warnings
📅 Bill payment reminders (3 days before)
🎰 Gambling pattern alerts
💰 High spending notifications
🎉 Festival preparation reminders
💡 Savings nudges on good income days

*Commands:*
/start - Register account
/skip - Use demo account
/balance - Quick balance check
/spending - This week's spending
/alerts - Test all proactive checks
/notifications - Toggle auto-alerts on/off
/help - This message

*Natural Language:*
Just talk to me normally in Hinglish!
"Mera balance?", "₹500 save karo", etc.

*How Proactive Works:*
Main har hour automatically check karti hoon aur zarurat hone pe alerts bhejti hoon - aapko kuch karna nahi padta! 🚀
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick balance check"""
    phone = context.user_data.get('phone')
    if not phone:
        await update.message.reply_text("Pehle /start dabao!")
        return
    
    await update.message.reply_text("💭 Checking...")
    response = await disha.process_message(phone, "Mera current balance kya hai?")
    await update.message.reply_text(response)


async def spending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick spending summary"""
    phone = context.user_data.get('phone')
    if not phone:
        await update.message.reply_text("Pehle /start dabao!")
        return
    
    await update.message.reply_text("💭 Analyzing...")
    response = await disha.process_message(phone, "Is hafte kitna kharch hua?")
    await update.message.reply_text(response)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages"""
    user_message = update.message.text
    
    # Check if phone is registered
    if 'phone' not in context.user_data:
        # Check if message is a phone number
        if user_message.isdigit() and len(user_message) == 10:
            chat_id = update.effective_chat.id
            context.user_data['phone'] = user_message
            
            user_name = update.message.from_user.first_name or "Friend"
            context.user_data['user_name'] = user_name
            
            # Register for proactive notifications
            save_registered_user(
                user_message,
                chat_id,
                {
                    "name": user_name,
                    "timestamp": str(asyncio.get_event_loop().time())
                }
            )
            
            await update.message.reply_text(
                f"✅ Account {user_message} connected!\n\n"
                f"Namaste Raju Bhai! 🙏\n\n"
                f"🔔 *Proactive Mode Enabled!*\n"
                f"Main automatically alerts bhejungi when needed.\n\n"
                f"Ab aap mujhse normally baat kar sakte ho!\n"
                f"/help - More options",
                parse_mode='Markdown'
            )
            return
        else:
            await update.message.reply_text(
                "❌ Invalid phone number!\n\n"
                "10-digit number bhejo (9876543210)\n"
                "Ya /skip for demo."
            )
            return
    
    # Process message with Disha
    phone = context.user_data['phone']
    await update.message.chat.send_action("typing")
    
    try:
        conversation_history = context.user_data.get('history', [])
        response = await disha.process_message(phone, user_message, conversation_history)
        
        # Update history
        conversation_history.append({"role": "user", "content": user_message})
        conversation_history.append({"role": "assistant", "content": response})
        
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]
        
        context.user_data['history'] = conversation_history
        
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(
            f"😅 Technical problem: {str(e)[:100]}"
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.message:
        await update.message.reply_text("😅 Error! Please try again.")


async def background_monitoring(application: Application):
    """Run proactive monitoring in background"""
    logger.info("🔄 Starting background monitoring...")
    
    # Load registered users
    users = load_registered_users()
    for phone, user_data in users.items():
        proactive_disha.register_user(phone, user_data['chat_id'])
    
    # Start monitoring loop (check every 60 minutes)
    while True:
        try:
            await proactive_disha.run_proactive_checks()
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
        
        await asyncio.sleep(3600)  # 60 minutes


def main():
    """Start the bot with background monitoring"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found!")
        return
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("skip", skip_phone))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("spending", spending_command))
    application.add_handler(CommandHandler("alerts", test_alerts_command))
    application.add_handler(CommandHandler("notifications", notifications_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Start background monitoring
    loop = asyncio.get_event_loop()
    loop.create_task(background_monitoring(application))
    
    print("🤖 Disha Bot with Proactive Features Starting...")
    print("✅ Background monitoring enabled (checks every 60 min)")
    print("📊 Bot is running! Press Ctrl+C to stop.")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()