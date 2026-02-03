# OpenRouter Model Recommendations

## ✅ Your OpenRouter Setup is Working!

Base URL: `https://openrouter.ai/api/v1`
Your API Key: Configured ✓

---

## 💰 Recommended Models for Comment Generation

### **Best Choice: GPT-3.5-Turbo** (Recommended)
- **Model ID**: `openai/gpt-3.5-turbo`
- **Cost**: ~$0.00007 per comment
- **Monthly cost** (250 comments/day × 30 days = 7,500 comments): **~$0.50/month**
- **Quality**: Excellent, natural, contextual
- **Speed**: Very fast
- **Why**: Best balance of quality and cost

### **Budget Option: GPT-4o-Mini**
- **Model ID**: `openai/gpt-4o-mini`
- **Cost**: ~$0.00015 per comment
- **Monthly cost**: **~$1.10/month**
- **Quality**: Even better than GPT-3.5
- **Speed**: Fast
- **Why**: Slightly better quality, still very cheap

### **Free Models** (May have availability issues)
Free models on OpenRouter can be unstable or overloaded. Use as fallback:

- **DeepSeek R1**: `deepseek/deepseek-r1` (FREE but may be slow/unavailable)
- **Qwen 2.5 72B**: `qwen/qwen-2.5-72b-instruct` (FREE)
- **Note**: Free models may have rate limits or availability issues

---

## 📊 Cost Comparison for Your Use Case

Assuming **10 agents × 25 comments/day = 250 comments/day = 7,500 comments/month**:

| Model | Cost per Comment | Monthly Cost | Quality | Speed |
|-------|------------------|--------------|---------|-------|
| **GPT-3.5-Turbo** | $0.00007 | **$0.50** | ⭐⭐⭐⭐ | ⚡⚡⚡⚡ |
| **GPT-4o-Mini** | $0.00015 | **$1.10** | ⭐⭐⭐⭐⭐ | ⚡⚡⚡⚡ |
| **GPT-4-Turbo** | $0.00200 | **$15.00** | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ |
| **Claude Haiku** | $0.00025 | **$1.90** | ⭐⭐⭐⭐⭐ | ⚡⚡⚡⚡ |
| **Free Models** | $0.00 | **$0.00** | ⭐⭐⭐ | ⚡⚡ |

**Recommendation**: Start with **GPT-3.5-Turbo** ($0.50/month) - excellent quality for pennies!

---

## 🔧 How to Change Models

### Option 1: Via CLI
```bash
source venv/bin/activate

# Set to GPT-3.5-Turbo (recommended)
python main.py config set-model openai/gpt-3.5-turbo

# Or GPT-4o-Mini (better quality)
python main.py config set-model openai/gpt-4o-mini

# Or Claude Haiku (great quality)
python main.py config set-model anthropic/claude-3-5-haiku

# Verify
python main.py config show
```

### Option 2: Edit .env Directly
```bash
nano .env
# Change line:
OPENAI_MODEL=openai/gpt-3.5-turbo
```

---

## 📝 Model ID Format

OpenRouter uses this format:
`provider/model-name`

Examples:
- `openai/gpt-3.5-turbo`
- `openai/gpt-4o-mini`
- `anthropic/claude-3-5-haiku`
- `google/gemini-flash-1.5`
- `meta-llama/llama-3.1-70b-instruct`

---

## 🧪 Test Your Model

```bash
# Test current configuration
source venv/bin/activate
python test_openrouter.py
```

You'll see:
- ✅ Connection status
- Generated sample comment
- Cost per request
- Token usage

---

## 💡 Pro Tips

1. **Start with GPT-3.5-Turbo**: $0.50/month is incredibly cheap for 7,500 AI-generated comments

2. **Try GPT-4o-Mini**: Only $0.60/month more for noticeably better quality

3. **Avoid Free Models for Production**: They can be unreliable (rate limits, downtime, slow)

4. **Monitor Costs**: OpenRouter dashboard shows usage: https://openrouter.ai/activity

5. **Test Different Models**: Easy to switch and compare quality!

---

## 📈 Scaling Costs

If you scale to more agents:

| Agents | Comments/Day | Comments/Month | Cost (GPT-3.5) | Cost (GPT-4o-mini) |
|--------|--------------|----------------|----------------|-------------------|
| 3 | 75 | 2,250 | $0.16 | $0.34 |
| 10 | 250 | 7,500 | $0.53 | $1.13 |
| 20 | 500 | 15,000 | $1.05 | $2.25 |
| 50 | 1,250 | 37,500 | $2.63 | $5.63 |
| 100 | 2,500 | 75,000 | $5.25 | $11.25 |

**Conclusion**: Even at 100 agents posting 2,500 comments/day, you're only spending **$5-11/month** on AI!

---

## 🎯 Current Configuration

Your bot is configured to use:
- **Model**: `meta-llama/llama-3.3-70b-instruct:free` (from .env)
- **Recommendation**: Switch to `openai/gpt-3.5-turbo`

### Quick Switch Command:
```bash
source venv/bin/activate
python main.py config set-model openai/gpt-3.5-turbo
```

---

## ❓ FAQ

**Q: Can I use multiple models?**
A: Yes! Change the model anytime. The bot will use whatever's in `.env`

**Q: How do I check my usage/costs?**
A: Visit https://openrouter.ai/activity

**Q: What if a model is down?**
A: Switch to another model with `python main.py config set-model <model-id>`

**Q: Can I use OpenAI directly instead?**
A: Yes! Change `OPENAI_BASE_URL=https://api.openai.com/v1` in `.env`

**Q: Which model generates the best TikTok comments?**
A: GPT-4o-Mini or Claude Haiku (both ~$1/month)

---

## ✅ Action Items

1. **Switch to GPT-3.5-Turbo** (recommended):
   ```bash
   python main.py config set-model openai/gpt-3.5-turbo
   ```

2. **Test it**:
   ```bash
   python test_openrouter.py
   ```

3. **Check configuration**:
   ```bash
   python main.py config show
   ```

---

**Status**: OpenRouter Working ✅
**Current Model**: Needs update (see above)
**Recommended Model**: `openai/gpt-3.5-turbo` ($0.50/month)

🚀 Ready for Week 3 - AI Comment Generation!
