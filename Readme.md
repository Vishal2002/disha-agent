# Disha Agent - Python AI Module

AI-powered financial advisor agent that connects to the banking backend via MCP protocol and provides proactive financial guidance through Telegram.

## 🚀 Features

- **Proactive Monitoring**: Automatically checks user finances every hour and sends alerts
- **Hinglish Support**: Communicates in Hindi + English mix for better accessibility
- **MCP Integration**: Secure connection to banking backend using Model Context Protocol
- **OpenAI Powered**: Uses GPT-4 for intelligent financial advice
- **Telegram Bot**: Easy access through Telegram messenger

## 📁 Project Structure

```
agent/
├── agent.py                    # Core Disha AI agent logic
├── telegram_bot.py             # Basic Telegram bot (reactive)
├── telegram_bot_with_proactive.py  # Telegram bot with background monitoring
├── proactive_agent.py          # Proactive check logic (alerts system)
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
└── README.md                   # This file
```

## 🛠️ Setup

### Prerequisites

- Python 3.8
- Backend server running on `http://localhost:3000`
- OpenAI API key
- Telegram Bot Token (from @BotFather)

### Installation

1. **Clone the repository**
   ```bash
   cd disha-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create `.env` file**
   ```bash
   touch .env
   ```

4. **Add environment variables to `.env`**
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   ```

## 🏃 Running the Agent

### Option 1: Terminal Chat (Testing)
```bash
python agent.py
```
Interactive terminal chat with Disha for testing.

### Option 2: Basic Telegram Bot
```bash
python telegram_bot.py
```
Telegram bot with reactive chat (responds to user messages).

### Option 3: Proactive Telegram Bot (Recommended)
```bash
python telegram_bot_with_proactive.py
```
Full-featured bot with background monitoring and automatic alerts.

## 📱 Using the Telegram Bot

1. **Start the bot** (run one of the Python files above)
2. **Open Telegram** and search for your bot
3. **Send `/start`** to begin
4. **Send `/skip`** to use demo account (phone: 9876543210)
5. **Start chatting!** Try:
   - "Mera balance kya hai?"
   - "Is hafte kitna kharch hua?"
   - "₹500 emergency fund mein daal do"

### Available Commands

- `/start` - Register your account
- `/skip` - Use demo account
- `/balance` - Quick balance check
- `/spending` - This week's spending
- `/alerts` - Manually trigger proactive checks
- `/help` - Show help message

## 🔍 Testing

Run integration tests to verify everything works:

```bash
python test_integration.py
```

This will check:
- Backend connectivity
- MCP protocol connection
- OpenAI API access
- All core features

## 🤖 How It Works

```
User (Telegram) 
    ↓
telegram_bot.py
    ↓
agent.py (DishaAgent)
    ↓
MCP Client (SSE)
    ↓
Backend MCP Server (http://localhost:3000/sse) or (https://disha-bank-mcp.onrender.com/sse)
    ↓
MongoDB (Bank Data)
```

## 🔔 Proactive Features

The proactive agent automatically checks for:

- ⚠️ Low balance warnings
- 📅 Upcoming bill reminders (3 days before)
- 🎰 Gambling/wasteful spending detection
- 💰 Emergency fund building nudges
- 🎉 Festival preparation alerts
- 💡 Good income day savings suggestions
- 📊 High spending pattern warnings

Runs every **60 minutes** in the background.

## 📝 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 | Yes |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token from BotFather | Yes |

## 🐛 Troubleshooting

**Bot not responding?**
- Check if backend server is running (`http://localhost:3000`)
- Verify `.env` file has correct API keys
- Check terminal for error messages
- For simplicity I deployed it (`https://disha-bank-mcp.onrender.com/`)

**"Session not found" error?**
- Restart the backend server
- MCP SSE connection might have timed out

**"Account not found" error?**
- Make sure backend database is seeded
- Use phone number: `9876543210` for demo

## 📚 Key Files Explained

- **`agent.py`**: Core `DishaAgent` class with MCP integration and OpenAI logic
- **`telegram_bot_with_proactive.py`**: Main bot file with background scheduler
- **`proactive_agent.py`**: Contains all proactive check logic (7 different alerts)

## 🚀 For Hackathon Demo

1. Start backend: `npm run dev` (in backend folder)
2. Start bot: `python telegram_bot_with_proactive.py`
3. Open Telegram → Send `/skip`
4. Demo queries:
   - "Mera balance kya hai?"
   - "Dream11 pe kitna gaya?"
   - "/alerts" (shows all proactive checks)


## 👥 Team

[Vishal Sharma , Utsav Sahu, Manish Singh]
