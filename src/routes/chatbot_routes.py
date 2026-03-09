from flask import Blueprint, request, jsonify
import os

chatbot_bp = Blueprint("chatbot", __name__, url_prefix="/api")

# ---- Safe Gemini Import ----
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except Exception:
    genai = None
    GEMINI_AVAILABLE = False


@chatbot_bp.post("/chatbot")
def chatbot_response():
    if not GEMINI_AVAILABLE:
        return jsonify({
            "success": False,
            "reply": "Gemini SDK not installed. Run: pip install google-generativeai"
        }), 500

    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    prediction = (data.get("prediction") or "").strip()

    if not user_message:
        return jsonify({
            "success": False,
            "message": "Message is required"
        }), 400

    api_key = (os.getenv("GEMINI_API_KEY") or "").strip()
    if not api_key:
        return jsonify({
            "success": False,
            "message": "GEMINI_API_KEY not configured"
        }), 500

    # Configure Gemini
    genai.configure(api_key=api_key)
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    model = genai.GenerativeModel(model_name)

    system_prompt = f"""
You are DEMNET Help — an AI assistant for an Alzheimer MRI Diagnosis System.

RULES:
- Answer ONLY Alzheimer, MRI, prediction, or DEMNET website help.
- Be clear, simple, and medically responsible.
- Do NOT answer unrelated topics.

WEBSITE NAVIGATION:
- Dashboard → Overview
- Upload → Upload MRI scans
- Reports → Generated reports
- Profile → Account & security
- Admin → System management (admins only)

LATEST MRI PREDICTION:
{prediction if prediction else "No MRI prediction available."}

USER QUESTION:
{user_message}
"""

    try:
        result = model.generate_content(system_prompt)
        reply = (getattr(result, "text", "") or "").strip()

        if not reply:
            reply = "I couldn't generate a response. Please try again."

        return jsonify({
            "success": True,
            "reply": reply
        }), 200

    except Exception as e:
        print("Gemini error:", str(e))
        return jsonify({
            "success": False,
            "reply": "AI service temporarily unavailable."
        }), 500
