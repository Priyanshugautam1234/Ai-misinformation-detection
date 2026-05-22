import re
import math
from typing import Dict, Any, List

# Simple dictionary-based classifier for demo and offline robust use
CLICKBAIT_KEYWORDS = [
    r"shocking", r"you won\'t believe", r"miracle cure", r"secret they won\'t",
    r"exposed", r"revealed", r"conspiracy", r"hidden truth", r"instant weight loss",
    r"make \$[0-9]+", r"secret trick", r"mind-blowing", r"what happened next will",
    r"scientists are quiet", r"doctor\'s warning", r"absolutely mental", r"going viral",
    r"this is why", r"will change your life", r"unbelievable", r"guaranteed success"
]

BIAS_LEFT_KEYWORDS = [
    r"systemic", r"corporate greed", r"progressive", r"oligarchs", r"marginalized",
    r"wealth gap", r"climate crisis", r"far-right extremism", r"redistribution", r"social justice"
]

BIAS_RIGHT_KEYWORDS = [
    r"woke agenda", r"deep state", r"socialist tyranny", r"border crisis", r"traditional values",
    r"liberty", r"tax theft", r"bureaucrats", r"patriot", r"mainstream media bias"
]

SENSATIONAL_PUNCTUATION_RE = re.compile(r"[\!\?\*]{2,}")
ALL_CAPS_RE = re.compile(r"\b[A-Z]{4,}\b")

# Sample database of known claim facts for simulated verification
FACT_CHECK_DATABASE = [
    {
        "keywords": ["covid", "vaccine", "microchip", "5g"],
        "claim": "COVID-19 vaccines contain 5G microchips for trackability.",
        "verdict": "FALSE / DEBUNKED",
        "explanation": "Extensive laboratory analysis and public medical records confirm vaccines do not contain electronic materials. 5G signals are radio waves and cannot interact with biological compounds in this manner.",
        "source": "World Health Organization (WHO), CDC",
        "confidence": 0.99
    },
    {
        "keywords": ["climate", "fake", "co2", "volcano"],
        "claim": "Volcanoes emit more carbon dioxide annually than human industry.",
        "verdict": "FALSE",
        "explanation": "According to the USGS, human activities emit roughly 60 to 100 times more CO2 than all global volcanic activity combined.",
        "source": "US Geological Survey (USGS), NASA",
        "confidence": 0.95
    },
    {
        "keywords": ["eating", "spiders", "sleep", "eight"],
        "claim": "Humans swallow an average of eight spiders per year in their sleep.",
        "verdict": "FALSE / MYTH",
        "explanation": "Spiders do not intentionally enter human mouths; the sleeping human body's vibrations (heartbeat, breathing) are frightening to spiders, which actively avoid humans.",
        "source": "Encyclopedia Britannica, Arachnology Society",
        "confidence": 0.92
    },
    {
        "keywords": ["banana", "hiv", "inject", "blood"],
        "claim": "Bananas in supermarkets are being injected with HIV-positive blood.",
        "verdict": "FALSE / HOAX",
        "explanation": "This viral social media claim is physically and biologically impossible. The HIV virus cannot survive outside the human host body long enough to infect consumers through fruit.",
        "source": "US Food and Drug Administration (FDA)",
        "confidence": 0.99
    }
]

def analyze_text(text: str) -> Dict[str, Any]:
    if not text or len(text.strip()) < 10:
        return {
            "success": False,
            "error": "Input text is too short. Please enter at least 10 characters."
        }

    text_lower = text.lower()
    
    # 1. Clickbait & Sensationalism Scoring
    clickbait_matches = []
    for kw in CLICKBAIT_KEYWORDS:
        matches = re.findall(kw, text_lower)
        if matches:
            clickbait_matches.append(kw)
            
    punc_matches = SENSATIONAL_PUNCTUATION_RE.findall(text)
    caps_matches = ALL_CAPS_RE.findall(text)
    
    # Calculate clickbait probability
    clickbait_score = 0
    if clickbait_matches:
        clickbait_score += min(len(clickbait_matches) * 20, 60)
    if punc_matches:
        clickbait_score += min(len(punc_matches) * 15, 30)
    if caps_matches:
        clickbait_score += min(len(caps_matches) * 10, 20)
        
    clickbait_score = min(clickbait_score, 100)
    
    # 2. Political Bias Analysis
    left_count = sum(len(re.findall(kw, text_lower)) for kw in BIAS_LEFT_KEYWORDS)
    right_count = sum(len(re.findall(kw, text_lower)) for kw in BIAS_RIGHT_KEYWORDS)
    
    bias_score = 50  # 0 is far Left, 50 is Neutral, 100 is far Right
    if left_count > 0 or right_count > 0:
        total_bias = left_count + right_count
        ratio = (right_count - left_count) / total_bias  # Range -1.0 to 1.0
        bias_score = int(50 + (ratio * 40))  # Scale to 10 - 90
        
    bias_label = "Neutral"
    if bias_score < 35:
        bias_label = "Left-Leaning" if bias_score >= 20 else "Left-Wing"
    elif bias_score > 65:
        bias_label = "Right-Leaning" if bias_score <= 80 else "Right-Wing"
        
    # 3. Sentiment & Emotional Intensity (Rage-bait check)
    # Simple word counting for emotional words
    rage_words = ["outrage", "disgrace", "infuriating", "destroying", "betrayal", "treason", "evil", "liars", "corrupt", "illegal"]
    rage_count = sum(len(re.findall(w, text_lower)) for w in rage_words)
    emotional_intensity = min(rage_count * 20, 100)
    
    # 4. Simulated Claim Matching / Fact-Checking
    matched_claims = []
    factuality_rating = "HIGH"
    factuality_numeric = 95
    
    for item in FACT_CHECK_DATABASE:
        matches = [kw for kw in item["keywords"] if kw in text_lower]
        # If at least two keywords match, we flag it
        if len(matches) >= 2:
            matched_claims.append({
                "claim": item["claim"],
                "verdict": item["verdict"],
                "explanation": item["explanation"],
                "source": item["source"],
                "confidence": item["confidence"]
            })
            # A flagged false claim drops factuality significantly
            factuality_rating = "LOW"
            factuality_numeric = min(factuality_numeric, 15)

    if not matched_claims and clickbait_score > 40:
        # If no hard debunked claim, but lots of clickbait/sensationalism
        factuality_rating = "MIXED"
        factuality_numeric = 60 - int(clickbait_score / 3)

    # 5. Overarching Trust Score Calculation (0 to 100)
    # High clickbait, high bias, high emotional intensity and low factuality reduce this score.
    bias_penalty = abs(bias_score - 50) * 0.4  # Max penalty 20
    clickbait_penalty = clickbait_score * 0.3  # Max penalty 30
    rage_penalty = emotional_intensity * 0.2    # Max penalty 20
    
    base_score = factuality_numeric
    if not matched_claims:
        base_score = 100 - (bias_penalty + clickbait_penalty + rage_penalty)
        
    trust_score = max(0, min(100, int(base_score)))
    
    # Language anomalies to display in frontend highlights
    highlights = []
    if caps_matches:
        highlights.append({
            "type": "sensational",
            "text": ", ".join(caps_matches[:3]),
            "description": "Excessive capitalization signals urgency or manufactured outrage."
        })
    if clickbait_matches:
        highlights.append({
            "type": "clickbait",
            "text": ", ".join([w.replace("\\", "") for w in clickbait_matches[:3]]),
            "description": "Sensationalized clickbait keywords commonly found in viral misinformation."
        })
    if rage_count > 0:
        highlights.append({
            "type": "ragebait",
            "text": "Highly emotional vocabulary detected",
            "description": "Rage-inducing language designed to bypass rational skepticism."
        })

    return {
        "success": True,
        "trust_score": trust_score,
        "metrics": {
            "clickbait_score": clickbait_score,
            "bias_score": bias_score,
            "bias_label": bias_label,
            "emotional_intensity": emotional_intensity,
            "factuality_rating": factuality_rating
        },
        "debunked_claims": matched_claims,
        "highlights": highlights,
        "char_count": len(text),
        "word_count": len(text.split())
    }
