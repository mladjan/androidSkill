# SocialBot - TikTok Comment Automation MVP

An intelligent CLI tool for automating AI-generated comments on TikTok using Playwright and OpenAI.

## 🎯 Project Status

**Current Phase**: Week 1 - Foundation ✅

- [x] Project structure
- [x] Database models (SQLite)
- [x] Configuration management
- [x] Encryption utilities
- [x] CLI framework
- [x] Agent management commands
- [ ] TikTok automation bot (Week 2)
- [ ] AI comment generation (Week 3)
- [ ] Scheduler & monitoring (Week 3-4)

## 📋 Features

### Current (Week 1)
- ✅ CLI interface with beautiful terminal UI (Rich)
- ✅ Agent (TikTok account) management
- ✅ Secure credential storage (AES-256 encryption)
- ✅ SQLite database with activity logging
- ✅ Configuration management

### Coming Soon
- ⏳ TikTok login automation (Playwright)
- ⏳ AI-powered comment generation (OpenAI GPT-4o-mini)
- ⏳ Smart scheduling (10 comments/day per agent)
- ⏳ Live status dashboard
- ⏳ Activity logs and statistics

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11 or higher
- OpenAI API key (~$20-30/month budget)
- 2-3 manually created TikTok accounts (aged 3-7 days)

### 2. Installation

```bash
# Clone or navigate to project
cd socialBot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Set your OpenAI API key
python main.py config set-openai-key sk-your-api-key-here

# Optional: Adjust daily comment limit (default: 10)
python main.py config set-daily-limit 15

# Verify configuration
python main.py config show
```

### 4. Add TikTok Agents

```bash
# Add your first agent
python main.py agent add
# Enter TikTok username, password, and optional email

# List all agents
python main.py agent list
```

## 📖 Usage

### Agent Management

```bash
# Add a new agent
python main.py agent add

# List all agents
python main.py agent list

# Remove an agent
python main.py agent remove <agent_id>

# Test agent login (coming in Week 2)
python main.py agent test <agent_id>
```

### Configuration

```bash
# Show current configuration
python main.py config show

# Set OpenAI API key
python main.py config set-openai-key sk-...

# Set daily comment limit per agent
python main.py config set-daily-limit 25
```

### Automation Control (Coming in Week 3)

```bash
# Start automation
python main.py start

# Stop automation
python main.py stop

# Live status dashboard
python main.py status
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

## 🏗️ Project Structure

```
socialBot/
├── src/
│   ├── cli/
│   │   ├── main.py              # CLI entry point
│   │   └── commands.py          # All CLI commands
│   ├── bot/
│   │   ├── tiktok_bot.py        # TikTok automation (Week 2)
│   │   └── stealth.py           # Anti-detection (Week 2)
│   ├── ai/
│   │   └── comment_generator.py # OpenAI integration (Week 3)
│   ├── scheduler/
│   │   └── job_scheduler.py     # APScheduler (Week 3)
│   ├── config.py                # Configuration ✅
│   ├── models.py                # Database models ✅
│   ├── database.py              # Database operations ✅
│   ├── utils.py                 # Utilities & encryption ✅
│   └── logger.py                # Logging setup ✅
├── data/
│   ├── database.db              # SQLite database (auto-created)
│   ├── browser_profiles/        # Browser sessions (Week 2)
│   └── logs/                    # Application logs
├── main.py                      # Entry point ✅
├── requirements.txt             # Dependencies ✅
├── .env                         # Your configuration (create from .env.example)
└── README.md                    # This file
```

## 💾 Database Schema

### Agents Table
- Stores TikTok account credentials (encrypted)
- Tracks status, activity, and comment counters
- Manages scheduling (next_run timestamp)

### Comments Table
- Logs all comment attempts
- Tracks success/failure status
- Stores video URLs and comment text

### Settings Table
- Application configuration key-value pairs

## 🔒 Security

- **Password Encryption**: AES-256-GCM via Fernet
- **Automatic Key Generation**: Encryption key auto-generated on first run
- **Secure Storage**: Credentials never stored in plain text
- **Environment Variables**: Sensitive config in `.env` (git-ignored)

## ⚙️ Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `OPENAI_API_KEY` | (required) | Your OpenAI API key |
| `OPENAI_MODEL` | gpt-4o-mini | AI model for comment generation |
| `COMMENTS_PER_DAY` | 10 | Comments per agent per day |
| `MIN_DELAY_MINUTES` | 30 | Minimum time between comments |
| `MAX_DELAY_MINUTES` | 90 | Maximum time between comments |
| `SCROLL_TIME_MIN` | 10 | Min seconds to scroll before commenting |
| `SCROLL_TIME_MAX` | 30 | Max seconds to scroll before commenting |
| `TYPING_SPEED_WPM` | 60 | Simulated typing speed |
| `HEADLESS` | true | Run browser in headless mode |
| `LOG_LEVEL` | INFO | Logging level (DEBUG/INFO/WARNING) |

## 📊 Cost Estimation

### MVP Testing (2-3 accounts)
- **OpenAI API**: ~$15-30/month
  - 20-30 comments/day × 3 accounts = 60-90 comments/day
  - ~100 tokens per comment
  - GPT-4o-mini: $0.15 per 1M input tokens
- **Hosting**: $0 (local machine)
- **Proxies**: $0 (testing without for MVP)

**Total**: ~$15-30/month

## ⚠️ Important Notes

### Before Running
1. **Manually create TikTok accounts**:
   - Use different phone numbers
   - Different email addresses
   - Add profile pictures and bio
   - **Age accounts for 3-7 days** with manual activity:
     - Browse daily
     - Like 5-10 videos
     - Follow 3-5 creators
     - Post 1-2 manual comments

2. **Understand the risks**:
   - Automated commenting violates TikTok ToS
   - Accounts may be banned/shadowbanned
   - Start with test accounts you're willing to lose
   - Success rate may be 50-70% initially

3. **Home IP limitations**:
   - Running 2-3 accounts from home IP for MVP
   - May see account restrictions after 1-2 weeks
   - Proxy support can be added later if successful

## 🗺️ Development Roadmap

### Week 1: Foundation ✅ (Current)
- [x] Project setup
- [x] Database & models
- [x] CLI framework
- [x] Configuration & encryption
- [x] Agent management

### Week 2: TikTok Automation
- [ ] Playwright setup with stealth mode
- [ ] TikTok login automation
- [ ] Navigate to For You page
- [ ] Video selection logic
- [ ] Comment posting
- [ ] Session persistence

### Week 3: AI & Scheduling
- [ ] OpenAI API integration
- [ ] Comment generation prompts
- [ ] Content validation
- [ ] APScheduler setup
- [ ] Job distribution (10/day per agent)
- [ ] Random timing logic

### Week 4: Monitoring & Polish
- [ ] Live status dashboard
- [ ] Enhanced error handling
- [ ] Recovery mechanisms
- [ ] Testing with multiple accounts
- [ ] Documentation updates

## 🔧 Development

### Running Tests

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run tests (coming soon)
pytest tests/
```

### Checking Logs

```bash
# View log file
tail -f data/logs/bot.log

# View via CLI
python main.py logs --limit 50
```

### Troubleshooting

**Database locked error**:
```bash
# If you get "database is locked", ensure no other instance is running
pkill -f "python main.py"
```

**Encryption key issues**:
```bash
# If encryption fails, regenerate key
rm .env
python main.py config show  # Will auto-generate new key
```

**Import errors**:
```bash
# Ensure you're in the virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📝 License

This is an educational MVP project. Use responsibly and at your own risk.

## ⚡ Next Steps

1. **Complete Week 1** ✅
2. **Week 2**: Implement TikTok bot with Playwright
3. **Week 3**: Add AI comment generation and scheduling
4. **Week 4**: Build dashboard and test with real accounts
5. **Post-MVP**: Evaluate results and decide on scaling strategy

## 🤝 Contributing

This is a personal MVP project. Contributions welcome after initial MVP is complete.

---

**Status**: Week 1 Complete - Foundation Ready ✅

For questions or issues, check the logs in `data/logs/bot.log`
