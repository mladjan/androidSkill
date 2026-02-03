# 🚀 Quick Start Guide

## ✅ Setup Complete!

Your SocialBot MVP foundation is fully installed and working!

- **Python Version**: 3.13.9 ✅
- **Virtual Environment**: Active ✅
- **Dependencies**: All installed (36 packages) ✅
- **Playwright**: Chromium browser ready ✅
- **Database**: SQLite initialized ✅
- **CLI**: Working perfectly ✅

---

## 📝 Next Steps (Do These Now!)

### 1. Set Your OpenAI API Key

```bash
# Activate virtual environment (always do this first!)
source venv/bin/activate

# Set your API key
python main.py config set-openai-key sk-your-key-here

# Verify
python main.py config show
```

### 2. Add Your First TikTok Account

```bash
python main.py agent add
```

You'll be prompted for:
- TikTok username
- TikTok password (hidden input)
- Email (optional)

The password will be encrypted with AES-256 and stored securely.

### 3. View Your Agents

```bash
python main.py agent list
```

You'll see a beautiful table with:
- Agent ID
- Username
- Status (🟢 Idle, 🔵 Active, 🔴 Error)
- Comment counts (today/total)
- Last activity

---

## 🎯 Common Commands

### Agent Management
```bash
# Add agent
python main.py agent add

# List all agents
python main.py agent list

# Remove agent
python main.py agent remove 1

# Test agent (coming Week 2)
python main.py agent test 1
```

### Configuration
```bash
# Show current config
python main.py config show

# Set OpenAI key
python main.py config set-openai-key sk-...

# Set daily comment limit (default: 10)
python main.py config set-daily-limit 15
```

### Monitoring
```bash
# View statistics
python main.py stats

# View recent activity
python main.py logs

# View last 50 comments
python main.py logs --limit 50
```

### Automation (Coming Week 3)
```bash
# Start bot
python main.py start

# Stop bot
python main.py stop

# Live dashboard
python main.py status
```

---

## 🔧 Development Workflow

### Always Activate venv First!
```bash
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows
```

### Check Logs
```bash
# View log file
tail -f data/logs/bot.log

# Or via CLI
python main.py logs
```

### Database Location
```bash
# SQLite database
data/database.db

# Can view with
sqlite3 data/database.db
# .tables
# .schema agents
# SELECT * FROM agents;
```

---

## 📅 Week-by-Week Plan

### ✅ Week 1: Foundation (DONE!)
- [x] Project structure
- [x] Database & CLI
- [x] Configuration
- [x] Encryption
- [x] Documentation

### ⏳ Week 2: TikTok Bot (Next!)
- [ ] Playwright stealth setup
- [ ] Login automation
- [ ] Navigate to For You
- [ ] Comment posting
- [ ] Test with 1 account

### ⏳ Week 3: AI & Scheduler
- [ ] OpenAI integration
- [ ] Comment generation
- [ ] APScheduler
- [ ] 10 comments/day automation

### ⏳ Week 4: Polish
- [ ] Live dashboard
- [ ] Error handling
- [ ] Full testing
- [ ] Documentation

---

## 🎓 Learning Resources

### Project Structure
```
src/
├── cli/          - All CLI commands
├── bot/          - TikTok automation (Week 2)
├── ai/           - OpenAI integration (Week 3)
├── scheduler/    - Job scheduling (Week 3)
├── config.py     - Configuration
├── models.py     - Database models
├── database.py   - Database operations
├── utils.py      - Helper functions
└── logger.py     - Logging setup
```

### Key Files
- `main.py` - Entry point
- `.env` - Your secrets (create from `.env.example`)
- `requirements.txt` - Python dependencies
- `README.md` - Full documentation
- `SETUP.md` - Installation guide

---

## ⚠️ Important Reminders

### Before Using the Bot

1. **Manually create TikTok accounts**:
   - Use different phone numbers
   - Use different emails
   - Add profile info (pic, bio)

2. **Age your accounts (3-7 days)**:
   - Browse daily (5-10 min)
   - Like 5-10 videos
   - Follow 3-5 creators
   - Post 1-2 manual comments
   - This makes accounts look real!

3. **Get OpenAI API key**:
   - Go to platform.openai.com
   - Create account + API key
   - Budget: ~$20-30/month for testing

4. **Understand the risks**:
   - Automation violates TikTok ToS
   - Accounts may get banned
   - Start with test accounts
   - Home IP = higher risk (OK for MVP)

---

## 🐛 Troubleshooting

### Virtual Environment Issues
```bash
# Deactivate and reactivate
deactivate
source venv/bin/activate
```

### Database Locked
```bash
# Kill any running instances
pkill -f "python main.py"
```

### Import Errors
```bash
# Ensure venv is active
source venv/bin/activate

# Check Python version (should be 3.13.9)
python --version

# Reinstall if needed
pip install -r requirements.txt --force-reinstall
```

### Can't Find Playwright Browsers
```bash
playwright install chromium
```

---

## 💡 Tips

1. **Always activate venv**: `source venv/bin/activate`
2. **Check config first**: `python main.py config show`
3. **View logs for debugging**: `python main.py logs` or `tail -f data/logs/bot.log`
4. **Test with 2-3 accounts max** for MVP
5. **Be patient**: Account aging is crucial!

---

## 📞 What's Working Right Now?

✅ **Fully Functional**:
- CLI interface
- Agent management (add/list/remove)
- Configuration management
- Secure credential storage
- Database operations
- Logging system
- Statistics tracking

❌ **Coming Soon**:
- TikTok bot automation (Week 2)
- AI comment generation (Week 3)
- Automatic scheduling (Week 3)
- Live status dashboard (Week 4)

---

## 🎉 You're Ready!

You can now:
1. Add TikTok accounts
2. Set OpenAI key
3. Explore the CLI commands
4. Read the code
5. Age your TikTok accounts manually

**Next session**: We'll build the TikTok bot! 🚀

---

*Generated: January 29, 2026*
*Status: Week 1 Complete ✅*
