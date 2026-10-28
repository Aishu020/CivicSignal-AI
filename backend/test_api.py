import json
import sqlite3
import urllib.error
import urllib.request
from urllib.parse import urlencode

BASE = "http://127.0.0.1:8000"
DB = "civicsignal.db"
PREFIX = "API_TEST_CivicSignal"


def request(method, path, data=None):
    headers = {}
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(
        BASE + path, data=body, headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            raw = response.read().decode()
            content_type = response.headers.get("Content-Type", "")
            if "text/csv" in content_type:
                return response.status, raw
            return response.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            result = json.loads(raw)
        except Exception:
            result = raw
        return e.code, result

def check(name, passed, detail=""):
    print(f"{'PASS' if passed else 'FAIL'} | {name}" +
          (f" | {detail}" if detail else ""))

created_ids = []

try:
    # Health and read endpoints
    status, health = request("GET", "/api/health")
    check("Health endpoint", status == 200 and health.get("status") == "healthy")

    status, before = request("GET", "/api/summary")
    check("Dashboard summary", status == 200 and "total" in before)

    status, initial = request("GET", "/api/incidents")
    check("Incident listing", status == 200 and isinstance(initial, list))

    # Create two closely located, similarly worded reports
    reports = [
        {
            "title": PREFIX + " streetlight failure A",
            "description": "Streetlight is not working near the public library entrance.",
            "neighborhood": "API Test Area",
            "latitude": 11.0168,
            "longitude": 76.9558,
            "severity": 3,
            "public_impact": 3
        },
        {
            "title": PREFIX + " streetlight failure B",
            "description": "Street lamp has stopped working near the public library entrance.",
            "neighborhood": "API Test Area",
            "latitude": 11.0169,
            "longitude": 76.9559,
            "severity": 4,
            "public_impact": 4
        }
    ]

    results = []
    for report in reports:
        status, result = request("POST", "/api/incidents", report)
        ok = status == 200 and isinstance(result, dict) and "id" in result
        check("Create incident", ok, f"HTTP {status}")
        if ok:
            created_ids.append(result["id"])
            results.append(result)

    if len(results) == 2:
        check("AI category returned",
              all(bool(r.get("category")) for r in results),
              ", ".join(str(r.get("category")) for r in results))
        check("Priority score and level returned",
              all(r.get("priority_score") is not None and r.get("priority_level")
                  for r in results))
        dup = results[1].get("duplicate_candidate")
        check("Duplicate detection response present", "duplicate_candidate" in results[1],
              str(dup))
        check("Duplicate linked to first report",
              bool(dup) and dup.get("id") == results[0]["id"],
              "Inspect candidate above if not linked")

        # Filtering and status update
        status, filtered = request(
            "GET", "/api/incidents?" +
            urlencode({"q": PREFIX})
        )
        check("Search/filter endpoint", status == 200 and len(filtered) >= 2)

        status, updated = request(
            "PATCH",
            f"/api/incidents/{results[0]['id']}/status?status=In%20Progress"
        )
        check("Status update", status == 200 and updated.get("status") == "In Progress")

        status, summary = request("GET", "/api/summary")
        check("Summary reflects saved reports",
              status == 200 and summary.get("total", 0) >= before.get("total", 0) + 2)

        status, csv_data = request("GET", "/api/export.csv")
        check("CSV export", status == 200 and isinstance(csv_data, str))
    else:
        print("Skipping dependent checks because both reports were not created.")

    # Invalid payload should be rejected
    status, invalid = request("POST", "/api/incidents", {"title": "x"})
    check("Invalid payload rejected", status == 422, f"HTTP {status}")

except Exception as exc:
    print("TEST ERROR:", repr(exc))

finally:
    # Remove only incidents created by this test; preserve all other records.
    if created_ids:
        with sqlite3.connect(DB) as conn:
            placeholders = ",".join("?" for _ in created_ids)
            conn.execute(
                f"DELETE FROM incidents WHERE id IN ({placeholders})",
                created_ids
            )
        print(f"\nCleanup: removed {len(created_ids)} test incident(s).")

print("\nAPI integration test run complete.")
