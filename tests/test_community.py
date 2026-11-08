"""Offline checks for the community checker. Run: python3 tests/test_community.py"""
import importlib.util, pathlib
spec = importlib.util.spec_from_file_location("vq", pathlib.Path(__file__).parents[1] / "scripts/verify_quotes.py")
vq = importlib.util.module_from_spec(spec); spec.loader.exec_module(vq)

A, B = "https://a.example/doc", "https://b.example/doc"
PAGES = {A: vq.norm("Readers do not block writers. Breakfast is served."), B: vq.norm("best balance between performance and safety")}

def fake(url):
    if url.endswith(".pdf"):
        raise ValueError("PDF source: PDF checking is in Quoteproof Pro")
    if url not in PAGES:
        raise OSError("down")
    return PAGES[url]

claims = [
    {"claim": "exact", "source": A, "quote": "Readers do NOT block writers."},
    {"claim": "wrong page", "source": A, "quote": "best balance between performance and safety"},
    {"claim": "partial word", "source": A, "quote": "fast is served"},
    {"claim": "elided", "source": A, "quote": "Readers … writers"},
    {"claim": "pdf", "source": "https://c.example/paper.pdf", "quote": "x"},
    {"claim": "down", "source": "https://d.example/", "quote": "x"},
]
got = [(r["status"], r.get("detail", "")[:20]) for r in vq.verify(claims, fetch=fake)]
assert [s for s, _ in got] == ["verified", "not_found", "not_found", "not_found", "fetch_failed", "fetch_failed"], got
assert "Pro" in vq.verify([claims[3]], fetch=fake)[0]["detail"]          # elided quote explains the limit
assert "Pro" in vq.verify([claims[4]], fetch=fake)[0]["detail"]          # PDF explains the limit
for bad in ["http://127.0.0.1/", "http://169.254.169.254/", "file:///etc/passwd", "http://[::1]/"]:
    assert not vq.public_url(bad), bad
print("community checker: all checks passed")
