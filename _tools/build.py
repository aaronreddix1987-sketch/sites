#!/usr/bin/env python3
"""Build one-page site from a JSON intake: python3 _tools/build.py intake.json OUTDIR
Intake keys: name, kind, area, phone, tagline, services[list], hours[list of [day, time]],
about (optional), area_text (optional), photos[list of local image paths] (optional),
accent (optional hex), sample (bool)."""
import html, json, os, re, sys, datetime, shutil
E = lambda s: html.escape(str(s or "").strip(), quote=True)
ACCENTS = ["#1f5f8b", "#2f6b3a", "#8a3b12", "#4b3a8f", "#9a2f4b", "#175e63", "#3d4a5c"]

def phone(p):
    d = re.sub(r"\D", "", p or "")
    if len(d) == 11 and d[0] == "1": d = d[1:]
    if len(d) != 10: raise SystemExit("phone must be a 10-digit US number")
    return "+1" + d, f"({d[:3]}) {d[3:6]}-{d[6:]}"

def main(src, out):
    j = json.load(open(src))
    for k in ("name", "kind", "area", "phone"):
        if not str(j.get(k) or "").strip(): raise SystemExit(f"missing {k}")
    services = [s for s in (j.get("services") or []) if str(s).strip()][:12]
    hours = [h for h in (j.get("hours") or []) if len(h) == 2][:10]
    if not services: raise SystemExit("missing services")
    if not hours: raise SystemExit("missing hours")
    e164, pretty = phone(j["phone"])
    accent = j.get("accent") if re.fullmatch(r"#[0-9a-fA-F]{6}", str(j.get("accent") or "")) else ACCENTS[sum(map(ord, j["name"])) % len(ACCENTS)]
    os.makedirs(out, exist_ok=True)
    pics = []
    for i, p in enumerate((j.get("photos") or [])[:6]):
        ext = os.path.splitext(p)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".webp"): continue
        name = f"photo{i+1}{'.jpg' if ext == '.jpeg' else ext}"
        try:
            from PIL import Image, ImageOps
            im = ImageOps.exif_transpose(Image.open(p)).convert("RGB"); im.thumbnail((1400, 1400))
            name = f"photo{i+1}.jpg"; im.save(os.path.join(out, name), "JPEG", quality=82)
        except Exception:
            shutil.copy(p, os.path.join(out, name))
        pics.append(name)
    sample = bool(j.get("sample"))
    alt = E(j.get("kind"))
    rep = {
        "name": E(j["name"]), "kind": E(j["kind"]), "area": E(j["area"]),
        "tagline": E(j.get("tagline") or f"{j['kind']} serving {j['area']}. Call to talk about your job."),
        "phone_e164": e164, "phone_pretty": pretty, "accent": accent, "year": str(datetime.date.today().year),
        "services": "".join(f"<li>{E(s)}</li>" for s in services),
        "hours": "".join(f"<tr><td>{E(d)}</td><td>{E(t)}</td></tr>" for d, t in hours),
        "area_text": E(j.get("area_text") or f"We serve {j['area']}. Not sure if we cover you? Call and ask."),
        "about": f'<section><div class="wrap"><h2>About us</h2><p>{E(j["about"])}</p></div></section>' if str(j.get("about") or "").strip() else "",
        "photos": ('<section><div class="wrap"><h2>Our work</h2><div class="photos">' + "".join(f'<img src="{n}" alt="{alt} work photo {i+1}" loading="lazy">' for i, n in enumerate(pics)) + "</div></div></section>") if pics else "",
        "sample_banner": '<div class="banner">SAMPLE SITE. This is a made-up business built by Total Transformation Inc. to show our one-page website service. The phone number is fictional.</div>' if sample else "",
        "noindex": '<meta name="robots" content="noindex">' if sample else "",
    }
    t = open(os.path.join(os.path.dirname(__file__), "template.html")).read()
    for k, v in rep.items(): t = t.replace("{{" + k + "}}", v)
    if "{{" in t: raise SystemExit("template left a placeholder")
    open(os.path.join(out, "index.html"), "w").write(t)
    print("built", os.path.join(out, "index.html"), "photos:", len(pics))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
