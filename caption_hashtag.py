import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_caption_and_hashtags(username, original_text):
    prompt = f"""
Create an Instagram caption and hashtags.

Rules:
- Same meaning
- Rewritten (copyright safe)
- Emojis
- Call to action
- Mention @{username}
- 8–12 hashtags

Original Content:
{original_text}

IMPORTANT:
Return ONLY in this format:

CAPTION:
<caption text>

HASHTAGS:
#tag1 #tag2 #tag3
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a professional Instagram content creator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    output = response.choices[0].message.content.strip()

    caption = ""
    hashtags = ""

    if "HASHTAGS:" in output:
        parts = output.split("HASHTAGS:")
        caption = parts[0].replace("CAPTION:", "").strip()
        hashtags = parts[1].strip()
    else:
        # fallback safety
        caption = output
        hashtags = "#reels #viral #instagram"

    return caption, hashtags
