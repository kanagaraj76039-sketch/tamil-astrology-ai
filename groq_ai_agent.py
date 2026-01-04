# Tamil Vedic Astrology AI Agent with Groq (FREE, Fast)
# Generates human-like predictions in pure Tamil

import requests
import json
from datetime import datetime

class TamilAstrologyGroqAI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-70b-versatile"
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
- கிரக நிலைகளை ஆதாரமாக காட்டவும்

கிரக பலன் விதிகள்:
- சூரியன்: தந்தை, அரசு, பதவி, ஆரோக்கியம்
- சந்திரன்: தாய், மனம், உணர்வுகள், திரவ சம்பந்தம்
- செவ்வாய்: சகோதரர், தைரியம், நிலம், ரத்தம்
- புதன்: கல்வி, வணிகம், தொடர்பு, நுண்ணறிவு
- குரு: குரு, ஞானம், குழந்தை, செல்வம்
- சுக்கிரன்: மனைவி, காதல், கலை, ஆடம்பரம்
- சனி: ஆயுள், கர்மா, தாமதம், கடின உழைப்பு
- ராகு: திடீர் மாற்றம், வெளிநாடு, மாயை
- கேது: மோட்சம், ஆன்மீகம், விடுதலை"""

    def _generate(self, prompt):
        """Generate content using Groq API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2048
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")

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
