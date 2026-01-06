# Mindly Health Chairman's Council - Quick Start Guide

## ⚡ 30-Minute Setup (Local Development)

### Prerequisites
- Python 3.10+ installed
- GitHub account
- OpenRouter API key (get one at openrouter.ai)
- Firebase project credentials

### Step 1: Clone and Setup (5 min)
```bash
# Clone the repository
git clone https://github.com/mindlyhealthin/mindly-chairmans-council.git
cd mindly-chairmans-council

# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
cd frontend && npm install && cd ..
```

### Step 2: Configure Environment (5 min)
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your keys:
OPENROUTER_API_KEY=sk-or-v1-your-key
FIREBASE_PROJECT_ID=mindly-chairmans-council
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
```

### Step 3: Run Locally (5 min)
```bash
# Terminal 1 - Backend
uv run python -m backend.main
# Runs on http://localhost:8000

# Terminal 2 - Frontend
cd frontend && npm run dev
# Runs on http://localhost:5173
```

### Step 4: Test It (15 min)
1. Open http://localhost:5173
2. Type a question (e.g., "How should we price our telepsychiatry platform?")
3. Click "Get Council Advice"
4. Wait 2-3 minutes for all advisors to respond
5. See results!

## 📚 Full Documentation

See the complete implementation guide: https://docs.google.com/document/d/10FjVJoozGJeTBKE2NsmHcSav5kCPh324ARBhJGjYWns/

## 🚀 Cloud Deployment

For production deployment to Google Cloud Run:
1. Follow Section 5 in the implementation guide
2. Uses asia-south1 (India region) for lowest latency
3. Estimated cost: $10-50/month

## 🆘 Troubleshooting

**Issue: "OpenRouter API key invalid"**
- Verify key format: `sk-or-v1-...`
- Check you have credits on your account

**Issue: "Firebase connection failed"**
- Ensure `firebase-credentials.json` is in project root
- Check `FIREBASE_PROJECT_ID` matches your project

**Issue: "Models not responding"**
- Check OpenRouter API status
- Verify your firewall allows outbound HTTPS

## 📞 Support

Refer to the comprehensive guide linked above for:
- Complete API documentation
- Healthcare-specific prompts
- Firebase Firestore schema
- Cloud Run deployment pipeline
- Cost optimization strategies
