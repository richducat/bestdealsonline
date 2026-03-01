-- DealTruth MVP schema for Cloudflare D1 (SQLite)
-- Canonical product records + normalized offers + historical prices + score snapshots.

CREATE TABLE IF NOT EXISTS asins (
  asin TEXT PRIMARY KEY,
  title TEXT,
  description TEXT,
  brand TEXT,
  category TEXT,
  image_url TEXT,
  affiliate_link TEXT,
  merchant TEXT DEFAULT 'Amazon',
  icon_name TEXT,
  rating REAL,
  reviews INTEGER,
  first_seen_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
  last_seen_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
  status TEXT NOT NULL DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS offers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  asin TEXT NOT NULL,
  observed_at TEXT NOT NULL,
  source TEXT NOT NULL DEFAULT 'paapi',
  seller_id TEXT NOT NULL DEFAULT '',
  seller_name TEXT,
  seller_rating REAL,
  seller_rating_count INTEGER,
  is_prime INTEGER NOT NULL DEFAULT 0,
  is_fba INTEGER NOT NULL DEFAULT 0,
  ships_from_amazon INTEGER NOT NULL DEFAULT 0,
  sold_by_amazon INTEGER NOT NULL DEFAULT 0,
  condition TEXT NOT NULL DEFAULT 'new',
  item_price REAL,
  shipping REAL DEFAULT 0,
  coupon REAL DEFAULT 0,
  promo_discounts REAL DEFAULT 0,
  subscribe_save REAL DEFAULT 0,
  effective_price REAL NOT NULL,
  currency TEXT NOT NULL DEFAULT 'USD',
  offer_json TEXT,
  FOREIGN KEY (asin) REFERENCES asins(asin),
  UNIQUE (asin, observed_at, seller_id, condition)
);

CREATE TABLE IF NOT EXISTS price_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  asin TEXT NOT NULL,
  observed_at TEXT NOT NULL,
  offer_id INTEGER,
  effective_price REAL NOT NULL,
  buy_box_price REAL,
  shipping REAL DEFAULT 0,
  coupon REAL DEFAULT 0,
  promo_discounts REAL DEFAULT 0,
  subscribe_save REAL DEFAULT 0,
  currency TEXT NOT NULL DEFAULT 'USD',
  source TEXT NOT NULL DEFAULT 'paapi',
  FOREIGN KEY (asin) REFERENCES asins(asin),
  FOREIGN KEY (offer_id) REFERENCES offers(id),
  UNIQUE (asin, observed_at)
);

CREATE TABLE IF NOT EXISTS score_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  asin TEXT NOT NULL,
  observed_at TEXT NOT NULL,
  dealtruth_score INTEGER NOT NULL,
  effective_price REAL,
  baseline_price_90d REAL,
  real_discount_pct REAL,
  percentile_180d REAL,
  rarity_score REAL,
  volatility REAL,
  quality_score REAL,
  seller_trust_score REAL,
  urgency_score REAL,
  scam_penalty REAL,
  confidence_level TEXT,
  confidence_reason TEXT,
  buy_wait_label TEXT,
  drop_chance_7d REAL,
  not_meaningful_deal INTEGER NOT NULL DEFAULT 0,
  components_json TEXT,
  FOREIGN KEY (asin) REFERENCES asins(asin),
  UNIQUE (asin, observed_at)
);

-- Optional per-category weight tuning overrides.
CREATE TABLE IF NOT EXISTS category_weight_overrides (
  category TEXT PRIMARY KEY,
  real_discount_weight REAL NOT NULL,
  rarity_weight REAL NOT NULL,
  quality_weight REAL NOT NULL,
  trust_weight REAL NOT NULL,
  urgency_weight REAL NOT NULL,
  updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_asins_category ON asins(category);
CREATE INDEX IF NOT EXISTS idx_offers_asin_observed_at ON offers(asin, observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_price_snapshots_asin_observed_at ON price_snapshots(asin, observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_score_snapshots_asin_observed_at ON score_snapshots(asin, observed_at DESC);

CREATE VIEW IF NOT EXISTS latest_scores AS
SELECT s.*
FROM score_snapshots s
JOIN (
  SELECT asin, MAX(observed_at) AS observed_at
  FROM score_snapshots
  GROUP BY asin
) latest
  ON latest.asin = s.asin
 AND latest.observed_at = s.observed_at;
