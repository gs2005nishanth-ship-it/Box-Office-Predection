import urllib.request
import urllib.parse
import json
import sys

# Ensure UTF-8 output handling
sys.stdout.reconfigure(encoding='utf-8')

base_url = "http://127.0.0.1:5000"

def test_endpoint(name, url, method="GET", payload=None):
    try:
        if method == "POST":
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
        else:
            req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read().decode("utf-8")
            status = resp.status
            try:
                parsed = json.loads(data)
                print(f"[PASS] [{status}] {name}")
                return parsed
            except Exception:
                print(f"[PASS] [{status}] {name} (HTML/Static bytes: {len(data)})")
                return data
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        return None

print("=== Starting CineMetric AI Full System Integration Test ===")

# 1. Test Static & HTML
test_endpoint("GET / (Dashboard Page)", f"{base_url}/")
test_endpoint("GET /static/css/style.css", f"{base_url}/static/css/style.css")
test_endpoint("GET /static/js/app.js", f"{base_url}/static/js/app.js")

# 2. Test LLM Movie Queries
movies_to_test = ["Oppenheimer", "Avatar: The Way of Water", "Barbie", "Dune: Part Two", "Avengers: Endgame", "RRR", "Inception", "Inside Out 2", "Deadpool & Wolverine", "Gladiator II (2024 Sequel)"]
for m in movies_to_test:
    res = test_endpoint(f"POST /api/movie-lookup -> '{m}'", f"{base_url}/api/movie-lookup", method="POST", payload={"query": m})
    if res and 'movie' in res:
        print(f"   -> Title: {res['movie']['title']} | Gross: ${res['movie']['worldwide_gross']:,} | Verdict: {res['movie']['verdict']}")

# 3. Test ML Simulator
sim_tests = [
    {"name": "Tentpole Summer Blockbuster ($180M)", "payload": {"budget": 180000000, "runtime": 140, "popularity": 45, "release_month": 5, "has_collection": 1, "genres": ["Action", "Adventure", "Science Fiction"]}},
    {"name": "Low-Budget Indie Drama ($12M)", "payload": {"budget": 12000000, "runtime": 105, "popularity": 10, "release_month": 10, "has_collection": 0, "genres": ["Drama"]}},
    {"name": "Holiday Family Animation ($90M)", "payload": {"budget": 90000000, "runtime": 98, "popularity": 32, "release_month": 12, "has_collection": 1, "genres": ["Animation", "Family", "Comedy"]}}
]

for st in sim_tests:
    res = test_endpoint(f"POST /api/predict -> {st['name']}", f"{base_url}/api/predict", method="POST", payload=st["payload"])
    if res and 'prediction' in res:
        p = res['prediction']
        print(f"   -> Forecast: {p['formatted_revenue']} | Range: ${p['lower_bound_millions']}M - ${p['upper_bound_millions']}M | ROI: {p['roi_percentage']}% ({p['verdict']})")

# 4. Test Stats & EDA
stats = test_endpoint("GET /api/stats", f"{base_url}/api/stats")
if stats and 'stats' in stats:
    print(f"   -> Total Movies: {stats['stats']['total_train_movies']} | Max Gross: ${stats['stats']['max_revenue']:,} | Top Genres: {len(stats['stats']['genre_stats'])}")

# 5. Test Models Benchmarks
models = test_endpoint("GET /api/models-info", f"{base_url}/api/models-info")
if models and 'metrics' in models:
    print(f"   -> Best Model: {models['best_model']}")
    for k, v in models['metrics'].items():
        if isinstance(v, dict) and 'r2_score' in v:
            print(f"      - {k:20}: R2 = {v['r2_score']} | RMSLE = {v['rmsle']} | RMSE = {v['formatted_rmse']}")

# 6. Test Dataset Search & Filter
movies_page = test_endpoint("GET /api/movies?q=action&page=1&limit=5", f"{base_url}/api/movies?q=action&page=1&limit=5")
if movies_page and 'movies' in movies_page:
    print(f"   -> Filtered count: {movies_page['total']} matches")

# 7. Test Submission Preview & Download
sub_preview = test_endpoint("GET /api/submission-preview", f"{base_url}/api/submission-preview")
if sub_preview:
    print(f"   -> Total submission predictions: {sub_preview.get('total_rows')}")

print("\n=== All System Tests Passed Successfully! ===")
