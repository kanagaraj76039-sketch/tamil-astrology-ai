# Tamil Vedic Astrology AI - Flask API Server
# Complete REST API for astrology predictions

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from skyfield_calculator import SkyfieldVedicCalculator
from config import AI_PROVIDER, GEMINI_API_KEY, ANTHROPIC_API_KEY, OLLAMA_MODEL, OLLAMA_URL, OPENAI_API_KEY
import json
import os

app = Flask(__name__)
CORS(app)

# Initialize components
calculator = SkyfieldVedicCalculator()

# Initialize AI agent based on provider
ai_agent = None
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

if AI_PROVIDER == "groq" and GROQ_API_KEY:
    from groq_ai_agent import TamilAstrologyGroqAI
    ai_agent = TamilAstrologyGroqAI(GROQ_API_KEY)
    print("✅ Groq AI Agent initialized (FREE, Fast)")
elif AI_PROVIDER == "openai" and OPENAI_API_KEY:
    from openai_ai_agent import TamilAstrologyOpenAI
    ai_agent = TamilAstrologyOpenAI(OPENAI_API_KEY)
    print("✅ OpenAI ChatGPT Agent initialized")
elif AI_PROVIDER == "ollama":
    from ollama_ai_agent import TamilAstrologyOllamaAI
    ai_agent = TamilAstrologyOllamaAI(model=OLLAMA_MODEL, base_url=OLLAMA_URL)
    print("✅ Ollama AI Agent initialized (local, free)")
elif AI_PROVIDER == "gemini" and GEMINI_API_KEY:
    from gemini_ai_agent_v2 import TamilAstrologyGeminiAI
    ai_agent = TamilAstrologyGeminiAI(GEMINI_API_KEY)
    print("✅ Gemini AI Agent initialized")
elif ANTHROPIC_API_KEY:
    from tamil_ai_agent import TamilAstrologyAI
    ai_agent = TamilAstrologyAI()
    print("✅ Anthropic AI Agent initialized")
else:
    print("⚠️ No AI configured. AI predictions disabled.")


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/api', methods=['GET'])
def api_info():
    return jsonify({
        "பெயர்": "தமிழ் வேத ஜோதிட AI",
        "பதிப்பு": "1.0.0",
        "சேவைகள்": [
            "ஜாதகம் கணிப்பு",
            "தினசரி/வாராந்திர/மாதாந்திர பலன்",
            "திருமண பொருத்தம்",
            "முகூர்த்தம்",
            "கேள்வி-பதில்"
        ]
    })


@app.route('/api/birth-chart', methods=['POST'])
def get_birth_chart():
    """Calculate birth chart from birth details"""
    try:
        data = request.json
        birth_date = data.get('birth_date')  # Format: YYYY-MM-DD
        birth_time = data.get('birth_time')  # Format: HH:MM
        birth_place = data.get('birth_place')  # City name
        
        if not all([birth_date, birth_time, birth_place]):
            return jsonify({"பிழை": "பிறந்த தேதி, நேரம், இடம் அனைத்தும் தேவை"}), 400
        
        chart = calculator.calculate_birth_chart(birth_date, birth_time, birth_place)
        return jsonify({"வெற்றி": True, "ஜாதகம்": chart})
    
    except Exception as e:
        return jsonify({"பிழை": str(e)}), 500


@app.route('/api/prediction', methods=['POST'])
def get_prediction():
    """Get AI-generated prediction based on birth chart"""
    try:
        
        data = request.json
        birth_date = data.get('birth_date')
        birth_time = data.get('birth_time')
        birth_place = data.get('birth_place')
        question_type = data.get('question_type', 'பொது')  # பொது, தொழில், திருமணம், உடல்நலம், பணம்
        specific_question = data.get('question')
        
        # Calculate chart
        chart = calculator.calculate_birth_chart(birth_date, birth_time, birth_place)
        
        # Get Jathaga Kattam
        jathaga_kattam = calculator.get_jathaga_kattam(chart)
        
        # Get current transits
        transits = calculator.get_current_transits()
        chart["கோசாரம்"] = transits["கோசாரம்"]
        
        # Generate AI prediction (optional - may fail due to rate limits)
        prediction = ""
        try:
            if ai_agent:
                prediction = ai_agent.generate_prediction(chart, question_type, specific_question)
        except Exception as ai_error:
            print(f"AI Error: {type(ai_error).__name__}: {str(ai_error)}")
            prediction = f"AI பலன் தற்போது கிடைக்கவில்லை. பிழை: {str(ai_error)[:100]}"
        
        return jsonify({
            "வெற்றி": True,
            "ஜாதகம்": chart,
            "ஜாதக_கட்டம்": jathaga_kattam,
            "பலன்": prediction
        })
    
    except Exception as e:
        return jsonify({"பிழை": str(e)}), 500


@app.route('/api/full-chart', methods=['POST'])
def get_full_chart():
    """Get complete birth chart with Jathaga Kattam and all Dasha-Bhukti details"""
    try:
        data = request.json
        birth_date = data.get('birth_date')
        birth_time = data.get('birth_time')
        birth_place = data.get('birth_place')
        name = data.get('name', '')
        
        if not all([birth_date, birth_time, birth_place]):
            return jsonify({"பிழை": "பிறந்த தேதி, நேரம், இடம் அனைத்தும் தேவை"}), 400
        
        # Calculate chart
        chart = calculator.calculate_birth_chart(birth_date, birth_time, birth_place)
        
        # Get Jathaga Kattam
        jathaga_kattam = calculator.get_jathaga_kattam(chart)
        
        # Get current transits
        transits = calculator.get_current_transits()
        
        return jsonify({
            "வெற்றி": True,
            "பெயர்": name,
            "ஜாதகம்": chart,
            "ஜாதக_கட்டம்": jathaga_kattam,
            "கோசாரம்": transits["கோசாரம்"]
        })
    
    except Exception as e:
        return jsonify({"பிழை": str(e)}), 500


@app.route('/api/daily-horoscope', methods=['POST'])
def get_daily_horoscope():
    """Get daily horoscope for a rasi"""
    try:
        if not ai_agent:
            return jsonify({"பிழை": "AI API key not configured. Set GEMINI_API_KEY environment variable."}), 503
        
        data = request.json
        
        # Option 1: Direct rasi input
        rasi = data.get('rasi')
        nakshatra = data.get('nakshatra')
        current_dasha = data.get('current_dasha', 'தெரியவில்லை')
        
        # Option 2: Calculate from birth details
        if not rasi and data.get('birth_date'):
            chart = calculator.calculate_birth_chart(
                data['birth_date'], 
                data.get('birth_time', '12:00'), 
                data.get('birth_place', 'Chennai')
            )
            rasi = chart['ராசி']
            nakshatra = chart['ஜென்ம நட்சத்திரம்']
            if chart['தசா']['தற்போதைய_தசா']:
                current_dasha = chart['தசா']['தற்போதைய_தசா']['தசா']
        
        if not rasi:
            return jsonify({"பிழை": "ராசி அல்லது பிறந்த விவரங்கள் தேவை"}), 400
        
        prediction = ai_agent.generate_daily_prediction(rasi, nakshatra or "தெரியவில்லை", current_dasha)
        
        return jsonify({
            "வெற்றி": True,
            "ராசி": rasi,
            "நட்சத்திரம்": nakshatra,
            "இன்றைய_பலன்": prediction
        })
    
    except Exception as e:
        return jsonify({"பிழை": str(e)}), 500


@app.route('/api/compatibility', methods=['POST'])
def check_compatibility():
    """Check marriage compatibility between two people"""
    try:
        data = request.json
        
        person1 = {
            "date": data['person1']['birth_date'],
            "time": data['person1'].get('birth_time', '12:00'),
            "place": data['person1'].get('birth_place', 'Chennai')
        }
        
        person2 = {
            "date": data['person2']['birth_date'],
            "time": data['person2'].get('birth_time', '12:00'),
            "place": data['person2'].get('birth_place', 'Chennai')
        }
        
        # Calculate compatibility
        compatibility = calculator.calculate_compatibility(person1, person2)
        
        # Get AI analysis
        analysis = ai_agent.generate_compatibility_analysis(compatibility)
        
        return jsonify({
            "வெற்றி": True,
            "பொருத்தம்": compatibility,
            "விரிவான_பகுப்பாய்வு": analysis
        })
    
    except Exception as e:
        return jsonify({"பிழை": str(e)}), 500


@app.route('/api/muhurtham', methods=['POST'])
def get_muhurtham():
    """Calculate auspicious time for an event"""
    try:
        data = request.json
        purpose = data.get('purpose')  # திருமணம், கிரகப்பிரவேசம், தொழில் தொடக்கம், etc.
        preferred_dates = data.get('preferred_dates')
        
        if not purpose:
            return jsonify({"பிழை": "நிகழ்வு விவரம் தேவை"}), 400
        
        muhurtham = ai_agent.calculate_muhurtham(purpose, preferred_dates)
        
        return jsonify({
            "வெற்றி": True,
            "நிகழ்வு": purpose,
            "முகூர்த்தம்": muhurtham
        })
    
    except Exception as e:
        return jsonify({"பிழை": str(e)}), 500


@app.route('/api/ask', methods=['POST'])
def ask_question():
    """Ask any astrology question"""
    try:
        data = request.json
        question = data.get('question')
        
        if not question:
            return jsonify({"பிழை": "கேள்வி தேவை"}), 400
        
        # If birth details provided, include chart
        chart = None
        if data.get('birth_date'):
            chart = calculator.calculate_birth_chart(
                data['birth_date'],
                data.get('birth_time', '12:00'),
                data.get('birth_place', 'Chennai')
            )
            transits = calculator.get_current_transits()
            chart["கோசாரம்"] = transits["கோசாரம்"]
        
        answer = ai_agent.answer_question(chart, question)
        
        return jsonify({
            "வெற்றி": True,
            "கேள்வி": question,
            "பதில்": answer
        })
    
    except Exception as e:
        return jsonify({"பிழை": str(e)}), 500


@app.route('/api/transits', methods=['GET'])
def get_transits():
    """Get current planetary transits"""
    try:
        transits = calculator.get_current_transits()
        return jsonify({"வெற்றி": True, "கோசாரம்": transits})
    except Exception as e:
        return jsonify({"பிழை": str(e)}), 500


if __name__ == '__main__':
    print("=" * 50)
    print("தமிழ் வேத ஜோதிட AI சேவையகம்")
    print("=" * 50)
    print("சேவையகம் தொடங்குகிறது: http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
