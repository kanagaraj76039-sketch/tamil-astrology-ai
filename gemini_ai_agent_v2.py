# Tamil Vedic Astrology AI Agent with Google Gemini (New SDK)
# Generates human-like predictions in pure Tamil

from google import genai
from google.genai import types
import json
from datetime import datetime

class TamilAstrologyGeminiAI:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.0-flash"
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self):
        return """நீங்கள் ஒரு அனுபவமிக்க வேத ஜோதிடர். 40 ஆண்டுகளுக்கும் மேலான அனுபவம் கொண்டவர். 
பிருகத் பராசர ஹோரா சாஸ்திரம், பலதீபிகா, ஜாதக பாரிஜாதம் போன்ற கிரந்தங்களில் தேர்ச்சி பெற்றவர்.

உங்கள் பணி:
1. ஜாதக விவரங்களை ஆராய்ந்து துல்லியமான பலன்கள் சொல்ல வேண்டும்
2. தசா-புக்தி பலன்களை விளக்க வேண்டும்
3. கோசார பலன்களை கணக்கில் எடுக்க வேண்டும்
4. பரிகாரங்கள் பரிந்துரைக்க வேண்டும்
5. சுப முகூர்த்தம் கணிக்க வேண்டும்

முக்கிய விதிகள்:
- எப்போதும் தூய தமிழில் பதில் அளிக்கவும்
- ஜோதிட சாஸ்திர விதிகளின்படி பலன் சொல்லவும்
- நம்பிக்கையூட்டும் வகையில் பேசவும்
- எதிர்மறை பலன்களுக்கு பரிகாரம் சொல்லவும்

கிரக பலன் விதிகள்:
- சூரியன்: தந்தை, அரசு, பதவி, ஆரோக்கியம்
- சந்திரன்: தாய், மனம், உணர்வுகள்
- செவ்வாய்: சகோதரர், தைரியம், நிலம்
- புதன்: கல்வி, வணிகம், தொடர்பு
- குரு: குரு, ஞானம், குழந்தை, செல்வம்
- சுக்கிரன்: மனைவி, காதல், கலை
- சனி: ஆயுள், கர்மா, தாமதம்
- ராகு: திடீர் மாற்றம், வெளிநாடு
- கேது: மோட்சம், ஆன்மீகம்

பரிகாரங்கள்:
- சூரியன்: ஆதித்ய ஹிருதயம், ஞாயிறு விரதம்
- சந்திரன்: சந்திர நமஸ்காரம், திங்கள் விரதம்
- செவ்வாய்: ஹனுமான் சாலிசா, செவ்வாய் விரதம்
- புதன்: விஷ்ணு சஹஸ்ரநாமம், புதன் விரதம்
- குரு: குரு ஸ்தோத்திரம், வியாழன் விரதம்
- சுக்கிரன்: லக்ஷ்மி ஸ்தோத்திரம், வெள்ளி விரதம்
- சனி: சனி ஸ்தோத்திரம், சனி விரதம்
- ராகு: துர்கா ஸ்தோத்திரம்
- கேது: கணபதி ஸ்தோத்திரம்"""

    def _generate(self, prompt):
        """Generate content using Gemini"""
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    temperature=0.7,
                    max_output_tokens=2048
                )
            )
            return response.text
        except Exception as e:
            # Try fallback model
            try:
                self.model_id = "gemini-1.5-flash"
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_prompt,
                        temperature=0.7,
                        max_output_tokens=2048
                    )
                )
                return response.text
            except Exception as e2:
                raise Exception(f"Gemini API error: {str(e2)}")

    def generate_prediction(self, chart_data, question_type, specific_question=None):
        """Generate prediction based on chart and question"""
        
        prompt = f"""ஜாதக விவரங்கள்:
{json.dumps(chart_data, ensure_ascii=False, indent=2)}

கேள்வி வகை: {question_type}
"""
        if specific_question:
            prompt += f"\nகுறிப்பிட்ட கேள்வி: {specific_question}"
        
        prompt += """

மேலே உள்ள ஜாதக விவரங்களை ஆராய்ந்து, கிரக நிலைகள், தசா-புக்தி ஆகியவற்றின் அடிப்படையில் விரிவான பலன் சொல்லுங்கள்.

பதில் கட்டமைப்பு:
1. ஜாதக சுருக்கம்
2. தற்போதைய தசா-புக்தி பலன்
3. கேள்விக்கான பதில்
4. எதிர்காலம் (அடுத்த 1 வருடம்)
5. பரிகாரங்கள்
"""
        
        return self._generate(prompt)
    
    def generate_daily_prediction(self, rasi, nakshatra, current_dasha="தெரியவில்லை"):
        """Generate daily horoscope"""
        
        prompt = f"""ராசி: {rasi}
நட்சத்திரம்: {nakshatra}
தற்போதைய தசா: {current_dasha}
இன்றைய தேதி: {datetime.now().strftime('%Y-%m-%d')}

இன்றைய ராசி பலன் சொல்லுங்கள்:
1. பொது பலன்
2. தொழில்/வேலை
3. பணம்
4. உடல்நலம்
5. உறவுகள்
6. அதிர்ஷ்ட நேரம்
7. அதிர்ஷ்ட எண்
8. அதிர்ஷ்ட நிறம்
"""
        
        return self._generate(prompt)
    
    def generate_compatibility_analysis(self, compatibility_data):
        """Generate detailed compatibility analysis"""
        
        prompt = f"""திருமண பொருத்த விவரங்கள்:
{json.dumps(compatibility_data, ensure_ascii=False, indent=2)}

மேலே உள்ள பொருத்த விவரங்களை ஆராய்ந்து விரிவான பகுப்பாய்வு செய்யுங்கள்:
1. ஒவ்வொரு பொருத்தத்தின் விளக்கம்
2. நல்ல அம்சங்கள்
3. கவனிக்க வேண்டிய விஷயங்கள்
4. திருமண வாழ்க்கை எப்படி இருக்கும்
5. பரிகாரங்கள் (தேவைப்பட்டால்)
"""
        
        return self._generate(prompt)
    
    def calculate_muhurtham(self, purpose, preferred_dates=None):
        """Calculate auspicious time for an event"""
        
        prompt = f"""நிகழ்வு: {purpose}
விரும்பும் தேதிகள்: {preferred_dates if preferred_dates else 'எந்த தேதியும் சரி'}
இன்றைய தேதி: {datetime.now().strftime('%Y-%m-%d')}

இந்த நிகழ்வுக்கு சுப முகூர்த்தம் கணிக்கவும்:
1. சுப தேதிகள் (அடுத்த 30 நாட்களில்)
2. சுப நேரம்
3. தவிர்க்க வேண்டிய நாட்கள்
4. செய்ய வேண்டிய சடங்குகள்
"""
        
        return self._generate(prompt)
    
    def answer_question(self, chart_data, question):
        """Answer any astrology question"""
        
        chart_info = ""
        if chart_data:
            chart_info = f"""ஜாதக விவரங்கள்:
{json.dumps(chart_data, ensure_ascii=False, indent=2)}
"""
        
        prompt = f"""{chart_info}
கேள்வி: {question}

இந்த கேள்விக்கு ஜோதிட சாஸ்திர அடிப்படையில் விரிவான பதில் அளிக்கவும்.
"""
        
        return self._generate(prompt)


# Test
if __name__ == "__main__":
    import os
    api_key = os.getenv("GEMINI_API_KEY", "AIzaSyAW47B8b0_I8oxZAjvbsRQQuYqDNMjAERI")
    
    if api_key:
        ai = TamilAstrologyGeminiAI(api_key)
        print("=== இன்றைய பலன் ===")
        result = ai.generate_daily_prediction("மேஷம்", "அஸ்வினி", "சுக்கிர தசா")
        print(result)
    else:
        print("GEMINI_API_KEY not set")
