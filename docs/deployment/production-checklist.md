# Production Deployment Checklist

Complete guide for deploying Capital Market Newsletter to production.

---

## Pre-Deployment Checklist

### 1. Environment Variables

Copy `.env.example` to your hosting platform and configure all required values.

#### Required Variables

| Variable | Description | How to Get |
|----------|-------------|------------|
| `OPENAI_API_KEY` | OpenAI API key (starts with `sk-`) | [OpenAI Platform](https://platform.openai.com/api-keys) |

#### Conditional Requirements

| Variable | Required When | Description |
|----------|---------------|-------------|
| `GEMINI_API_KEY` | `LLM_PROVIDER=gemini` or `TTS_PROVIDER=gemini` | [Google AI Studio](https://aistudio.google.com/apikey) |
| `EMAIL_FROM_ADDRESS` | `EMAIL_API_KEY` is set | Must be verified in SendGrid |
| `GOOGLE_CLIENT_SECRET` | `GOOGLE_CLIENT_ID` is set | OAuth credentials |
| `GOOGLE_REDIRECT_URI` | `GOOGLE_CLIENT_ID` is set | Must match Google Console |

#### Production Values (Override Defaults)

```bash
# Security - CRITICAL
FLASK_DEBUG=false          # NEVER enable in production
FORCE_HTTPS=true           # Enable HTTPS redirect
CSP_REPORT_ONLY=false      # Enforce Content Security Policy

# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Base URL for emails
BASE_URL=https://your-domain.com

# OAuth redirect (must match domain)
GOOGLE_REDIRECT_URI=https://your-domain.com/api/auth/google/callback

# Logging
LOG_FORMAT=json            # Structured logs for production
LOG_LEVEL=INFO             # Or WARNING for less verbosity

# Monitoring
SENTRY_DSN=https://...@sentry.io/...
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

---

### 2. Database Setup

- [x] Create PostgreSQL database (Supabase, Railway, or other)
- [x] Set `DATABASE_URL` with connection string
- [x] Verify connection: tables auto-created on first startup
- [x] Enable Row Level Security if using Supabase

> **Supabase Note:** The app automatically strips the `pgbouncer=true` parameter
> from Supabase connection strings (psycopg2 doesn't support it). No manual
> URL editing needed.

---

### 3. External Services

#### SendGrid (Email)
- [x] Create SendGrid account
- [x] Verify sender email address
- [x] Generate API key with Mail Send permission
- [x] Set `EMAIL_API_KEY`

#### Google OAuth
- [x] Create project in [Google Cloud Console](https://console.cloud.google.com)
- [x] Configure OAuth consent screen
- [x] Create OAuth 2.0 credentials
- [x] Add production redirect URI
- [x] Set `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`

#### Sentry (Error Monitoring)
- [x] Create Sentry project
- [x] Copy DSN to `SENTRY_DSN`
- [x] Set `SENTRY_ENVIRONMENT=production`

---

### 4. Security Checklist

- [ ] `FLASK_DEBUG=false`
- [ ] `FORCE_HTTPS=true`
- [ ] `CSP_REPORT_ONLY=false`
- [ ] `ADMIN_API_KEY` set to secure random string
- [ ] All API keys stored as environment variables (not in code)
- [ ] Database credentials use strong passwords
- [ ] Rate limiting enabled (`RATE_LIMIT_ENABLED=true`)

---

### 5. Infrastructure Requirements

#### Persistent Storage
- [ ] **Audio cache directory**: Mount persistent volume at `audio_cache/`
  - Required for podcast caching (~97% cost reduction)
  - Size: ~50MB per day of audio

#### Resources (Recommended)
- CPU: 1 vCPU
- Memory: 512MB - 1GB
- Disk: 1GB (plus audio cache volume)

---

## Deployment Steps

### Option A: Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and link project
railway login
railway link

# Set environment variables
railway variables set OPENAI_API_KEY=sk-...
railway variables set DATABASE_URL=postgresql://...
# ... set all other variables

# Deploy
railway up
```

### Option B: Render

1. Connect GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `.venv/bin/python -m backend.web_app`
4. Add environment variables in dashboard
5. Add persistent disk at `/app/audio_cache`

### Option C: Fly.io

```bash
# Install flyctl
brew install flyctl

# Initialize
fly launch

# Set secrets
fly secrets set OPENAI_API_KEY=sk-...
fly secrets set DATABASE_URL=postgresql://...

# Create volume for audio cache
fly volumes create audio_cache --size 1

# Deploy
fly deploy
```

---

## Post-Deployment Verification

### 1. Health Check
```bash
curl https://your-domain.com/api/health
# Expected: {"status": "healthy", ...}
```

### 2. Test Authentication
- [ ] Navigate to your domain
- [ ] Click "Sign in with Google"
- [ ] Verify OAuth flow completes
- [ ] Check user appears in database

### 3. Test Newsletter Generation
- [ ] Click "Generate Newsletter"
- [ ] Verify content loads
- [ ] Check all 4 categories (US, Israel, AI, Crypto)

### 4. Test Podcast Generation
- [ ] Click "Listen" button
- [ ] Verify audio plays
- [ ] Check audio file cached (subsequent loads are instant)

### 5. Monitor Errors
- [ ] Check Sentry for any errors
- [ ] Review application logs
- [ ] Verify scheduler is running (check logs for generation times)

---

## Troubleshooting

### App Won't Start

**Check logs for:**
- `ConfigurationError`: Missing or invalid environment variable
- `OPENAI_API_KEY`: Verify key starts with `sk-`
- Database connection errors: Check `DATABASE_URL` format
- `invalid dsn: invalid keyword 'pgbouncer'`: Update to v1.49.3+ (auto-strips this param)

### OAuth Not Working

- Verify `GOOGLE_REDIRECT_URI` exactly matches Google Console
- Check `BASE_URL` matches your production domain
- Ensure `FORCE_HTTPS=true` for production

### Emails Not Sending

- Verify `EMAIL_FROM_ADDRESS` is verified in SendGrid
- Check SendGrid API key has Mail Send permission
- Review SendGrid activity log for errors

### Podcast Not Playing

- Check `audio_cache/` directory has write permissions
- Verify persistent volume is mounted
- Check OpenAI/Gemini API key for TTS provider

---

## Monitoring Checklist

- [ ] Sentry alerts configured for critical errors
- [ ] Uptime monitoring (UptimeRobot, Pingdom, etc.)
- [ ] Log aggregation if needed (Papertrail, Logtail)
- [ ] Database backup schedule (if self-hosted)

---

## Rollback Plan

1. Keep previous deployment version noted
2. Railway/Render: Redeploy previous version from dashboard
3. Fly.io: `fly releases` to list, `fly deploy --image <old-image>` to rollback
4. Verify rollback with health check

---

## Environment Reference

See `.env.example` for complete list of all 52 environment variables with descriptions.
