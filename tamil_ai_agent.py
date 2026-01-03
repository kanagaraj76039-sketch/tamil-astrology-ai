# Tamil Vedic Astrology AI Agent with Claude
# Generates human-like predictions in pure Tamil

import anthropic
import json
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, PLANETS_TAMIL, RASIS_TAMIL, NAKSHATRAS_TAMIL

class TamilAstrologyAI:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
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
- கேது: மோட்சம், ஆன்மீகம், விடுதலை

பாவ பலன்கள்:
- 1ம் பாவம்: உடல், ஆளுமை
- 2ம் பாவம்: குடும்பம், பணம், வாக்கு
- 3ம் பாவம்: சகோதரர், தைரியம்
- 4ம் பாவம்: தாய், வீடு, வாகனம்
- 5ம் பாவம்: குழந்தை, கல்வி, புத்தி
- 6ம் பாவம்: எதிரி, நோய், கடன்
- 7ம் பாவம்: திருமணம், கூட்டாளி
- 8ம் பாவம்: ஆயுள், மரணம், மறைவு
- 9ம் பாவம்: பாக்கியம், தந்தை, தர்மம்
- 10ம் பாவம்: தொழில், புகழ்
- 11ம் பாவம்: லாபம், மூத்த சகோதரர்
- 12ம் பாவம்: செலவு, வெளிநாடு, மோட்சம்

பரிகாரங்கள்:
- சூரியன்: ஆதித்ய ஹிருதயம், சிவப்பு பூ
- சந்திரன்: சந்திர நமஸ்காரம், வெள்ளை பூ
- செவ்வாய்: ஹனுமான் சாலிசா, சிவப்பு பழம்
- புதன்: விஷ்ணு சஹஸ்ரநாமம், பச்சை பழம்
- குரு: குரு ஸ்தோத்திரம், மஞ்சள் பூ
- சுக்கிரன்: லக்ஷ்மி ஸ்தோத்திரம், வெள்ளை பூ
- சனி: சனி ஸ்தோத்திரம், கருப்பு எள்
- ராகு: துர்கா ஸ்தோத்திரம், நீல பூ
- கேது: கணபதி ஸ்தோத்திரம், பழுப்பு நிற பூ"""

    def generate_prediction(self, chart_data, question_type, specific_question=None):
        """Generate prediction based on chart and question"""
        
        prompt = f"""
ஜாதக விவரங்கள்:
{json.dumps(chart_data, ensure_ascii=False, indent=2)}

கேள்வி வகை: {question_type}
"""
        if specific_question:
            prompt += f"\nகுறிப்பிட்ட கேள்வி: {specific_question}"
        
        prompt += """

மேலே உள்ள ஜாதக விவரங்களை ஆராய்ந்து, கிரக நிலைகள், தசா-புக்தி, கோசாரம் ஆகியவற்றின் அடிப்படையில் விரிவான பலன் சொல்லுங்கள்.

பதில் கட்டமைப்பு:
1. ஜாதக சுருக்கம்
2. தற்போதைய தசா-புக்தி பலன்
3. கேள்விக்கான பதில்
4. எதிர்காலம் (அடுத்த 1 வருடம்)
5. பரிகாரங்கள்
6. சுப நாட்கள்/நேரங்கள்
"""
        
        response = self.client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            system=self.system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def generate_daily_prediction(self, rasi, nakshatra, current_dasha):
        """Generate daily horoscope"""
        
        prompt = f"""
ராசி: {rasi}
நட்சத்திரம்: {nakshatra}
தற்போதைய தசா: {current_dasha}
இன்றைய தேதி: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}

இன்றைய ராசி பலன் சொல்லுங்கள். பின்வரும் அம்சங்களை உள்ளடக்கவும்:
1. பொது பலன்
2. தொழில்/வேலை
3. பணம்
4. உடல்நலம்
5. உறவுகள்
6. அதிர்ஷ்ட நேரம்
7. அதிர்ஷ்ட எண்
8. அதிர்ஷ்ட நிறம்
"""
        
        response = self.client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2048,
            system=self.system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def generate_compatibility_analysis(self, compatibility_data):
        """Generate detailed compatibility analysis"""
        
        prompt = f"""
திருமண பொருத்த விவரங்கள்:
{json.dumps(compatibility_data, ensure_ascii=False, indent=2)}

மேலே உள்ள பொருத்த விவரங்களை ஆராய்ந்து விரிவான பகுப்பாய்வு செய்யுங்கள்:
1. ஒவ்வொரு பொருத்தத்தின் விளக்கம்
2. நல்ல அம்சங்கள்
3. கவனிக்க வேண்டிய விஷயங்கள்
4. திருமண வாழ்க்கை எப்படி இருக்கும்
5. பரிகாரங்கள் (தேவைப்பட்டால்)
6. சுப முகூர்த்த பரிந்துரை
"""
        
        response = self.client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=3000,
            system=self.system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def calculate_muhurtham(self, purpose, preferred_dates=None):
        """Calculate auspicious time for an event"""
        
        prompt = f"""
நிகழ்வு: {purpose}
விரும்பும் தேதிகள்: {preferred_dates if preferred_dates else 'எந்த தேதியும் சரி'}

இந்த நிகழ்வுக்கு சுப முகூர்த்தம் கணிக்கவும்:
1. சுப தேதிகள் (அடுத்த 30 நாட்களில்)
2. சுப நேரம் (லக்னம்)
3. தவிர்க்க வேண்டிய நாட்கள்
4. முகூர்த்த விவரங்கள் (திதி, நட்சத்திரம், யோகம்)
5. செய்ய வேண்டிய சடங்குகள்
"""
        
        response = self.client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2048,
            system=self.system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def answer_question(self, chart_data, question):
        """Answer any astrology question"""
        
        prompt = f"""
ஜாதக விவரங்கள்:
{json.dumps(chart_data, ensure_ascii=False, indent=2)}

கேள்வி: {question}

இந்த கேள்விக்கு ஜோதிட சாஸ்திர அடிப்படையில் விரிவான பதில் அளிக்கவும். 
கிரக நிலைகள், தசா-புக்தி, கோசாரம் ஆகியவற்றை ஆதாரமாக காட்டவும்.
"""
        
        response = self.client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=3000,
            system=self.system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text


# Test
if __name__ == "__main__":
    ai = TamilAstrologyAI()
    
    # Test daily prediction
    print("=== இன்றைய பலன் ===")
    result = ai.generate_daily_prediction("மேஷம்", "அஸ்வினி", "சுக்கிர தசா")
    print(result)
