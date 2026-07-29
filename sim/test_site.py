"""
Full site regression. Lives in the repo so it survives, unlike /tmp.

Run:  python3 sim/test_site.py
Needs: pip install playwright && python3 -m playwright install chromium
"""
import sys, csv, glob, os

BAD = []
def chk(name, ok, detail=""):
    print(("  ok      " if ok else "  BROKEN  ") + name + (f"  [{detail}]" if detail else ""))
    if not ok:
        BAD.append(name)


def data_consistency():
    """Every headline number on the site must exist in a CSV."""
    print("\n[SITE NUMBERS TRACE BACK TO DATA]")
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html = "".join(open(f).read() for f in glob.glob(os.path.join(root, "finch/*.html")))
    simd = os.path.join(root, "sim")

    v2 = list(csv.DictReader(open(os.path.join(simd, "regime_v2.csv"))))
    for row in v2:
        g = float(row["improvement_pct"])
        # only the five presets the site actually offers
        if "Low-k" in row["case"] or "25 W" in row["case"]:
            continue
        chk(f"regime_v2 {row['case'][:24]:26s} {g:5.1f}%", f"{g:.1f}%" in html)

    air = list(csv.DictReader(open(os.path.join(simd, "airflow_test.csv"))))[-1]
    for lbl, key in [("claimed", "gain_v4_flat"), ("honest", "gain_v4_air"),
                     ("rebuilt", "gain_v5_air")]:
        v = float(air[key])
        chk(f"airflow {lbl:8s} {v:+6.1f}%", f"{abs(v):.1f}%" in html)


def no_contradictions():
    print("\n[PAGE DOES NOT CONTRADICT ITSELF]")
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    f = open(os.path.join(root, "finch/findings.html")).read()
    chk("no bare 'No radiation' claim", "No radiation, which would matter" not in f)
    chk("no bare 'Steady state only' claim",
        "<li>Steady state only. No transients" not in f)
    chk("no bare '15% floor' claim",
        "<li>Its two constants, a 15% floor" not in f)
    chk("radiation documented", "Stefan-Boltzmann" in f)
    chk("channel model documented", "channel starvation" in f.lower())
    chk("control group requirements stated", "Equal material allocation" in f)
    chk("future scope present", "Future scope" in f)
    chk("no process narrative", "BUG " not in f and "I proved" not in f
        and "my own" not in f)
    chk("no strikethrough retractions", "<s>" not in f)
    chk("sections balanced",
        f.count("<section") == f.count("</section>"),
        f"{f.count('<section')} vs {f.count('</section>')}")


def browser():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("\n[BROWSER] skipped, playwright not installed")
        return
    print("\n[BROWSER]")
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with sync_playwright() as p:
        b = p.chromium.launch()
        for page in ("home.html", "index.html", "findings.html"):
            for w, h in ((1440, 900), (834, 1112), (412, 880)):
                q = b.new_page(viewport={"width": w, "height": h},
                               is_mobile=(w < 500), has_touch=(w < 500))
                errs = []
                q.on("pageerror", lambda e: errs.append(str(e)))
                q.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
                q.goto(f"file://{root}/finch/{page}")
                q.wait_for_timeout(1700)
                ov = q.evaluate("()=>document.documentElement.scrollWidth>window.innerWidth+2")
                chk(f"{page} @{w}", (not ov) and len(errs) == 0,
                    f"overflow={ov} errors={len(errs)}")
                q.close()

        t = b.new_page(viewport={"width": 1340, "height": 900})
        te = []
        t.on("pageerror", lambda e: te.append(str(e)))
        t.goto(f"file://{root}/finch/index.html")
        t.wait_for_timeout(2200)
        chk("derived choke gap present",
            abs(t.evaluate("()=>chokeGap()*1000") - 4.645) < 0.05)
        chk("radiation on", t.evaluate("()=>RADIATION"))
        t.click('[data-mode="me"]')
        t.wait_for_timeout(1800)
        t.click("#run")
        t.wait_for_timeout(12000)
        if "Stop" in t.inner_text("#run"):
            t.click("#run")
        t.wait_for_timeout(500)
        chk("archive fills", t.evaluate("()=>archive.size") > 25,
            f"{t.evaluate('()=>archive.size')} of 100")
        chk("no JS errors", len(te) == 0, str(te[:2]))
        b.close()


if __name__ == "__main__":
    print("=" * 70)
    print("FINCH site regression")
    print("=" * 70)
    data_consistency()
    no_contradictions()
    browser()
    print("\n" + "=" * 70)
    print("BROKEN:", BAD if BAD else "nothing")
    print("=" * 70)
    sys.exit(1 if BAD else 0)
