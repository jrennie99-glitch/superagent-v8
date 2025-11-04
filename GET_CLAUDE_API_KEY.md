# 🔑 How to Get Your Claude API Key

## Quick Steps

1. **Sign up:** https://console.anthropic.com/
2. **Add payment method** (required, but you get $5 free!)
3. **Create API key:** https://console.anthropic.com/settings/keys
4. **Copy it immediately** (you can only see it once!)
5. **Add to Vercel** environment variables

---

## Detailed Walkthrough

### Step 1: Sign Up for Anthropic

1. Go to: **https://console.anthropic.com/**
2. Click **"Sign Up"** or **"Get Started"**
3. Enter your email address
4. Create a strong password
5. Check your email and **verify your account**

---

### Step 2: Add Payment Method

**Important:** Anthropic requires a credit card to use the API.

**But don't worry:**
- ✅ You get **$5 in FREE credits** when you sign up
- ✅ This is enough for 100-500 API calls
- ✅ Perfect for testing and development!

**How to add payment:**
1. Go to: **https://console.anthropic.com/settings/billing**
2. Click **"Add Payment Method"**
3. Enter your credit card information
4. Click **"Save"**

**Set a spending limit (recommended):**
1. In Billing settings, find **"Spending Limit"**
2. Set to **$10/month** (or whatever you're comfortable with)
3. This prevents unexpected charges!

---

### Step 3: Generate Your API Key

1. Go to: **https://console.anthropic.com/settings/keys**
2. Click **"Create Key"** or **"Generate API Key"**
3. Give it a descriptive name:
   - Example: `SuperAgent API`
   - Example: `Vercel Production`
4. Click **"Create"**

---

### Step 4: COPY YOUR KEY IMMEDIATELY! ⚠️

**CRITICAL:** You can only see your API key **ONCE** when it's created!

Your key will look like this:
```
sk-ant-api03-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**Save it somewhere safe:**
- ✅ Password manager (1Password, LastPass, etc.)
- ✅ Notes app (Apple Notes, Notion, etc.)
- ✅ Secure document

**DO NOT:**
- ❌ Share it publicly
- ❌ Commit it to GitHub
- ❌ Post it in Discord/Slack
- ❌ Email it to yourself (insecure)

---

## Cost Information

### Free Credits
- **$5 free** when you sign up
- No code needed - automatically applied
- Expires after a few months (check console)

### Pricing for Claude 4.5 Sonnet

| Type | Cost |
|------|------|
| **Input tokens** | $3 per million tokens |
| **Output tokens** | $15 per million tokens |

**What does this mean in practice?**

| Task | Approx. Cost |
|------|--------------|
| Generate a simple function (10 lines) | $0.01 - $0.02 |
| Generate a full file (100 lines) | $0.05 - $0.10 |
| Generate a complex app (1000 lines) | $0.50 - $1.00 |

**Your $5 free credits can generate:**
- ~100-500 functions
- ~50-100 full files
- ~5-10 complex applications

**Very affordable!** 💰

---

## Add API Key to Vercel

Once you have your API key, add it to Vercel:

### Step 1: Go to Vercel Dashboard
https://vercel.com/dashboard

### Step 2: Select Your Project
Click on **"superagent1"** (or your project name)

### Step 3: Add Environment Variables
1. Click **"Settings"** (top menu)
2. Click **"Environment Variables"** (left sidebar)
3. Click **"Add New"**

### Step 4: Add ANTHROPIC_API_KEY
- **Key:** `ANTHROPIC_API_KEY`
- **Value:** `sk-ant-api03-XXXX...` (paste your key)
- **Environments:** Select **all** (Production, Preview, Development)
- Click **"Save"**

### Step 5: Add SUPERAGENT_API_KEY
- **Key:** `SUPERAGENT_API_KEY`
- **Value:** `dev-key-change-in-production` (for testing)
  - Or generate a secure one: `openssl rand -hex 32`
- **Environments:** Select **all**
- Click **"Save"**

### Step 6: Redeploy
1. Go to **"Deployments"** tab
2. Find the latest deployment
3. Click the three dots **(...)** next to it
4. Click **"Redeploy"**
5. Wait 1-2 minutes

### Step 7: Test Your API
```bash
curl https://your-project.vercel.app/health
```

Should return:
```json
{
  "status": "healthy",
  "message": "SuperAgent API is running on Vercel"
}
```

**If it works, you're done!** 🎉

---

## Security Best Practices

### ✅ DO:
- Store API keys in environment variables only
- Set spending limits in Anthropic Console
- Monitor your usage regularly
- Rotate keys periodically (every 3-6 months)
- Use different keys for different environments (dev/prod)

### ❌ DON'T:
- Hard-code API keys in your source code
- Commit keys to GitHub (even private repos!)
- Share keys in chat/email
- Use the same key everywhere
- Ignore spending alerts

---

## Troubleshooting

### "Invalid API Key" Error
- Make sure you copied the entire key (starts with `sk-ant-`)
- Check for extra spaces before/after the key
- Make sure you added it to the correct environment variable name: `ANTHROPIC_API_KEY`

### "Insufficient Credits" Error
- Check your balance: https://console.anthropic.com/settings/billing
- Add a payment method if you haven't already
- Increase your spending limit if it's too low

### "Rate Limit Exceeded" Error
- You're making too many requests too quickly
- Free tier has lower rate limits
- Wait a few seconds between requests
- Consider upgrading to a paid plan

### Can't Find Settings/Keys Page
- Make sure you're logged in
- Direct link: https://console.anthropic.com/settings/keys
- Try refreshing the page
- Clear browser cache if needed

---

## FAQ

### Q: Do I need a credit card to sign up?
**A:** Yes, Anthropic requires a credit card even for the free tier. But you get $5 free credits!

### Q: How long do the free credits last?
**A:** The $5 free credits typically last a few months. Check your Anthropic Console for expiration date.

### Q: What happens when I run out of free credits?
**A:** Your API calls will start using your credit card. Set a spending limit to control costs!

### Q: Can I use the same key for multiple projects?
**A:** Yes, but it's better to create separate keys for each project so you can track usage and revoke keys independently.

### Q: How do I check my usage?
**A:** Go to https://console.anthropic.com/settings/billing to see your current usage and costs.

### Q: Can I delete an API key?
**A:** Yes! Go to https://console.anthropic.com/settings/keys and click "Delete" next to the key. Create a new one if needed.

### Q: Is Claude 4.5 Sonnet available?
**A:** Yes! It was just released on September 29, 2025. Use model: `claude-sonnet-4-5-20250929`

---

## Useful Links

| Resource | URL |
|----------|-----|
| **Anthropic Console** | https://console.anthropic.com/ |
| **API Keys** | https://console.anthropic.com/settings/keys |
| **Billing** | https://console.anthropic.com/settings/billing |
| **Pricing** | https://www.anthropic.com/pricing |
| **Documentation** | https://docs.anthropic.com/ |
| **API Reference** | https://docs.anthropic.com/api-reference |

---

## After You Get Your Key

Once you have your Claude API key and have added it to Vercel:

1. ✅ Your Vercel deployment will work
2. ✅ The `/generate` endpoint will create code
3. ✅ You can test your SuperAgent API
4. ✅ Start building toward #1! 🏆

---

## Next Steps

After your API is working on Vercel:

1. **Test it thoroughly** with different prompts
2. **Monitor your usage** in Anthropic Console
3. **Set spending limits** to avoid surprises
4. **Consider building Phase 1 features** (to reach #1!)
   - Long-term planning
   - Sandboxed execution
5. **Share your API** with others (securely!)

---

## Need Help?

If you have issues getting your API key or setting it up:

1. Check the **Troubleshooting** section above
2. Review the **VERCEL_TROUBLESHOOT.md** file
3. Let me know what error you're seeing and I'll help fix it!

**Once you have your key, tell me and I'll help you add it to Vercel!** 🚀

