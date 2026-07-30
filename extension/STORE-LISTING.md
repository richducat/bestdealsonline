# Ask Penny — Chrome Web Store submission kit

## Richard's steps (the only parts that need you, ~10 minutes)
1. Go to https://chrome.google.com/webstore/devconsole and sign in with richducat@gmail.com.
2. Pay the one-time **$5** developer registration fee.
3. Click **New item** → upload `extension/dist/ask-penny.zip` from this repo.
4. Paste the listing fields below, upload the screenshots from `extension/store-assets/`, submit for review.
Review usually takes 1–3 days for a no-permissions extension like this.

## Listing fields

**Name:** Ask Penny — Amazon Deal Checker

**Summary (132 chars max):**
Is that Amazon "sale" real? Penny reads the price on the page and tells you: buy it, wait, or it's a fake discount.

**Description:**
Half of those "50% off!" tags on Amazon are measured against prices nobody ever paid.

Ask Penny tells you the truth before your money leaves your pocket. Open any Amazon product page and Penny automatically checks the price against what the product normally costs:

✅ "Buy it — you're really saving $18"
🚩 "Skip it — that sale tag is a trick"
😐 "No rush — this is the everyday price"

She also gives you the number to hold out for ("a real deal on this is $51 or less") and a one-tap search to see if another store beats the price.

Everything happens on your device. No account, no tracking, no data collection — see the privacy policy.

From the team at bestdealsonline.us. As an Amazon Associate, we earn from qualifying purchases.

**Category:** Shopping
**Language:** English
**Privacy policy URL:** https://bestdealsonline.us/extension-privacy.html
**Single purpose description:** Shows a deal-quality verdict for the Amazon product page the user is viewing, computed locally from prices visible on that page.
**Permissions justification (storage):** Keeps a local count of checks run; no other data stored, no network requests.

## Build
`cd extension && npx esbuild src/content.js --bundle --format=iife --outfile=dist/content.js --minify`
then zip manifest.json, dist/, icons/ into dist/ask-penny.zip (see build step in repo).

## Screenshots (1280x800 required by the store)
Open `extension/test/mock-product.html` via a local server with the extension loaded
(chrome://extensions → Developer mode → Load unpacked → this folder), or on a real
Amazon page, and capture the verdict card in both a "Buy it" and a "Fake discount" state.
