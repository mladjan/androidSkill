# 🔑 Passkey Account Workaround

If your TikTok account uses **passkey-only** authentication, you have two options:

---

## ✅ **Option 1: Add a Password** (Recommended)

Most reliable long-term solution.

### **Steps:**

1. **Open TikTok** (app or website)
2. Go to **Profile → Settings → Account → Password**
3. Select **"Set password"** or **"Add password"**
4. Create a strong password
5. Save it securely

**Then use the bot normally:**
```bash
python main.py agent add
# Use your username and NEW password
```

**Benefits:**
- ✅ Works reliably
- ✅ No session expiration issues
- ✅ Passkey still works for your manual use
- ✅ Full automation support

---

## 🔄 **Option 2: Import Browser Session** (Workaround)

Use your existing logged-in session from browser.

### **Steps:**

#### **1. Login to TikTok Manually**
- Open Chrome/Firefox
- Login with your passkey
- Verify you're logged in

#### **2. Export Cookies**

**Using Chrome Extension**:
1. Install **[EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)** or **[Cookie-Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)**
2. Click the extension icon while on tiktok.com
3. Click **"Export"** → **"Export as JSON"**
4. Save to a file (e.g., `tiktok_cookies.json`)

**Manual Export** (Chrome DevTools):
1. Open DevTools (F12)
2. Go to **Application** tab
3. Left sidebar: **Cookies** → `https://www.tiktok.com`
4. Right-click → **Copy all**
5. Paste into a JSON file

#### **3. Add Agent (Without Login)**
```bash
# Add agent with dummy password (won't be used)
python main.py agent add
# Username: your_tiktok_username
# Password: dummy123 (won't be used)
```

#### **4. Import Session**
```bash
source venv/bin/activate
python import_session.py 1 tiktok_cookies.json
```

**Expected Output:**
```
Importing session for agent 'your_username'...
Found 12 TikTok cookies
✓ Session imported successfully!
Saved to: data/browser_profiles/agent_1/storage_state.json
```

#### **5. Test Session**
```bash
python main.py agent test 1
```

---

## ⚠️ **Important Limitations (Option 2)**

### **Session Expiration**:
- Browser sessions expire after 7-30 days
- You'll need to re-import cookies periodically
- Bot will fail when session expires

### **Security Token Changes**:
- TikTok may invalidate sessions on:
  - Password change
  - Security settings change
  - Suspicious activity detection
  - Location changes

### **Manual Re-import Needed**:
When bot fails with "not logged in" error:
1. Login manually in browser
2. Export cookies again
3. Re-run import script

---

## 🔧 **Troubleshooting**

### **"No TikTok cookies found"**
- Make sure you're logged into TikTok
- Export from `tiktok.com` domain
- Check JSON format is correct

### **"Session expired" after import**
- Cookies may be already expired
- Login fresh in browser
- Export immediately
- Try different browser

### **Bot can't find login state**
```bash
# Verify session file exists
ls data/browser_profiles/agent_1/storage_state.json

# Check it contains cookies
cat data/browser_profiles/agent_1/storage_state.json
```

---

## 💡 **Which Option Should You Choose?**

| Factor | Option 1 (Add Password) | Option 2 (Import Session) |
|--------|------------------------|---------------------------|
| **Ease of Setup** | Easy | Medium |
| **Reliability** | ⭐⭐⭐⭐⭐ High | ⭐⭐⭐ Medium |
| **Maintenance** | None | Re-import monthly |
| **Automation** | Full | Full (until expiry) |
| **Security** | Password + Passkey | Passkey only |
| **Recommendation** | ✅ Best for automation | ⚠️ Temporary solution |

---

## 🎯 **Recommendation**

**For automation**: Choose **Option 1** (Add Password)
- One-time setup
- No maintenance
- Most reliable

**For testing**: Choose **Option 2** (Import Session)
- Quick test
- No password needed
- Good for proof-of-concept

---

## 🔮 **Future Enhancement**

We could potentially implement **WebAuthn passkey automation**, but it would require:
- Browser automation with user interaction
- Biometric simulation (not possible)
- Device-specific credential handling
- Much more complex code

**Current status**: Not planned for MVP

---

## 📝 **Example: Full Workflow (Option 2)**

```bash
# 1. Add agent
python main.py agent add
# Username: mytiktok
# Password: temp123 (won't be used)

# 2. Login to TikTok in Chrome (with passkey)
# Export cookies to cookies.json

# 3. Import session
python import_session.py 1 cookies.json

# 4. Test
python main.py agent test 1

# 5. Use bot normally
# (Will work until session expires)
```

---

## 🆘 **Need Help?**

1. Try **Option 1** first (add password to account)
2. Check logs: `tail -f data/logs/bot.log`
3. Verify cookies are valid
4. Re-import if session expires

---

**Recommendation**: Add a password to your TikTok account for best results! 🔑
