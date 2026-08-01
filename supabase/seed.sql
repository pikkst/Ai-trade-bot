-- Seed data for local development
-- Synthetic, deterministic, safe to commit, free of production identifiers.

-- Workspace
INSERT INTO workspaces (id, name, slug)
VALUES ('00000000-0000-0000-0000-000000000001', 'Daily Roast AI', 'daily-roast-ai');

-- Symbol metadata
INSERT INTO symbols (id, symbol, base_asset, quote_asset, exchange)
VALUES
  ('00000000-0000-0000-0000-000000000010', 'BTC/EUR', 'BTC', 'EUR', 'binance');