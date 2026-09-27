import sys
import json
from groq import Groq

import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

API_KEY = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=API_KEY)

query = "Polladhavan (Tamil film starring Dhanush)"

prompt = f"""You are the world's leading Hollywood, Indian, and International Box Office Financial Analyst.
Analyze the exact, verified real-world box office performance for the film: "{query}".
Provide accurate historical box office figures, budget, and commercial verdict.

Respond strictly with valid JSON with NO surrounding markdown backticks or commentary.
Required JSON schema:
{{
  "title": "Exact Official Movie Title",
  "release_year": 2007,
  "worldwide_gross": 4800000,
  "domestic_gross": 4200000,
  "international_gross": 600000,
  "budget": 950000,
  "local_currency_note": "₹18-20 Crore Worldwide Gross | ₹3.5-4 Crore Production Budget",
  "roi_percentage": 405.2,
  "profit_multiplier": 5.05,
  "verdict": "Blockbuster (Cult Classic Hit)",
  "badge_color": "#10b981",
  "director": "Vetrimaaran",
  "top_cast": ["Dhanush", "Divya Spandana", "Daniel Balaji", "Kishore"],
  "genres": ["Action", "Crime", "Drama"],
  "synopsis": "Prabhu, a carefree youth from Chennai, gets a job and buys his dream bike. When the bike is stolen, he gets dragged into the dark criminal underworld to recover it.",
  "financial_breakdown": "Polladhavan emerged as a massive commercial blockbuster in Tamil cinema, grossing ₹18-20 crore worldwide against a ₹3.5-4 crore budget, yielding a 5x return.",
  "key_success_factors": ["Vetrimaaran's gritty realistic direction", "Dhanush's mass appeal and authentic performance", "GV Prakash Kumar's chartbuster soundtrack", "Relatable youth storyline with the Bajaj Pulsar bike"],
  "fun_fact": "Marked the debut of director Vetrimaaran, kickstarting one of Indian cinema's most acclaimed actor-director partnerships with Dhanush."
}}"""

models_to_try = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"]

for model in models_to_try:
    try:
        res = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a professional film box office financial analyst. Output strictly valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        content = res.choices[0].message.content.strip()
        parsed = json.loads(content)
        print(f"Success with {model}:")
        print(json.dumps(parsed, indent=2))
        break
    except Exception as e:
        print(f"Failed with {model}: {e}")
