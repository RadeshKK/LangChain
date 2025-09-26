from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
from dotenv import load_dotenv
import json
import time

load_dotenv()


def response_by_model(api_key, text):
    # Enable local SQLite cache to dedupe identical prompts
    set_llm_cache(SQLiteCache(database_path=".langchain.db"))

    # Candidate models in decreasing preference; fall back on NotFound/access errors
    candidate_models = [
        "gemini-1.5-flash-8b",  # widely available, cost-effective
        "gemini-1.5-flash-001", # older pinned version
        "gemini-1.5-flash",     # alias may resolve to -002 (not available for some)
        "gemini-pro",           # legacy, broadly available
    ]
    model_index = 0

    # Single prompt: ask for both variants in strict JSON to avoid extra calls
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            (
                "You are a precise content generator. Output ONLY strict JSON with keys "
                "'fb_tips' and 'linkedin_tips'. No additional text. Each value must be a single "
                "paragraph of up to 150 words. Do not include links."
            ),
        ),
        (
            "human",
            (
                "Create two platform-specific posts about the topic: {topic}.\n"
                "- 'fb_tips': friendly, conversational, emojis ok, engaging CTA, a few hashtags.\n"
                "- 'linkedin_tips': professional, concise, insightful, industry-relevant hashtags, clear CTA."
            ),
        ),
    ])

    # Simple exponential backoff for 429/ResourceExhausted, with model fallbacks on NotFound
    max_attempts = 4
    backoff_seconds = 1.0
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            # Build model/chain each attempt in case we change models
            model_name = candidate_models[min(model_index, len(candidate_models) - 1)]
            model = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=0.4,
                api_key=api_key,
            )
            chain = prompt | model | StrOutputParser()

            raw = chain.invoke({"topic": text})
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                # Best-effort extraction if model added extra text
                start = raw.find("{")
                end = raw.rfind("}")
                if start != -1 and end != -1 and end > start:
                    data = json.loads(raw[start : end + 1])
                else:
                    raise
            # Normalize keys for frontend
            fb = data.get("fb_tips") or data.get("facebook") or ""
            ln = data.get("linkedin_tips") or data.get("linkedin") or ""
            return {"fb_tips": fb, "linkedin_tips": ln}
        except Exception as err:
            message = str(err)
            last_error = err
            # If model not found or access denied, try the next model immediately
            not_found = (
                "NotFound" in message
                or "was not found" in message
                or "does not have access" in message
            )
            if not_found and model_index < len(candidate_models) - 1:
                model_index += 1
                continue
            is_rate_limited = (
                "429" in message
                or "ResourceExhausted" in message
                or "quota" in message.lower()
                or "rate" in message.lower()
            )
            if attempt == max_attempts or not is_rate_limited:
                raise
            time.sleep(backoff_seconds)
            backoff_seconds *= 2

    # If all retries failed, re-raise last error
    raise last_error

