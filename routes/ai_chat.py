from flask import Blueprint, request, jsonify, current_app
import google.generativeai as genai
import os

ai_bp = Blueprint('ai_bp', __name__)

# ── THE PERSONA: This is the brain of your AI ───────────────────────
SYSTEM_PROMPT = """
You are the official AI assistant representing Deepmani Mishraa on his personal website. 
You speak in the first-person plural as his assistant (e.g., "Deepmani is...", "We are building...").

Here is the factual information about Deepmani you must use to answer questions:
- Name: Deepmani Mishraa
- Education: Pursuing a BS in Data Science & Applications at IIT Madras.
- Location: Based in Areraj, District- East Champaran, Bihar- 845425, India.
- Primary Startup: Co-Founder of PRAMANIIK.
- PRAMANIIK Details: An application to make user's data private and is focused on the Indian market. It acts as a "Digital Iron Dome" using "Zero-Knowledge" and "Zero Trust" architecture (strict local-first verification, data encryption, absolutely NO contact syncing or data harvesting). Full launch plan will be updating soon.
- Content Creation: Manages a faceless YouTube channel named 'FinBiz Funda' focusing on finance and business content.
- Personal Context: Single. His father is an Educator at his own coaching institute named- Apex Institute Of Science & English.

Interaction Rules:
1. Tone: Professional, highly knowledgeable, and slightly enthusiastic about cybersecurity and AI.
2. Brevity: Keep answers concise and web-friendly (1-3 short paragraphs max).
3. Honesty: Do not hallucinate or invent skills, projects, or personal details not listed above. If you don't know the answer, politely state that the user should use the Contact form to ask Deepmani directly.
"""

@ai_bp.route('/chat', methods=['POST'])
def chat():
    # 1. Grab the incoming data from the frontend
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'reply': 'No message provided.'}), 400

    user_message = data['message']
    history = data.get('history', [])

    # 2. Check for the API Key
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key or api_key == 'your_gemini_api_key_here':
        return jsonify({'reply': 'My AI persona is currently offline. Please check back later!'}), 500

    try:
        # 3. Configure Gemini
        genai.configure(api_key=api_key)
        
        # 4. Clean up the chat history to match Gemini's strict format requirements
        formatted_history = []
        for msg in history:
            # The frontend sends 'user' or 'model', which Gemini accepts natively
            role = msg.get('role', 'user') 
            parts = msg.get('parts', [{'text': ''}])
            text = parts[0].get('text', '') if parts else ''
            formatted_history.append({'role': role, 'parts': [text]})

        # 5. Initialize the specific model with your persona
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT
        )

        # 6. Start the chat with history and send the new message
        chat_session = model.start_chat(history=formatted_history)
        response = chat_session.send_message(user_message)

        # 7. Return the AI's reply to the frontend
        return jsonify({'reply': response.text})

    except Exception as e:
        print(f"AI Chat Error: {e}")
        return jsonify({'reply': 'Sorry, I am having a slight connection hiccup right now. Please try again in a moment!'}), 500