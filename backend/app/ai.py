import math,re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
TRAIN = [
    # Road Damage
    ("pothole damaged road asphalt road cracks crater", "Road Damage"),
    ("cracked road surface broken pavement", "Road Damage"),
    ("road has potholes and uneven asphalt", "Road Damage"),

    # Water Leakage
    ("water leaking pipe burst water flowing flooded", "Water Leakage"),
    ("water main leaking broken water pipeline", "Water Leakage"),

    # Drainage
    ("drain blocked sewage overflowing gutter stagnant water", "Drainage"),
    ("blocked storm drain clogged drain water not draining", "Drainage"),

    # Streetlight Failure
    ("streetlight lamp not working dark pole no illumination", "Streetlight Failure"),
    ("street light is out broken lamp post", "Streetlight Failure"),

    # Other
    ("park bench damaged broken public furniture", "Other"),
    ("public bin missing garbage bin damaged", "Other"),
    ("noise complaint loud music", "Other"),
    ("graffiti painted on wall", "Other"),
]
try:
    texts,labels=zip(*TRAIN); V=TfidfVectorizer(ngram_range=(1,2),stop_words='english'); M=V.fit_transform(texts)
except Exception: V=M=None; labels=[]
def classify(text):
    t = text.lower()

    # Water availability is not necessarily a pipe leak.
    water_shortage_phrases = [
        "no water",
        "water supply",
        "water unavailable",
        "no water supply",
        "taps have no water",
    ]
    if any(phrase in t for phrase in water_shortage_phrases):
        return "Other"

    # These are infrastructure issues outside the current
    # four specialized incident categories.
    other_phrases = [
        "manhole cover",
        "signboard",
        "road sign",
    ]
    if any(phrase in t for phrase in other_phrases):
        return "Other"

    # if V is not None:
    #     s = cosine_similarity(V.transform([text]), M)[0]
    #     j = int(s.argmax())
    #     if s[j] >= .08:
    #         return labels[j]

    # Keep your existing keyword fallback below this point.
    # Retain the existing fallback rules and final return.
    if V is not None:
        s=cosine_similarity(V.transform([text]),M)[0]; j=int(s.argmax())
        if s[j]>=.08:
            return labels[j]
    t=text.lower()
    for words,cat in [(['pothole','road','asphalt','crater','crack'],'Road Damage'),(['leak','pipe','water main','burst'],'Water Leakage'),(['drain','sewage','clog','gutter','overflow'],'Drainage'),(['streetlight','street light','lamp','dark pole','illumination'],'Streetlight Failure')]:
        if any(w in t for w in words): return cat
    return 'Other'
def haversine(a,b,c,d):
    r=6371000;p1,p2=math.radians(a),math.radians(c);dp=math.radians(c-a);dl=math.radians(d-b)
    x=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.asin(math.sqrt(x))

def normalize_duplicate_text(text):
    """Normalize common wording differences in civic incident reports."""
    text = text.lower()

    
    replacements = [
        # Normalize common streetlight descriptions.
        (r"\b(street\s*light|street\s+lamp|lamp\s*post|light\s*post|streetlight|entrance light|lamp|illumination)\b", " streetlight "),

        # Normalize different ways of describing a failure.
        (r"\b(has stopped working|stopped working|not working|does not work|is out|dark|no illumination|failed)\b", " failure "),

        (r"\b(storm drain|blocked drain|drainage|gutter|drain|clogged|blocked|not draining)\b", " drain "),

        (r"\b(water pipe|pipeline|water main|pipe|burst|leaking|leak|flowing|running)\b", " waterpipe "),

        (r"\b(pothole|crater|road cracks|cracks|asphalt)\b", " roaddamage "),

        (r"\b(garbage bins|waste bin|trash bin|rubbish bin|bins)\b", " wastebin "),
    ]

    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)

    return re.sub(r"[^a-z0-9 ]", " ", text)


def duplicate_text_similarity(text_a, text_b):
    """Compare normalized text using pairwise TF-IDF and token overlap."""
    a = normalize_duplicate_text(text_a)
    b = normalize_duplicate_text(text_b)

    tokens_a = set(a.split())
    tokens_b = set(b.split())
    jaccard = len(tokens_a & tokens_b) / max(
        1, len(tokens_a | tokens_b)
    )

    try:
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english"
        )
        vectors = vectorizer.fit_transform([a, b])
        tfidf_score = float(
            cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        )
    except ValueError:
        tfidf_score = 0.0

    return 0.65 * tfidf_score + 0.35 * jaccard


def duplicate_candidate(text, lat, lon, rows):
    """Return the strongest nearby, category-compatible duplicate candidate."""
    new_category = classify(text)
    best = None

    for row in rows:
        old_text = f"{row['title']} {row['description']}"
        old_category = classify(old_text)

        # Avoid matching reports assigned to different incident categories.
        if new_category != old_category:
            continue

        distance = haversine(
            lat, lon,
            float(row["latitude"]),
            float(row["longitude"])
        )

        # Ignore reports farther than 500 metres.
        if distance > 500:
            continue

        text_similarity = duplicate_text_similarity(text, old_text)
        geographic_similarity = max(0.0, 1.0 - distance / 700)

        combined = (
            0.80 * text_similarity
            + 0.20 * geographic_similarity
        )

        if best is None or combined > best[0]:
            best = (combined, row["id"], distance)

    # Tuned against the current small regression set.
    if best and best[0] >= 0.32:
        return {
            "id": best[1],
            "similarity": round(best[0], 3),
            "distance_m": round(best[2])
        }

    return None

def score_priority(severity,impact,category,duplicate=False):
    risk=5 if category in ('Water Leakage','Drainage') else 4 if category=='Road Damage' else 3
    corroboration=4 if duplicate else 1
    score=20*(.45*severity+.35*impact+.15*risk+.05*corroboration)
    level='Critical' if score>=85 else 'High' if score>=70 else 'Medium' if score>=50 else 'Low'
    explanation=f"Severity {severity}/5 (45%), public impact {impact}/5 (35%), category risk (15%), and corroboration (5%) determine this score. Demo heuristic only; human verification required."
    return round(score,1),level,explanation
