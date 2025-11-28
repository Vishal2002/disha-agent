import asyncio
import os
import logging
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

load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEFAULT_USER_PHONE = "9876543210"  # Fallback for demo

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Disha Agent
disha = DishaAgent()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = """
🙏 Namaste! Main Disha hoon - Aapki financial advisor!

Mujhe aapke bank account se connect karna hai.

📱 *Apna registered phone number bhejo* (10 digits)
Example: 9876543210

Ya fir /skip dabao demo ke liye.
    """
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown'
    )


async def skip_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /skip command - use demo account"""
    context.user_data['phone'] = DEFAULT_USER_PHONE
    context.user_data['user_name'] = "Raju"
    
    await update.message.reply_text(
        "✅ Demo account connected (Raju - 9876543210)\n\n"
        "Ab mujhse kuch bhi pucho:\n"
        "• Mera balance kitna hai?\n"
        "• Is mahine kitna kharch hua?\n"
        "• ₹500 savings mein daal do\n"
        "• Dream11 pe kitna gaya?\n\n"
        "Commands:\n"
        "/balance - Quick balance check\n"
        "/spending - This week's spending\n"
        "/help - More info"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
🤖 *Disha - Aapki Financial Advisor*

*Main kya kar sakti hoon:*
✅ Balance check karna
✅ Spending pattern dikhana
✅ Savings mein paise transfer karna
✅ Emergency fund banana
✅ Wasteful expenses pe warn karna

*Quick Commands:*
/balance - Current balance
/spending - Is hafte ka kharch
/savings - Savings suggestions
/help - Ye message

*Examples:*
"Mera balance kitna hai?"
"Is mahine kitna Dream11 pe kharch hua?"
"₹1000 emergency fund mein daal do"
"School fees ke liye kitna save karna chahiye?"
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick balance check"""
    phone = context.user_data.get('phone')
    if not phone:
        await update.message.reply_text(
            "Pehle /start dabao aur apna phone number register karo!"
        )
        return
    
    await update.message.reply_text("💭 Checking...")
    response = await disha.process_message(phone, "Mera current balance kya hai?")
    await update.message.reply_text(response)


async def spending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick spending summary"""
    phone = context.user_data.get('phone')
    if not phone:
        await update.message.reply_text(
            "Pehle /start dabao aur apna phone number register karo!"
        )
        return
    
    await update.message.reply_text("💭 Analyzing...")
    response = await disha.process_message(phone, "Is hafte kitna kharch hua?")
    await update.message.reply_text(response)


async def savings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Savings suggestions"""
    phone = context.user_data.get('phone')
    if not phone:
        await update.message.reply_text(
            "Pehle /start dabao aur apna phone number register karo!"
        )
        return
    
    await update.message.reply_text("💭 Thinking...")
    response = await disha.process_message(
        phone, 
        "Mujhe savings ke liye kya advice dogi? Aur emergency fund kitna hona chahiye?"
    )
    await update.message.reply_text(response)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages"""
    user_message = update.message.text
    
    # Check if phone is registered
    if 'phone' not in context.user_data:
        # Check if message is a phone number
        if user_message.isdigit() and len(user_message) == 10:
            context.user_data['phone'] = user_message
            
            # Try to get user name from first message
            user_name = update.message.from_user.first_name or "Friend"
            context.user_data['user_name'] = user_name
            
            await update.message.reply_text(
                f"✅ Account {user_message} connected!\n\n"
                f"Namaste {user_name}! 🙏\n\n"
                "Ab aap mujhse financial advice le sakte ho.\n\n"
                "*Try these:*\n"
                "• Mera balance kitna hai?\n"
                "• Is mahine kitna kharch hua?\n"
                "• Dream11 pe kitna gaya?\n"
                "• ₹500 savings pocket mein daal do\n\n"
                "Ya /help dabao for more options!",
                parse_mode='Markdown'
            )
            return
        else:
            await update.message.reply_text(
                "❌ Ye valid phone number nahi hai!\n\n"
                "Please 10-digit number bhejo (Example: 9876543210)\n"
                "Ya /skip dabao demo ke liye."
            )
            return
    
    # Process message with Disha
    phone = context.user_data['phone']
    
    # Show typing indicator
    await update.message.chat.send_action("typing")
    
    try:
        # Get conversation history (last 5 messages for context)
        conversation_history = context.user_data.get('history', [])
        
        # Process with Disha
        response = await disha.process_message(phone, user_message, conversation_history)
        
        # Update conversation history
        conversation_history.append({"role": "user", "content": user_message})
        conversation_history.append({"role": "assistant", "content": response})
        
        # Keep only last 10 messages (5 pairs)
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]
        
        context.user_data['history'] = conversation_history
        
        # Send response
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text(
            "😅 Sorry, thoda technical problem aa gaya. Please try again!\n\n"
            f"Error: {str(e)[:100]}"
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.message:
        await update.message.reply_text(
            "😅 Oops! Kuch gadbad ho gayi. Please try again!"
        )


def main():
    """Start the bot"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env file!")
        print("\nSteps to fix:")
        print("1. Talk to @BotFather on Telegram")
        print("2. Create a new bot with /newbot")
        print("3. Copy the token and add to .env:")
        print("   TELEGRAM_BOT_TOKEN=your_token_here")
        return
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("skip", skip_phone))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("spending", spending_command))
    application.add_handler(CommandHandler("savings", savings_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    print("🤖 Disha Telegram Bot is starting...")
    print("✅ Bot is running! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()