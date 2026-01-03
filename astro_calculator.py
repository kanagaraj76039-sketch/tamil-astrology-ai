# Vedic Astrology Calculator - Pure Python Implementation
# Calculates Rasi, Nakshatra, Dasha, Planetary Positions
# No external ephemeris library required

import math
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz
from config import (
    NAKSHATRAS_TAMIL, RASIS_TAMIL, PLANETS_TAMIL,
    DASHA_YEARS, DASHA_ORDER, NAKSHATRA_LORDS
)


class VedicAstroCalculator:
    """Pure Python Vedic Astrology Calculator"""
    
    # Lahiri Ayanamsa constants (approximate)
    AYANAMSA_BASE = 23.85  # Ayanamsa on Jan 1, 2000
    AYANAMSA_RATE = 50.29 / 3600  # degrees per year
    
    def __init__(self):
        self.geolocator = Nominatim(user_agent="tamil_astrology_ai")
        self.tf = TimezoneFinder()
    
    def get_location_coords(self, place_name):
        """Get latitude, longitude, timezone from place name"""
        try:
            location = self.geolocator.geocode(place_name)
            if location:
                lat = location.latitude
                lon = location.longitude
                tz_name = self.tf.timezone_at(lat=lat, lng=lon)
                return lat, lon, tz_name
        except Exception as e:
            print(f"Location error: {e}")
        return 13.0827, 80.2707, "Asia/Kolkata"  # Default: Chennai
    
    def datetime_to_jd(self, year, month, day, hour=0):
        """Convert date/time to Julian Day Number"""
        if month <= 2:
            year -= 1
            month += 12
        
        A = int(year / 100)
        B = 2 - A + int(A / 4)
        
        jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + hour/24.0 + B - 1524.5
        return jd
    
    def get_ayanamsa(self, jd):
        """Calculate Lahiri Ayanamsa for given Julian Day"""
        # Reference: Jan 1, 2000 = JD 2451545.0
        years_from_2000 = (jd - 2451545.0) / 365.25
        ayanamsa = self.AYANAMSA_BASE + (self.AYANAMSA_RATE * years_from_2000)
        return ayanamsa
    
    def calculate_sun_longitude(self, jd):
        """Calculate Sun's tropical longitude (simplified)"""
        # Days from J2000.0
        d = jd - 2451545.0
        
        # Mean longitude of the Sun
        L = (280.46646 + 0.9856474 * d) % 360
        
        # Mean anomaly of the Sun
        g = math.radians((357.52911 + 0.98560028 * d) % 360)
        
        # Equation of center
        C = 1.9148 * math.sin(g) + 0.02 * math.sin(2*g)
        
        # True longitude
        sun_lon = (L + C) % 360
        return sun_lon
    
    def calculate_moon_longitude(self, jd):
        """Calculate Moon's tropical longitude (simplified)"""
        d = jd - 2451545.0
        
        # Mean longitude of Moon
        L = (218.3165 + 13.176396 * d) % 360
        
        # Mean anomaly of Moon
        M = math.radians((134.9634 + 13.064993 * d) % 360)
        
        # Mean elongation
        D = math.radians((297.8502 + 12.190749 * d) % 360)
        
        # Argument of latitude
        F = math.radians((93.2721 + 13.229350 * d) % 360)
        
        # Corrections
        moon_lon = L + 6.289 * math.sin(M)
        moon_lon += 1.274 * math.sin(2*D - M)
        moon_lon += 0.658 * math.sin(2*D)
        moon_lon += 0.214 * math.sin(2*M)
        moon_lon -= 0.186 * math.sin(math.radians((134.9634 + 13.064993 * d) % 360))
        
        return moon_lon % 360
    
    def calculate_planet_longitude(self, jd, planet):
        """Calculate planetary longitude (simplified mean positions)"""
        d = jd - 2451545.0
        
        # Orbital elements (simplified)
        planets_data = {
            "Mars": {"L0": 355.433, "rate": 0.5240208},
            "Mercury": {"L0": 252.251, "rate": 4.0923344},
            "Jupiter": {"L0": 34.351, "rate": 0.0830853},
            "Venus": {"L0": 181.979, "rate": 1.6021302},
            "Saturn": {"L0": 50.077, "rate": 0.0334442}
        }
        
        if planet in planets_data:
            data = planets_data[planet]
            lon = (data["L0"] + data["rate"] * d) % 360
            return lon
        return 0
    
    def calculate_rahu_longitude(self, jd):
        """Calculate Rahu (Mean North Node) longitude"""
        d = jd - 2451545.0
        # Rahu moves retrograde
        rahu_lon = (125.0445 - 0.0529539 * d) % 360
        return rahu_lon
    
    def tropical_to_sidereal(self, tropical_lon, jd):
        """Convert tropical longitude to sidereal (Lahiri)"""
        ayanamsa = self.get_ayanamsa(jd)
        sidereal = (tropical_lon - ayanamsa) % 360
        return sidereal
    
    def longitude_to_rasi(self, longitude):
        """Convert longitude to Rasi (0-11)"""
        return int(longitude / 30) % 12
    
    def longitude_to_nakshatra(self, longitude):
        """Convert longitude to Nakshatra (0-26) and Pada (1-4)"""
        nakshatra_span = 360 / 27  # 13.333... degrees
        nakshatra = int(longitude / nakshatra_span) % 27
        pada = int((longitude % nakshatra_span) / (nakshatra_span / 4)) + 1
        return nakshatra, pada
    
    def calculate_lagna(self, jd, lat, lon):
        """Calculate Ascendant (Lagna)"""
        # Local Sidereal Time
        d = jd - 2451545.0
        gmst = (280.46061837 + 360.98564736629 * d) % 360
        lst = (gmst + lon) % 360
        
        # Obliquity of ecliptic
        eps = math.radians(23.4393 - 0.0000004 * d)
        
        # Ascendant calculation
        lst_rad = math.radians(lst)
        lat_rad = math.radians(lat)
        
        y = -math.cos(lst_rad)
        x = math.sin(lst_rad) * math.cos(eps) + math.tan(lat_rad) * math.sin(eps)
        
        asc = math.degrees(math.atan2(y, x)) % 360
        return asc
    
    def calculate_birth_chart(self, birth_date, birth_time, birth_place):
        """Calculate complete birth chart"""
        # Parse date and time
        dt_str = f"{birth_date} {birth_time}"
        birth_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        
        # Get location
        lat, lon, tz_name = self.get_location_coords(birth_place)
        
        # Convert to UTC
        tz = pytz.timezone(tz_name)
        local_dt = tz.localize(birth_dt)
        utc_dt = local_dt.astimezone(pytz.UTC)
        
        # Calculate Julian Day
        hour_decimal = utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0
        jd = self.datetime_to_jd(utc_dt.year, utc_dt.month, utc_dt.day, hour_decimal)
        
        # Calculate planetary positions
        chart = {
            "பிறந்த தேதி": birth_date,
            "பிறந்த நேரம்": birth_time,
            "பிறந்த இடம்": birth_place,
            "அட்சரேகை": round(lat, 4),
            "தீர்க்கரேகை": round(lon, 4),
            "கிரகங்கள்": {}
        }
        
        # Sun
        sun_trop = self.calculate_sun_longitude(jd)
        sun_sid = self.tropical_to_sidereal(sun_trop, jd)
        sun_rasi = self.longitude_to_rasi(sun_sid)
        sun_nak, sun_pada = self.longitude_to_nakshatra(sun_sid)
        chart["கிரகங்கள்"]["சூரியன்"] = {
            "ராசி": RASIS_TAMIL[sun_rasi],
            "நட்சத்திரம்": NAKSHATRAS_TAMIL[sun_nak],
            "பாதம்": sun_pada,
            "பாகை": round(sun_sid % 30, 2)
        }
        
        # Moon
        moon_trop = self.calculate_moon_longitude(jd)
        moon_sid = self.tropical_to_sidereal(moon_trop, jd)
        moon_rasi = self.longitude_to_rasi(moon_sid)
        moon_nak, moon_pada = self.longitude_to_nakshatra(moon_sid)
        chart["கிரகங்கள்"]["சந்திரன்"] = {
            "ராசி": RASIS_TAMIL[moon_rasi],
            "நட்சத்திரம்": NAKSHATRAS_TAMIL[moon_nak],
            "பாதம்": moon_pada,
            "பாகை": round(moon_sid % 30, 2)
        }
        
        # Other planets
        for planet_en, planet_ta in [("Mars", "செவ்வாய்"), ("Mercury", "புதன்"), 
                                      ("Jupiter", "குரு"), ("Venus", "சுக்கிரன்"), 
                                      ("Saturn", "சனி")]:
            planet_trop = self.calculate_planet_longitude(jd, planet_en)
            planet_sid = self.tropical_to_sidereal(planet_trop, jd)
            planet_rasi = self.longitude_to_rasi(planet_sid)
            planet_nak, planet_pada = self.longitude_to_nakshatra(planet_sid)
            chart["கிரகங்கள்"][planet_ta] = {
                "ராசி": RASIS_TAMIL[planet_rasi],
                "நட்சத்திரம்": NAKSHATRAS_TAMIL[planet_nak],
                "பாதம்": planet_pada,
                "பாகை": round(planet_sid % 30, 2)
            }
        
        # Rahu and Ketu
        rahu_trop = self.calculate_rahu_longitude(jd)
        rahu_sid = self.tropical_to_sidereal(rahu_trop, jd)
        rahu_rasi = self.longitude_to_rasi(rahu_sid)
        rahu_nak, rahu_pada = self.longitude_to_nakshatra(rahu_sid)
        chart["கிரகங்கள்"]["ராகு"] = {
            "ராசி": RASIS_TAMIL[rahu_rasi],
            "நட்சத்திரம்": NAKSHATRAS_TAMIL[rahu_nak],
            "பாதம்": rahu_pada,
            "பாகை": round(rahu_sid % 30, 2)
        }
        
        ketu_sid = (rahu_sid + 180) % 360
        ketu_rasi = self.longitude_to_rasi(ketu_sid)
        ketu_nak, ketu_pada = self.longitude_to_nakshatra(ketu_sid)
        chart["கிரகங்கள்"]["கேது"] = {
            "ராசி": RASIS_TAMIL[ketu_rasi],
            "நட்சத்திரம்": NAKSHATRAS_TAMIL[ketu_nak],
            "பாதம்": ketu_pada,
            "பாகை": round(ketu_sid % 30, 2)
        }
        
        # Lagna (Ascendant)
        lagna_trop = self.calculate_lagna(jd, lat, lon)
        lagna_sid = self.tropical_to_sidereal(lagna_trop, jd)
        lagna_rasi = self.longitude_to_rasi(lagna_sid)
        lagna_nak, lagna_pada = self.longitude_to_nakshatra(lagna_sid)
        chart["லக்னம்"] = {
            "ராசி": RASIS_TAMIL[lagna_rasi],
            "நட்சத்திரம்": NAKSHATRAS_TAMIL[lagna_nak],
            "பாதம்": lagna_pada
        }
        
        # Janma Nakshatra and Rasi (based on Moon)
        chart["ஜென்ம நட்சத்திரம்"] = NAKSHATRAS_TAMIL[moon_nak]
        chart["ராசி"] = RASIS_TAMIL[moon_rasi]
        
        # Calculate Dasha
        chart["தசா"] = self.calculate_dasha(birth_dt, moon_sid, tz_name)
        
        return chart
    
    def calculate_dasha(self, birth_dt, moon_longitude, tz_name):
        """Calculate Vimshottari Dasha periods with Bhukti"""
        nakshatra_span = 360 / 27
        nakshatra_index = int(moon_longitude / nakshatra_span) % 27
        
        # Position within nakshatra (0 to 1)
        position_in_nak = (moon_longitude % nakshatra_span) / nakshatra_span
        
        # Starting Dasha lord
        start_lord = NAKSHATRA_LORDS[nakshatra_index]
        start_index = DASHA_ORDER.index(start_lord)
        
        # Remaining portion of first dasha
        first_dasha_total = DASHA_YEARS[start_lord]
        first_dasha_remaining = first_dasha_total * (1 - position_in_nak)
        
        # Build dasha periods
        dasha_periods = []
        current_date = birth_dt
        
        # First (birth) dasha with bhukti
        end_date = current_date + timedelta(days=first_dasha_remaining * 365.25)
        first_dasha = {
            "தசா": PLANETS_TAMIL.get(start_lord, start_lord),
            "தசா_அதிபதி": start_lord,
            "தொடக்கம்": current_date.strftime("%Y-%m-%d"),
            "முடிவு": end_date.strftime("%Y-%m-%d"),
            "ஆண்டுகள்": round(first_dasha_remaining, 2),
            "புக்தி": self.calculate_bhukti(start_lord, current_date, first_dasha_remaining)
        }
        dasha_periods.append(first_dasha)
        current_date = end_date
        
        # Remaining dashas (complete cycle)
        for i in range(1, 9):
            lord_index = (start_index + i) % 9
            lord = DASHA_ORDER[lord_index]
            years = DASHA_YEARS[lord]
            end_date = current_date + timedelta(days=years * 365.25)
            
            dasha_periods.append({
                "தசா": PLANETS_TAMIL.get(lord, lord),
                "தசா_அதிபதி": lord,
                "தொடக்கம்": current_date.strftime("%Y-%m-%d"),
                "முடிவு": end_date.strftime("%Y-%m-%d"),
                "ஆண்டுகள்": years,
                "புக்தி": self.calculate_bhukti(lord, current_date, years)
            })
            current_date = end_date
        
        # Find current dasha and bhukti
        today = datetime.now()
        current_dasha = None
        current_bhukti = None
        
        for period in dasha_periods:
            start = datetime.strptime(period["தொடக்கம்"], "%Y-%m-%d")
            end = datetime.strptime(period["முடிவு"], "%Y-%m-%d")
            if start <= today <= end:
                current_dasha = {
                    "தசா": period["தசா"],
                    "தொடக்கம்": period["தொடக்கம்"],
                    "முடிவு": period["முடிவு"]
                }
                # Find current bhukti
                for bhukti in period["புக்தி"]:
                    b_start = datetime.strptime(bhukti["தொடக்கம்"], "%Y-%m-%d")
                    b_end = datetime.strptime(bhukti["முடிவு"], "%Y-%m-%d")
                    if b_start <= today <= b_end:
                        current_bhukti = bhukti
                        break
                break
        
        return {
            "அனைத்து_தசாக்கள்": dasha_periods,
            "தற்போதைய_தசா": current_dasha,
            "தற்போதைய_புக்தி": current_bhukti
        }
    
    def calculate_bhukti(self, dasha_lord, dasha_start, dasha_years):
        """Calculate Bhukti (Antardasha) periods within a Dasha"""
        bhukti_periods = []
        start_index = DASHA_ORDER.index(dasha_lord)
        current_date = dasha_start
        total_dasha_days = dasha_years * 365.25
        
        for i in range(9):
            bhukti_lord_index = (start_index + i) % 9
            bhukti_lord = DASHA_ORDER[bhukti_lord_index]
            
            # Bhukti duration = (Dasha years * Bhukti lord years) / 120
            bhukti_years = (dasha_years * DASHA_YEARS[bhukti_lord]) / 120
            bhukti_days = bhukti_years * 365.25
            
            end_date = current_date + timedelta(days=bhukti_days)
            
            bhukti_periods.append({
                "புக்தி": PLANETS_TAMIL.get(bhukti_lord, bhukti_lord),
                "புக்தி_அதிபதி": bhukti_lord,
                "தொடக்கம்": current_date.strftime("%Y-%m-%d"),
                "முடிவு": end_date.strftime("%Y-%m-%d"),
                "மாதங்கள்": round(bhukti_years * 12, 1),
                "நாட்கள்": round(bhukti_days)
            })
            current_date = end_date
        
        return bhukti_periods
    
    def get_jathaga_kattam(self, chart):
        """Generate South Indian style Jathaga Kattam (birth chart grid)"""
        # South Indian chart - fixed rasi positions
        # Grid layout (4x4 with center empty):
        #  மீனம் | மேஷம் | ரிஷபம் | மிதுனம்
        #  கும்பம்|       |       | கடகம்
        #  மகரம் |       |       | சிம்மம்
        #  தனுசு | விருச்சிகம் | துலாம் | கன்னி
        
        rasi_positions = {
            "மீனம்": (0, 0), "மேஷம்": (0, 1), "ரிஷபம்": (0, 2), "மிதுனம்": (0, 3),
            "கும்பம்": (1, 0), "கடகம்": (1, 3),
            "மகரம்": (2, 0), "சிம்மம்": (2, 3),
            "தனுசு": (3, 0), "விருச்சிகம்": (3, 1), "துலாம்": (3, 2), "கன்னி": (3, 3)
        }
        
        # Initialize grid
        grid = [[[] for _ in range(4)] for _ in range(4)]
        
        # Planet abbreviations
        planet_abbrev = {
            "சூரியன்": "சூ", "சந்திரன்": "ச", "செவ்வாய்": "செ",
            "புதன்": "பு", "குரு": "கு", "சுக்கிரன்": "சு",
            "சனி": "சனி", "ராகு": "ரா", "கேது": "கே"
        }
        
        # Place planets in grid
        for planet, data in chart["கிரகங்கள்"].items():
            rasi = data["ராசி"]
            if rasi in rasi_positions:
                row, col = rasi_positions[rasi]
                abbrev = planet_abbrev.get(planet, planet[:2])
                grid[row][col].append(f"{abbrev}")
        
        # Place Lagna
        lagna_rasi = chart["லக்னம்"]["ராசி"]
        if lagna_rasi in rasi_positions:
            row, col = rasi_positions[lagna_rasi]
            grid[row][col].insert(0, "லக்")
        
        # Create kattam structure
        kattam = {
            "வடிவம்": "தென்னிந்திய",
            "கட்டம்": [],
            "ராசி_கிரகங்கள்": {}
        }
        
        # Build display grid
        rasi_order = [
            ["மீனம்", "மேஷம்", "ரிஷபம்", "மிதுனம்"],
            ["கும்பம்", "", "", "கடகம்"],
            ["மகரம்", "", "", "சிம்மம்"],
            ["தனுசு", "விருச்சிகம்", "துலாம்", "கன்னி"]
        ]
        
        for i, row in enumerate(rasi_order):
            kattam_row = []
            for j, rasi in enumerate(row):
                if rasi:
                    planets_in_rasi = grid[i][j]
                    kattam_row.append({
                        "ராசி": rasi,
                        "கிரகங்கள்": planets_in_rasi
                    })
                    kattam["ராசி_கிரகங்கள்"][rasi] = planets_in_rasi
                else:
                    kattam_row.append({"ராசி": "", "கிரகங்கள்": []})
            kattam["கட்டம்"].append(kattam_row)
        
        return kattam
    
    def calculate_compatibility(self, person1_data, person2_data):
        """Calculate marriage compatibility (Porutham)"""
        chart1 = self.calculate_birth_chart(
            person1_data["date"], person1_data["time"], person1_data["place"]
        )
        chart2 = self.calculate_birth_chart(
            person2_data["date"], person2_data["time"], person2_data["place"]
        )
        
        # Get nakshatra indices
        nak1_name = chart1["ஜென்ம நட்சத்திரம்"]
        nak2_name = chart2["ஜென்ம நட்சத்திரம்"]
        nak1_idx = NAKSHATRAS_TAMIL.index(nak1_name)
        nak2_idx = NAKSHATRAS_TAMIL.index(nak2_name)
        
        # Get rasi indices
        rasi1_name = chart1["ராசி"]
        rasi2_name = chart2["ராசி"]
        rasi1_idx = RASIS_TAMIL.index(rasi1_name)
        rasi2_idx = RASIS_TAMIL.index(rasi2_name)
        
        poruthams = {}
        
        # 1. Dina Porutham (Nakshatra count)
        dina_count = (nak2_idx - nak1_idx) % 27 + 1
        dina_good = dina_count not in [2, 4, 6, 8, 9, 11, 13, 15, 18, 20, 22, 24, 26]
        poruthams["தின பொருத்தம்"] = {"பொருத்தம்": dina_good, "மதிப்பு": 1 if dina_good else 0}
        
        # 2. Gana Porutham
        gana_groups = {
            "தேவ": [0, 4, 6, 7, 12, 16, 21, 26],
            "மனித": [1, 3, 5, 10, 11, 19, 20, 24, 25],
            "அசுர": [2, 8, 9, 13, 14, 15, 17, 18, 22, 23]
        }
        gana1 = gana2 = None
        for gana, naks in gana_groups.items():
            if nak1_idx in naks:
                gana1 = gana
            if nak2_idx in naks:
                gana2 = gana
        gana_good = (gana1 == gana2) or (gana1 == "தேவ") or (gana2 == "தேவ")
        poruthams["கண பொருத்தம்"] = {"பொருத்தம்": gana_good, "மதிப்பு": 1 if gana_good else 0}
        
        # 3. Rasi Porutham
        rasi_diff = (rasi2_idx - rasi1_idx) % 12
        rasi_good = rasi_diff in [1, 2, 3, 4, 5, 7, 9, 11]
        poruthams["ராசி பொருத்தம்"] = {"பொருத்தம்": rasi_good, "மதிப்பு": 1 if rasi_good else 0}
        
        # 4. Yoni Porutham
        yoni_good = abs(nak1_idx - nak2_idx) % 2 == 0
        poruthams["யோனி பொருத்தம்"] = {"பொருத்தம்": yoni_good, "மதிப்பு": 1 if yoni_good else 0}
        
        # 5. Rajju Porutham
        rajju_groups = [[0,5,6,11,12,17,18,23,24], [1,4,7,10,13,16,19,22,25], [2,3,8,9,14,15,20,21,26]]
        rajju1 = rajju2 = 0
        for i, group in enumerate(rajju_groups):
            if nak1_idx in group:
                rajju1 = i
            if nak2_idx in group:
                rajju2 = i
        rajju_good = rajju1 != rajju2
        poruthams["ரஜ்ஜு பொருத்தம்"] = {"பொருத்தம்": rajju_good, "மதிப்பு": 1 if rajju_good else 0}
        
        # 6. Vedha Porutham
        vedha_good = abs(nak1_idx - nak2_idx) not in [1, 3, 5, 7]
        poruthams["வேதை பொருத்தம்"] = {"பொருத்தம்": vedha_good, "மதிப்பு": 1 if vedha_good else 0}
        
        # 7. Vasya Porutham
        vasya_good = rasi_diff in [2, 5, 6, 8, 9]
        poruthams["வசிய பொருத்தம்"] = {"பொருத்தம்": vasya_good, "மதிப்பு": 1 if vasya_good else 0}
        
        # 8. Mahendra Porutham
        mahendra_count = (nak2_idx - nak1_idx) % 27 + 1
        mahendra_good = mahendra_count in [4, 7, 10, 13, 16, 19, 22, 25]
        poruthams["மகேந்திர பொருத்தம்"] = {"பொருத்தம்": mahendra_good, "மதிப்பு": 1 if mahendra_good else 0}
        
        # 9. Stree Deergha Porutham
        stree_count = (nak2_idx - nak1_idx) % 27 + 1
        stree_good = stree_count >= 13
        poruthams["ஸ்திரீ தீர்க்க பொருத்தம்"] = {"பொருத்தம்": stree_good, "மதிப்பு": 1 if stree_good else 0}
        
        # 10. Nadi Porutham
        nadi_groups = [[0,3,6,9,12,15,18,21,24], [1,4,7,10,13,16,19,22,25], [2,5,8,11,14,17,20,23,26]]
        nadi1 = nadi2 = 0
        for i, group in enumerate(nadi_groups):
            if nak1_idx in group:
                nadi1 = i
            if nak2_idx in group:
                nadi2 = i
        nadi_good = nadi1 != nadi2
        poruthams["நாடி பொருத்தம்"] = {"பொருத்தம்": nadi_good, "மதிப்பு": 1 if nadi_good else 0}
        
        # Total score
        total = sum(p["மதிப்பு"] for p in poruthams.values())
        
        return {
            "நபர்1": {"நட்சத்திரம்": nak1_name, "ராசி": rasi1_name},
            "நபர்2": {"நட்சத்திரம்": nak2_name, "ராசி": rasi2_name},
            "பொருத்தங்கள்": poruthams,
            "மொத்த_மதிப்பு": f"{total}/10",
            "பரிந்துரை": "மிகச்சிறந்த பொருத்தம்" if total >= 8 else "நல்ல பொருத்தம்" if total >= 6 else "சாதாரண பொருத்தம்" if total >= 4 else "குறைவான பொருத்தம்"
        }
    
    def get_current_transits(self):
        """Get current planetary transits"""
        now = datetime.now()
        utc_now = now.astimezone(pytz.UTC) if now.tzinfo else pytz.UTC.localize(now)
        
        hour_decimal = utc_now.hour + utc_now.minute/60.0
        jd = self.datetime_to_jd(utc_now.year, utc_now.month, utc_now.day, hour_decimal)
        
        transits = {"தேதி": now.strftime("%Y-%m-%d %H:%M"), "கோசாரம்": {}}
        
        # Sun
        sun_sid = self.tropical_to_sidereal(self.calculate_sun_longitude(jd), jd)
        transits["கோசாரம்"]["சூரியன்"] = {
            "ராசி": RASIS_TAMIL[self.longitude_to_rasi(sun_sid)],
            "நட்சத்திரம்": NAKSHATRAS_TAMIL[self.longitude_to_nakshatra(sun_sid)[0]]
        }
        
        # Moon
        moon_sid = self.tropical_to_sidereal(self.calculate_moon_longitude(jd), jd)
        transits["கோசாரம்"]["சந்திரன்"] = {
            "ராசி": RASIS_TAMIL[self.longitude_to_rasi(moon_sid)],
            "நட்சத்திரம்": NAKSHATRAS_TAMIL[self.longitude_to_nakshatra(moon_sid)[0]]
        }
        
        # Other planets
        for planet_en, planet_ta in [("Mars", "செவ்வாய்"), ("Mercury", "புதன்"), 
                                      ("Jupiter", "குரு"), ("Venus", "சுக்கிரன்"), 
                                      ("Saturn", "சனி")]:
            planet_sid = self.tropical_to_sidereal(self.calculate_planet_longitude(jd, planet_en), jd)
            transits["கோசாரம்"][planet_ta] = {
                "ராசி": RASIS_TAMIL[self.longitude_to_rasi(planet_sid)],
                "நட்சத்திரம்": NAKSHATRAS_TAMIL[self.longitude_to_nakshatra(planet_sid)[0]]
            }
        
        # Rahu/Ketu
        rahu_sid = self.tropical_to_sidereal(self.calculate_rahu_longitude(jd), jd)
        transits["கோசாரம்"]["ராகு"] = {
            "ராசி": RASIS_TAMIL[self.longitude_to_rasi(rahu_sid)],
            "நட்சத்திரம்": NAKSHATRAS_TAMIL[self.longitude_to_nakshatra(rahu_sid)[0]]
        }
        ketu_sid = (rahu_sid + 180) % 360
        transits["கோசாரம்"]["கேது"] = {
            "ராசி": RASIS_TAMIL[self.longitude_to_rasi(ketu_sid)],
            "நட்சத்திரம்": NAKSHATRAS_TAMIL[self.longitude_to_nakshatra(ketu_sid)[0]]
        }
        
        return transits


# Test
if __name__ == "__main__":
    calc = VedicAstroCalculator()
    
    print("=== ஜாதகம் கணிப்பு ===")
    chart = calc.calculate_birth_chart("1990-05-15", "10:30", "Chennai")
    
    print(f"\nபிறந்த தேதி: {chart['பிறந்த தேதி']}")
    print(f"பிறந்த நேரம்: {chart['பிறந்த நேரம்']}")
    print(f"பிறந்த இடம்: {chart['பிறந்த இடம்']}")
    print(f"\nராசி: {chart['ராசி']}")
    print(f"ஜென்ம நட்சத்திரம்: {chart['ஜென்ம நட்சத்திரம்']}")
    print(f"லக்னம்: {chart['லக்னம்']['ராசி']}")
    
    print("\n=== கிரக நிலைகள் ===")
    for planet, data in chart['கிரகங்கள்'].items():
        print(f"{planet}: {data['ராசி']} - {data['நட்சத்திரம்']} பாதம் {data['பாதம்']}")
    
    if chart['தசா']['தற்போதைய_தசா']:
        print(f"\n=== தற்போதைய தசா ===")
        dasha = chart['தசா']['தற்போதைய_தசா']
        print(f"{dasha['தசா']} தசா: {dasha['தொடக்கம்']} முதல் {dasha['முடிவு']} வரை")
