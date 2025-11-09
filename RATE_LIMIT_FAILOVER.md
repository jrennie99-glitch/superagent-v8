# 🔄 Automatic Rate Limit Failover System

## Overview
SuperAgent now features **intelligent automatic failover** between GROQ and Gemini AI providers. When one provider hits rate limits, the system automatically switches to the backup provider without manual intervention.

## How It Works

### 1. **Smart Provider Selection**
- **Default Priority:** GROQ (fastest inference) → Gemini (large free tier)
- System checks which providers are available and not rate-limited
- Automatically selects the best available option

### 2. **Automatic Failover**
When GROQ hits rate limit:
```
⚠️ GROQ hit rate limit! Attempting failover...
✅ Switching to GEMINI as backup provider
```

When Gemini hits rate limit:
```
⚠️ Gemini hit rate limit! Attempting failover...
✅ Switching to GROQ as backup provider
```

### 3. **Reset Time Tracking**
- System automatically detects reset times from API error messages
- Tracks when each provider will be available again
- Returns to preferred provider when rate limit resets

## Usage

### Check Rate Limit Status
```bash
curl http://localhost:5000/api/v1/rate-limit-status
```

**Response:**
```json
{
  "message": "✅ All providers available",
  "status": {
    "groq": {
      "available": true,
      "has_key": true,
      "reset_time": null,
      "seconds_until_reset": 0
    },
    "gemini": {
      "available": true,
      "has_key": true,
      "reset_time": null,
      "seconds_until_reset": 0
    },
    "recommended_provider": "groq"
  },
  "automatic_failover": "enabled"
}
```

### When GROQ is Rate Limited:
```json
{
  "message": "⚠️ GROQ rate limited. Using Gemini as backup. GROQ resets in 192s",
  "status": {
    "groq": {
      "available": false,
      "has_key": true,
      "reset_time": "2025-11-09T01:15:23",
      "seconds_until_reset": 192
    },
    "gemini": {
      "available": true,
      "has_key": true,
      "reset_time": null,
      "seconds_until_reset": 0
    },
    "recommended_provider": "gemini"
  },
  "automatic_failover": "enabled"
}
```

## Rate Limits

### GROQ Free Tier
- **Tokens/Day:** 100,000 (TPD)
- **Tokens/Min:** 12,000 (TPM)
- **Requests/Min:** 30 (RPM)
- **Requests/Day:** 1,000 (RPD)
- **Reset:** Midnight Pacific Time

### Gemini Free Tier
- **Requests/Day:** 1,500
- **Context Window:** Up to millions of tokens
- **Reset:** Daily

## Configuration

Both providers use your custom API keys:
- `USER_GROQ_API_KEY` - Your personal GROQ key
- `USER_GEMINI_API_KEY` - Your personal Gemini key

**No configuration needed!** Failover is automatic.

## Technical Details

### Files Modified
- `api/rate_limit_failover.py` - Rate limit tracking and provider selection
- `api/enterprise_builder.py` - Automatic failover in code generation
- `api/custom_key_manager.py` - Rate limit status endpoint

### Error Detection
The system detects rate limits from:
- Error code 429
- Keywords: "rate_limit", "quota", "too many requests"
- Reset time parsing from error messages

### Failover Logic
1. Attempt generation with primary provider (GROQ)
2. If rate limit error detected:
   - Extract reset time from error
   - Mark provider as unavailable
   - Switch to alternative provider
   - Retry generation once
3. Track reset times in `/tmp/rate_limits.json`
4. Automatically clear limits when reset time passes

## Benefits

✅ **Zero Downtime:** Never wait for rate limits - automatic backup
✅ **Transparent:** System handles failover automatically
✅ **Smart Reset:** Returns to preferred provider when available
✅ **Cost Optimized:** Uses free tiers efficiently

## Example Flow

```
User: "Build a calculator"
 ↓
System: Using GROQ (100K tokens/day)
 ↓
GROQ: Rate limit hit (99,573/100,000 used)
 ↓
System: ⚠️ GROQ rate limited! Switching to Gemini...
 ↓
System: ✅ Using Gemini (1,500 requests/day available)
 ↓
Calculator built successfully!
 ↓
3 hours later...
 ↓
System: GROQ rate limit reset - back to primary provider
```

## Monitoring

Check current provider status:
- API Key Status: `/api/v1/api-key-status`
- Rate Limit Status: `/api/v1/rate-limit-status`

Both endpoints return real-time information about:
- Which provider is currently active
- Which providers are available
- Reset times for rate-limited providers
