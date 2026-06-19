from flask import Blueprint, request, jsonify, current_app

ai_bp = Blueprint('ai', __name__)

SYSTEM_PROMPT = """You are an AI assistant for Deepmani Mishraa's personal website.

About Deepmani Mishraa:
- Nickname: DM Babu
- DOB: 2004-September-04 (Original), 2005-September-04
- Family: 
  -Father- Ratnesh Kumar Mishra (Educator, Director of Apex Institute Of Science & English) 
  -Mother- Brijkishori Devi 
  -Brother- Abhishek Kumar (Doctor) 
  -Sister- Minakshi Kumari
-Education:
  - Primary Schooling: Class- UKG to 3rd from Little Flower Public School, Kauwaha and Class 4th to 6th from Maa Suthra Vidyapith, Areraj
  - High School: Class 9th and 10th (Passing Year- 2020) from Govt High School, Paharpur
  - Intermediate: Class 11th and 12th (Passing Year- 2022) from Laxmi Narayan Dubey College (L.N.D), Motihari
  - Higher Education (UG): Currently pursuing BSc in Data Science & Applications from IIT Madras and CSE(AI) from Govt Engineering College, Lakhisarai, Bihar 
-Relationship Status: Single
- Traveled: 25+ places in India (19+ Districts of Bihar, Deoghar (Jan 2024), Varanasi (Jan 2024) , Prayagraj (Feb 2025), Gorakhpur (Apr 2025), Kolkata (May 2025), Bhubaneswar (Jun 2025), Vishakhapatnam (Jun 2025), Chennai (Jun 2025), Kanpur (Mar 2026), Agra (Mar 2026), Mathura (Mar 2026), Vrindavan (Mar 2026), Barsana (Mar 2026), New Delhi (Mar 2026))
- Hobbies: Entrepreneurship, Reading, Traveling, Exploring new places, Listening to Music, Watching Movies
- Co-Founder of PRAMANIIK — a cybersecurity startup focused on data privacy and digital trust
- Vision: Lead this era with technology to solve real-world problems and build scalable ecosystems
- Goals: Make India 'Vishwa Guru' in tech, AI, innovation. Become the world's biggest tech identity
- Personality: Visionary, passionate, driven, intellectually curious, humble yet ambitious

Reply warmly and professionally. Represent Deepmani well. If asked about collaborations or opportunities, encourage them to use the Contact form. Keep answers short and professional unless more detail is asked for. Answer only what is asked, reply with a counter question about what they would like to know. In case of DOB, Do not reply the Original DOB unless asked for it."""

@ai_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get('message') or '').strip()
    history      = data.get('history', [])

    if not user_message:
        return jsonify({'error': 'Empty message'}), 400

    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        return jsonify({'reply': (
            "AI chat is being set up — API key not configured yet. "
            "Please reach out via the Contact form in the meantime! 📬"
        )})

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)

        # 🛠️ FIX: Format history exactly as the Python SDK expects
        safe_history = []
        for h in history[-8:]:
            role = h.get('role', '')
            if role not in ('user', 'model'):
                continue
            
            # Extract text safely depending on how the frontend structures it
            text = ""
            raw_parts = h.get('parts', [])
            if isinstance(raw_parts, list) and len(raw_parts) > 0:
                if isinstance(raw_parts[0], dict):
                    text = raw_parts[0].get('text', '')
                elif isinstance(raw_parts[0], str):
                    text = raw_parts[0]
            elif isinstance(raw_parts, str):
                text = raw_parts

            if text:
                # SDK requires 'parts' to be a list of strings
                safe_history.append({'role': role, 'parts': [text]})

        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
        
        session  = model.start_chat(history=safe_history)
        
        # 1. Ask Gemini to stream the response
        response = session.send_message(user_message, stream=True)
        
        # 2. Create a generator to send chunks to the frontend immediately
        from flask import Response, stream_with_context
        def generate():
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        return Response(stream_with_context(generate()), mimetype='text/plain')

    except ImportError:
        error_msg = "Library missing. Please run: pip install google-generativeai"
        print(f"🔥 {error_msg}")
        return jsonify({'reply': f"🛠️ DEV ERROR: {error_msg}"})
        
    except Exception as e:
        err = str(e)
        # 🛠️ FIX: Print the actual error to the VS Code terminal
        print(f"\n🔥 GEMINI API ERROR 🔥\n{err}\n")

        if 'API_KEY' in err.upper() or 'PERMISSION' in err.upper():
            reply = "The AI key needs to be configured in the admin settings."
        elif 'QUOTA' in err.upper() or 'RATE' in err.upper():
            reply = "I'm a little overwhelmed right now 😅 — try again in a moment..."
        else:
            reply = "Something went sideways on my end. Please try again!"
            
        # 🛠️ FIX: Temporarily append the raw error so you can see it in the UI!
        reply += f"\n\n🛠️ DEV MODE RAW ERROR:\n{err}"
        
        return jsonify({'reply': reply})