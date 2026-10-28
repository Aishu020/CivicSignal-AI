"""Small, deterministic smoke evaluation for CivicSignal AI's current baseline.

Run from the backend folder:
    python evaluate_baseline.py

This is a hand-authored development set, not a representative benchmark.
"""
from app.ai import classify, duplicate_candidate, score_priority
from app.ai import duplicate_text_similarity
from app.ai import classify, duplicate_text_similarity

a = "Street lamp is dark beside the school"
b = "The school entrance light has stopped working"

print("Streetlight A category:", classify(a))
print("Streetlight B category:", classify(b))
print("Streetlight text similarity:", duplicate_text_similarity(a, b))


print(
    "Streetlight text similarity:",
    duplicate_text_similarity(
        "Street lamp is dark beside the school",
        "The school entrance light has stopped working",
    ),
)

CASES = [
    ("Pothole on the road", "A deep pothole has damaged the asphalt near the junction.", "Road Damage"),
    ("Cracked road surface", "Several large cracks and a crater are visible in the street.", "Road Damage"),
    ("Burst water pipe", "Clean water is flowing continuously from a broken pipeline.", "Water Leakage"),
    ("Water main leaking", "A pipe has burst and water is flooding the roadside.", "Water Leakage"),
    ("Blocked storm drain", "The drain is clogged and rainwater cannot flow away.", "Drainage"),
    ("Sewage overflowing", "Sewage is backing up from the gutter and stagnant water is accumulating.", "Drainage"),
    ("Street light is out", "The streetlight lamp is not working and the road is dark at night.", "Streetlight Failure"),
    ("Dark street corner", "No illumination from the lamp post makes this corner difficult to see.", "Streetlight Failure"),
    ("Park bench damaged", "A bench in the public park has a broken wooden seat.", "Other"),
    ("Public bin missing", "The waste bin has disappeared from the park entrance.", "Other"),
    ("Noise complaint", "Loud construction noise continues late at night.", "Other"),
    ("Graffiti on wall", "Painted graffiti has appeared on the wall beside the library.", "Other"),
        # Additional wording and ambiguity tests
    ("Lamp flickering", "The lamp post keeps flickering and the street is poorly lit.", "Streetlight Failure"),
    ("Pipe dripping", "A water pipe is dripping continuously beside the footpath.", "Water Leakage"),
    ("Drain smells bad", "There is a foul smell coming from the roadside drain.", "Drainage"),
    ("Water covering road", "Rainwater is collecting because the roadside gutter is blocked.", "Drainage"),
    ("Uneven pavement", "The asphalt surface is broken and vehicles are swerving around it.", "Road Damage"),
    ("Broken park bench", "The wooden seat in the public garden has snapped.", "Other"),
    ("Missing manhole cover", "A manhole cover has disappeared from the pavement.", "Other"),
    ("Overflowing rubbish", "Waste is spilling out of a public garbage container.", "Other"),
    ("Damaged signboard", "A road sign has been bent and damaged by a vehicle.", "Other"),
    ("Fallen tree branch", "A large tree branch has fallen beside the footpath.", "Other"),
    ("Water supply complaint", "Residents report that their taps have no water today.", "Other"),
    ("Roadside lamp outage", "The lamp beside the bus shelter no longer lights up.", "Streetlight Failure"),
]

# Each item: query text, candidate text, distance in meters, should_be_duplicate.
# Coordinates are converted into a short north/south offset at Coimbatore latitude.
DUPLICATE_CASES = [
    ("Water pipe leaking near bus stop; water flowing onto road", "Broken pipeline beside bus stop; water running onto the street", 35, True),
    ("Large pothole near market entrance", "Deep pothole at the market entrance damaging vehicles", 50, True),
    ("Streetlight not working outside school", "Lamp post is dark near the school gate", 80, True),
    ("Blocked drain with stagnant water", "Gutter clogged and water is not draining", 60, True),
    ("Water pipe leaking near bus stop", "Streetlight not working near the school", 40, False),
    ("Large pothole near market entrance", "Garbage bins overflowing beside the park", 45, False),
    ("Blocked drain with stagnant water", "A bench is broken in the public park", 55, False),
    ("Streetlight not working outside school", "Water pipe burst near the market", 75, False),
        # Additional wording and geographic-distance tests
    ("Street lamp is dark beside the school",
     "The school entrance light has stopped working", 90, True),

    ("Rainwater trapped in blocked gutter",
     "Water is standing because the roadside drain is clogged", 75, True),

    ("Pipe burst and flooding near the clinic",
     "A broken water pipeline is flooding the clinic road", 110, True),

    ("Deep crater in asphalt near the crossing",
     "A large pothole is damaging vehicles at the crossing", 65, True),

    # Similar words, but different incidents
    ("Water pipe leaking beside the school",
     "Streetlight not working beside the school", 40, False),

    ("Blocked drain outside the market",
     "Broken park bench outside the market", 35, False),

    # Same wording, but beyond the configured 500 m search radius
    ("Water pipe leaking near the bus stop",
     "Water pipe leaking near the bus stop", 650, False),

    ("Streetlight not working near the school",
     "Streetlight not working near the school", 800, False),
]


def run_classification():
    correct = 0
    print("CLASSIFICATION")
    for title, description, expected in CASES:
        predicted = classify(f"{title}. {description}")
        ok = predicted == expected
        correct += int(ok)
        print(f"{'PASS' if ok else 'FAIL'} | expected={expected:<20} predicted={predicted:<20} | {title}")
    total = len(CASES)
    print(f"Classification accuracy: {correct}/{total} = {correct / total:.1%}\n")
    return correct, total


def run_duplicates():
    tp = fp = fn = tn = 0
    print("DUPLICATE DETECTION")
    # A local latitude degree is approximately 111,000 m. At this latitude,
    # longitude distance is scaled by cosine(latitude).
    import math
    lat0, lon0 = 11.0183, 76.9675
    for i, (query, candidate, distance_m, expected) in enumerate(DUPLICATE_CASES, start=1):
        candidate_row = {
            "id": i,
            "title": candidate,
            "description": "",
            "latitude": lat0 + distance_m / 111000,
            "longitude": lon0,
        }
        result = duplicate_candidate(query, lat0, lon0, [candidate_row])
        predicted = result is not None
        if predicted and expected: tp += 1
        elif predicted and not expected: fp += 1
        elif not predicted and expected: fn += 1
        else: tn += 1
        print(f"{'PASS' if predicted == expected else 'FAIL'} | expected_duplicate={expected!s:<5} predicted_duplicate={predicted!s:<5} | pair {i}")
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    print(f"Confusion counts: TP={tp}, FP={fp}, FN={fn}, TN={tn}")
    print(f"Precision={precision:.1%} | Recall={recall:.1%} | F1={f1:.1%}\n")
    return tp, fp, fn, tn


def run_priority_sanity_check():
    low = score_priority(1, 1, "Other")[0]
    high = score_priority(5, 5, "Water Leakage")[0]
    ok = high > low
    print("PRIORITY SANITY CHECK")
    print(f"{'PASS' if ok else 'FAIL'} | low-risk sample={low:.1f}, high-risk sample={high:.1f}")
    return ok


if __name__ == "__main__":
    run_classification()
    run_duplicates()
    run_priority_sanity_check()
    print("Note: This tiny hand-authored set is for regression testing only. Do not report it as real-world model performance.")
