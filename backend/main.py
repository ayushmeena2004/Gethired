from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import pdfplumber
from dotenv import load_dotenv
from groq import Groq
import os
import json
import razorpay

load_dotenv()  # Load environment variables from .env file
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

class UserInput(BaseModel):
    interest: str
    skill: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def home():
    return {"message": "Backend running 🚀"}

@app.post("/get-career")
def get_career(data: UserInput):
    if data.interest == "Tech" and data.skill == "Logic":
        return {
            "career": "Data Science / AI",
            "desc": "You are strong in logic and analysis."
        }
    elif data.interest == "Business":
        return {
            "career": "Marketing",
            "desc": "You are good with strategy and communication."
        }
    else:
        return {
            "career": "Web Development",
            "desc": "You can build apps and websites."
        }
    


@app.post("/analyze-resume")
async def analyze_resume(file: UploadFile = File(...)):
    text = ""

    # Extract text from PDF
    with pdfplumber.open(file.file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    # Limit text (important for AI)
    text = text[:3000]

    prompt = f"""
You are a professional resume reviewer.

Analyze this resume and return ONLY valid JSON.

IMPORTANT:
- Score MUST be between 0 and 100 (not 0–10)
- Do NOT return score like 7 or 8
- Return realistic ATS-style score (e.g., 65, 78, 82)

Format:
{{
  "score": number (0-100),
  "suggestions": ["point1", "point2", "point3", "point4", "point5"]
}}

Resume:
{text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )

    import re

    ai_output = response.choices[0].message.content.strip()

# ✅ Remove ```json ``` if present
    ai_output = re.sub(r"```json|```", "", ai_output).strip()

# ✅ Extract JSON from text (important)
    match = re.search(r"\{.*\}", ai_output, re.DOTALL)

    if match:
     json_text = match.group()
    else:
     json_text = ai_output  # fallback

# ✅ Parse safely
    try:
     parsed = json.loads(json_text)
    except Exception as e:
     print("Parsing Error:", e)
     print("AI Output:", ai_output)
     parsed = {
        "score": 70,
        "suggestions": ["AI response parsing failed"]
    }
    

    return parsed




razorpay_client = razorpay.Client(auth=(
    os.getenv("RAZORPAY_KEY_ID"),
    os.getenv("RAZORPAY_KEY_SECRET")
))

@app.post("/create-order")
def create_order():
    order = razorpay_client.order.create({
        "amount": 4900,  # ₹49 in paise
        "currency": "INR",
        "payment_capture": 1
    })

    return order

# Endpoint to handle resume rewriting (bonus feature)
import pdfplumber
from fastapi import FastAPI, File, UploadFile
from textwrap import dedent  # <--- This is your best friend for prompts

@app.post("/rewrite")
async def rewrite_resume(file: UploadFile = File(...)):
    try:
        # Read PDF
        with pdfplumber.open(file.file) as pdf:
            text = "".join(page.extract_text() or "" for page in pdf.pages)

        if not text.strip():
            return {"error": "Could not extract text from PDF"}

        # Using dedent allows you to indent the prompt so it looks good in VS Code
        # but removes the leading whitespace before sending it to GROQ.
        prompt = f"""
Rewrite this resume in clean HTML format.

Rules:
- Use <h1> for name
- Use <h2> for section headings
- Use <ul><li> for bullet points
- No markdown (** or *)
- Keep it ATS-friendly and professional

Resume:
{text}
"""

        # Call GROQ AI
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )

        rewritten = response.choices[0].message.content
        html_resume = rewritten.replace("\n", "<br>")
        return {"rewritten_resume": html_resume}

    except Exception as e:
        return {"error": str(e)}