# BDO ops

## Lead mailer (send_lead_deals.py)
Runs on the CadetCatch Lightsail box (`ssh -i ~/.ssh/cadetcatch_lightsail_deploy_ed25519 ubuntu@api.cadetcatch.com`),
deployed at `/opt/bdo-lead-mailer/` with a venv (google-auth), root cron every 15 min.
- Reads Firestore `leads` (service account key at `/etc/bdo-lead-mailer-sa.json`, NOT in git).
- Sends the Penny "3 best real deals" email via the eb28.co cPanel relay
  (creds reused from `/etc/cadetcatch-access-api.env`).
- Stamps `emailedAt` + `emailStatus` so each address is emailed at most once, ever.
- Log: `/var/log/bdo-lead-mailer.log` on the box.
This file is the source of truth; the deployed copy should match it.
