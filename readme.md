## Social Media Content Generator (Gemini + LangChain + Streamlit)

A simple Streamlit app that generates platform-tailored content from a single topic using Google Gemini via LangChain. The app returns two outputs in one request:
- Facebook post (`fb_tips`)
- LinkedIn post (`linkedin_tips`)

It is optimized for the Gemini free tier with:
- Single model call that returns both outputs in strict JSON
- Automatic model fallback (helps when a model/version isn’t enabled in your region/account)
- Exponential backoff for 429/rate-limit errors
- Local SQLite prompt cache to deduplicate identical requests

### Features
- Generate concise, on-brand posts for Facebook and LinkedIn from one topic
- Fast defaults using `gemini-1.5-flash-8b` with fallbacks
- Works with your Gemini API key (no server required)

## Project Structure
```
.
├─ main.py          # LangChain pipeline, model fallback, cache, retry/backoff
├─ frontend.py      # Streamlit UI
├─ requirements.txt # Python dependencies
└─ readme.md        # This file
```

## Requirements
- Python 3.10+
- A Google Gemini API key

Get a key and enable access: see `https://ai.google.dev/` (Gemini API), ensure access to `us-central1`. Free-tier quotas may be limited in some regions/accounts.

## Setup (Windows PowerShell)
```powershell
cd C:\Users\<you>\Desktop\langchain
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -r requirements.txt
```

## Configuration
This app reads your API key from the UI sidebar. You can also use a `.env` file if desired (optional):
```env
# .env
GOOGLE_API_KEY=your_gemini_api_key_here
```

If present, the key will be auto-loaded by `dotenv`. The UI field will override if you enter a key there.

## Run
```powershell
streamlit run frontend.py
```
Open the browser URL that Streamlit prints. Enter a topic and your Gemini API key in the sidebar.

## How It Works
- `main.py` builds a single prompt that asks Gemini to return strict JSON with two keys: `fb_tips` and `linkedin_tips`.
- The chain uses these optimizations:
  - Model preference order: `gemini-1.5-flash-8b` → `gemini-1.5-flash-001` → `gemini-1.5-flash` → `gemini-pro` (fallbacks help avoid NotFound/access issues).
  - Exponential backoff for 429/quota/rate-limit responses.
  - SQLite cache (via `langchain_community.cache.SQLiteCache`) to dedupe identical prompts locally.

## Troubleshooting
- 404 NotFound for model
  - Your account/region may not have the requested version. The app will automatically try fallbacks; ensure your key is for the Gemini API and allowed in `us-central1`.
- 429 Quota/Rate limits
  - The app backs off and retries. If you’re on a free tier with 0 remaining quota, wait for reset, shorten prompts, or upgrade your plan.
- Missing cache dependency
  - Install: `python -m pip install -U langchain-community`. It’s listed in `requirements.txt`.
- gRPC/ALTS warnings (benign)
  - You can suppress in PowerShell: `$env:GRPC_VERBOSITY="ERROR"; $env:GRPC_TRACE=""`

## Customization
- Adjust temperature and model order in `main.py`.
- Change prompt wording in `main.py` to fit your brand style.
- Add more platforms by extending the JSON schema and frontend rendering.

## Security Notes
- Do not hardcode secrets. Prefer the UI input or `.env` with care.
- Treat your API key as sensitive; avoid committing it to source control.

## License
MIT (or your preferred license). Replace this section if you have a different license.