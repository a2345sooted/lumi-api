ALTER TABLE user_water_logs ADD COLUMN drank_at TIMESTAMP WITH TIME ZONE;

-- Initialize drank_at with created_at for existing rows
UPDATE user_water_logs SET drank_at = created_at;

-- Make drank_at NOT NULL after initialization
ALTER TABLE user_water_logs ALTER COLUMN drank_at SET NOT NULL;

-- Default for future inserts
ALTER TABLE user_water_logs ALTER COLUMN drank_at SET DEFAULT CURRENT_TIMESTAMP;

CREATE INDEX idx_user_water_logs_drank_at ON user_water_logs(drank_at);
