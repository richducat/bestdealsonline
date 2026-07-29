#!/usr/bin/env python3
"""BestDealsOnline lead mailer.

Every run: finds Firestore `leads` docs that have an email and no
`emailedAt`, builds a Penny-voice "3 best real deals" email from the
live site catalog, sends it through the eb28.co cPanel relay, and
stamps the lead so it never double-sends. One email per address per
run; an address that was ever emailed is skipped forever.

Runs on the CadetCatch Lightsail box (always on, SMTP creds already
in /etc/cadetcatch-access-api.env). Cron: every 15 minutes.
"""

import json
import logging
import os
import re
import smtplib
import ssl
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import google.auth.transport.requests
from google.oauth2 import service_account

SA_KEY_PATH = "/etc/bdo-lead-mailer-sa.json"
SMTP_ENV_PATH = "/etc/cadetcatch-access-api.env"
STATE_LOG = "/var/log/bdo-lead-mailer.log"
PROJECT = "bestdealsonline-us"
BASE = f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents"
CATALOG_URL = "https://bestdealsonline.us/data/products.json"
AFF_TAG = "bestdeals00d9-20"
FROM_NAME = "Penny at BestDealsOnline"
MAX_PER_RUN = 20

logging.basicConfig(
    filename=STATE_LOG if os.access(os.path.dirname(STATE_LOG), os.W_OK) else None,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("bdo-lead-mailer")

CATEGORY_MAP = [
    (r"tv|monitor|charg|cable|speaker|headphone|earbud|router|ssd|drive|power bank|dash cam|webcam|tablet|tech|electronic|laptop|phone", "Electronics"),
    (r"kitchen|air fryer|coffee|espresso|pan|skillet|knife|blender|cook|baking|kettle|rice|thermometer", "Kitchen"),
    (r"kid|toy|school|backpack|lunch|toddler|baby|child", "Kids"),
    (r"tool|drill|wrench|garage|work ?glove|grill", "Tools"),
    (r"beauty|skin|hair|makeup|groom", "Beauty"),
    (r"fit|gym|yoga|dumbbell|exercise|workout", "Fitness"),
    (r"pet|dog|cat|litter", "Pets"),
]


def gtoken():
    creds = service_account.Credentials.from_service_account_file(
        SA_KEY_PATH, scopes=["https://www.googleapis.com/auth/datastore"]
    )
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token


def fs_request(token, method, path, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def fields_to_dict(fields):
    out = {}
    for k, v in (fields or {}).items():
        out[k] = list(v.values())[0]
    return out


def load_smtp_env():
    env = {}
    with open(SMTP_ENV_PATH) as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip('"').strip("'")
    return {
        "host": env.get("CADETCATCH_SMTP_HOST"),
        "port": int(env.get("CADETCATCH_SMTP_PORT", "465")),
        "user": env.get("CADETCATCH_SMTP_USERNAME"),
        "password": env.get("CADETCATCH_SMTP_PASSWORD"),
        "sender": env.get("CADETCATCH_INVITE_EMAIL_FROM", env.get("CADETCATCH_SMTP_USERNAME")),
    }


def load_catalog():
    with urllib.request.urlopen(CATALOG_URL, timeout=30) as resp:
        return json.load(resp)["items"]


def match_category(looking_for):
    text = (looking_for or "").lower()
    for pattern, cat in CATEGORY_MAP:
        if re.search(pattern, text):
            return cat
    return "Home"


def score_item(item, words):
    title = item.get("title", "").lower()
    return sum(1 for w in words if len(w) > 2 and w in title)


def pick_items(catalog, looking_for, count=3):
    words = re.split(r"[^a-z0-9]+", (looking_for or "").lower())
    cat = match_category(looking_for)
    in_cat = [i for i in catalog if i.get("category") == cat and i.get("affiliateLink")]
    ranked = sorted(in_cat, key=lambda i: (-score_item(i, words), -(i.get("reviews") or 0)))
    picks, seen = [], set()
    for item in ranked:
        t = item.get("title")
        if t in seen:
            continue
        seen.add(t)
        picks.append(item)
        if len(picks) == count:
            break
    return cat, picks


def budget_phrase(budget):
    return budget.lower() if budget else "your budget"


def search_link(looking_for, budget):
    q = looking_for or ""
    if budget and budget.lower().startswith("under"):
        q += " " + budget.lower()
    return (
        "https://www.amazon.com/s?k=" + urllib.parse.quote(q.strip())
        + f"&tag={AFF_TAG}&utm_source=bestdealsonline&utm_medium=email&utm_campaign=penny_lead"
    )


def build_email(lead, cat, picks):
    looking = lead.get("lookingFor", "something great")
    budget = lead.get("budget", "")
    slink = search_link(looking, budget)

    def pick_html(i, item):
        return (
            f'<tr><td style="padding:10px 0;border-bottom:1px solid #EDE0CE">'
            f'<div style="font-weight:700;color:#382C22">{i}. {item.get("title")}</div>'
            f'<div style="font-size:13px;color:#6B584A;margin-top:2px">{item.get("rating","4.5")}★ · a researched pick from our {cat} list</div>'
            f'<a href="{item.get("affiliateLink")}" style="display:inline-block;margin-top:6px;font-size:13px;font-weight:700;color:#B85C38">See today&rsquo;s price on Amazon &rarr;</a>'
            f"</td></tr>"
        )

    picks_html = "".join(pick_html(i + 1, p) for i, p in enumerate(picks)) or (
        '<tr><td style="padding:10px 0;color:#6B584A">Our researched list for this category is at '
        '<a href="https://bestdealsonline.us" style="color:#B85C38">bestdealsonline.us</a>.</td></tr>'
    )

    subject = f"your {looking.strip()[:40]} picks are in \U0001F440"
    html = f"""
<div style="font-family:Inter,-apple-system,Segoe UI,Roboto,sans-serif;background:#FAF5EE;padding:24px">
 <div style="max-width:560px;margin:0 auto;background:#fff;border-radius:16px;padding:28px;border:1px solid #EDE0CE">
  <div style="font-weight:800;font-size:18px;color:#382C22">hiii, it's Penny \U0001F44B\U0001F495</div>
  <p style="color:#382C22;line-height:1.6">you asked me for the best real deals on <b>{looking}</b> ({budget_phrase(budget)}) — so I did the digging. here's the play:</p>
  <p style="color:#382C22;line-height:1.6"><b>first, your live search</b> — this one's sorted for {budget_phrase(budget)} and shows today's actual prices:<br>
  <a href="{slink}" style="display:inline-block;margin-top:8px;background:#B85C38;color:#FAF5EE;text-decoration:none;font-weight:700;padding:12px 20px;border-radius:999px">See the live matches on Amazon &rarr;</a></p>
  <p style="color:#382C22;line-height:1.6;margin-bottom:4px"><b>and here are researched picks from our {cat} list:</b></p>
  <table style="width:100%;border-collapse:collapse">{picks_html}</table>
  <p style="color:#382C22;line-height:1.6;margin-top:18px"><b>before you tap buy:</b> run the price through me first — paste the link at
  <a href="https://bestdealsonline.us/deal-check.html" style="color:#B85C38;font-weight:700">bestdealsonline.us/deal-check</a> and I'll tell you if that "sale" is real or if they're playing you \U0001F6A9</p>
  <p style="font-size:12px;color:#6B584A;line-height:1.6;margin-top:22px;border-top:1px solid #EDE0CE;padding-top:14px">
   You asked for this one email on bestdealsonline.us — we won't email you again unless you ask.
   As an Amazon Associate, we earn from qualifying purchases. Prices change fast; always confirm on Amazon.<br>
   BestDealsOnline &middot; an EB28 property &middot; Melbourne, FL
  </p>
 </div>
</div>"""
    text = (
        f"hi, it's Penny from BestDealsOnline!\n\nYou asked for the best real deals on {looking} ({budget_phrase(budget)}).\n\n"
        f"Live matches sorted for your budget: {slink}\n\n"
        + "\n".join(f"{i+1}. {p.get('title')} — {p.get('affiliateLink')}" for i, p in enumerate(picks))
        + "\n\nBefore you buy, check the price is real: https://bestdealsonline.us/deal-check.html\n\n"
        "You asked for this one email — we won't email you again unless you ask. "
        "As an Amazon Associate, we earn from qualifying purchases."
    )
    return subject, html, text


def send_email(smtp, to_addr, subject, html, text):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{FROM_NAME} <{smtp['sender']}>"
    msg["To"] = to_addr
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp["host"], smtp["port"], timeout=30, context=ctx) as server:
        server.login(smtp["user"], smtp["password"])
        server.sendmail(smtp["sender"], [to_addr], msg.as_string())


def main():
    token = gtoken()
    smtp = load_smtp_env()
    if not (smtp["host"] and smtp["user"] and smtp["password"]):
        log.error("SMTP env incomplete; aborting")
        sys.exit(1)

    docs = fs_request(token, "GET", "/leads?pageSize=300").get("documents", [])
    catalog = None
    emailed_addresses = set()
    pending = []
    for doc in docs:
        data = fields_to_dict(doc.get("fields"))
        addr = (data.get("email") or "").strip().lower()
        if not addr:
            continue
        if data.get("emailedAt"):
            emailed_addresses.add(addr)
            continue
        pending.append((doc, data, addr))

    sent = 0
    for doc, data, addr in pending:
        if sent >= MAX_PER_RUN:
            break
        if addr in emailed_addresses:
            # someone re-submitted; stamp without re-sending
            mark(token, doc, status="duplicate")
            continue
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$", addr):
            mark(token, doc, status="invalid-email")
            continue
        if catalog is None:
            catalog = load_catalog()
        cat, picks = pick_items(catalog, data.get("lookingFor"))
        subject, html, text = build_email(data, cat, picks)
        try:
            send_email(smtp, addr, subject, html, text)
        except Exception:
            log.exception("send failed for %s", addr)
            continue
        emailed_addresses.add(addr)
        mark(token, doc, status="sent")
        sent += 1
        log.info("sent picks email to %s (lookingFor=%r)", addr, data.get("lookingFor"))

    log.info("run complete: %d sent, %d pending seen", sent, len(pending))
    print(f"sent={sent} pending={len(pending)}")


def mark(token, doc, status):
    doc_path = "/" + "/".join(doc["name"].split("/")[5:])
    now = datetime.now(timezone.utc).isoformat()
    fs_request(
        token,
        "PATCH",
        f"{doc_path}?updateMask.fieldPaths=emailedAt&updateMask.fieldPaths=emailStatus",
        {"fields": {"emailedAt": {"stringValue": now}, "emailStatus": {"stringValue": status}}},
    )


if __name__ == "__main__":
    main()
