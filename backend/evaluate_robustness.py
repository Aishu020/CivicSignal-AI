
from app.ai import classify, duplicate_candidate

# CivicSignal AI — Robustness Evaluation
# These examples are separate from the original regression tests.
# They are hand-authored challenge cases, not real-world data.

CLASSIFICATION_CASES = [
    ("Large pothole near the bus stop", "Road Damage"),
    ("The street surface is broken and uneven", "Road Damage"),
    ("Water is leaking from a broken main pipe", "Water Leakage"),
    ("Pipe burst and water is running onto the road", "Water Leakage"),
    ("Storm drain is clogged after the rain", "Drainage"),
    ("Sewage is spilling out of the gutter", "Drainage"),
    ("Street lamp is dark after sunset", "Streetlight Failure"),
    ("The lamp post has stopped working", "Streetlight Failure"),
    ("There is no water supply in our area", "Other"),
    ("Someone damaged the bench in the park", "Other"),
    ("A road sign has fallen down", "Other"),
    ("Loud music from a nearby building", "Other"),
    # Noisy inputs: these may expose limitations in the current baseline.
    ("Pothol on the road near school", "Road Damage"),
    ("Street lite not working", "Streetlight Failure"),
    ("Water piple is leaking", "Water Leakage"),
    ("Dran is blocked", "Drainage"),
]

# Each tuple: new report, existing report, expected duplicate?
# All reports are placed at the same coordinates to test text matching.
DUPLICATE_CASES = [
    (
        "Large pothole near the bus stop",
        "A big crater in the road by the bus stop",
        True,
    ),
    (
        "Street lamp is dark beside the school",
        "The school entrance light has stopped working",
        True,
    ),
    (
        "Water leaking from a broken pipe",
        "A pipe is leaking water onto the street",
        True,
    ),
    (
        "Storm drain is clogged",
        "The drain is blocked and water cannot flow",
        True,
    ),
    (
        "Pothole on the road",
        "Streetlight is not working",
        False,
    ),
    (
        "Water pipe is leaking",
        "Public park bench is broken",
        False,
    ),
    (
        "Blocked drain near the market",
        "Water main has burst near the market",
        False,
    ),
    (
        "Streetlight is out near the school",
        "Streetlight is out near the school",
        True,
    ),
    (
        "A pothole is damaging the road",
        "Road surface has a pothole",
        True,
    ),
    (
        "Noise complaint about loud music",
        "Graffiti painted on a public wall",
        False,
    ),
    (
        "Water supply is unavailable",
        "A water pipe is leaking",
        False,
    ),
    (
        "A broken bench in the park",
        "A missing public rubbish bin",
        False,
    ),
]

def run_classification_tests():
    print("\n=== UNSEEN CLASSIFICATION TESTS ===")
    passed = 0

    for i, (text, expected) in enumerate(CLASSIFICATION_CASES, 1):
        predicted = classify(text)
        ok = predicted == expected
        passed += int(ok)
        print(
            f"{'PASS' if ok else 'FAIL'} | "
            f"expected={expected:<22} predicted={predicted:<22} | {text}"
        )

    total = len(CLASSIFICATION_CASES)
    print(f"Classification: {passed}/{total} ({passed / total:.1%})")
    return passed, total

def run_duplicate_tests():
    print("\n=== UNSEEN DUPLICATE TESTS ===")
    passed = 0
    tp = fp = fn = tn = 0

    for i, (new_text, old_text, expected) in enumerate(DUPLICATE_CASES, 1):
        # Reports are intentionally close together geographically.
        rows = [{
            "id": i,
            "title": old_text,
            "description": "",
            "latitude": 11.0168,
            "longitude": 76.9558,
        }]

        result = duplicate_candidate(
            new_text, 11.0169, 76.9559, rows
        )
        predicted = result is not None
        ok = predicted == expected
        passed += int(ok)

        if expected and predicted:
            tp += 1
        elif not expected and predicted:
            fp += 1
        elif expected and not predicted:
            fn += 1
        else:
            tn += 1

        details = (
            f"score={result['similarity']:.3f}, "
            f"distance={result['distance_m']}m"
            if result else "no match"
        )
        print(
            f"{'PASS' if ok else 'FAIL'} | "
            f"expected={str(expected):<5} predicted={str(predicted):<5} | "
            f"{details} | {new_text!r} <> {old_text!r}"
        )

    total = len(DUPLICATE_CASES)
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0
    )

    print(f"Duplicate tests: {passed}/{total} ({passed / total:.1%})")
    print(f"TP={tp}, FP={fp}, FN={fn}, TN={tn}")
    print(
        f"Precision={precision:.1%} | "
        f"Recall={recall:.1%} | F1={f1:.1%}"
    )
    return passed, total

if __name__ == "__main__":
    class_passed, class_total = run_classification_tests()
    dup_passed, dup_total = run_duplicate_tests()

    print("\n=== ROBUSTNESS SUMMARY ===")
    print(f"Classification: {class_passed}/{class_total}")
    print(f"Duplicate detection: {dup_passed}/{dup_total}")
    print(
        "Interpret failures as areas to investigate; "
        "do not tune against this set and call it independent validation."
    )
