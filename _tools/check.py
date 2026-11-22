#!/usr/bin/env python3
"""Check a delivered page: python3 _tools/check.py URL "Business name" PHONE10 [screenshot.png]
Waits up to 12 minutes for GitHub Pages. Exit 0 = OK."""
import re, sys, time, urllib.request
url, name, phone = sys.argv[1], sys.argv[2], re.sub(r"\D", "", sys.argv[3])[-10:]
import html as H
deadline, last = time.time() + 720, ""
while True:
    try:
        req = urllib.request.Request(url + ("&" if "?" in url else "?") + f"t={int(time.time())}", headers={"Cache-Control": "no-cache"})
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read().decode("utf-8", "replace"); code = r.status
        problems = []
        if code != 200: problems.append(f"HTTP {code}")
        if H.escape(name.strip()) not in body and name.strip() not in body: problems.append("business name missing")
        if f'href="tel:+1{phone}"' not in body: problems.append("call button missing or wrong number")
        if "{{" in body: problems.append("unfilled placeholder")
        if 'name="viewport"' not in body: problems.append("not mobile ready")
        if not problems:
            break
        last = ", ".join(problems)
    except Exception as e:
        last = str(e)
    if time.time() > deadline:
        sys.exit("FAILED: " + last)
    time.sleep(30)
if len(sys.argv) > 4:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(viewport={"width": 390, "height": 844})
            pg.goto(url); pg.wait_for_timeout(800); pg.screenshot(path=sys.argv[4], full_page=True); b.close()
        print("screenshot", sys.argv[4])
    except Exception as e:
        print("screenshot skipped:", e)
print("OK", url)
