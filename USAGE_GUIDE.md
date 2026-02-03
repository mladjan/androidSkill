# 🚀 SocialBot Usage Guide

Quick reference for using the TikTok automation bot.

---

## 📋 Prerequisites

1. ✅ Python 3.13 environment activated
2. ✅ All dependencies installed
3. ✅ OpenRouter API key configured
4. ✅ At least one TikTok account created & aged

---

## 🎯 Step-by-Step Guide

### **1. Activate Environment** (Always First!)
```bash
cd /Users/mladjanantic/Work/socialBot
source venv/bin/activate
```

### **2. Configure API Key** (One-time)
```bash
# Already done! But to verify:
python main.py config show

# Should show:
# AI API Key: ***f8d0dbe9
# AI Model: openai/gpt-3.5-turbo
```

### **3. Add Your First TikTok Account**
```bash
python main.py agent add

# You'll be prompted for:
# - TikTok username (or email)
# - Password (hidden)
# - Email (optional)
```

**Example**:
```
TikTok username: my_tiktok_account
TikTok password: ************
Email (optional): myemail@gmail.com
✓ Agent 'my_tiktok_account' added successfully (ID: 1)
```

### **4. Test Login** (Important!)
```bash
# For first-time login, use non-headless mode
# Edit .env first:
nano .env
# Change: HEADLESS=false

# Then test login
python main.py agent test 1
```

**What Happens**:
- Browser window opens
- Navigates to TikTok login
- Types your credentials
- Clicks login
- **If CAPTCHA appears**: Solve it manually
- Saves session
- Closes browser

**Expected Output**:
```
Testing login for agent 'my_tiktok_account'...
[Agent 1] Launching browser...
[Agent 1] Navigating to login page...
[Agent 1] Entering credentials...
[Agent 1] ✓ Login successful!
✓ Login successful for 'my_tiktok_account'!
```

### **5. View Your Agents**
```bash
python main.py agent list
```

**Example Output**:
```
┏━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ ID ┃ Username         ┃ Email       ┃ Status   ┃ Today/Total┃ Last Activity┃
┡━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ 1  │ my_tiktok_account│ myemail@... │ 🟢 Idle  │ 0/0        │ Never        │
└────┴──────────────────┴─────────────┴──────────┴────────────┴──────────────┘
```

### **6. Manual Comment Test** (Python)

Create a test script `test_comment.py`:
```python
#!/usr/bin/env python3
from src.bot.tiktok_bot import TikTokBot
from src.database import db

# Get agent
agent = db.get_agent(1)
password = db.get_agent_password(1)

# Create bot
bot = TikTokBot(
    agent_id=agent.id,
    username=agent.username,
    password=password
)

# Post a comment (will login if needed)
result = bot.run_comment_cycle("This is amazing! 🔥")

print(f"Status: {result['status']}")
print(f"Video: {result['video_info']}")
print(f"Error: {result['error']}")
```

Run it:
```bash
python test_comment.py
```

---

## 🛠️ Common Commands

### **Agent Management**
```bash
# Add agent
python main.py agent add

# List agents
python main.py agent list

# Test agent login
python main.py agent test 1

# Remove agent
python main.py agent remove 1
```

### **Configuration**
```bash
# View config
python main.py config show

# Change AI model
python main.py config set-model openai/gpt-4o-mini

# Set daily limit
python main.py config set-daily-limit 20

# Set headless mode (via .env)
nano .env  # Change HEADLESS=true/false
```

### **Monitoring**
```bash
# View statistics
python main.py stats

# View recent activity
python main.py logs

# View last 50 comments
python main.py logs --limit 50

# Watch logs live
tail -f data/logs/bot.log
```

---

## ⚙️ Configuration Options

### **Edit .env File**:
```bash
nano .env
```

### **Important Settings**:
```bash
# AI Configuration
OPENAI_API_KEY=sk-or-v1-your-key-here
OPENAI_MODEL=openai/gpt-3.5-turbo

# Bot Behavior
COMMENTS_PER_DAY=10
MIN_DELAY_MINUTES=30
MAX_DELAY_MINUTES=90

# Browser
HEADLESS=false  # Set to 'true' after first login

# Typing Speed
TYPING_SPEED_WPM=60
```

---

## 🐛 Troubleshooting

### **Problem: Login Fails**
```bash
# Solution 1: Use non-headless mode
nano .env
# Change: HEADLESS=false

# Solution 2: Check credentials
python main.py agent list
python main.py agent remove 1
python main.py agent add  # Re-add with correct password

# Solution 3: Check logs
tail -f data/logs/bot.log
```

### **Problem: CAPTCHA Appears**
```bash
# Solution: Use non-headless mode and solve manually
nano .env
# Change: HEADLESS=false

python main.py agent test 1
# When CAPTCHA appears, solve it
# Bot waits 60 seconds
```

### **Problem: Can't Find Comment Box**
```
# TikTok's UI may have changed
# Check logs for specific error
tail -f data/logs/bot.log

# You may need to update selectors in:
# src/bot/tiktok_bot.py
```

### **Problem: Session Not Saving**
```bash
# Check permissions
ls -la data/browser_profiles/
chmod -R 755 data/

# Verify session file exists after test
ls data/browser_profiles/agent_1/
```

---

## 📊 Monitoring Your Bots

### **Real-time Logs**:
```bash
# Watch logs as they happen
tail -f data/logs/bot.log

# Filter for specific agent
tail -f data/logs/bot.log | grep "Agent 1"

# Filter for errors only
tail -f data/logs/bot.log | grep "ERROR"
```

### **Check Database**:
```bash
# SQLite command line
sqlite3 data/database.db

# View agents
SELECT * FROM agents;

# View recent comments
SELECT * FROM comments ORDER BY posted_at DESC LIMIT 10;

# Exit
.quit
```

### **Check Statistics**:
```bash
python main.py stats

# Example output:
# Total Agents:      2
# Total Comments:    15
# Comments Today:    5
# Success Rate:      86.7%
```

---

## 🎯 Week 3 Preview (Coming Soon)

### **Automated Scheduling** (Not yet implemented):
```bash
# Start automation (runs in background)
python main.py start

# All agents will automatically:
# 1. Generate AI comments
# 2. Post 10-30 comments/day
# 3. Random timing (30-90 min apart)
# 4. Handle errors gracefully

# Stop automation
python main.py stop

# Live dashboard
python main.py status
```

---

## 💡 Pro Tips

### **First Time Setup**:
1. Set `HEADLESS=false` in `.env`
2. Add one agent
3. Test login: `python main.py agent test 1`
4. Solve CAPTCHA if needed
5. Once session saved, set `HEADLESS=true`

### **Account Aging**:
Before automation:
- Use account manually for 3-7 days
- Like videos, follow people
- Post 1-2 manual comments
- Build account age/trust

### **Testing**:
- Start with 1 account
- Post 2-3 manual comments first
- Wait 30-60 min between comments
- Monitor for shadowbans

### **Headless Mode**:
- **First login**: `HEADLESS=false` (for CAPTCHA)
- **After session saved**: `HEADLESS=true` (production)

### **Rate Limiting**:
- Don't exceed 30 comments/day per account
- Wait at least 30 min between comments
- Mix times of day
- Take breaks (1-2 days per week)

---

## 📱 Quick Reference Card

```
╔════════════════════════════════════════════════════════╗
║             SOCIALBOT QUICK COMMANDS                   ║
╠════════════════════════════════════════════════════════╣
║ Activate:  source venv/bin/activate                   ║
║ Add Agent: python main.py agent add                   ║
║ Test Bot:  python main.py agent test 1                ║
║ View List: python main.py agent list                  ║
║ Check Config: python main.py config show              ║
║ View Stats:   python main.py stats                    ║
║ View Logs:    python main.py logs                     ║
║ Live Logs:    tail -f data/logs/bot.log               ║
╚════════════════════════════════════════════════════════╝
```

---

## 🔗 Documentation Links

- **README.md** - Full project documentation
- **WEEK2_COMPLETE.md** - Week 2 implementation details
- **OPENROUTER_MODELS.md** - AI model selection guide
- **QUICKSTART.md** - Quick setup guide
- **STATUS.md** - Project status & progress

---

**Last Updated**: January 29, 2026
**Version**: 0.2.0 (Week 2 Complete)

Ready to test? Run:
```bash
source venv/bin/activate
python main.py agent test 1
```
