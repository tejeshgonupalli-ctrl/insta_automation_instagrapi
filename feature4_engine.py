
# FOURTH RUN AUTOMATION SCRIPT

"""
feature4_engine.py

Usage:
1) Create a .env file in same folder with:
   OPENROUTER_KEYS=key1,key2         # comma separated OpenRouter (or provider) API keys
   MODELS=openai/gpt-oss-20b,google/gemini-2.0-flash-exp,xai/grok-4.1-fast,deepseek/deepseek-r1t2

2) Update INPUT_BASE / LOGGING options below if needed.
3) Run: python feature4_engine.py

NOTE:
- This script assumes an OpenRouter-style chat completions endpoint:
  POST https://api.openrouter.ai/v1/chat/completions
  Header: Authorization: Bearer <API_KEY>
  JSON: {"model": "<model>", "messages":[{"role":"user","content":"..."}], "max_tokens":...}

- If your provider uses a different endpoint, adjust send_request() accordingly.
- Do NOT paste your keys here. Keep them in .env locally.
"""

import os, time, json, random, math
from pathlib import Path
import requests
from typing import List, Dict
from itertools import cycle

# -------- CONFIG --------
INPUT_BASE = r"C:\Users\w10\Desktop\WebScrapping\filtered_downloads_watermarked"
# files will be written inside each post folder (per your pinned rule)
MAX_TOKENS = 512
TEMPERATURE = 0.9
REQUEST_TIMEOUT = 60  # seconds
RETRY_LIMIT = 3

# Default models order (can be overridden in .env)
DEFAULT_MODELS = [
    "openai/gpt-oss-20b",
    "google/gemini-2.0-flash-exp"
]


OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"


def safe_retry(func, fallback_text):
    for _ in range(3):
        try:
            res = func()
            if res and str(res).strip():
                return res
        except:
            pass
    return fallback_text

# -------- HELPERS: .env loading & rotation setup --------
def load_env():
    env = {}
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf8").splitlines():
            line=line.strip()
            if not line or line.startswith("#"): continue
            if "=" not in line: continue
            k,v = line.split("=",1)
            env[k.strip()] = v.strip()
    return env

env = load_env()
KEYS = []
if "OPENROUTER_KEYS" in env and env["OPENROUTER_KEYS"].strip():
    KEYS = [k.strip() for k in env["OPENROUTER_KEYS"].split(",") if k.strip()]

MODELS = DEFAULT_MODELS
if "MODELS" in env and env["MODELS"].strip():
    MODELS = [m.strip() for m in env["MODELS"].split(",") if m.strip()]

if not KEYS:
    print("WARNING: No API keys found in .env (OPENROUTER_KEYS). Script will fail to call APIs.")
    print("Please add keys to .env. Example:")
    print("OPENROUTER_KEYS=key1,key2")
    # continue, but will error at runtime

# Iterators for round-robin
key_cycle = cycle(KEYS) if KEYS else None
model_cycle = cycle(MODELS)

# -------- PROMPT TEMPLATES --------
PROMPTS = {
    "caption_rewrite": lambda orig: f"""Rewrite the following Instagram caption in Viral Attitude Hook Style.

Rules:
- Line 1: Strong hook
- Line 2: Attitude vibe line
- 3–5 emojis
- Keep it short, bold & high-engagement.

Original caption:
{orig}

Return only the rewritten caption text (no extra explanation).""",

    "hook": lambda orig: f"""Generate 3 short 'stop-scroller' hook lines (one-per-line) suitable for this reel caption. Keep attitude style, 6-10 words max each.

Caption context:
{orig}
""",

    "cta": lambda orig: f"""Generate 5 short Call-To-Action lines (one-per-line). Style: punchy, 3-6 words, suitable for Instagram Reels (attitude vibe).

Caption context:
{orig}
""",

    "hashtags": lambda orig, niche=None: f"""Generate 12 relevant Instagram hashtags for the following caption and niche.
Rules:
- Include 4 broad hashtags, 4 niche-specific hashtags and 4 micro/trending hashtags.
- Return as one line separated by spaces (e.g. #a #b #c ...).

Caption:
{orig}
Niche: {niche or 'general'}
""",

    "keywords": lambda orig: f"""Extract 8 short keyword phrases (comma separated) useful for tagging & SEO based on this caption/video vibe.

Caption:
{orig}
""",

}

# -------- API CALL --------
def send_request_openrouter(model: str, api_key: str, user_prompt: str, max_tokens=MAX_TOKENS, temperature=TEMPERATURE):
    """
    Sends a chat-like request to OpenRouter-compatible endpoint.
    If your provider needs a different shape, update this function.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": user_prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    try:
        r = requests.post(OPENROUTER_CHAT_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        # openrouter style: data['choices'][0]['message']['content'] often
        # but multiple providers vary; try common locations
        # Try nested access defensively:
        if isinstance(data, dict):
            if "choices" in data and data["choices"]:
                ch = data["choices"][0]
                if isinstance(ch, dict):
                    # Chat-style
                    if "message" in ch and isinstance(ch["message"], dict) and "content" in ch["message"]:
                        return ch["message"]["content"].strip()
                    if "delta" in ch and isinstance(ch["delta"], dict) and "content" in ch["delta"]:
                        return ch["delta"]["content"].strip()
                    if "text" in ch:
                        return ch["text"].strip()
            # fallback: some providers return generated_text in list
            if "generated_text" in data:
                return data["generated_text"].strip()
        # final fallback: try parsing choices[0].text
        try:
            return data["choices"][0]["text"].strip()
        except Exception:
            pass
        return json.dumps(data)  # return raw if nothing matched
    except Exception as e:
        raise

# -------- MULTI-PROVIDER REQUEST SYSTEM (OpenRouter → OpenAI → Gemini) --------

# Correct OpenRouter endpoint
OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"

# Load extra keys from .env
OPENAI_KEY = env.get("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = env.get("OPENAI_MODEL", "").strip()

GEMINI_KEY = env.get("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = env.get("GEMINI_MODEL", "").strip()

OPENAI_URL = "https://api.openai.com/v1/chat/completions"
GEMINI_URL = None
if GEMINI_KEY and GEMINI_MODEL:
    GEMINI_URL = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_KEY}"
    )

# -----------------------------------------------
# Provider 1 → OpenRouter (multiple keys)
# -----------------------------------------------
def call_openrouter(model, prompt):
    if not KEYS:
        return None

    for _ in range(RETRY_LIMIT):
        api_key = next(key_cycle)

        try:
            r = requests.post(
                OPENROUTER_CHAT_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": MAX_TOKENS,
                    "temperature": TEMPERATURE,
                },
                timeout=REQUEST_TIMEOUT,
            )

            if r.status_code != 200:
                continue  # try next key

            data = r.json()

            # -------- SAFE PARSING --------
            if (
                isinstance(data, dict)
                and "choices" in data
                and isinstance(data["choices"], list)
                and len(data["choices"]) > 0
            ):
                ch = data["choices"][0]

                # Chat format
                if (
                    isinstance(ch, dict)
                    and "message" in ch
                    and isinstance(ch["message"], dict)
                    and "content" in ch["message"]
                ):
                    return ch["message"]["content"].strip()

                # Delta streaming format (some providers)
                if (
                    "delta" in ch
                    and isinstance(ch["delta"], dict)
                    and "content" in ch["delta"]
                ):
                    return ch["delta"]["content"].strip()

                # Fallback: raw text
                if "text" in ch:
                    return str(ch["text"]).strip()

            # Some providers respond with "generated_text"
            if "generated_text" in data:
                return str(data["generated_text"]).strip()

        except Exception:
            continue

    return None


# -----------------------------------------------
# Provider 2 → OpenAI Direct API
# -----------------------------------------------
def call_openai(prompt):
    if not OPENAI_KEY or not OPENAI_MODEL:
        return None

    try:
        r = requests.post(
            OPENAI_URL,
            headers={
                "Authorization": f"Bearer {OPENAI_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENAI_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": MAX_TOKENS,
                "temperature": TEMPERATURE,
            },
            timeout=REQUEST_TIMEOUT,
        )

        if r.status_code != 200:
            return None

        data = r.json()

        # ---- SAFE PARSING ----
        if (
            isinstance(data, dict)
            and "choices" in data
            and isinstance(data["choices"], list)
            and len(data["choices"]) > 0
        ):
            ch = data["choices"][0]

            # Normal OpenAI format
            if (
                isinstance(ch, dict)
                and "message" in ch
                and isinstance(ch["message"], dict)
                and "content" in ch["message"]
            ):
                return ch["message"]["content"].strip()

            # Sometimes providers send "text"
            if "text" in ch:
                return str(ch["text"]).strip()

        return None

    except Exception:
        return None


# -----------------------------------------------
# Provider 3 → Google Gemini Direct API
# -----------------------------------------------
def call_gemini(prompt):
    # Agar key ya model nahi hai to directly skip
    if not GEMINI_KEY or not GEMINI_MODEL or not GEMINI_URL:
        return None

    try:
        r = requests.post(
            GEMINI_URL,
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=REQUEST_TIMEOUT,
        )

        data = r.json()

        # Safe parsing
        if isinstance(data, dict) and "candidates" in data and data["candidates"]:
            cand = data["candidates"][0]
            if (
                isinstance(cand, dict)
                and "content" in cand
                and "parts" in cand["content"]
                and cand["content"]["parts"]
                and "text" in cand["content"]["parts"][0]
            ):
                return cand["content"]["parts"][0]["text"].strip()

    except Exception:
        return None

    return None

# -----------------------------------------------
# MASTER FALLBACK REQUEST — automatically picks:
# OpenRouter → OpenAI → Gemini
# -----------------------------------------------

def fallback_defaults(kind):
    if kind == "caption":
        return "🔥 Stay tuned. Big content coming soon!"

    if kind == "hook":
        return ("Unbelievable moment ahead! 👀\n"
                "Wait till the end 🔥\n"
                "This hits different 💯")

    if kind == "cta":
        return ("Follow for more 🔥\n"
                "Drop a ❤️\n"
                "Save this now\n"
                "Share with friends\n"
                "Stay tuned!")

    if kind == "hashtags":
        return ("#viral #trending #reels #explore #motivation "
                "#inspiration #attitude #lifestyle #dailyquotes "
                "#mindset #success #focus")

    if kind == "keywords":
        return "viral, trending, reels, attitude, lifestyle, motivation, mindset, quotes"

    return ""  # default


def request_with_rotation(model, prompt, fallback_type=None):
    for attempt in range(RETRY_LIMIT):

        # 1) Try OPENROUTER
        res = call_openrouter(model, prompt)
        if res:
            return res

        rate_limit_sleep(attempt)   

        # 2) Try OPENAI
        res = call_openai(prompt)
        if res:
            return res

        rate_limit_sleep(attempt)   

        # 3) Try GEMINI
        res = call_gemini(prompt)
        if res:
            return res

        rate_limit_sleep(attempt)   

    # If everything fails → fallback
    return fallback_defaults(fallback_type)



# -------- DISTRIBUTION / SCHEDULER LOGIC --------
def choose_model_for_index(index: int, total: int) -> str:
    """
    Distributes load evenly across all models.
    - If few posts, use fewer models.
    - If more posts, gradually introduce more models.
    - Once n models chosen, use round-robin for perfect balance.
    """

    model_count = len(MODELS)

    # How many models to use based on total workload
    if total <= 10:
        n = 1
    elif total <= 50:
        n = min(2, model_count)
    elif total <= 150:
        n = min(3, model_count)
    elif total <= 300:
        n = min(4, model_count)
    else:
        n = model_count

    # Round-robin selection
    return MODELS[index % n]


import re

def clean_output(text: str) -> str:
    if not text:
        return ""

    # Remove markdown code fences
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

    # Remove markdown styling: **bold**, *italic*
    text = text.replace("**", "").replace("*", "")

    # Remove headings like "Here is the caption:", "Final:", etc.
    text = re.sub(r"(?i)(here is.*?:|final.*?:|output.*?:|caption.*?:)\s*", "", text)

    # Remove leading dashes and bullets
    text = re.sub(r"^[\-•]+\s*", "", text, flags=re.MULTILINE)

    # Remove extra quotes
    text = text.strip().strip('"').strip("'")

    # Collapse multiple blank lines into one
    text = re.sub(r"\n{2,}", "\n", text)

    return text.strip()

def rate_limit_sleep(attempt):
    """
    Smart sleep:
    - No delay for first attempt
    - Small delay for 2nd attempt
    - Bigger delay for 3rd attempt
    - Adds jitter for randomness
    """
    base = [0, 1.0, 3.0]  # seconds
    delay = base[min(attempt, 2)] + random.uniform(0.3, 0.7)
    time.sleep(delay)

# -------- MAIN PROCESSING --------
def process_all_posts():
    # gather all post folders
    folders = [d for d in os.listdir(INPUT_BASE) if os.path.isdir(os.path.join(INPUT_BASE,d))]
    total = len(folders)
    if total == 0:
        print("No post folders found in INPUT_BASE:", INPUT_BASE)
        return
    print(f"Found {total} post folders. Starting generation...")

    for idx, folder in enumerate(sorted(folders)):
        post_path = os.path.join(INPUT_BASE, folder)
        # find caption.txt inside this folder
        caption_file = os.path.join(post_path, "caption.txt")
        if not os.path.isfile(caption_file):
            print(f"Skipping {folder}: caption.txt not found.")
            continue
        original_caption = Path(caption_file).read_text(encoding="utf8").strip()
        # choose model:
        model_choice = choose_model_for_index(idx // 2, total)
        print(f"\n[{idx+1}/{total}] {folder} → model={model_choice}")

        # 1) Caption rewrite
        try:
            prompt = PROMPTS["caption_rewrite"](original_caption)
            out = request_with_rotation(model_choice, prompt)
            out_caption = clean_output(out)
        except Exception as e:
            print("  caption rewrite failed:", e)
            out_caption = original_caption  # fallback: keep original

        # save caption.txt (overwrite or write new? We'll overwrite caption.txt to reflect final)
        caption_out_path = os.path.join(post_path, "caption.txt")
        with open(caption_out_path, "w", encoding="utf8") as f:
            f.write(out_caption)
        print("  ✔ caption saved")

        # generate other assets using same model choice (or rotate for variety)
        # hook
        try:
            hook_prompt = PROMPTS["hook"](out_caption)
            hooks_raw = request_with_rotation(model_choice, hook_prompt)
            hooks = clean_output(hooks_raw)
        except Exception as e:
            hooks = ""
            print("  hook generation failed:", e)
        with open(os.path.join(post_path, "hook.txt"), "w", encoding="utf8") as f:
            f.write(hooks)
        print("  ✔ hook saved")

        # cta
        try:
            cta_prompt = PROMPTS["cta"](out_caption)
            cta_raw = request_with_rotation(model_choice, cta_prompt)
            cta = clean_output(cta_raw)
        except Exception as e:
            cta = ""
            print("  cta generation failed:", e)
        with open(os.path.join(post_path, "cta.txt"), "w", encoding="utf8") as f:
            f.write(cta)
        print("  ✔ cta saved")

        # hashtags
        try:
            tags_prompt = PROMPTS["hashtags"](out_caption)
            tags_raw = request_with_rotation(model_choice, tags_prompt)
            # normalize to single-line space-separated
            tags_clean = clean_output(tags_raw)
            tags_line = " ".join([t.strip() for t in tags_clean.replace("\n", " ").split() if t.strip()])[:900]
        except Exception as e:
            tags_line = ""
            print("  hashtags failed:", e)
        with open(os.path.join(post_path, "hashtags.txt"), "w", encoding="utf8") as f:
            f.write(tags_line)
        print("  ✔ hashtags saved")

        # keywords
        try:
            keywords_prompt = PROMPTS["keywords"](out_caption)
            keywords_raw = request_with_rotation(model_choice, keywords_prompt)
        except Exception as e:
            keywords_raw = ""
            print("  keywords failed:", e)
        with open(os.path.join(post_path, "keywords.txt"), "w", encoding="utf8") as f:
            f.write(keywords_raw.strip())
        print("  ✔ keywords saved")

        # small sleep to avoid bursting
        time.sleep(0.5 + random.random() * 0.6)

    print("\n✅ All done. Generated files saved inside each post folder.")

if __name__ == "__main__":
    process_all_posts()
