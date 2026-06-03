import os
from groq import Groq
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get API key
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("❌ GROQ_API_KEY not found in .env file")

# Initialize Groq client
client = Groq(api_key=api_key)

# -----------------------------
# SYSTEM PROMPT (AGENTIC AI)
# -----------------------------
SYSTEM_PROMPT = """
You are Smart Timetable AI, an intelligent agentic assistant for students.

You help with:
- Study planning
- Timetable management
- Assignments tracking
- Productivity improvement
- Daily scheduling

Rules:
- Always respond in a helpful, simple, and modern way.
- Never mention knowledge cutoff or training data.
- Assume current year is 2026.
- If unsure about real-time info, give best logical answer.
- Be concise and practical.
"""

# -----------------------------
# MAIN AI FUNCTION
# -----------------------------
def ask_ai(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ AI Error: {str(e)}"