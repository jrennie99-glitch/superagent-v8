# 🔒 SuperAgent API Security Guide

Your SuperAgent API is now **secured with API key authentication**!

---

## 🎯 How It Works

All API endpoints (except `/` and `/health`) now require an API key in the request header.

**Without a valid API key → Access Denied! ✅**

---

## 🔑 Setting Up Your API Key

### **On Vercel:**

1. Go to your project dashboard
2. Click **"Settings"**
3. Click **"Environment Variables"**
4. Add a new variable:
   - **Key:** `SUPERAGENT_API_KEY`
   - **Value:** `your-secret-key-here` (create a strong random key!)
5. Click **"Save"**
6. Click **"Redeploy"** to apply the changes

### **Locally:**

```bash
export SUPERAGENT_API_KEY="your-secret-key-here"
```

Or add to your `.env` file:
```
SUPERAGENT_API_KEY=your-secret-key-here
```

---

## 🔐 Generating a Secure API Key

Use one of these methods:

### **Method 1: OpenSSL**
```bash
openssl rand -hex 32
```

### **Method 2: Python**
```python
import secrets
print(secrets.token_urlsafe(32))
```

### **Method 3: Online**
Go to: https://randomkeygen.com/ (use "Fort Knox Passwords")

---

## 📡 How to Use the API

### **Public Endpoints (No Key Needed):**

```bash
# Root
curl https://your-app.vercel.app/

# Health check
curl https://your-app.vercel.app/health
```

### **Protected Endpoints (Key Required):**

Include the `X-API-Key` header:

```bash
# Execute instruction
curl -X POST https://your-app.vercel.app/execute \
  -H "X-API-Key: your-secret-key-here" \
  -H "Content-Type: application/json" \
  -d '{"instruction": "Create a Hello World app", "project_name": "hello"}'

# Check job status
curl https://your-app.vercel.app/jobs/{job_id} \
  -H "X-API-Key: your-secret-key-here"

# Debug project
curl -X POST https://your-app.vercel.app/debug \
  -H "X-API-Key: your-secret-key-here" \
  -H "Content-Type: application/json" \
  -d '{"project_path": "./my-project"}'

# Run tests
curl -X POST https://your-app.vercel.app/test \
  -H "X-API-Key: your-secret-key-here" \
  -H "Content-Type: application/json" \
  -d '{"project_path": "./my-project"}'

# Get stats
curl https://your-app.vercel.app/stats \
  -H "X-API-Key: your-secret-key-here"
```

---

## 🐍 Python Example

```python
import requests

API_URL = "https://your-app.vercel.app"
API_KEY = "your-secret-key-here"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Execute instruction
response = requests.post(
    f"{API_URL}/execute",
    headers=headers,
    json={
        "instruction": "Create a calculator app",
        "project_name": "calculator"
    }
)

print(response.json())
```

---

## 🌐 JavaScript Example

```javascript
const API_URL = "https://your-app.vercel.app";
const API_KEY = "your-secret-key-here";

const headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
};

// Execute instruction
fetch(`${API_URL}/execute`, {
    method: "POST",
    headers: headers,
    body: JSON.stringify({
        instruction: "Create a calculator app",
        project_name: "calculator"
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## ❌ Error Responses

### **No API Key:**
```json
{
    "detail": "API key is missing. Include 'X-API-Key' header."
}
```
Status: `401 Unauthorized`

### **Invalid API Key:**
```json
{
    "detail": "Invalid API key. Access denied."
}
```
Status: `403 Forbidden`

---

## 🔒 Security Best Practices

### ✅ DO:
- Use a strong, random API key (32+ characters)
- Store API key in environment variables
- Use HTTPS only
- Rotate keys periodically
- Use different keys for different environments (dev/prod)
- Keep keys secret (don't commit to Git!)

### ❌ DON'T:
- Use simple or guessable keys
- Hardcode keys in your code
- Share keys publicly
- Use the same key forever
- Commit keys to version control

---

## 🔄 Rotating Your API Key

1. Generate a new key
2. Update `SUPERAGENT_API_KEY` in Vercel
3. Redeploy
4. Update all clients with new key
5. Old key is now invalid

---

## 👥 Multiple Users

Want different keys for different users?

You can modify the code to support multiple keys:

```python
VALID_API_KEYS = {
    "user1-key-here": "user1",
    "user2-key-here": "user2",
}

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return VALID_API_KEYS[api_key]  # Returns username
```

---

## 🧪 Testing Your Security

### **Test without key (should fail):**
```bash
curl https://your-app.vercel.app/stats
# Expected: 401 error
```

### **Test with wrong key (should fail):**
```bash
curl https://your-app.vercel.app/stats -H "X-API-Key: wrong-key"
# Expected: 403 error
```

### **Test with correct key (should work):**
```bash
curl https://your-app.vercel.app/stats -H "X-API-Key: your-correct-key"
# Expected: Stats JSON
```

---

## 📊 What's Protected

| Endpoint | Public? | Requires API Key? |
|----------|---------|-------------------|
| `GET /` | ✅ Yes | ❌ No |
| `GET /health` | ✅ Yes | ❌ No |
| `GET /docs` | ✅ Yes | ❌ No |
| `POST /execute` | ❌ No | ✅ Yes |
| `GET /jobs/{id}` | ❌ No | ✅ Yes |
| `POST /debug` | ❌ No | ✅ Yes |
| `POST /deploy` | ❌ No | ✅ Yes |
| `POST /test` | ❌ No | ✅ Yes |
| `GET /stats` | ❌ No | ✅ Yes |

---

## 🎉 You're Secure!

Your SuperAgent API is now protected. Only requests with a valid API key can access your endpoints!

**Next Steps:**
1. Generate a strong API key
2. Add `SUPERAGENT_API_KEY` to Vercel
3. Redeploy
4. Test with your key
5. Start using your secure API!

---

**Questions?** Check the API docs at: `https://your-app.vercel.app/docs`

