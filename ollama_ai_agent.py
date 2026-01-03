# Tamil Vedic Astrology AI Agent with Ollama (Local, Free)
# Generates human-like predictions in pure Tamil

import requests
import json
from datetime import datetime

class TamilAstrologyOllamaAI:
    def __init__(self, model="llama3.2", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self):
        return """நீங்கள் ஒரு அனுபவமிக்க வேத ஜோதிடர். 40 ஆண்டுகளுக்கும் மேலான அனுபவம் கொண்டவர்.

உங்கள் பணி:
1. ஜாதக விவரங்களை ஆராய்ந்து துல்லியமான பலன்கள் சொல்ல வேண்டும்
2. தசா-புக்தி பலன்களை விளக்க வேண்டும்
3. பரிகாரங்கள் பரிந்துரைக்க வேண்டும்

முக்கிய விதிகள்:
- எப்போதும் தூய தமிழில் பதில் அளிக்கவும்
- நம்பிக்கையூட்டும் வகையில் பேசவும்
- எதிர்மறை பலன்களுக்கு பரிகாரம் சொல்லவும்

கிரக பலன்கள்:
- சூரியன்: தந்தை, அரசு, பதவி
- சந்திரன்: தாய், மனம்
- செவ்வாய்: சகோதரர், தைரியம்
- புதன்: கல்வி, வணிகம்
- குரு: ஞானம், செல்வம்
- சுக்கிரன்: காதல், கலை
- சனி: கர்மா, தாமதம்
- ராகு: திடீர் மாற்றம்
- கேது: ஆன்மீகம்"""

    def _generate(self, prompt):
        """Generate content using Ollama"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": self.system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 1024
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                raise Exception(f"Ollama error: {response.text}")
        except requests.exceptions.ConnectionError:
            raise Exception("Ollama server not running. Start with: ollama serve")
        except Exception as e:
            raise Exception(f"Ollama error: {str(e)}")

    def generate_prediction(self, chart_data, question_type, specific_question=None):
        """Generate prediction based on chart and question"""
        
        prompt = f"""ஜாதக விவரங்கள்:
{json.dumps(chart_data, ensure_ascii=False, indent=2)}

கேள்வி வகை: {question_type}
"""
        if specific_question:
            prompt += f"\nகுறிப்பிட்ட கேள்வி: {specific_question}"
        
        prompt += """

மேலே உள்ள ஜாதக விவரங்களை ஆராய்ந்து பலன் சொல்லுங்கள்:
1. ஜாதக சுருக்கம்
2. தற்போதைய தசா பலன்
3. கேள்விக்கான பதில்
4. பரிகாரங்கள்
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
2. தொழில்
3. பணம்
4. உடல்நலம்
5. அதிர்ஷ்ட நேரம்
6. அதிர்ஷ்ட எண்
7. அதிர்ஷ்ட நிறம்
"""
        
        return self._generate(prompt)
    
    def generate_compatibility_analysis(self, compatibility_data):
        """Generate detailed compatibility analysis"""
        
        prompt = f"""திருமண பொருத்த விவரங்கள்:
{json.dumps(compatibility_data, ensure_ascii=False, indent=2)}

பொருத்த பகுப்பாய்வு செய்யுங்கள்:
1. ஒவ்வொரு பொருத்தத்தின் விளக்கம்
2. நல்ல அம்சங்கள்
3. கவனிக்க வேண்டியவை
4. பரிகாரங்கள்
"""
        
        return self._generate(prompt)
    
    def calculate_muhurtham(self, purpose, preferred_dates=None):
        """Calculate auspicious time for an event"""
        
        prompt = f"""நிகழ்வு: {purpose}
விரும்பும் தேதிகள்: {preferred_dates if preferred_dates else 'எந்த தேதியும் சரி'}

சுப முகூர்த்தம் கணிக்கவும்:
1. சுப தேதிகள்
2. சுப நேரம்
3. தவிர்க்க வேண்டிய நாட்கள்
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

ஜோதிட அடிப்படையில் பதில் அளிக்கவும்.
"""
        
        return self._generate(prompt)


# Test
if __name__ == "__main__":
    ai = TamilAstrologyOllamaAI()
    print("=== இன்றைய பலன் ===")
    try:
        result = ai.generate_daily_prediction("மேஷம்", "அஸ்வினி", "சுக்கிர தசா")
        print(result)
    except Exception as e:
        print(f"Error: {e}")
